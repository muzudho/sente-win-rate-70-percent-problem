#
# やっつけプログラム１号
# python automatic_no1.py
#
#

import traceback
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, BRUTE_FORCE, UPPER_LIMIT_FAILURE_RATE
from create_a_csv_to_data_evenizer import Automation as AutomationForData
from create_a_csv_to_view_evenizer_in_excel_ver2 import Automation as AutomationForView


LOG_FILE_PATH = 'logs/automatic_no1.log'


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        generation_algorythm = BRUTE_FORCE
        specified_trials_series = 2000

        for specified_turn_system in [ALTERNATING_TURN, FROZEN_TURN]:

            # ［将棋の引分け率］
            for specified_failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5):   # 5％刻み
                specified_failure_rate = specified_failure_rate_percent / 100

                progress = f"[{datetime.datetime.now()}] {specified_failure_rate=}"

                print(progress)

                # ファイルへログ出力
                with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
                    f.write(f"{progress}\n")

                
                automation_for_data = AutomationForData(
                        specified_failure_rate=specified_failure_rate,
                        specified_turn_system=specified_turn_system,
                        generation_algorythm=generation_algorythm,
                        specified_trials_series=specified_trials_series,
                        specified_abs_small_error=0.0009)
                
                automation_for_data.execute()


                automation_for_view = AutomationForView(
                        specified_failure_rate=specified_failure_rate,
                        specified_turn_system=specified_turn_system,
                        specified_trials_series=specified_trials_series)

                automation_for_view.execute()


        progress = f"[{datetime.datetime.now()}] 完了"

        # 表示
        print(progress)
  
        # ファイルへログ出力
        with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
            f.write(f"{progress}\n")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
