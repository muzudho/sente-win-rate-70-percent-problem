#
# python step_oa32o0_automatic_kd.py
#
# ［かくきんデータ］（KD）エクセルファイルを作成する
#

import traceback
import time
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, Converter
from library.file_paths import KakukinDataFilePaths
from library.logging import Logging
from scripts.step_oa32o0_create_kd_excel import Automation as StepOa32o0CreateKDExcel
from config import DEFAULT_UPPER_LIMIT_FAILURE_RATE, DEFAULT_TRIAL_SERIES


# 実行間隔タイマー
#INTERVAL_SECONDS = 5   # 5 秒
INTERVAL_SECONDS = 7 * 60   # ７分。［素数ゼミ］参考


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    try:
        # ロギング
        Logging.notice_log(
                file_path=KakukinDataFilePaths.as_log(),
                message=f"start to create KD table. {INTERVAL_SECONDS=}",
                shall_print=True)


        # 無限ループ
        while True:

            time.sleep(INTERVAL_SECONDS)

            # ［かくきんデータ］エクセル・ファイルの作成
            #
            #   NOTE 先にKDSファイルを作成しておく必要があります
            #
            automation = StepOa32o0CreateKDExcel(
                    trial_series=DEFAULT_TRIAL_SERIES)
            automation.execute()

            # ロギング
            Logging.notice_log(
                    file_path=KakukinDataFilePaths.as_log(),
                    message=f"restart to create KD table. {INTERVAL_SECONDS=}",
                    shall_print=True)


        # 完了しません


    except Exception as err:
        print(f"""\
おお、残念！　例外が投げられてしまった！
{type(err)=}  {err=}

以下はスタックトレース表示じゃ。
{traceback.format_exc()}
""")
