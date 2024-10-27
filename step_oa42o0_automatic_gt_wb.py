#
# python step_oa42o0_automatic_gt_wb.py
#
#   * `gt`` - game tree
#
#   １シリーズのコインの出目について、全パターン網羅した樹形図をCSV形式で出力します。
#   レコードは可変列です
#

import os
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


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # 無限ループ
        while True:
            # GT のファイル名一覧取得
            #
            #   📖 [ファイル名のみの一覧を取得](https://note.nkmk.me/python-listdir-isfile-isdir/#_1)
            #
            dir_path = "./temp/game_tree"

            basenames = [
                f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))
            ]
            #print(basenames)

            # シャッフル
            random.shuffle(basenames)

            generator_of_gtwb = GeneratorOfGTWB()

            # ファイル名をパース
            pattern = re.compile(r'GT_(alter|froze)_f([\d.]+)_p([\d.]+)_s(\d+)_t(\d+)_h(\d+)\.csv')

            for basename in basenames:
                result = pattern.match(basename)
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


                    # 出力先のファイル名を作成
                    wb_file_path = GameTreeWorkbookFilePaths.as_workbook(
                            spec=spec,
                            span=span,
                            t_step=t_step,
                            h_step=h_step)


                    # ファイルが存在しなければ実行
                    if not os.path.isfile(wb_file_path):
                        generator_of_gtwb.execute(
                                spec=series_rule.spec,
                                specified_series_rule=series_rule,
                                debug_write=False)

            # １秒休む
            time.sleep(1)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
