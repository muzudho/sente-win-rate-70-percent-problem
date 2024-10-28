# python step_oa43o0_automatic_wrb.py
#

import time
import random
import openpyxl as xl
from .library import get_list_of_basename
from library.file_basename import BasenameOfGameTreeWorkbookFile
from .library.file_paths import GameTreeWorkbookFilePaths


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # # １秒休む
        # time.sleep(1)

        # TODO game_tree_wb フォルダーを見る
        basename_list = get_list_of_basename(dir_path=GameTreeWorkbookFilePaths.get_directory_path())

        # シャッフル
        random.shuffle(basename_list)


        for basename in basename_list:

            # ファイル名から［シリーズ・ルール］を取得する
            series_rule = BasenameOfGameTreeFile.to_series_rule(basename=basename)

            if series_rule is not None:

                # TODO GTWB ワークブック（.xlsx）ファイルを開く
                wb = xl.load_workbook(filename=basename)

                # TODO GTWB ワークブック（.xlsx）ファイルの Summary シートの B2 セル（先手勝率）を見る
                summary_ws = wb['Summary']
                failure_rate = float(summary_ws["B3"])
                sente_win_rate = float(summary_ws["B2"]) / (1 - failure_rate)

                # TODO sente_win_rate_detail (SWRD) ファイル名を作成する。ファイル名には turn system, failure rate, p が含まれる

                # TODO sente_win_rate_detail (SWRD) ファイルに span, t_step, h_step 毎の先手勝率を記録する

        # TODO （step44o0）sente_win_rate_summary (SWRS) ファイル毎の最小の先手勝率を集計し、 turn system, failure rate, p 毎に WRB ファイルに記録する

    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
