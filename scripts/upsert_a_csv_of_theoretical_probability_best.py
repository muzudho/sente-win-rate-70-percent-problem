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
        self._best_theoretical_win_rate_error = None
        self._best_record = None


    def on_each(self, record_tp):

        error = record_tp.theoretical_a_win_rate - EVEN

        # 誤差が縮まれば更新
        if abs(error) < abs(self._best_theoretical_win_rate_error):
            is_update = True
        
        # 誤差が同じでも、引分け率が新しく判明したか、引き分け率が下がれば更新
        elif error == self._best_theoretical_win_rate_error and (self._best_record.theoretical_no_win_match_rate is None or record_tp.theoretical_no_win_match_rate < self._best_record.theoretical_no_win_match_rate):
            is_update = True
        
        else:
            is_update = False


        if is_update:
            self._best_theoretical_win_rate_error = error
            self._best_record = TheoreticalProbabilityBestRecord(
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


    def execute_one(self):
        """
        Returns
        -------
        is_dirty : bool
            ファイル変更の有無
        df_best : DataFrame
            データフレーム
        
        Returns
        -------
        is_dirty : bool
            ファイルに変更があったか？
        df_best : DataFrame
            データフレーム
        """

        is_dirty = False

        turn_system_name = Converter.turn_system_id_to_code(self._spec.turn_system_id)

        # 読み込む［理論的確率データ］ファイルがなければ無視
        df_tp, is_new = TheoreticalProbabilityTable.read_df(spec=self._spec, new_if_it_no_exists=False)

        if is_new:
            return


        # リセット
        self._best_record = TheoreticalProbabilityBestTable.create_none_record()
        self._best_theoretical_win_rate_error = ABS_OUT_OF_ERROR    # a_win_rate と EVEN の誤差


        # 読み込む［理論的確率ベストデータ］ファイルが存在しなかったなら、空データフレーム作成
        df_best, is_new = TheoreticalProbabilityBestTable.read_df(new_if_it_no_exists=True)


        if is_new:
            is_dirty = True
        
        # ［理論的確率ベストデータ］ファイルが存在したなら、読込
        else:
            # 該当する［理論的確率ベストデータ］レコードのキー
            key_b = (df_best['turn_system_name']==turn_system_name) & (df_best['failure_rate']==self._spec.failure_rate) & (df_best['p']==self._spec.p)

            # 該当する［理論的確率ベストデータ］レコードが既存なら、取得
            if key_b.any():
                self._best_record = TheoreticalProbabilityBestTable.get_record_by_key(df=df_best, key=key_b)
                self._best_theoretical_win_rate_error = self._best_record.theoretical_a_win_rate - EVEN


        # ［理論的確率データ］の各レコードについて
        TheoreticalProbabilityTable.for_each(df=df_tp, on_each=self.on_each)


        if self._best_record.turn_system_name is not None:
            # レコードの新規作成または更新
            is_dirty_temp = TheoreticalProbabilityBestTable.upsert_record(df=df_best, record=self._best_record)
            if is_dirty_temp:
                is_dirty = True


        return is_dirty, df_best


class AutomationAll():


    def execute_all(self):
        # ［先後の決め方］
        for specified_turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:
            turn_system_name = Converter.turn_system_id_to_code(specified_turn_system_id)

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

                # ファイルに変更があれば、CSVファイル保存
                if is_dirty:
                    csv_file_path_to_wrote = TheoreticalProbabilityBestTable.to_csv(df=df_best)
                    print(f"[{datetime.datetime.now()}][turn_system_name={turn_system_name}  failure_rate={specified_failure_rate * 100:.1f}%  p={specified_p * 100:.1f}] write theoretical probability best to `{csv_file_path_to_wrote}` file ...")
