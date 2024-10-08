#
# 自動プログラム
# python step_o8o0_automatic.py
#
#

import traceback
import datetime
import time

from library import FROZEN_TURN, ALTERNATING_TURN, UPPER_LIMIT_FAILURE_RATE
from library.file_paths import KakukinDataSheetFilePaths
from library.logging import Logging
from config import DEFAULT_TRIAL_SERIES
from scripts.step_o8o0_create_kds_table import Automation as StepO8o0CreateKDSTable


# 実行間隔タイマー
INTERVAL_SECONDS = 5 * 60   # ５分


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ロギング
        Logging.notice_log(
                file_path=KakukinDataSheetFilePaths.as_log(),
                message=f"Step o8o0: start to create KDS table. {INTERVAL_SECONDS=}",
                shall_print=True)

        # ［試行シリーズ回数］
        specified_trial_series = DEFAULT_TRIAL_SERIES

        # 無限ループ
        while True:
            
            time.sleep(INTERVAL_SECONDS)

            # ［先後の決め方］
            for specified_turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:

                # ［将棋の引分け率］
                #  0％～上限、5%刻み
                for specified_failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5):
                    specified_failure_rate = specified_failure_rate_percent / 100


                    ###############################
                    # Step.o1o2o0 かくきんデータ作成
                    ###############################

                    # ロギング
                    Logging.notice_log(
                            file_path=KakukinDataSheetFilePaths.as_log(),
                            message=f"Step o8o0: create KDS table...",
                            shall_print=True)

                    # CSV作成 ［かくきんデータ・エクセル・ファイルの各シートの元データ］
                    step_o8o0_create_kds_table = StepO8o0CreateKDSTable(
                            specified_failure_rate=specified_failure_rate,
                            specified_turn_system_id=specified_turn_system_id,
                            specified_trial_series=specified_trial_series)

                    step_o8o0_create_kds_table.execute()


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
