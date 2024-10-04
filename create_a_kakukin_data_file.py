#
# TODO 作成中
#
# python create_a_kakukin_data_file.py
#
# Excel ファイルを作ろう
#
import traceback

from library import FROZEN_TURN, ALTERNATING_TURN, Converter
from scripts.create_kakukin_data_excel_file import Automation as CreateKakukinDataExcelFileAutomation


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
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
            specified_turn_system = FROZEN_TURN
        elif choice == '2':
            specified_turn_system = ALTERNATING_TURN
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


        automation = CreateKakukinDataExcelFileAutomation(
                specified_failure_rate=specified_failure_rate,
                specified_turn_system=specified_turn_system,
                specified_trials_series=specified_trials_series)

        automation.execute()


    except Exception as err:
        print(f"""\
おお、残念！　例外が投げられてしまった！
{type(err)=}  {err=}

以下はスタックトレース表示じゃ。
{traceback.format_exc()}
""")
