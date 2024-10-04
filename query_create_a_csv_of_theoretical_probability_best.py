#
# 分析
# python query_create_a_csv_of_theoretical_probability_best.py
#
#   ［仕様］［シリーズ・ルール］について、５分５分に近いものをピックアップします
#

import traceback
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, EVEN, ABS_OUT_OF_ERROR, UPPER_LIMIT_FAILURE_RATE, Converter, Specification, ThreeRates
from library.file_paths import get_theoretical_probability_best_csv_file_path
from library.database import TheoreticalProbabilityTable, TheoreticalProbabilityBestRecord, TheoreticalProbabilityBestTable
from scripts.create_a_csv_of_theoretical_probability_best import Automation


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［先後の決め方］
        for specified_turn_system in [ALTERNATING_TURN, FROZEN_TURN]:

            # ［将棋の引分け率］
            for failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5): # 5％刻み
                specified_failure_rate = failure_rate_percent / 100

                # ［将棋の先手勝率］
                for p_percent in range(50, 96):
                    specified_p = p_percent / 100

                    # 仕様
                    spec = Specification(
                            p=specified_p,
                            failure_rate=specified_failure_rate,
                            turn_system=specified_turn_system)

                    # 理論的確率のベスト集作成
                    automation = Automation()
                    automation.execute(spec=spec)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
