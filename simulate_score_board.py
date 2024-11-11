#
# 分析
# python simulate_score_board.py
#
#   １シリーズのコインの出目について、全パターン網羅した表を作成します
#

import traceback
import datetime
import random
import math
import xltree as tr

from library import HEAD, TAIL, ALICE, SUCCESSFUL, FACE_OF_COIN, FROZEN_TURN, ALTERNATING_TURN, ALICE_FULLY_WON, BOB_FULLY_WON, ALICE_POINTS_WON, BOB_POINTS_WON, NO_WIN_MATCH, Specification, SeriesRule, judge_series, Converter, LargeSeriesTrialSummary, SequenceOfFaceOfCoin, ScoreBoard
from library.file_paths import ScoreBoardFilePaths
from library.views import stringify_series_log, stringify_csv_of_score_board_view_header, stringify_csv_of_score_board_view_body, stringify_csv_of_score_board_view_footer, PromptCatalog
from library.score_board import search_all_score_boards


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


        # CSVファイルパス
        csv_file_path = ScoreBoardFilePaths.as_csv(
                p=specified_series_rule.spec.p,
                failure_rate=specified_series_rule.spec.failure_rate,
                turn_system_id=specified_series_rule.spec.turn_system_id,
                h_step=specified_series_rule.get_step_by(face_of_coin=HEAD),
                t_step=specified_series_rule.get_step_by(face_of_coin=TAIL),
                span=specified_series_rule.step_table.span)


        # NOTE データテーブルの形式ではない（レポート形式）ので、 pandas を使わずテキスト出力してみる


        # CSVファイル出力（上書き）
        #
        #   ファイルをクリアーしたいだけ
        #
        print(f"write csv to `{csv_file_path}` file ...")
        with open(csv_file_path, 'w', encoding='utf8') as f:
            f.write(stringify_csv_of_score_board_view_header(spec=specified_series_rule.spec, series_rule=specified_series_rule))


        def on_score_board_created(score_board):
            csv = stringify_csv_of_score_board_view_body(score_board=score_board)

            print(csv) # 表示

            # CSVファイル出力
            csv_file_path = ScoreBoardFilePaths.as_csv(
                    p=score_board.spec.p,
                    failure_rate=score_board.spec.failure_rate,
                    turn_system_id=score_board.spec.turn_system_id,
                    h_step=score_board.series_rule.get_step_by(face_of_coin=HEAD),
                    t_step=score_board.series_rule.get_step_by(face_of_coin=TAIL),
                    span=score_board.series_rule.step_table.span)
            print(f"write csv to `{csv_file_path}` file ...")
            with open(csv_file_path, 'a', encoding='utf8') as f:
                f.write(f"{csv}\n")


        print(f"[{datetime.datetime.now()}] get score board (1) ...")
        result = search_all_score_boards(
                series_rule=specified_series_rule,
                on_score_board_created=on_score_board_created,
                timeout=tr.timeout(seconds=7))
        print(f"[{datetime.datetime.now()}] got score board")

        
        if timeout.is_expired('get score board (1)'):
            print(f"[{datetime.datetime.now()}] time-out. {timeout.message}")
        
        else:
            # CSVファイル出力（追記）
            print(f"write csv to `{csv_file_path}` file ...")
            with open(csv_file_path, 'a', encoding='utf8') as f:
                f.write(stringify_csv_of_score_board_view_footer(
                        three_rates=result['three_rates'],
                        all_patterns_p=result['all_patterns_p']))


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
