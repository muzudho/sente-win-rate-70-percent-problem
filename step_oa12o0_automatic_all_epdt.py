#
# python step_oa12o0_automatic_all_epdt.py
#
# EPDTテーブルの仮行埋め
#

import traceback
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, SMALL_P_ABS_ERROR, Converter
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths
from library.logging import Logging
from scripts import ForEachTsFr
from scripts.step_o_9o0_ready_disable_epdt_record import Automation as StepO09o0ReadyDisableEPDTRecord
from config import DEFAULT_TRIAL_SERIES, DEFAULT_UPPER_LIMIT_FAILURE_RATE


class Automatic():


    def __init__(self, trial_series):
        # ［試行シリーズ回数］
        self._trial_series = trial_series


    def on_each_tsfr(self, turn_system_id, failure_rate):
        turn_system_name = Converter.turn_system_id_to_name(turn_system_id)

        # 進捗記録
        Logging.notice_log(
                file_path=EmpiricalProbabilityDuringTrialsFilePaths.as_log(
                        trial_series=self._trial_series,
                        turn_system_id=turn_system_id,
                        failure_rate=failure_rate),
                message=f"[trial_series={self._trial_series}  {turn_system_name=}  {failure_rate=}] ready disable epdt record...",
                shall_print=True)


        # CSV作成 ［試行中の経験的確率データファイル］
        automation = StepO09o0ReadyDisableEPDTRecord(
                specified_trial_series=self._trial_series,
                specified_failure_rate=failure_rate,
                specified_turn_system_id=turn_system_id,
                smaller_abs_error=SMALL_P_ABS_ERROR)
        
        is_update_table = automation.execute()


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """Step o_9o0 EPDT 仮行埋め"""

    try:
        trial_series = DEFAULT_TRIAL_SERIES

        automatic_1 = Automatic(trial_series=trial_series)
        ForEachTsFr.execute(on_each_tsfr=automatic_1.on_each_tsfr)


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
