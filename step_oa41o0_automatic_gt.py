#
# python step_oa41o0_automatic_gt.py
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
from scripts.step_oa41o0_gt import Automatic
from config import DEFAULT_UPPER_LIMIT_SPAN


class SubAutomatic():


    def on_each_spec(self, spec):
        # TODO ［目標の点数］
        for specified_span in (1, DEFAULT_UPPER_LIMIT_SPAN):
            for specified_t_step in (1, specified_span):
                for specified_h_step in (1, specified_t_step):

                    # ［シリーズ・ルール］。任意に指定します
                    specified_series_rule = SeriesRule.make_series_rule_base(
                            spec=spec,
                            span=specified_span,
                            t_step=specified_t_step,
                            h_step=specified_h_step)

                    self.on_each_series_rule(specified_series_rule=specified_series_rule)


    def on_each_series_rule(self, specified_series_rule):

        # FIXME 便宜的に［試行シリーズ数］は 1 固定
        specified_trial_series = 1

        # GTテーブル。ファイルが無ければ作成します
        gt_table, file_read_result = GameTreeTable.from_csv(
                spec=specified_series_rule.spec,
                span=specified_series_rule.step_table.span,
                t_step=specified_series_rule.step_table.get_step_by(face_of_coin=TAIL),
                h_step=specified_series_rule.step_table.get_step_by(face_of_coin=HEAD),
                new_if_it_no_exists=True)
        

        automatic = Automatic(spec=specified_series_rule.spec, gt_table=gt_table)

        three_rates, all_patterns_p = search_all_score_boards(
                series_rule=specified_series_rule,
                on_score_board_created=automatic.on_score_board_created)


        # CSVファイル出力（追記）
        SaveOrIgnore.execute(
                log_file_path=GameTreeFilePaths.as_log(
                        spec=specified_series_rule.spec,
                        span=specified_series_rule.step_table.span,
                        t_step=specified_series_rule.step_table.get_step_by(face_of_coin=TAIL),
                        h_step=specified_series_rule.step_table.get_step_by(face_of_coin=HEAD)),
                on_save_and_get_file_name=gt_table.to_csv)


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
