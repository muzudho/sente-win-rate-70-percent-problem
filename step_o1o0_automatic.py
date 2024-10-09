#
# 自動プログラム o1o0 号
# python step_o1o0_automatic.py
#
#

import traceback
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, ABS_SMALL_P_ERROR, Converter
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths
from library.logging import Logging
from scripts.step_o1o0_create_all_epdt_tables import Automation as StepO1o0CreateAllEPDTTables
from config import DEFAULT_TRIAL_SERIES, DEFAULT_UPPER_LIMIT_FAILURE_RATE


# １つのテーブルに割り当てる最大処理時間（秒）
INTERVAL_SECONDS_ON_TABLE = 60


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """Step.o1o0 EPDT 作成"""

    try:
        # ［試行シリーズ回数］
        trial_series = DEFAULT_TRIAL_SERIES

        automatic_1 = StepO1o0CreateAllEPDTTables(
                trial_series=trial_series,
                abs_small_error=ABS_SMALL_P_ERROR,
                interval_seconds=INTERVAL_SECONDS_ON_TABLE)
        automatic_1.execute_all_epdt_tables()


        # ログ出力
        Logging.notice_log(
                file_path=EmpiricalProbabilityDuringTrialsFilePaths.as_log(
                        trial_series=trial_series),
                message="完了",
                shall_print=True)
  

    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
