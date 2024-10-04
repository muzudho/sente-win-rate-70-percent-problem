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
from scripts.upsert_a_csv_of_theoretical_probability_best import Automation as UpsertCsvOfTheoreticalProbabilityBestAll



########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［理論的確率ベストデータ］新規作成または更新
        upsert_csv_of_theoretical_probability_best_all = UpsertCsvOfTheoreticalProbabilityBestAll()
        upsert_csv_of_theoretical_probability_best_all.execute_all()


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
