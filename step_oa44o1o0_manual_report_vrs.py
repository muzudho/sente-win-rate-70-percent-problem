#
# TODO 作成中
#
# python step_oa44o1o0_manual_report_vrs.py
#
#   VRS表を CSV形式から XLSX形式へ変換します
#

import traceback
import os
import random
import math
import pandas as pd
import openpyxl as xl
from openpyxl.styles import PatternFill, Font
from openpyxl.styles.borders import Border, Side
from openpyxl.styles.alignment import Alignment

from library import HEAD, TAIL, toss_a_coin
from library.file_paths import VictoryRateSummaryFilePaths


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:

        # ファイルパス取得
        # ---------------

        # VRS表 CSV
        csv_file_path = VictoryRateSummaryFilePaths.as_csv()

        # ワークブック
        wb_file_path = VictoryRateSummaryFilePaths.as_workbook()

        # VRS表(CSV)の読取
        if os.path.isfile(csv_file_path):   # ファイルが既存ならそれを読取る
            df = pd.read_csv(
                    csv_file_path,
                    encoding="utf-8")
        
        else:
            raise ValueError(f"file not found {csv_file_path=}")


        # ワークブックの新規作成
        wb = xl.Workbook()

        # 既定シート名変更
        wb['Sheet'].title = 'Summary'

        # シート取得
        ws = wb['Summary']

        # 列名の変更
        new_column_name_dict = {
            'turn_system_name':'ターン',
            'failure_rate':'失敗率',
            'p':'p',
            'span':'優勝点',
            't_step':'ｳﾗ点',
            'h_step':'表点',
            'a_victory_rate_by_trio':'Ａさんの三分率',
            'b_victory_rate_by_trio':'Ｂさんの三分率',
            'no_victory_rate':'勝者なし率',
            'a_victory_rate_by_duet':'Ａさんの優勝率',
            'b_victory_rate_by_duet':'Ｂさんの優勝率',
            'unfair_point':'２乗誤差',
            't_time':'必要ｳﾗ回数',
            'h_time':'必要表回数',
            'shortest_coins':'最短対局数',
            'upper_limit_coins':'対局数上限'}

        # ヘッダー文字色・背景色
        header_font = Font(color='EEFFEE')
        header_background_fill = PatternFill(patternType='solid', fgColor='336633')

        # ヘッダー出力
        for column_th, column_name in enumerate(df.columns.values, 1):
            column_letter = xl.utils.get_column_letter(column_th)
            cell = ws[f'{column_letter}1']
            cell.value = new_column_name_dict[column_name]
            cell.font = header_font
            cell.fill = header_background_fill


        # TODO データ出力
        column_letter_and_column_name = [
            ('A', 'turn_system_name'),
            ('B', 'failure_rate'),
            ('C', 'p'),
            ('D', 'span'),
            ('E', 't_step'),
            ('F', 'h_step'),
            ('G', 'a_victory_rate_by_trio'),
            ('H', 'b_victory_rate_by_trio'),
            ('I', 'no_victory_rate'),
            ('J', 'a_victory_rate_by_duet'),
            ('K', 'b_victory_rate_by_duet'),
            ('L', 'unfair_point'),
            ('M', 't_time'),
            ('N', 'h_time'),
            ('O', 'shortest_coins'),
            ('P', 'upper_limit_coins'),
        ]

        for data_no, row in df.iterrows():
            #print(f"{row_th=} {type(row)=}")
            row_th = data_no + 2

            for column_no in range(0, len(row)):
                cell = ws[f'{column_letter_and_column_name[column_no][0]}{row_th}']
                cell.value = row[column_letter_and_column_name[column_no][1]]

        # ウィンドウ枠の固定
        ws.freeze_panes = 'A2'

        # TODO 罫線出力


        # ワークブックの保存
        wb.save(wb_file_path)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
