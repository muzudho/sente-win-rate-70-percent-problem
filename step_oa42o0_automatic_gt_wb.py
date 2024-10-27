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

from library import HEAD, TAIL, Converter, Specification, SeriesRule
from library.file_paths import GameTreeFilePaths, GameTreeWorkbookFilePaths
from library.database import GameTreeTable
from library.views import PromptCatalog
from scripts import SaveOrIgnore, ForEachSpec
from scripts.step_oa42o0_gt_wb import GeneratorOfGTWB
from config import DEFAULT_UPPER_LIMIT_SPAN


class Automatic():


    # ファイル名をパース
    _pattern = re.compile(r'GT_(alter|froze)_f([\d.]+)_p([\d.]+)_s(\d+)_t(\d+)_h(\d+)\.csv')


    @staticmethod
    def get_list_of_basename_of_gt(dir_path):
        """GT のファイル名一覧取得
        
        📖 [ファイル名のみの一覧を取得](https://note.nkmk.me/python-listdir-isfile-isdir/#_1)
        """
        basename_list = [
            f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))
        ]
        #print(basename_list)

        return basename_list


    @classmethod
    def get_series_rule_by_bestname(clazz, basename):

        result = clazz._pattern.match(basename)

        if result:
            print(f"[{datetime.datetime.now()}] step_oa42o0 {basename=}")

            turn_system_id = Converter.turn_system_code_to_id(code=result.group(1))
            # １００分率になってるので、0～1 に戻します
            failure_rate = float(result.group(2)) / 100
            p = float(result.group(3)) / 100
            span = int(result.group(4))
            t_step = int(result.group(5))
            h_step = int(result.group(6))

            # 仕様
            spec = Specification(
                    turn_system_id=turn_system_id,
                    failure_rate=failure_rate,
                    p=p)

            # ［シリーズ・ルール］
            series_rule = SeriesRule.make_series_rule_base(
                    spec=spec,
                    span=span,
                    t_step=t_step,
                    h_step=h_step)
            
            return series_rule
        
        
        return None


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
            basename_list = Automatic.get_list_of_basename_of_gt(dir_path=dir_path)

            # シャッフル
            random.shuffle(basename_list)


            for basename in basename_list:

                series_rule = Automatic.get_series_rule_by_bestname(basename=basename)

                if series_rule is None:
                    continue


                generator_of_gtwb = GeneratorOfGTWB.instantiate(series_rule=series_rule)

                # ファイルが存在しなければワークブック（.xlsx）ファイルを書き出す
                if not os.path.isfile(generator_of_gtwb.workbook_file_path):
                    generator_of_gtwb.write_workbook(debug_write=False)

                    # TODO 元ファイルを、チェック済みフォルダーへ移す
                    print(f"[{datetime.datetime.now()}] move file `{generator_of_gtwb.source_csv_file_path}` to `{generator_of_gtwb.checked_csv_file_path}`")
                    shutil.move(generator_of_gtwb.source_csv_file_path, generator_of_gtwb.checked_csv_file_path)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
