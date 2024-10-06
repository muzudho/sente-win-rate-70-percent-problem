#
# python step_o1o2o0_manual_create_a_csv_to_view_ep_in_excel_ver2.py
#
#   ［かくきんデータ］を作成する。
#   ［かくきんデータ］とは、Excel で［かくきんシステムの表］を表示するための CSV
#
#   NOTE 書式のような仕様は頻繁に変更することがあります
#

import traceback

from library import FROZEN_TURN, ALTERNATING_TURN, Converter
from scripts.step_o1o2o0_create_kakukin_data_sheet_csv_file import Automation as StepO1o2o0CreateKakukinDataSheetCsvFile


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［将棋の引分け率］を尋ねます
        prompt = f"""\

Example: 10% is 0.1
What is the failure rate? """
        specified_failure_rate = float(input(prompt))


        # ［先後の決め方］を尋ねます
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

(0) Try       2 series
(1) Try      20 series
(2) Try     200 series
(3) Try    2000 series
(4) Try   20000 series
(5) Try  200000 series
(6) Try 2000000 series

Example: 3
How many times do you want to try the series(0-6)? """
        precision = int(input(prompt))
        specified_trials_series = Converter.precision_to_trials_series(precision)


        step_o1o2o0_create_kakukin_data_sheet_csv_file = StepO1o2o0CreateKakukinDataSheetCsvFile(
                specified_failure_rate=specified_failure_rate,
                specified_turn_system_id=specified_turn_system_id,
                specified_trials_series=specified_trials_series)

        step_o1o2o0_create_kakukin_data_sheet_csv_file.execute()


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
