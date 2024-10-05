import traceback
import datetime
import time

from library import FROZEN_TURN, ALTERNATING_TURN, EVEN, ABS_OUT_OF_ERROR, UPPER_LIMIT_FAILURE_RATE, Converter, Specification, ThreeRates
from library.file_paths import TheoreticalProbabilityBestFilePaths
from library.database import TheoreticalProbabilityTable, TheoreticalProbabilityBestRecord, TheoreticalProbabilityBestTable


# CSV保存間隔（秒）
INTERVAL_SECONDS_FOR_SAVE_CSV = 30


class AutomationOne():


    def __init__(self, df_best):
        """初期化
        
        Parameters
        ----------
        df_best : DataFrame
            データフレーム
        """

        self._df_best = df_best

        self._spec = None
        self._is_update_df_best = False
        self._best_record = None


    def on_match(self, record_tp):

        # ベスト値と比較したい。

        try:
            shall_upsert_record = False

            # 絞り込み。 0～複数件の DataFrame型が返ってくる
            # とりえあず主キーは［先後の決め方］［コインを投げて表も裏も出ない確率］［コインを投げて表が出る確率］の３列
            df_result_set_by_index = TheoreticalProbabilityBestTable.get_result_set_by_index(
                    df=self._df_best,
                    turn_system_name=record_tp.turn_system_name,
                    failure_rate=record_tp.failure_rate,
                    p=record_tp.p)

            
            # TODO 該当なしなら、即、ベスト値追加
            if 0 == len(df_result_set_by_index):
                shall_upsert_record = True

            # 該当する［理論的確率ベストデータ］レコードが既存なら、取得
            else:
                row_index = df_result_set_by_index.index[0]  # 行番号を取得

                # 既存のベスト値
                old_theoretical_a_win_rate = df_result_set_by_index.at[row_index, 'theoretical_a_win_rate']
                old_theoretical_no_win_match_rate = df_result_set_by_index.at[row_index, 'theoretical_no_win_match_rate']

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
                        df_result_set_by_index=df_result_set_by_index,
                        welcome_record=welcome_record)

                if is_dirty_temp:
                    self._is_update_df_best = True


        except KeyError as ex:
            print(f"列名がないという例外が発生中")
            for index, column_name in enumerate(self._df_best.columns.values, 1):
                print(f"({index}) {column_name=}")
            raise # 再スロー


    def get_reocrd_of_best_tp_or_none(self, df_tp):
        """TODO ［理論的確率データ］テーブルから、イーブンに一番近い行を抽出します"""

        df_result_set_by_index = TheoreticalProbabilityTable.get_result_set_by_index(
                df=df_tp,
                turn_system_name=Converter.turn_system_id_to_name(self._spec.turn_system_id),
                failure_rate=self._spec.failure_rate,
                p=self._spec.p)

        # ［Ａさんの勝率］と 0.5 との誤差の絶対値が最小のレコードのセット
        df_result_set = df_result_set_by_index.loc[abs(df_result_set_by_index['theoretical_a_win_rate'] - 0.5) == min(abs(df_result_set_by_index['theoretical_a_win_rate'] - 0.5))]

        # それでも１件に絞り込めない場合、［コインを投げて表も裏も出ない確率］が最小のレコードのセット
        if 1 < len(df_result_set):
            df_result_set = df_result_set_by_index.loc[df_result_set_by_index['theoretical_no_win_match_rate'] == min(df_result_set_by_index['theoretical_no_win_match_rate'])]

            # それでも１件に絞り込めない場合、［上限対局数］が最小のレコードのセット
            if 1 < len(df_result_set):
                df_result_set = df_result_set_by_index.loc[df_result_set_by_index['upper_limit_coins'] == min(df_result_set_by_index['upper_limit_coins'])]


        # 該当レコードがあれば、適当に先頭の１件だけ返す。無ければナンを返す
        if 0 < len(df_result_set):
            return df_result_set_by_index.iloc[0]

        return None


    def execute_one(self, spec):
        """
        
        Returns
        -------
        is_dirty : bool
            ファイル変更の有無
        """

        if self._df_best is None:
            raise ValueError("self._df_best を先に設定しておかなければいけません")

        self._spec = spec
        self._is_update_df_best = False

        turn_system_name = Converter.turn_system_id_to_name(self._spec.turn_system_id)

        # 読み込む［理論的確率データ］ファイルがなければ無視
        df_tp, is_new = TheoreticalProbabilityTable.read_df(spec=self._spec, new_if_it_no_exists=False)

        if df_tp is None:
            print(f"[{datetime.datetime.now()}][turn_system={Converter.turn_system_id_to_name(self._spec.turn_system_id)}  failure_rate={self._spec.failure_rate * 100:.1f}%  p={self._spec.p * 100:.1f}%] スキップ。［理論的確率データ］ファイルがない。")
            return False

        if is_new:
            self._is_update_df_best = True


        # ［理論的確率データ］の各レコードについて
        #
        #   FIXME TPテーブルは行が膨大にあるので、for_each するのは良くない。まず、ベスト・レコードを取得すべき
        #
        record_in_best_tp_or_none = self.get_reocrd_of_best_tp_or_none(df_tp=df_tp)
        if record_in_best_tp_or_none is not None:
            self.on_match(record_tp=record_in_best_tp_or_none)


        return self._is_update_df_best


