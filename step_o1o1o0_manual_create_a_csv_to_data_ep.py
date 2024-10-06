#
# 生成
# python step_o1o1o0_manual_create_a_csv_to_data_ep.py
#
#   ［表勝ちだけでの対局数］と、［裏勝ちだけでの対局数］を探索する。
#

import traceback

from library import FROZEN_TURN, ALTERNATING_TURN, Converter
from scripts.step_o1o1o0_create_a_csv_to_epdt import CreateCsvToEPDT


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［将棋の引分け率］を尋ねる
        prompt = f"""\
What is the failure rate?
Example: 10% is 0.1
? """
        specified_failure_rate = float(input(prompt))


        # ［先後の決め方］を尋ねる
        prompt = f"""\
(1) Frozen turn
(2) Alternating turn
Which one(1-2)? """
        choice = input(prompt)
        if choice == '1':
            specified_turn_system_id = FROZEN_TURN
        elif choice == '2':
            specified_turn_system_id = ALTERNATING_TURN
        else:
            raise ValueError(f"{choice=}")


        # ［試行シリーズ数］を尋ねる
        prompt = f"""\
How many times do you want to try the series?

(0) Try       2 series
(1) Try      20 series
(2) Try     200 series
(3) Try    2000 series
(4) Try   20000 series
(5) Try  200000 series
(6) Try 2000000 series

Example: 3
(0-6)? """
        precision = int(input(prompt))
        specified_trials_series = Converter.precision_to_trials_series(precision)
        specified_abs_small_error = Converter.precision_to_small_error(precision)


        create_csv_to_epdt = CreateCsvToEPDT(
                specified_failure_rate=specified_failure_rate,
                specified_turn_system_id=specified_turn_system_id,
                specified_trials_series=specified_trials_series,
                specified_abs_small_error=specified_abs_small_error)
        
        create_csv_to_epdt.execute()


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
