import traceback
import datetime
import time

from library import FROZEN_TURN, ALTERNATING_TURN, EVEN, ABS_OUT_OF_ERROR, UPPER_LIMIT_FAILURE_RATE, Converter, Specification, ThreeRates
from library.file_paths import TheoreticalProbabilityBestFilePaths
from library.database import TheoreticalProbabilityTable, TheoreticalProbabilityBestRecord, TheoreticalProbabilityBestTable


# CSV保存間隔（秒）
INTERVAL_SECONDS_FOR_SAVE_CSV = 30


class AutomationOne():


    def __init__(self, spec):
        """初期化
        
        Parameters
        ----------
        spec : Specification
            ［仕様］
        """
        self._spec = spec

        self._df_best = None
        self._is_update_df_best = False
        self._best_record = None


    def on_each(self, record_tp):

        # ベスト値と比較したい。
        # とりえあず主キーは［先後の決め方］［コインを投げて表も裏も出ない確率］［コインを投げて表が出る確率］［目標の点数］［裏番で勝ったときの勝ち点］［表番で勝ったときの勝ち点］の６列

        try:
            shall_upsert_record = False

            # FIXME set_index() するとおかしくなる？
#             print(f"""\
# FIXME set_index() するとおかしくなる？
# {self._df_best.columns.values=}
# {self._df_best.index=}
# """)
            #self._df_best:
            #{self._df_best}

            # 絞り込み。 1件の DataFrame型が返ってくる
            df_result_set_by_primary_key = TheoreticalProbabilityBestTable.get_result_set_by_primary_key(
                    df=self._df_best,
                    turn_system_name=record_tp.turn_system_name,
                    failure_rate=record_tp.failure_rate,
                    p=record_tp.p,
                    span=record_tp.span,
                    t_step=record_tp.t_step,
                    h_step=record_tp.h_step)

            if 1 < len(df_result_set_by_primary_key):
                raise ValueError(f"複数件該当するのはおかしい {len(df_result_set_by_primary_key)=}")
            
            # TODO 該当なしなら、即、ベスト値追加
            if 0 == len(df_result_set_by_primary_key):
                shall_upsert_record = True

            # 該当する［理論的確率ベストデータ］レコードが既存なら、取得
            else:
                row_index = df_result_set_by_primary_key.index[0]  # 行番号を取得

                # 既存のベスト値
                old_theoretical_a_win_rate=df_result_set_by_primary_key.at[row_index, 'theoretical_a_win_rate']
                old_theoretical_no_win_match_rate=df_result_set_by_primary_key.at[row_index, 'theoretical_no_win_match_rate']

                # 誤差が縮まれば更新
                welcome_theoretical_a_win_error = record_tp.theoretical_a_win_rate - EVEN
                if abs(welcome_theoretical_a_win_error) < abs(old_theoretical_a_win_rate - EVEN):
                    shall_upsert_record = True

                # 誤差が同じでも、引分け率が新しく判明したか、引き分け率が下がれば更新
                elif welcome_theoretical_a_win_error == abs(old_theoretical_a_win_rate - EVEN) and (old_theoretical_no_win_match_rate is None or record_tp.theoretical_no_win_match_rate < old_theoretical_no_win_match_rate):
                    shall_upsert_record = True


            if shall_upsert_record:
                # 型変換
                welcome_record = TheoreticalProbabilityBestRecord(
                        turn_system_name=record_tp.turn_system_name,
                        failure_rate=record_tp.failure_rate,
                        p=record_tp.p,
                        span=record_tp.span,
                        t_step=record_tp.t_step,
                        h_step=record_tp.h_step,
                        shortest_coins=record_tp.shortest_coins,
                        upper_limit_coins=record_tp.upper_limit_coins,
                        theoretical_a_win_rate=record_tp.theoretical_a_win_rate,
                        theoretical_no_win_match_rate=record_tp.theoretical_no_win_match_rate)

                # レコードの新規作成または更新
                is_dirty_temp = TheoreticalProbabilityBestTable.upsert_record(
                        df=self._df_best,
                        df_result_set_by_primary_key=df_result_set_by_primary_key,
                        welcome_record=welcome_record)

                if is_dirty_temp:
                    self._is_update_df_best = True


        except KeyError as ex:
            print(f"列名がないという例外が発生中")
            for index, column_name in enumerate(self._df_best.columns.values, 1):
                print(f"({index}) {column_name=}")
            raise # 再スロー


    def execute_one(self):
        """
        
        Returns
        -------
        is_dirty : bool
            ファイル変更の有無
        df_best : DataFrame
            データフレーム
        """

        self._is_update_df_best = False

        turn_system_name = Converter.turn_system_id_to_name(self._spec.turn_system_id)

        # 読み込む［理論的確率データ］ファイルがなければ無視
        df_tp, is_new = TheoreticalProbabilityTable.read_df(spec=self._spec, new_if_it_no_exists=False)

        if is_new:
            return


        # 書込み先の［理論的確率ベストデータ］ファイルが存在しなかったなら、空データフレーム作成
        self._df_best, is_new = TheoreticalProbabilityBestTable.read_df(new_if_it_no_exists=True)


        if is_new:
            self._is_update_df_best = True


        # ［理論的確率データ］の各レコードについて
        TheoreticalProbabilityTable.for_each(df=df_tp, on_each=self.on_each)


        return self._is_update_df_best, self._df_best


class AutomationAll():


    def execute_all(self):
        # ［先後の決め方］
        for specified_turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:
            turn_system_name = Converter.turn_system_id_to_name(specified_turn_system_id)

            # ［将棋の引分け率］
            for failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5): # 5％刻み
                specified_failure_rate = failure_rate_percent / 100

                # リセット
                is_dirty = False    # ファイル変更の有無
                df_best = None

                # ［将棋の先手勝率］
                for p_percent in range(50, 96):
                    specified_p = p_percent / 100

                    # 仕様
                    spec = Specification(
                            p=specified_p,
                            failure_rate=specified_failure_rate,
                            turn_system_id=specified_turn_system_id)

                    # ［理論的確率ベストデータ］新規作成または更新
                    automation_one = AutomationOne(spec=spec)
                    is_dirty_temp, df_best = automation_one.execute_one()

                    if is_dirty_temp:
                        is_dirty = True

                        # TODO ここでタイマーで保存してもいいのでは？

                # ファイルに変更があれば、CSVファイル保存
                if is_dirty:
                    csv_file_path_to_wrote = TheoreticalProbabilityBestTable.to_csv(df=df_best)
                    print(f"[{datetime.datetime.now()}][turn_system_name={turn_system_name}  failure_rate={specified_failure_rate * 100:.1f}%  p={specified_p * 100:.1f}] write theoretical probability best to `{csv_file_path_to_wrote}` file ...")
