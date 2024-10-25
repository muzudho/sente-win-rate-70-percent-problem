#
# python step_oa41o0_automatic_gt.py
#
#   * `gt`` - game tree
#
#   １シリーズのコインの出目について、全パターン網羅した樹形図をCSV形式で出力します。
#   レコードは可変列です
#

import traceback
import xltree as tr

from library import HEAD, TAIL, Specification, SeriesRule
from library.file_paths import GameTreeFilePaths
from library.database import GameTreeTable
from library.views import PromptCatalog
from library.score_board import search_all_score_boards
from scripts import SaveOrIgnore, ForEachSpec
from scripts.step_oa41o1o0_gt import Automatic
from config import DEFAULT_UPPER_LIMIT_SPAN


class SubAutomatic():


    def on_each_spec(self, spec):
        # TODO ［目標の点数］
        #for specified_span in (1, DEFAULT_UPPER_LIMIT_SPAN):
        for specified_span in range(1, 4):
            for specified_t_step in range(1, specified_span + 1):

                for specified_h_step in range(1, specified_t_step + 1):

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

        # FIXME 便宜的に［試行シリーズ数］は 1 固定
        specified_trial_series = 1


        forest = tr.planting()
        root_entry = forest.tree_root(edge_text=None, node_text='1')

        automatic = Automatic(spec=specified_series_rule.spec, root_entry=root_entry)

        three_rates, all_patterns_p = search_all_score_boards(
                series_rule=specified_series_rule,
                on_score_board_created=automatic.on_score_board_created)


        # CSVファイル出力（追記）
        forest.to_csv(csv_file_path=GameTreeFilePaths.as_csv(
                spec=specified_series_rule.spec,
                span=specified_series_rule.step_table.span,
                t_step=specified_series_rule.step_table.get_step_by(face_of_coin=TAIL),
                h_step=specified_series_rule.step_table.get_step_by(face_of_coin=HEAD)))


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
