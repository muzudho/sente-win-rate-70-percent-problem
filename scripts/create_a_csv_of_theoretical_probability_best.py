import traceback
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, EVEN, ABS_OUT_OF_ERROR, UPPER_LIMIT_FAILURE_RATE, Converter, Specification, ThreeRates
from library.file_paths import get_theoretical_probability_best_csv_file_path
from library.database import TheoreticalProbabilityTable, TheoreticalProbabilityBestRecord, TheoreticalProbabilityBestTable


class Automation():


    def __init__(self, spec):
        self._spec = spec
        self._best_win_rate_error = None
        self._best_record = None


    def on_each(self, record):

        error = record.three_rates.a_win_rate - EVEN

        # 誤差が縮まれば更新
        if abs(error) < abs(self._best_win_rate_error):
            is_update = True
        
        # 誤差が同じでも、引き分け率が下がれば更新
        elif error == self._best_win_rate_error and (self._best_record.three_rates.no_win_match_rate is None or record.three_rates.no_win_match_rate < self._best_record.three_rates.no_win_match_rate):
            is_update = True
        
        else:
            is_update = False


        if is_update:
            self._best_win_rate_error = error
            self._best_record = TheoreticalProbabilityBestRecord(
                    turn_system_str=record.turn_system_str,
                    failure_rate=record.failure_rate,
                    p=record.p,
                    span=record.span,
                    t_step=record.t_step,
                    h_step=record.h_step,
                    shortest_coins=record.shortest_coins,
                    upper_limit_coins=record.upper_limit_coins,
                    three_rates=ThreeRates(
                            a_win_rate=record.three_rates.a_win_rate,
                            no_win_match_rate=record.three_rates.no_win_match_rate))


    def execute(self):
        """
        Returns
        -------
        is_terminated : bool
            計算停止
        """

        turn_system_str = Converter.turn_system_to_code(self._spec.turn_system)

        df_d, is_new = TheoreticalProbabilityTable.read_df(spec=self._spec, new_if_it_no_exists=False)

        # 読み込むファイルが存在しなければ無視
        if is_new:
            return True


        # CSVファイルパス（書き込むファイル）
        best_csv_file_path = get_theoretical_probability_best_csv_file_path()


        self._best_record = TheoreticalProbabilityBestTable.create_none_record()

        # a_win_rate と EVEN の誤差
        self._best_win_rate_error = ABS_OUT_OF_ERROR


        # ファイルが存在しなかったなら、空データフレーム作成
        df_b, is_new = TheoreticalProbabilityBestTable.read_df(new_if_it_no_exists=True)

        # ファイルが存在したなら、読込
        if not is_new:
            # （書き込むファイルの）該当レコードのキー
            key_b = (df_b['turn_system']==turn_system_str) & (df_b['failure_rate']==self._spec.failure_rate) & (df_b['p']==self._spec.p)

            # データが既存なら、取得
            if key_b.any():
                self._best_record = TheoreticalProbabilityBestTable.get_record_by_key(df=df_b, key=key_b)

                self._best_win_rate_error = self._best_record.three_rates.a_win_rate - EVEN


        TheoreticalProbabilityBestTable.for_each(df=df_b, on_each=self.on_each)


        if self._best_record.turn_system_str is not None:
            # データフレーム更新
            # 新規レコード追加
            TheoreticalProbabilityBestTable.append_record(df=df_b, record=self._best_record)

            csv_file_path_to_wrote = TheoreticalProbabilityBestTable.to_csv(df=df_b)
            print(f"[{datetime.datetime.now()}][turn_system={self._best_record.turn_system_str}  failure_rate={self._best_record.failure_rate}  p={self._best_record.p}] write a csv to `{csv_file_path_to_wrote}` file ...")
