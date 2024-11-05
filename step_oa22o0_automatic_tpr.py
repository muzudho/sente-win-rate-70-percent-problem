#
# python step_oa22o0_automatic_tpr.py
#
# ［理論的確率データ］（TP）表のスリー・レーツ列を更新する
#

import traceback
import os
import time
import datetime
import pandas as pd

from library import HEAD, TAIL, ALICE, FROZEN_TURN, ALTERNATING_TURN, TERMINATED, YIELD, CONTINUE, CALCULATION_FAILED, EVEN, Converter, Specification, SeriesRule, Precision
from library.file_paths import TheoreticalProbabilityRatesFilePaths
from library.database import TheoreticalProbabilityTable, TheoreticalProbabilityRatesTable
from library.views import DebugWrite
from config import DEFAULT_MAX_DEPTH, DEFAULT_UPPER_LIMIT_FAILURE_RATE
from scripts import SaveOrIgnore
from scripts.step_oa22o0_tpr import GeneratorOfTPR


# タイムアップ間隔（秒）。タイムシェアリング間隔。短いとオーバーヘッドの時間の方が長くなる。depth 値を足すかも
INTERVAL_SECONDS = 5


class AllTheoreticalProbabilityFilesOperation():


    def __init__(self, depth):
        self._depth = depth
        
        self._start_time_for_save = None    # CSV保存用タイマー
        
        self._number_of_not_found = 0
        self._number_of_dirty = 0   # ファイルを新規作成したときに 1、レコードを１件追加したときも 1 増える


    @property
    def depth(self):
        return self._depth


    @property
    def number_of_not_found(self):
        return self._number_of_not_found


    def execute_by_spec(self, spec):
        # ファイルが存在しなければ無視する。あれば読み込む
        tp_table, file_read_result = TheoreticalProbabilityTable.from_csv(spec=spec, new_if_it_no_exists=False)


        if tp_table is None:
            print("ファイルが存在しない？")
            self._number_of_not_found += 1
            return


        # ファイルが存在しなければ、新規作成する。あれば読み込む
        tpr_table, tpr_file_read_result = TheoreticalProbabilityRatesTable.from_csv(spec=spec, new_if_it_no_exists=True)


        turn_system_name = Converter.turn_system_id_to_name(spec.turn_system_id)


        if tpr_file_read_result.is_file_not_found:
            # テーブルを新規作成したのなら、ファイルとして保存しておく。保存できなかったら無視して続行する
            successful, target_file_path = SaveOrIgnore.execute(
                    log_file_path=TheoreticalProbabilityRatesFilePaths.as_log(
                            turn_system_id=spec.turn_system_id,
                            failure_rate=spec.failure_rate,
                            p=spec.p),
                    on_save_and_get_file_name=tpr_table.to_csv)
            
            if not successful:
                print(f"スキップ。［理論的確率の率データ］表ファイルが存在せず、新規作成するも保存できませんでした")
                self._number_of_not_found += 1
                return

            print(f"{DebugWrite.stringify(depth=self._depth, spec=spec)} NEW_FILE(A) file={target_file_path}")

            # １件も処理してないが、ファイルを保存したいのでフラグを立てる
            self._number_of_dirty += 1

        else:
            # min() 等のメソッドを使いたいので、テーブルに１件以上入っていることを確認する
            if 0 < len(tpr_table.df):
                # ファイルが既存で、テーブルの中で、誤差がほぼ０の行が含まれているなら、探索打ち切り
                min_abs_error = (tpr_table.df['expected_a_victory_rate_by_duet'] - EVEN).abs().min()
                if Precision.is_it_zero_enough(min_abs_error):
                    print(f"{DebugWrite.stringify(depth=self._depth, spec=spec)}READY_EVEN {min_abs_error=}")
                    return


        ##########################################################
        # Step o2o2o0 ［理論的確率データ］のスリー・レーツ列を更新する
        ##########################################################

        #print(f"{DebugWrite.stringify(depth=self._depth, spec=spec)}step o2o2o0 update three-rates of tp...")
        generator_of_tpr = GeneratorOfTPR(
                # depth が深くなれば、インターバル時間も伸ばすことにする
                seconds_of_time_up=INTERVAL_SECONDS + self._depth)


        # upper_limit_coins が 6 ぐらいなら計算はすぐ終わる。 7 ぐらいから激重になる
        upper_limit_upper_limit_coins = self._depth + 5
        # if upper_limit_upper_limit_coins < 6:
        #     upper_limit_upper_limit_coins = 6


        calculation_status = generator_of_tpr.update_rates_and_save(
                spec=spec,
                tp_table=tp_table,
                tpr_table=tpr_table,

                # ［上限対局数］の上限。探索を打ち切る閾値
                #
                #   NOTE upper_limit_coins は、ツリーの深さに直結するから、数字が増えると処理が重くなる
                #   7 ぐらいで激重
                #
                upper_limit_upper_limit_coins=upper_limit_upper_limit_coins)

        # # 途中の行まで処理したところでタイムアップ(A)
        # if calculation_status == YIELD:
        #     #print(f"[{datetime.datetime.now()}] 途中の行まで処理したところでタイムアップ(A)")
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
                for failure_rate_percent in range(0, int(DEFAULT_UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5): # 5％刻み。 100%は除く。0除算が発生するので
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
