import traceback
import random
import math

import pandas as pd

from library import HEAD, TAIL, ALICE, SUCCESSFUL, FACE_OF_COIN, FROZEN_TURN, ALTERNATING_TURN, ALICE_FULLY_WON, BOB_FULLY_WON, ALICE_POINTS_WON, BOB_POINTS_WON, NO_WIN_MATCH, Specification, SeriesRule, judge_series, Converter, LargeSeriesTrialSummary, SequenceOfFaceOfCoin, ScoreBoard
from library.file_paths import get_score_board_view_csv_file_path
from library.views import stringify_series_log, stringify_csv_of_score_board_view_header, stringify_csv_of_score_board_view_body, stringify_csv_of_score_board_view_footer


def search_all_score_boards(series_rule, on_score_board_created):

    list_of_trial_results_for_one_series = []

    # ［出目シーケンス］の全パターンを網羅します
    list_of_all_pattern_face_of_coin = SequenceOfFaceOfCoin.make_list_of_all_pattern_face_of_coin(
            can_failure=0 < series_rule.spec.failure_rate,
            series_rule=series_rule)
    

    distinct_set = set()


    # list_of_all_pattern_face_of_coin は、上限対局数の長さ
    for list_of_face_of_coin in list_of_all_pattern_face_of_coin:
        #print(f"動作テスト {list_of_face_of_coin=}")

        # 最短対局数を下回る対局シートはスキップします
        if len(list_of_face_of_coin) < series_rule.shortest_coins:
            #print(f"{series_rule.spec.p=} 指定の対局シートの長さ {len(list_of_face_of_coin)} は、最短対局数の理論値 {series_rule.shortest_coins} を下回っています。このような対局シートを指定してはいけません")
            continue

        # ［シリーズ］１つ分の試行結果を返す
        #
        #   FIXME 決着したあとにまだリストの要素が続いていてはいけません
        #
        trial_results_for_one_series = judge_series(
                spec=series_rule.spec,
                series_rule=series_rule,
                list_of_face_of_coin=list_of_face_of_coin)


        # FIXME 検証
        if trial_results_for_one_series.number_of_coins < series_rule.shortest_coins:
            text = f"{series_rule.spec.p=} 最短対局数の実際値 {trial_results_for_one_series.number_of_coins} が理論値 {series_rule.shortest_coins} を下回った"
            print(f"""{text}
{list_of_face_of_coin=}
{series_rule.upper_limit_coins=}
{trial_results_for_one_series.stringify_dump('   ')}
""")
            raise ValueError(text)

        # FIXME 検証
        if series_rule.upper_limit_coins < trial_results_for_one_series.number_of_coins:
            text = f"{series_rule.spec.p=} 上限対局数の実際値 {trial_results_for_one_series.number_of_coins} が理論値 {series_rule.upper_limit_coins} を上回った"
            print(f"""{text}
{list_of_face_of_coin=}
{series_rule.shortest_coins=}
{trial_results_for_one_series.stringify_dump('   ')}
""")
            raise ValueError(text)


        # コインの出目のリストはサイズが切り詰められて縮まってるケースがある
        id = ''.join([str(num) for num in trial_results_for_one_series.list_of_face_of_coin])

        # 既に処理済みのものはスキップ
        if id in distinct_set:
            #print(f"スキップ  {id=}  {trial_results_for_one_series.list_of_face_of_coin=}  {list_of_face_of_coin=}")
            continue

        distinct_set.add(id)

        list_of_trial_results_for_one_series.append(trial_results_for_one_series)


    all_patterns_p = 0
    a_win_rate = 0
    b_win_rate = 0
    no_win_match_rate = 0


    for pattern_no, trial_results_for_one_series in enumerate(list_of_trial_results_for_one_series, 1):

        score_board = ScoreBoard.make_score_board(
                pattern_no=pattern_no,
                spec=series_rule.spec,
                series_rule=series_rule,
                list_of_face_of_coin=trial_results_for_one_series.list_of_face_of_coin)


        on_score_board_created(score_board=score_board)


        all_patterns_p += score_board.pattern_p

        # 満点で,Ａさんの勝ち
        # 勝ち点差で,Ａさんの勝ち
        if score_board.game_results == ALICE_FULLY_WON or score_board.game_results == ALICE_POINTS_WON:
            a_win_rate += score_board.pattern_p

        # 満点で,Ｂさんの勝ち
        # 勝ち点差で,Ｂさんの勝ち
        elif score_board.game_results == BOB_FULLY_WON or score_board.game_results == BOB_POINTS_WON:
            b_win_rate += score_board.pattern_p
        
        # 勝者なし
        elif score_board.game_results == NO_WIN_MATCH:
            no_win_match_rate += score_board.pattern_p
        
        else:
            raise ValueError(f"{score_board.game_results=}")

    
    return a_win_rate, b_win_rate, no_win_match_rate, all_patterns_p
