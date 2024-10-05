#
# 分析
# python query_upsert_a_csv_of_theoretical_probability_best.py
#
#   ［仕様］［シリーズ・ルール］について、５分５分に近いものをピックアップします
#

import traceback
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, EVEN, ABS_OUT_OF_ERROR, UPPER_LIMIT_FAILURE_RATE, Converter, Specification, ThreeRates
from library.database import TheoreticalProbabilityTable, TheoreticalProbabilityBestRecord, TheoreticalProbabilityBestTable
from scripts.upsert_a_csv_of_theoretical_probability_best import AutomationOne as UpsertCsvOfTheoreticalProbabilityBestOne



########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［将棋の先手勝率］を尋ねます
        prompt = f"""\

Example: 70% is 0.7
What is the probability of flipping a coin and getting heads? """
        specified_p = float(input(prompt))


        # ［将棋の引分け率］を尋ねる
        prompt = f"""\
What is the failure rate?
Example: 10% is 0.1
? """
        specified_failure_rate = float(input(prompt))


        # ［先後の決め方］を尋ねる
        prompt = f"""\
(1) Frozen turn
(2) Alternating turn
Which one(1-2)? """

        choice = input(prompt)
        if choice == '1':
            specified_turn_system_id = FROZEN_TURN
        elif choice == '2':
            specified_turn_system_id = ALTERNATING_TURN
        else:
            raise ValueError(f"{choice=}")


        # ［仕様］
        spec = Specification(
                p=specified_p,
                failure_rate=specified_failure_rate,
                turn_system_id=specified_turn_system_id)


        # ［理論的確率ベストデータ］新規作成または更新
        upsert_csv_of_theoretical_probability_best_one = UpsertCsvOfTheoreticalProbabilityBestOne(spec=spec)
        upsert_csv_of_theoretical_probability_best_one.execute_one()


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
