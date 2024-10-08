#
# python step_o9o0_automatic.py
#
#

import traceback
import time
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, UPPER_LIMIT_FAILURE_RATE, Converter
from library.file_paths import KakukinDataFilePaths
from library.logging import Logging
from scripts.step_o9o0_create_kakukin_data_excel_file import Automation as StepO9o0CreateKakukinDataExcelFileAutomation


# 実行間隔タイマー
INTERVAL_SECONDS = 6 * 60   # ６分


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    try:
        # ロギング
        Logging.notice_log(
                file_path=KakukinDataFilePaths.as_log(),
                message=f"Step o8o0: start to create KD table. {INTERVAL_SECONDS=}",
                shall_print=True)

        # 無限ループ
        while True:

            time.sleep(INTERVAL_SECONDS)


            # ［先後の決め方］
            for specified_turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:

                # ［将棋の引分け率］
                for failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5):   # 5％刻み
                    specified_failure_rate = failure_rate_percent / 100

                    # ロギング
                    Logging.notice_log(
                            file_path=KakukinDataFilePaths.as_log(),
                            message=f"[turn_system_name={Converter.turn_system_id_to_name(specified_turn_system_id)}  failure_rete={specified_failure_rate * 100:.1f}%] Step o9o0: create KD table. {INTERVAL_SECONDS=}",
                            shall_print=True)

                    # ［かくきんデータ］エクセル・ファイルの作成
                    #
                    #   NOTE 先にKDSファイルを作成しておく必要があります
                    #
                    automation = StepO9o0CreateKakukinDataExcelFileAutomation(
                            specified_trial_series=2000,
                            specified_turn_system_id=specified_turn_system_id,
                            specified_failure_rate=specified_failure_rate)

                    automation.execute()


            # ロギング
            Logging.notice_log(
                    file_path=KakukinDataFilePaths.as_log(),
                    message=f"Step o9o0: restart to create KD table. {INTERVAL_SECONDS=}",
                    shall_print=True)


        # 完了しません


    except Exception as err:
        print(f"""\
おお、残念！　例外が投げられてしまった！
{type(err)=}  {err=}

以下はスタックトレース表示じゃ。
{traceback.format_exc()}
""")
