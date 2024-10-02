#
# 分析
# python create_a_csv_to_view_score_board.py
#
#   １シリーズのコインの出目について、全パターン網羅した表を作成します
#

import traceback
import random
import math

import pandas as pd

from library import HEAD, TAIL, ALICE, SUCCESSFUL, FACE_OF_COIN, FROZEN_TURN, ALTERNATING_TURN, ALICE_FULLY_WON, BOB_FULLY_WON, ALICE_POINTS_WON, BOB_POINTS_WON, NO_WIN_MATCH, Specification, SeriesRule, judge_series, Converter, LargeSeriesTrialSummary, SequenceOfFaceOfCoin, ScoreBoard
from library.file_paths import get_score_board_view_csv_file_path
from library.views import stringify_series_log, stringify_csv_of_score_board_view_header, stringify_csv_of_score_board_view_body, stringify_csv_of_score_board_view_footer
from library.score_board import search_all_score_boards


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［将棋の先手勝率］
        prompt = f"""\

Example: 70% is 0.7
What is the probability of flipping a coin and getting heads? """
        specified_p = float(input(prompt))


        # ［将棋の引分け率］
        prompt = f"""\

Example: 10% is 0.1
What is the failure rate? """
        specified_failure_rate = float(input(prompt))


        # ［先後の決め方］
        prompt = f"""\

(1) Frozen turn
(2) Alternating turn
Example: Alternating turn is 2
Which one(1-2)? """
        choice = input(prompt)

        if choice == '1':
            specified_turn_system = FROZEN_TURN

        elif choice == '2':
            specified_turn_system = ALTERNATING_TURN

        else:
            raise ValueError(f"{choice=}")


        # ［先手で勝ったときの勝ち点］
        prompt = f"""\

Example: 2
How many win points of head of coin? """
        specified_h_step = int(input(prompt))


        # ［後手で勝ったときの勝ち点］
        prompt = f"""\

Example: 3
How many win points of tail of coin? """
        specified_t_step = int(input(prompt))


        # ［目標の点数］
        prompt = f"""\

Example: 6
How many goal win points? """
        specified_span = int(input(prompt))


        # 仕様
        spec = Specification(
                p=specified_p,
                failure_rate=specified_failure_rate,
                turn_system=specified_turn_system)

        # FIXME 便宜的に［試行シリーズ数］は 1 固定
        specified_trials_series = 1

        # ［シリーズ・ルール］。任意に指定します
        specified_series_rule = SeriesRule.make_series_rule_base(
                spec=spec,
                trials_series=specified_trials_series,      # この［シリーズ・ルール］を作成するために行われた［試行シリーズ数］
                h_step=specified_h_step,
                t_step=specified_t_step,
                span=specified_span)


        # CSVファイル出力（上書き）
        #
        #   ファイルをクリアーしたいだけ
        #
        csv_file_path = get_score_board_view_csv_file_path(
                p=specified_series_rule.spec.p,
                failure_rate=specified_series_rule.spec.failure_rate,
                turn_system=specified_series_rule.spec.turn_system,
                h_step=specified_series_rule.step_table.get_step_by(face_of_coin=HEAD),
                t_step=specified_series_rule.step_table.get_step_by(face_of_coin=TAIL),
                span=specified_series_rule.step_table.span)
        print(f"write csv to `{csv_file_path}` file ...")
        with open(csv_file_path, 'w', encoding='utf8') as f:
            f.write(stringify_csv_of_score_board_view_header(spec=specified_series_rule.spec, series_rule=specified_series_rule))


        def on_score_board_created(score_board):
            csv = stringify_csv_of_score_board_view_body(score_board=score_board)

            print(csv) # 表示

            # CSVファイル出力
            csv_file_path = get_score_board_view_csv_file_path(
                    p=score_board.spec.p,
                    failure_rate=score_board.spec.failure_rate,
                    turn_system=score_board.spec.turn_system,
                    h_step=score_board.series_rule.step_table.get_step_by(face_of_coin=HEAD),
                    t_step=score_board.series_rule.step_table.get_step_by(face_of_coin=TAIL),
                    span=score_board.series_rule.step_table.span)
            print(f"write csv to `{csv_file_path}` file ...")
            with open(csv_file_path, 'a', encoding='utf8') as f:
                f.write(f"{csv}\n")


        three_rates, all_patterns_p = search_all_score_boards(
                series_rule=specified_series_rule,
                on_score_board_created=on_score_board_created)


        # CSVファイル出力（追記）
        csv_file_path = get_score_board_view_csv_file_path(
                p=specified_series_rule.spec.p,
                failure_rate=specified_series_rule.spec.failure_rate,
                turn_system=specified_series_rule.spec.turn_system,
                h_step=specified_series_rule.step_table.get_step_by(face_of_coin=HEAD),
                t_step=specified_series_rule.step_table.get_step_by(face_of_coin=TAIL),
                span=specified_series_rule.step_table.span)
        print(f"write csv to `{csv_file_path}` file ...")
        with open(csv_file_path, 'a', encoding='utf8') as f:
            f.write(stringify_csv_of_score_board_view_footer(
                    three_rates=three_rates,
                    all_patterns_p=all_patterns_p))


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
