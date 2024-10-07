import traceback
import time
import datetime

from library import TERMINATED, YIELD, CALCULATION_FAILED, OUT_OF_P, Converter, SeriesRule
from library.score_board import search_all_score_boards


class Automation():
    """次に、［理論的確率データ］のスリー・レーツ列を更新する"""


    def __init__(self):

        # CSV保存用タイマー
        self._start_time_for_save = None

        # ファイルを新規作成したときに 1、レコードを１件追加したときも 1 増える
        self._number_of_dirty = 0


    def update_three_rates_for_a_file_and_save(self, spec, tp_table, upper_limit_upper_limit_coins):
        """次に、スリー・レーツを更新する

        ファイルの保存機能も含む
        
        Returns
        -------
        calculation_status : int
            計算状況
        """

        def on_score_board_created(score_board):
            pass

        turn_system_name = Converter.turn_system_id_to_name(spec.turn_system_id)

        # リセット
        self._number_of_dirty = 0
        self._start_time_for_save = time.time()       # CSV保存用タイマー


        # 該当行
        list_of_enable_each_row = (tp_table.df['theoretical_a_win_rate']==OUT_OF_P) & (tp_table.df['upper_limit_coins']<=upper_limit_upper_limit_coins)

        # 該当行が１つでもあれば
        if list_of_enable_each_row.any():

            for index, row in tp_table.df[list_of_enable_each_row].iterrows():

                # 指定間隔（秒）でループを抜ける
                end_time_for_save = time.time()
                if INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - self._start_time_for_save:
                    # 途中の行まで処理したところでタイムアップ。譲る（タイムシェアリング）
                    return YIELD

                # FIXME int型の行から、float型が取れてしまう？
                h_step = int(row['h_step'])
                t_step = int(row['t_step'])
                span = int(row['span'])

                # ［シリーズ・ルール］
                specified_series_rule = SeriesRule.make_series_rule_base(
                        spec=spec,
                        h_step=h_step,
                        t_step=t_step,
                        span=span)

                # 確率を求める
                #
                #   NOTE 指数関数的に激重になっていく処理
                #
                three_rates, all_patterns_p = search_all_score_boards(
                        series_rule=specified_series_rule,
                        on_score_board_created=on_score_board_created)

                # データフレーム更新
                #
                #   FIXME ここは .at[] では不正なスカラーアクセスになる。なんで？
                #
                tp_table.df.loc[index, 'theoretical_a_win_rate'] = three_rates.a_win_rate
                tp_table.df.loc[index, 'theoretical_no_win_match_rate'] = three_rates.no_win_match_rate

                self._number_of_dirty += 1


        # 変更があれば保存
        if 0 < self._number_of_dirty:
            # CSVファイルへ書き出し
            csv_file_path_to_wrote = tp_table.to_csv()

            print(f"{self.stringify_log_stamp(spec=spec)}SAVE____ dirty={self._number_of_dirty}  write file to `{csv_file_path_to_wrote}` ...")

            # このファイルは処理完了した
            return TERMINATED


        # 処理失敗
        print(f"{self.stringify_log_stamp(spec=spec)}UNCHANGE dirty={self._number_of_dirty}")
        return CALCULATION_FAILED




    def stringify_log_stamp(self, spec):
        turn_system_name = Converter.turn_system_id_to_name(spec.turn_system_id)
        return f"""\
[{datetime.datetime.now()}][turn_system_name={turn_system_name:11}  p={spec.p:.2f}  failure_rate={spec.failure_rate:.2f}] \
"""
