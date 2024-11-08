#
# python step_oa43o0_automatic_vrd.py
#

import traceback
import os
import math
import time
import datetime
import random
import openpyxl as xl
import pandas as pd
from library import TAIL, HEAD, SeriesRule, get_list_of_basename
from library.file_basename import BasenameOfGameTreeWorkbookFile
from library.file_paths import GameTreeWorkbookFilePaths, VictoryRateDetailFilePaths
from library.xlutils import XlUtils


class TransferData():


    def __init__(self, a_victory_rate_by_trio, b_victory_rate_by_trio, no_victory_rate):
        self._a_victory_rate_by_trio = a_victory_rate_by_trio
        self._b_victory_rate_by_trio = b_victory_rate_by_trio
        self._no_victory_rate = no_victory_rate


    @property
    def a_victory_rate_by_trio(self):
        return self._a_victory_rate_by_trio


    @property
    def b_victory_rate_by_trio(self):
        return self._b_victory_rate_by_trio


    @property
    def no_victory_rate(self):
        return self._no_victory_rate


class Automatic():


    @staticmethod
    def get_values_from_worksheet(gtwb_workbook_file_path):
        # ファイルを開く
        # -------------
        #
        #   GTWB ワークブック（.xlsx）
        #
        wb = xl.load_workbook(filename=gtwb_workbook_file_path)

        # GTWB ワークブック（.xlsx）ファイルの Summary シートの B2 セル（先手勝率）を見る
        summary_ws = wb['Summary']

        # ［Ａさん（シリーズを表で始めた方）が優勝した率］
        a_victory_rate_by_trio = XlUtils.lookup_vertical(
                worksheet=summary_ws,
                column_letter_for_scan='A',
                find_value=['Ａさん（シリーズを表で始めた方）が優勝した率', 'Ａさん（シリーズを先手で始めた方）が優勝した率'],  # ２番目の値は旧名
                column_letter_for_get='B')

        if a_victory_rate_by_trio is None:
            raise ValueError("not found ［Ａさん（シリーズを表で始めた方）が優勝した率］")

        a_victory_rate_by_trio = float(a_victory_rate_by_trio)


        # ［Ｂさん（シリーズをｳﾗで始めた方）が優勝した率］
        b_victory_rate_by_trio = XlUtils.lookup_vertical(
                worksheet=summary_ws,
                column_letter_for_scan='A',
                find_value=['Ｂさん（シリーズをｳﾗで始めた方）が優勝した率', 'Ｂさん（シリーズを後手で始めた方）が優勝した率'],  # ２番目の値は旧名
                column_letter_for_get='B')

        if b_victory_rate_by_trio is None:
            raise ValueError("not found ［Ｂさん（シリーズをｳﾗで始めた方）が優勝した率］")

        b_victory_rate_by_trio = float(b_victory_rate_by_trio)


        # ［優勝が決まらなかった率］
        no_victory_rate = XlUtils.lookup_vertical(
                worksheet=summary_ws,
                column_letter_for_scan='A',
                find_value='優勝が決まらなかった率',
                column_letter_for_get='B')

        if no_victory_rate is None:
            raise ValueError("not found ［優勝が決まらなかった率］")

        no_victory_rate = float(no_victory_rate)


        return TransferData(a_victory_rate_by_trio=a_victory_rate_by_trio, b_victory_rate_by_trio=b_victory_rate_by_trio, no_victory_rate=no_victory_rate)


    @staticmethod
    def open_df_and_insert_new_row_to_vrd(vrd_csv_file_path, transfer_data):
        # victory_rate_detail (VRD) ファイル名を作成する。ファイル名には turn system, failure rate, p が含まれる
        print(f"[{datetime.datetime.now()}] step_oa43o0_automatic_vrd {vrd_csv_file_path=}")
        
        # ファイルを開く
        # -------------
        #
        #   CSV ファイル。既存時
        #
        if os.path.isfile(vrd_csv_file_path):
            df = pd.read_csv(
                    vrd_csv_file_path,
                    encoding="utf-8")

            # 以下の列があれば削除
            for column_name in ['t_time', 'h_time', 'shortest_coins', 'upper_limit_coins']:
                if column_name in df.columns.values:
                    df = df.drop(column_name, axis=1)
                    print(f"[{datetime.datetime.now()}] drop column `{column_name}`")


        # ファイルの新規作成
        # -----------------
        #
        #   CSV ファイル。非存在時
        #
        else:
            df = pd.DataFrame(columns=[
                'span',
                't_step',
                'h_step',
                'a_victory_rate_by_trio',
                'b_victory_rate_by_trio',
                'no_victory_rate',
                'a_victory_rate_by_duet',
                'b_victory_rate_by_duet',
                'unfair_point'])


        # 型設定
        dtypes = {
            'span':'int64',
            't_step':'int64',
            'h_step':'int64',
            'a_victory_rate_by_trio':'float64',
            'b_victory_rate_by_trio':'float64',
            'no_victory_rate':'float64',
            'a_victory_rate_by_duet':'float64',
            'b_victory_rate_by_duet':'float64',
            'unfair_point':'float64'}
        df.astype(dtypes)


        # 行の追加
        # --------
        #
        #   victory_rate_detail (VRD) ファイルに span, t_step, h_step 毎の先手勝率を記録する
        #
        a_victory_rate_by_duet = transfer_data.a_victory_rate_by_trio/(1 - transfer_data.no_victory_rate)
        b_victory_rate_by_duet = transfer_data.b_victory_rate_by_trio/(1 - transfer_data.no_victory_rate)
        df.loc[len(df) + 1] = {
            'span':series_rule.step_table.span,
            't_step':series_rule.step_table.get_step_by(face_of_coin=TAIL),
            'h_step':series_rule.step_table.get_step_by(face_of_coin=HEAD),
            'a_victory_rate_by_trio':transfer_data.a_victory_rate_by_trio,
            'b_victory_rate_by_trio':transfer_data.b_victory_rate_by_trio,
            'no_victory_rate':transfer_data.no_victory_rate,
            'a_victory_rate_by_duet':a_victory_rate_by_duet,
            'b_victory_rate_by_duet':b_victory_rate_by_duet,
            'unfair_point':(a_victory_rate_by_duet - 0.5) ** 2 + (b_victory_rate_by_duet - 0.5) ** 2}


        return df


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        while True:

            # １秒休む
            time.sleep(1)

            # ファイル名一覧取得
            basename_list = get_list_of_basename(dir_path=GameTreeWorkbookFilePaths.get_temp_directory_path())

            # シャッフル
            random.shuffle(basename_list)


            for basename in basename_list:
                print(f"[{datetime.datetime.now()}] step_oa43o0_automatic_vrd {basename=}")

                # １秒休む
                time.sleep(1)

                # ファイル名から［シリーズ・ルール］を取得する
                series_rule = BasenameOfGameTreeWorkbookFile.to_series_rule(basename=basename)

                if series_rule is None:
                    continue


                # ファイルパス取得
                # ---------------
                gtwb_workbook_file_path = f'./{GameTreeWorkbookFilePaths.get_temp_directory_path()}/{basename}'     # GTWB ワークブック
                vrd_csv_file_path = VictoryRateDetailFilePaths.as_csv(spec=series_rule.spec)                        # VRD CSV

                try:
                    # データ読取
                    transfer_data = Automatic.get_values_from_worksheet(gtwb_workbook_file_path=gtwb_workbook_file_path)

                    # データフレーム開く＆更新
                    df = Automatic.open_df_and_insert_new_row_to_vrd(vrd_csv_file_path=vrd_csv_file_path, transfer_data=transfer_data)

                    # ソート
                    # ------
                    #
                    #   ＡさんとＢさんの勝率が 0.5 から離れていない順に並んでほしい。［勝負なし］は少ないほど好ましい。span も短いほど好ましい。
                    #
                    df.sort_values(['unfair_point', 'no_victory_rate', 'span', 't_step', 'h_step'], inplace=True)
                    
                    # FIXME 重複データが無いようにする ----> 効いてない？
                    df.drop_duplicates(inplace=True)

                    # ファイル保存
                    df.to_csv(vrd_csv_file_path, index=False)
                    print(f"[{datetime.datetime.now()}] please look `{vrd_csv_file_path}`")


                except KeyError as e:
                    message = f"[{datetime.datetime.now()}] ファイルが壊れているかも？ {gtwb_workbook_file_path=} {vrd_csv_file_path=} {e=}"
                    print(message)
                    # スタックトレース表示
                    print(traceback.format_exc())

                    log_file_path = VictoryRateDetailFilePaths.as_log(spec=series_rule.spec)
                    with open(log_file_path, 'a', encoding='utf-8') as f:
                        f.write(f"{message}\n")    # ファイルへ出力

                    # １分休む
                    seconds = 60
                    print(f"[{datetime.datetime.now()}] retry after {seconds} seconds")
                    time.sleep(seconds)


                except Exception as e:
                    message = f"[{datetime.datetime.now()}] 予期せぬ例外 {gtwb_workbook_file_path=} {vrd_csv_file_path=} {e=}"
                    print(message)
                    # スタックトレース表示
                    print(traceback.format_exc())

                    log_file_path = VictoryRateDetailFilePaths.as_log(spec=series_rule.spec)
                    with open(log_file_path, 'a', encoding='utf-8') as f:
                        f.write(f"{message}\n")    # ファイルへ出力

                    # １分休む
                    seconds = 60
                    print(f"[{datetime.datetime.now()}] retry after {seconds} seconds")
                    time.sleep(seconds)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
