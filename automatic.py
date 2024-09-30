#
# やっつけプログラム
# python automatic.py
#
#

import traceback
import random
import math
import datetime
import pandas as pd

from library import HEAD, TAIL, ALTERNATING_TURN, BRUTE_FORCE, toss_a_coin
from create_a_csv_to_data_evenizer import automatic


LOG_FILE_PATH = 'logs/automatic.log'


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        specified_turn_system = ALTERNATING_TURN
        generation_algorythm = BRUTE_FORCE
        specified_trials_series = 2000

        for specified_failure_rate_percent in range(0, 100, 5):
            specified_failure_rate = specified_failure_rate_percent / 100

            progress = f"[{datetime.datetime.now()}] {specified_failure_rate=}"

            print(progress)

            # ファイルへログ出力
            with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
                f.write(f"{progress}\n")


            automatic(
                    specified_failure_rate=specified_failure_rate,
                    specified_turn_system=specified_turn_system,
                    generation_algorythm=generation_algorythm,
                    specified_trials_series=specified_trials_series,
                    specified_abs_small_error=0.0009)



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
