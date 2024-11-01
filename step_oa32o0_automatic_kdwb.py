#
# python step_oa32o0_automatic_kdwb.py
#
# ［かくきんデータ］（KD）エクセルファイルを作成する
#

import traceback
import time
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, Converter
from library.file_paths import KakukinDataWorkbookFilePaths
from library.logging import Logging
from scripts.step_oa32o0_create_kdwb_excel import GeneratorOfKDWB
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
                file_path=KakukinDataWorkbookFilePaths.as_log(),
                message=f"start to create KDWB. {INTERVAL_SECONDS=}",
                shall_print=True)


        # 無限ループ
        while True:

            time.sleep(INTERVAL_SECONDS)

            # ［かくきんデータ］エクセル・ファイルの作成
            #
            #   NOTE 先にKDSファイルを作成しておく必要があります
            #
            generator_of_kdwb = GeneratorOfKDWB(
                    trial_series=DEFAULT_TRIAL_SERIES)
            generator_of_kdwb.execute()

            # ロギング
            Logging.notice_log(
                    file_path=KakukinDataWorkbookFilePaths.as_log(),
                    message=f"restart to create KDWB. {INTERVAL_SECONDS=}",
                    shall_print=True)


        # 完了しません


    except Exception as err:
        print(f"""\
おお、残念！　例外が投げられてしまった！
{type(err)=}  {err=}

以下はスタックトレース表示じゃ。
{traceback.format_exc()}
""")
