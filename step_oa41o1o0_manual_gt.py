#
# python step_oa41o1o0_manual_gt.py
#
#   * `gt`` - game tree
#
#   １シリーズのコインの出目について、全パターン網羅した樹形図をCSV形式で出力します。
#   レコードは可変列です
#

import traceback
import datetime
import xltree as tr

from library import HEAD, TAIL, Specification, SeriesRule
from library.file_paths import GameTreeFilePaths
from library.database import GameTreeTable
from library.views import PromptCatalog
from library.score_board import search_all_score_boards
from scripts import SaveOrIgnore
from scripts.step_oa41o1o0_gt import GeneratorOfGT


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［先後の決め方］を尋ねます
        specified_turn_system_id = PromptCatalog.which_method_do_you_use_to_determine_sente_and_gote()


        # ［将棋の引分け率］を尋ねます
        specified_failure_rate = PromptCatalog.what_is_the_failure_rate()


        # ［将棋の先手勝率］を尋ねます
        specified_p = PromptCatalog.what_is_the_probability_of_flipping_a_coin_and_getting_heads()


        # ［目標の点数］を尋ねます
        specified_span = PromptCatalog.how_many_goal_win_points()


        # ［後手で勝ったときの勝ち点］を尋ねます
        specified_t_step = PromptCatalog.how_many_win_points_of_tail_of_coin()


        # ［先手で勝ったときの勝ち点］を尋ねます
        specified_h_step = PromptCatalog.how_many_win_points_of_head_of_coin()


        # ［仕様］
        spec = Specification(
                turn_system_id=specified_turn_system_id,
                failure_rate=specified_failure_rate,
                p=specified_p)

        # FIXME 便宜的に［試行シリーズ数］は 1 固定
        specified_trial_series = 1

        # ［シリーズ・ルール］。任意に指定します
        specified_series_rule = SeriesRule.make_series_rule_base(
                spec=spec,
                span=specified_span,
                t_step=specified_t_step,
                h_step=specified_h_step)

        
        forest = tr.planting()
        root_entry = forest.tree_root(edge_text=None, node_text='1')

        generator_of_gt = GeneratorOfGT(spec=spec, root_entry=root_entry)


        print(f"[{datetime.datetime.now()}] get score board (3) ...")
        timeout = tr.timeout(seconds=7)
        result = search_all_score_boards(
                series_rule=specified_series_rule,
                on_score_board_created=generator_of_gt.on_score_board_created,
                timeout=timeout)
        print(f"[{datetime.datetime.now()}] got score board")


        if timeout.is_expired('get score board (3)'):
            print(f"[{datetime.datetime.now()}] time-out. {timeout.message}")

        else:
            # CSVファイル出力（追記）
            csv_file_path = GameTreeFilePaths.as_csv(
                    spec=specified_series_rule.spec,
                    span=specified_series_rule.span,
                    t_step=specified_series_rule.get_step_by(face_of_coin=TAIL),
                    h_step=specified_series_rule.get_step_by(face_of_coin=HEAD))

            result = forest.to_csv(
                    csv_file_path=csv_file_path,
                    timeout=timeout)

            if timeout.is_expired('get score board (3b)'):
                print(f"[{datetime.datetime.now()}] time-out. {timeout.message}")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
