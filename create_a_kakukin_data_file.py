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

from library import FROZEN_TURN, ALTERNATING_TURN, Converter, Specification
from library.file_paths import get_kakukin_data_excel_file_path, get_kakukin_data_sheet_csv_file_path
from library.database import KakukinDataSheetTable


class Automation():


    def __init__(self, specified_failure_rate, specified_turn_system, specified_trials_series):
        self._specified_failure_rate = specified_failure_rate
        self._specified_turn_system = specified_turn_system
        self._specified_trials_series = specified_trials_series

        self._ws = None
        self._row_number = 0


    def execute(self):
        excel_file_path = get_kakukin_data_excel_file_path(
                turn_system=self._specified_turn_system,
                trials_series=self._specified_trials_series)


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


        # 最初に Sheet という名前のシートができているので、それを参照します
        #self._ws = wb["Sheet"]
        #self._ws.title = sheet_name

        # シートの名前を作成するぞ
        #
        #   Example: ［将棋の引分け率］が 0.05 なら `f5.0%`
        #
        sheet_name = f'f{self._specified_failure_rate * 100:.1f}%'
        self._ws = wb.create_sheet(title=sheet_name)

        # 例えば `KDS_alter_f0.0_try2000.csv` といったファイルの内容を、シートに移していきます
        # 📖 [openpyxlで別ブックにシートをコピーする](https://qiita.com/github-nakasho/items/fb9df8e423bb8784cbbd)

        df_kds = KakukinDataSheetTable.read_df(
                failure_rate=self._specified_failure_rate,
                turn_system=self._specified_turn_system,
                trials_series=self._specified_trials_series)


        for index, column_name in enumerate(df_kds.columns.values, 1):
            self._ws[f'{xl.utils.get_column_letter(index)}1'] = column_name

        # データ部
        # --------

        self._row_number = 2

        def on_each(record):
            self._ws[f'A{self._row_number}'].value = record.p
            self._ws[f'B{self._row_number}'].value = record.failure_rate
            self._ws[f'C{self._row_number}'].value = record.turn_system
            self._ws[f'D{self._row_number}'].value = record.head_step
            self._ws[f'E{self._row_number}'].value = record.tail_step
            self._ws[f'F{self._row_number}'].value = record.span
            self._ws[f'G{self._row_number}'].value = record.shortest_coins
            self._ws[f'H{self._row_number}'].value = record.upper_limit_coins
            self._ws[f'I{self._row_number}'].value = record.trials_series
            self._ws[f'J{self._row_number}'].value = record.series_shortest_coins
            self._ws[f'K{self._row_number}'].value = record.series_longest_coins
            self._ws[f'L{self._row_number}'].value = record.wins_a
            self._ws[f'M{self._row_number}'].value = record.wins_b
            self._ws[f'N{self._row_number}'].value = record.succucessful_series
            self._ws[f'O{self._row_number}'].value = record.s_ful_wins_a
            self._ws[f'P{self._row_number}'].value = record.s_ful_wins_b
            self._ws[f'Q{self._row_number}'].value = record.s_pts_wins_a
            self._ws[f'R{self._row_number}'].value = record.s_pts_wins_b
            self._ws[f'S{self._row_number}'].value = record.failed_series
            self._ws[f'T{self._row_number}'].value = record.f_ful_wins_a
            self._ws[f'U{self._row_number}'].value = record.f_ful_wins_b
            self._ws[f'V{self._row_number}'].value = record.f_pts_wins_a
            self._ws[f'W{self._row_number}'].value = record.f_pts_wins_b
            self._ws[f'X{self._row_number}'].value = record.no_wins_ab

            self._row_number += 1

        KakukinDataSheetTable.for_each(
                df=df_kds,
                on_each=on_each)


        wb.save(excel_file_path)

        print(f"""\
{excel_file_path} ファイルを保存しました。

でーきたっ！""")


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


        automation = Automation(
                specified_failure_rate=specified_failure_rate,
                specified_turn_system=specified_turn_system,
                specified_trials_series=specified_trials_series)

        automation.execute()


    except Exception as err:
        print(f"""\
おお、残念！　例外が投げられてしまった！  
{err=}  {type(err)=}

以下はスタックトレース表示じゃ。
{traceback.format_exc()}
""")
