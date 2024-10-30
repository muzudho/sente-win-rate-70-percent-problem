#
# python step_oa42o0_automatic_gt_wb.py
#
#   * `gt`` - game tree
#
#   １シリーズのコインの出目について、全パターン網羅した樹形図をCSV形式で出力します。
#   レコードは可変列です
#

import os
import shutil
import re
import traceback
import time
import datetime
import random

from library import HEAD, TAIL, Converter, Specification, SeriesRule, get_list_of_basename
from library.file_basename import BasenameOfGameTreeFile
from library.file_paths import GameTreeFilePaths, GameTreeWorkbookFilePaths
from library.database import GameTreeTable
from library.views import PromptCatalog
from scripts import SaveOrIgnore, ForEachSpec
from scripts.step_oa42o0_gt_wb import GeneratorOfGTWB
from config import DEFAULT_UPPER_LIMIT_SPAN


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # 無限ループ
        while True:

            # １秒休む
            time.sleep(1)

            # './' を付ける
            dir_path = f"./{GameTreeFilePaths.get_directory_path()}"
            print(f"[{datetime.datetime.now()}] step42 {dir_path=}")
            basename_list = get_list_of_basename(dir_path=dir_path)

            # シャッフル
            random.shuffle(basename_list)


            for basename in basename_list:
                print(f"[{datetime.datetime.now()}] step_oa42o0 {basename=}")

                # １秒休む
                time.sleep(1)

                series_rule = BasenameOfGameTreeFile.to_series_rule(basename=basename)

                if series_rule is None:
                    continue


                generator_of_gtwb = GeneratorOfGTWB.instantiate(series_rule=series_rule)

                # ファイルが存在しなければワークブック（.xlsx）ファイルを書き出す
                if not os.path.isfile(generator_of_gtwb.workbook_file_path):

                    # TODO 高速化したい
                    generator_of_gtwb.write_workbook(debug_write=False)

                    # TODO 元ファイルを、チェック済みフォルダーへ移す
                    print(f"[{datetime.datetime.now()}] move file `{generator_of_gtwb.source_csv_file_path}` to `{generator_of_gtwb.checked_csv_file_path}`")
                    shutil.move(generator_of_gtwb.source_csv_file_path, generator_of_gtwb.checked_csv_file_path)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
