#
# 自動プログラム１号
# python step_o1o0_automatic.py
#
#

import traceback
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, UPPER_LIMIT_FAILURE_RATE, ABS_SMALL_P_ERROR
from library.file_paths import StepO1o0AutomaticFilePaths, EmpiricalProbabilityDuringTrialsFilePaths
from library.logging import Logging
from scripts.step_o1o0_create_epdt_table import Automation as StepO1o1o0CreateEPDTTable
from config import DEFAULT_TRIAL_SERIES


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［試行シリーズ回数］
        specified_trial_series = DEFAULT_TRIAL_SERIES

        # ［先後の決め方］
        for specified_turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:

            # ［将棋の引分け率］
            #  0％～上限、5%刻み
            for specified_failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5):
                specified_failure_rate = specified_failure_rate_percent / 100


                # 進捗記録
                Logging.notice_log(
                        file_path=EmpiricalProbabilityDuringTrialsFilePaths.as_log(
                                trial_series=specified_trial_series,
                                turn_system_id=specified_turn_system_id,
                                failure_rate=specified_failure_rate),
                        message=f"failure_rate={specified_failure_rate}",
                        shall_print=True)


                #####################
                # Step.o1o0 EPDT 作成
                #####################

                # CSV作成 ［試行中の経験的確率データファイル］
                automation = StepO1o1o0CreateEPDTTable(
                        specified_failure_rate=specified_failure_rate,
                        specified_turn_system_id=specified_turn_system_id,
                        specified_trial_series=specified_trial_series,
                        specified_abs_small_error=ABS_SMALL_P_ERROR)
                
                automation.execute()


        progress = f"[{datetime.datetime.now()}] 完了"

        # 表示
        print(progress)
  
        # ファイルへログ出力
        log_file_path = StepO1o0AutomaticFilePaths.as_log()
        with open(log_file_path, 'a', encoding='utf8') as f:
            f.write(f"{progress}\n")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
