#
# python step_oa42o0_automatic_gt_wb.py
#
#   * `gt`` - game tree
#
#   １シリーズのコインの出目について、全パターン網羅した樹形図をCSV形式で出力します。
#   レコードは可変列です
#

import traceback

from library import HEAD, TAIL, Specification, SeriesRule
from library.file_paths import GameTreeFilePaths
from library.database import GameTreeTable
from library.views import PromptCatalog
from library.score_board import search_all_score_boards
from scripts import SaveOrIgnore, ForEachSpec
from scripts.step_oa42o0_gt_wb import Automation
from config import DEFAULT_UPPER_LIMIT_SPAN


class SubAutomatic():


    def on_each_spec(self, spec):
        # TODO ［目標の点数］
        #for specified_span in (1, DEFAULT_UPPER_LIMIT_SPAN):
        for specified_span in (1, 3):
            for specified_t_step in (1, specified_span):

                for specified_h_step in (1, specified_t_step):

                    # ［シリーズ・ルール］。任意に指定します
                    specified_series_rule = SeriesRule.make_series_rule_base(
                            spec=spec,
                            span=specified_span,
                            t_step=specified_t_step,
                            h_step=specified_h_step)

                    self.on_each_series_rule(specified_series_rule=specified_series_rule)

            #         print(f"デバッグ ループ途中終了  {spec.stringify_dump('')}  {specified_h_step=}")
            #         break


            #     print(f"デバッグ ループ途中終了  {spec.stringify_dump('')}  {specified_t_step=}")
            #     break


            # print(f"デバッグ ループ途中終了  {spec.stringify_dump('')}  {specified_span=}")
            # break


    def on_each_series_rule(self, specified_series_rule):

        automation = Automation()
        automation.execute(
                spec=specified_series_rule.spec,
                specified_series_rule=specified_series_rule,
                debug_write=False)


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        sub_automatic = SubAutomatic()

        ForEachSpec.execute(on_each_spec=sub_automatic.on_each_spec)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
