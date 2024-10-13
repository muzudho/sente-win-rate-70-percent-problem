#
# ［かくきんデータ］Excel ファイルを作ろう
#
import openpyxl as xl
import pandas as pd
import os
import time
import random
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, Converter, Specification
from library.file_paths import KakukinDataFilePaths
from library.logging import Logging
from library.database import KakukinDataSheetTable
from scripts import SaveWithRetry, ForEachFr


class SheetToAppend():


    def __init__(self, trial_series, turn_system_id, excel_writer):
        self._trial_series = trial_series
        self._turn_system_id = turn_system_id
        self._excel_writer = excel_writer


    def on_each_fr(self, failure_rate):

        # KDS ファイルの読込
        kds_table, kds_file_read_result = KakukinDataSheetTable.from_csv(
                failure_rate=failure_rate,
                turn_system_id=self._turn_system_id,
                trial_series=self._trial_series)

        # KDSファイルが無かったのならスキップする
        if kds_table is None:
            print(f"[{datetime.datetime.now()}] KDSファイルが無かったのならスキップする")
            return


        # KDエクセルのシートの名前を作成するぞ（シートが既存なら上書き）
        #
        #   Example: ［将棋の引分け率］が 0.05 なら `f5.0per`
        #   NOTE シート名に "%" を付けると Excel の式が動かなくなった
        #
        sheet_name = f'f{failure_rate * 100:.1f}per'

        print(f"{sheet_name=}")

        kds_table.df.to_excel(self._excel_writer, sheet_name=sheet_name)


class Automation():
    """自動化"""


    def __init__(self, trial_series):
        """初期化

        Parameters
        ----------
        trial_series : int
            ［シリーズ試行回数］
        """
        self._trial_series = trial_series


    def execute(self):
        """実行
        
        NOTE 先にKDSファイルを作成しておく必要があります
        """

        # ［シリーズ試行回数］と［先後の決め方］でエクセル・ファイル名が決まる

        # ［先後の決め方］
        for turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:

            # KDエクセル・ファイルへのパス
            kd_excel_file_path = KakukinDataFilePaths.as_excel(
                    trial_series=self._trial_series,
                    turn_system_id=turn_system_id)

            # エクセル・ファイルが既存なら削除する
            if os.path.isfile(kd_excel_file_path):
                # 削除前の安全策
                if not kd_excel_file_path.endswith('.xlsx'):
                    raise ValueError(f"エクセル形式のファイルが指定されていません。 {kd_excel_file_path=}")

                try:               
                    os.remove(kd_excel_file_path)
                
                # FIXME エクセルファイルが開けっ放しのとき
                # PermissionError: [WinError 32] プロセスはファイルにアクセスできません。別のプロセスが使用中です。: 'reports/kakukin/auto_generated_kakukin_data_try2000_alter.xlsx'
                except PermissionError as e:
                    print(f"""\
既存のエクセルファイルを削除できませんでした。作業をスキップします。
error={e}""")
                    continue

            # （シートを追加する前に）エクセルファイルを新規作成する必要がある。エクセルファイルは .zip 圧縮ファイルなので追記モードで新規作成は行ってくれず、このような手間が必要
            # ワークブックの作成
            wb = xl.Workbook()
            wb.save(kd_excel_file_path)


            # ［かくきんデータ・エクセル・ファイル］にシートを追記
            with pd.ExcelWriter(kd_excel_file_path, mode='a') as excel_writer:

                sheet_to_append = SheetToAppend(
                        trial_series=self._trial_series,
                        turn_system_id=turn_system_id,
                        excel_writer=excel_writer)

                # ［コインを投げて表も裏も出ない確率］でループ
                ForEachFr.execute(on_each_fr=sheet_to_append.on_each_fr)


            # デフォルトのシートを削除する
            wb = xl.load_workbook(kd_excel_file_path)
            wb.remove(wb['Sheet'])
            wb.save(kd_excel_file_path)
