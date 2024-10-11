#
# python step_oa31o0_automatic_kds.py
#
# ［かくきんデータシート］（KDS）ファイルを作成する
#

import traceback
import datetime
import time

from library import FROZEN_TURN, ALTERNATING_TURN
from library.file_paths import KakukinDataSheetFilePaths
from library.logging import Logging
from config import DEFAULT_TRIAL_SERIES, DEFAULT_UPPER_LIMIT_FAILURE_RATE
from scripts import ForEachTsFr
from scripts.step_oa31o0_create_kds_table import Automation as StepO31o0CreateKDSTable


# 実行間隔タイマー
INTERVAL_SECONDS = 5 * 60   # ５分


class Automation():


    def __init__(self, trial_series):
        self._trial_series = trial_series


    def on_each_tsfr(self, turn_system_id, failure_rate):
        ###############################
        # Step.o1o2o0 かくきんデータ作成
        ###############################

        # ロギング
        Logging.notice_log(
                file_path=KakukinDataSheetFilePaths.as_log(
                        trial_series=self._trial_series,
                        turn_system_id=turn_system_id,
                        failure_rate=failure_rate),
                message=f"Step o8o0: create KDS table...",
                shall_print=True)

        # CSV作成 ［かくきんデータ・エクセル・ファイルの各シートの元データ］
        automation = StepO31o0CreateKDSTable(
                specified_trial_series=self._trial_series,
                specified_turn_system_id=turn_system_id,
                specified_failure_rate=failure_rate)

        automation.execute()


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［試行シリーズ回数］
        specified_trial_series = DEFAULT_TRIAL_SERIES

        # ロギング
        Logging.notice_log(
                file_path=KakukinDataSheetFilePaths.as_log(trial_series=specified_trial_series),
                message=f"Step o8o0: start to create KDS table. {INTERVAL_SECONDS=}",
                shall_print=True)

        automation = Automation(trial_series=specified_trial_series)

        # 無限ループ
        while True:
            
            time.sleep(INTERVAL_SECONDS)

            ForEachTsFr.execute(on_each_tsfr=automation.on_each_tsfr)


            # ロギング
            Logging.notice_log(
                    file_path=KakukinDataSheetFilePaths.as_log(),
                    message=f"Step o8o0: restart to create KDS table. {INTERVAL_SECONDS=}",
                    shall_print=True)


        # 完了しません


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
