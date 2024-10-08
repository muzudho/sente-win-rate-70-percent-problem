#
# python step_o6o0_automatic.py
#
# ［理論的確率データ］のスリー・レーツ列を更新する
#

import traceback
import os
import time
import datetime
import pandas as pd

from library import HEAD, TAIL, ALICE, FROZEN_TURN, ALTERNATING_TURN, TERMINATED, YIELD, CONTINUE, CALCULATION_FAILED, OUT_OF_P, OUT_OF_UPPER_SPAN, UPPER_LIMIT_FAILURE_RATE, EVEN, Converter, Specification, SeriesRule, is_almost_zero
from library.score_board import search_all_score_boards
from library.database import TheoreticalProbabilityTable, TheoreticalProbabilityRecord
from config import DEFAULT_MAX_DEPTH
from scripts.step_o6o0_update_three_rates_for_a_file import Automation as StepO6o0UpdateThreeRatesForAFile


# タイムアップ間隔（秒）。タイムシェアリング間隔
INTERVAL_SECONDS_FOR_SAVE_CSV = 5


class AllTheoreticalProbabilityFilesOperation():


    def __init__(self, depth):

        # CSV保存用タイマー
        self._start_time_for_save = None

        # ファイルを新規作成したときに 1、レコードを１件追加したときも 1 増える
        self._number_of_dirty = 0

        self._depth = depth


    @property
    def depth(self):
        return self._depth


    def stringify_log_stamp(self, spec):
        turn_system_name = Converter.turn_system_id_to_name(spec.turn_system_id)
        return f"""\
[{datetime.datetime.now()}][depth={self._depth}  turn_system_name={turn_system_name:11}  p={spec.p:.2f}  failure_rate={spec.failure_rate:.2f}] \
"""


    def execute_by_spec(self, spec):
        # ファイルが存在しなければ、新規作成する。あれば読み込む
        tp_table, is_tp_file_created = TheoreticalProbabilityTable.read_csv(spec=spec, new_if_it_no_exists=True)

        turn_system_name = Converter.turn_system_id_to_name(spec.turn_system_id)

        if is_tp_file_created:
            print(f"{self.stringify_log_stamp(spec=spec)}NEW_FILE")

            # １件も処理してないが、ファイルを保存したいのでフラグを立てる
            self._number_of_dirty += 1

        else:
            # ファイルが既存で、テーブルの中で、誤差がほぼ０の行が含まれているなら、探索打ち切り
            #
            #   FIXME このコードの書き方で動くのかわからない。もし書けないなら、１件ずつ調べていけばいいか
            #
            min_abs_error = (tp_table.df['theoretical_a_win_rate'] - EVEN).abs().min()
            if is_almost_zero(min_abs_error):
                print(f"{self.stringify_log_stamp(spec=spec)}READY_EVEN....")
                return


        ##########################################################
        # Step o2o2o0 ［理論的確率データ］のスリー・レーツ列を更新する
        ##########################################################

        print(f"{self.stringify_log_stamp(spec=spec)}step o2o2o0 update three-rates of tp...")
        step_o6o0_update_three_rates_for_a_file = StepO6o0UpdateThreeRatesForAFile(
                seconds_of_time_up=INTERVAL_SECONDS_FOR_SAVE_CSV)


        # upper_limit_coins が 6 ぐらいなら計算はすぐ終わる。 7 ぐらいから激重になる
        upper_limit_upper_limit_coins = self._depth
        if upper_limit_upper_limit_coins < 6:
            upper_limit_upper_limit_coins = 6


        calculation_status = step_o6o0_update_three_rates_for_a_file.update_three_rates_for_a_file_and_save(
                spec=spec,
                tp_table=tp_table,

                #
                # NOTE upper_limit_coins は、ツリーの深さに直結するから、数字が増えると処理が重くなる
                # 7 ぐらいで激重
                #
                upper_limit_upper_limit_coins=upper_limit_upper_limit_coins)

        # # 途中の行まで処理したところでタイムアップ
        # if calculation_status == YIELD:
        #     #print(f"[{datetime.datetime.now()}] 途中の行まで処理したところでタイムアップ")
        #     pass

        # # このファイルは処理失敗した
        # elif calculation_status == CALCULATION_FAILED:
        #     print(f"[{datetime.datetime.now()}] このファイルは処理失敗した")

        # # このファイルは処理完了した
        # elif calculation_status == TERMINATED:
        #     #print(f"[{datetime.datetime.now()}] このファイルは処理完了した")
        #     pass
        
        # else:
        #     raise ValueError(f"{calculation_status=}")


        # TODO ［理論的確率データ］のうち、［理論的確率ベスト・データ］に載っているものについて、試行して、その結果を［理論的確率の試行結果データ］に保存したい


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # TODO 自動調整のいい方法が思い浮かばない
        # とりあえず、 depth が どんどん増えていくものとする。
        for depth in range(1, DEFAULT_MAX_DEPTH):

            all_theoretical_probability_files_operation = AllTheoreticalProbabilityFilesOperation(depth=depth)


            # ［先後の決め方］
            for turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:
                turn_system_name = Converter.turn_system_id_to_name(turn_system_id)

                # ［将棋の引分け率］
                for failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5): # 5％刻み。 100%は除く。0除算が発生するので
                    failure_rate = failure_rate_percent / 100

                    # ［将棋の先手勝率］
                    for p_percent in range(50, 96):
                        p = p_percent / 100

                        # 仕様
                        spec = Specification(
                                turn_system_id=turn_system_id,
                                failure_rate=failure_rate,
                                p=p)
                        
                        all_theoretical_probability_files_operation.execute_by_spec(spec=spec)


        # 現実的に、完了しない想定
        print("完了")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