class AutomationAll():


    def execute_all(self):

        # 書込み先の［理論的確率ベストデータ］ファイルが存在しなかったなら、空データフレーム作成
        df_best, is_new = TheoreticalProbabilityBestTable.read_df(new_if_it_no_exists=True)

        if df_best is None:
            raise ValueError("ここで df_best がナンなのはおかしい")

        # ［理論的確率ベストデータ］新規作成または更新
        automation_one = AutomationOne(df_best=df_best)

        # ［先後の決め方］
        for specified_turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:
            turn_system_name = Converter.turn_system_id_to_name(specified_turn_system_id)

            # ［将棋の引分け率］
            for failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5): # 5％刻み
                specified_failure_rate = failure_rate_percent / 100

                # リセット
                number_of_dirty_rows = 0                # 変更された行数
                number_of_bright_rows = 0               # 変更されなかった行数
                start_time_for_save = time.time()       # CSV保存用タイマー

                # ［将棋の先手勝率］
                for p_percent in range(50, 96):
                    specified_p = p_percent / 100
                    #print(f"[{datetime.datetime.now()}][turn_system_name={turn_system_name}  failure_rate={specified_failure_rate * 100:.1f}  p={specified_p * 100:.1f}] ...")

                    # 仕様
                    spec = Specification(
                            p=specified_p,
                            failure_rate=specified_failure_rate,
                            turn_system_id=specified_turn_system_id)

                    is_dirty_temp = automation_one.execute_one(spec=spec)

                    if is_dirty_temp:
                        number_of_dirty_rows += 1
                    
                    else:
                        number_of_bright_rows += 1
                    

                    if 0 < number_of_dirty_rows:
                        # 指定間隔（秒）でファイル保存
                        end_time_for_save = time.time()
                        if INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - start_time_for_save:
                            csv_file_path_to_wrote = TheoreticalProbabilityBestTable.to_csv(df=df_best)
                            print(f"[{datetime.datetime.now()}][turn_system_name={turn_system_name}  failure_rate={specified_failure_rate * 100:.1f}%  p={specified_p * 100:.1f}] {number_of_dirty_rows} row(s) changed. {number_of_bright_rows} row(s) unchanged. write theoretical probability best to `{csv_file_path_to_wrote}` file ...")

                            # リセット
                            start_time_for_save = time.time()
                            number_of_dirty_rows = 0
                            number_of_bright_rows = 0


                # 忘れずに flush
                if 0 < number_of_dirty_rows:
                    csv_file_path_to_wrote = TheoreticalProbabilityBestTable.to_csv(df=df_best)
                    # specified_p はまだ入ってるはず
                    print(f"[{datetime.datetime.now()}][turn_system_name={turn_system_name}  failure_rate={specified_failure_rate * 100:.1f}%  p={specified_p * 100:.1f}] {number_of_dirty_rows} row(s) changed. {number_of_bright_rows} row(s) unchanged. write theoretical probability best to `{csv_file_path_to_wrote}` file ...")
