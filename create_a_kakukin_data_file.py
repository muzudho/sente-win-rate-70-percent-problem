#
# TODO 作成中
#
# python create_a_kakukin_data_file.py
#
# Excel ファイルを作ろう
#
import traceback
import openpyxl as xl
import os

from library import FROZEN_TURN, ALTERNATING_TURN, Converter
from library.file_paths import get_kakukin_data_excel_file_path


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    try:

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
        specified_abs_small_error = Converter.precision_to_small_error(precision)


        excel_file_path = get_kakukin_data_excel_file_path(turn_system=specified_turn_system, trials_series=specified_trials_series)


        # ワークブックの作成
        wb = xl.Workbook()

        while True:
            if os.path.isfile(excel_file_path):
                command = input(f"""\
{excel_file_path} という名前のファイルは既にあります。
上書きしますか(Y/n)? """)

                if command == 'n':
                    continue

            break

        wb.save(excel_file_path)

        print(f"""\
{excel_file_path} を保存しました。
""")

        sheet_name = "f0"

        # 最初に Sheet という名前のシートができているので、それを参照します
        ws = wb["Sheet"]

        # シートの名前を変更します
        ws.title = sheet_name
        wb.save(excel_file_path)

        print(f"""\
シートの名前を {ws.title} に変更しました。
{excel_file_path} を保存しました。
""")

        # 列名 A ～
        column_names = [
            'p',
            'failure_rate',
            'turn_system',
            'head_step',
            'tail_step',
            'span',
            'shortest_coins',
            'upper_limit_coins',
            'trials_series',
            'series_shortest_coins',
            'series_longest_coins',
            'wins_a',
            'wins_b',
            'succucessful_series',
            's_ful_wins_a',
            's_ful_wins_b',
            's_pts_wins_a',
            's_pts_wins_b',
            'failed_series',
            'f_ful_wins_a',
            'f_ful_wins_b',
            'f_pts_wins_a',
            'f_pts_wins_b',
            'no_wins_ab',
        ]

        for index, column_name in enumerate(column_names, 1):
            ws[f'{xl.utils.get_column_letter(index)}1'] = column_name

        wb.save(excel_file_path)

        print(f"""\
{ws.title} シートの１行目に列名を入れました。
{excel_file_path} を保存しました。
""")

    except Exception as err:
        print(f"""\
おお、残念！　例外が投げられてしまった！  
{err=}  {type(err)=}

以下はスタックトレース表示じゃ。
{traceback.format_exc()}
""")
