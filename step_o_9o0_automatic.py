#
# python step_o_9o0_automatic.py
#
# EPDTテーブルの仮行埋め
#

import traceback
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, ABS_SMALL_P_ERROR, Converter
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths
from library.logging import Logging
from scripts.step_o_9o0_ready_disable_epdt_record import Automation as StepO09o0ReadyDisableEPDTRecord
from config import DEFAULT_TRIAL_SERIES, DEFAULT_UPPER_LIMIT_FAILURE_RATE


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """Step o_9o0 EPDT 仮行埋め"""

    try:
        # ［試行シリーズ回数］
        specified_trial_series = DEFAULT_TRIAL_SERIES

        # ［先後の決め方］
        for specified_turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:
            turn_system_name = Converter.turn_system_id_to_name(specified_turn_system_id)

            # ［将棋の引分け率］
            #  0％～上限、5%刻み
            for specified_failure_rate_percent in range(0, int(DEFAULT_UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5):
                specified_failure_rate = specified_failure_rate_percent / 100


                # 進捗記録
                Logging.notice_log(
                        file_path=EmpiricalProbabilityDuringTrialsFilePaths.as_log(
                                trial_series=specified_trial_series,
                                turn_system_id=specified_turn_system_id,
                                failure_rate=specified_failure_rate),
                        message=f"[trial_series={specified_trial_series}  turn_system_name={turn_system_name}  failure_rate={specified_failure_rate}] ready disable epdt record...",
                        shall_print=True)


                # CSV作成 ［試行中の経験的確率データファイル］
                automation = StepO09o0ReadyDisableEPDTRecord(
                        specified_trial_series=specified_trial_series,
                        specified_failure_rate=specified_failure_rate,
                        specified_turn_system_id=specified_turn_system_id,
                        specified_abs_small_error=ABS_SMALL_P_ERROR)
                
                is_update_table = automation.execute()


        # ログ出力
        Logging.notice_log(
                file_path=EmpiricalProbabilityDuringTrialsFilePaths.as_log(
                        trial_series=specified_trial_series,
                        turn_system_id=specified_turn_system_id,
                        failure_rate=specified_failure_rate),
                message="完了",
                shall_print=True)
  

    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
