#
# やっつけプログラム３号
# python automatic_no3.py
#
#

import traceback
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, UPPER_LIMIT_FAILURE_RATE, Converter
from scripts.create_kakukin_data_excel_file import Automation as CreateKakukinDataExcelFileAutomation


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    try:

        # ［先後の決め方］
        for specified_turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:

            # ［将棋の引分け率］
            for failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5):   # 5％刻み
                specified_failure_rate = failure_rate_percent / 100

                print(f"[{datetime.datetime.now()}][turn_system_name={Converter.turn_system_id_to_name(specified_turn_system_id)}  failure_rete={specified_failure_rate * 100:.1f}%] create kakukin data excel file ...")

                # ［かくきんデータ］エクセル・ファイルの作成
                automation = CreateKakukinDataExcelFileAutomation(
                        specified_failure_rate=specified_failure_rate,
                        specified_turn_system_id=specified_turn_system_id,
                        specified_trials_series=2000)

                automation.execute()

        print(f"""\
でーきたっ！""")


    except Exception as err:
        print(f"""\
おお、残念！　例外が投げられてしまった！
{type(err)=}  {err=}

以下はスタックトレース表示じゃ。
{traceback.format_exc()}
""")
