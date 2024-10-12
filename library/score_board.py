import traceback

from library import ALICE, ALICE_FULLY_WON, BOB_FULLY_WON, ALICE_POINTS_WON, BOB_POINTS_WON, NO_WIN_MATCH, judge_series, AllPatternsFaceOfCoin, ScoreBoard, ThreeRates
from library.views import DebugWrite


def search_all_score_boards(series_rule, on_score_board_created):

    list_of_trial_results_for_one_series = []

    # ［出目シーケンス］の全パターンを網羅します
    tree_of_all_pattern_face_of_coin = AllPatternsFaceOfCoin(
            can_failure=0 < series_rule.spec.failure_rate,
            series_rule=series_rule).make_tree_of_all_pattern_face_of_coin()
    

    distinct_set = set()


    # tree_of_all_pattern_face_of_coin は、上限対局数の長さ
    list_of_path_of_face_of_coin = tree_of_all_pattern_face_of_coin.create_list_of_path_of_face_of_coin()
    if len(list_of_path_of_face_of_coin) < 1:
        raise ValueError(f"経路が０本なのはおかしい {len(list_of_path_of_face_of_coin)=}")


    for path_of_face_of_coin in list_of_path_of_face_of_coin:
        #print(f"動作テスト {path_of_face_of_coin=}")

        if len(path_of_face_of_coin) < 1:
            raise ValueError(f"要素を持たない経路があるのはおかしい {len(path_of_face_of_coin)=}")

        # 最短対局数を下回る対局シートはスキップします
        if len(path_of_face_of_coin) < series_rule.shortest_coins:
            #print(f"{DebugWrite.stringify(spec=series_rule.spec)}指定の対局シートの長さ {len(path_of_face_of_coin)} は、最短対局数の理論値 {series_rule.shortest_coins} を下回っています。このような対局シートを指定してはいけません")
            continue

        # ［シリーズ］１つ分の試行結果を返す
        #
        #   FIXME 決着したあとにまだリストの要素が続いていてはいけません
        #
        trial_results_for_one_series = judge_series(
                spec=series_rule.spec,
                series_rule=series_rule,
                path_of_face_of_coin=path_of_face_of_coin)


        # FIXME 検証
        if trial_results_for_one_series.number_of_coins < series_rule.shortest_coins:
            text = f"{series_rule.spec.p=} 最短対局数の実際値 {trial_results_for_one_series.number_of_coins} が理論値 {series_rule.shortest_coins} を下回った"
            print(f"""{text}
{path_of_face_of_coin=}
{series_rule.upper_limit_coins=}
{trial_results_for_one_series.stringify_dump('   ')}
""")
            raise ValueError(text)

        # FIXME 検証
        if series_rule.upper_limit_coins < trial_results_for_one_series.number_of_coins:
            text = f"{series_rule.spec.p=} 上限対局数の実際値 {trial_results_for_one_series.number_of_coins} が理論値 {series_rule.upper_limit_coins} を上回った"
            print(f"""{text}
{path_of_face_of_coin=}
{series_rule.shortest_coins=}
{trial_results_for_one_series.stringify_dump('   ')}
""")
            raise ValueError(text)


        # コインの出目のリストはサイズが切り詰められて縮まってるケースがある
        id = ''.join([str(num) for num in trial_results_for_one_series.path_of_face_of_coin])

        # 既に処理済みのものはスキップ
        if id in distinct_set:
            #print(f"既に処理済みのものはスキップ  {id=}  {trial_results_for_one_series.path_of_face_of_coin=}  {path_of_face_of_coin=}")
            continue

        distinct_set.add(id)

        list_of_trial_results_for_one_series.append(trial_results_for_one_series)


    if len(list_of_trial_results_for_one_series) < 1:
        raise ValueError(f"経路が０本なのはおかしい {len(list_of_trial_results_for_one_series)=}")


    all_patterns_p = 0
    a_win_rate_with_draw = 0
    b_win_rate_with_draw = 0
    no_win_match_rate = 0


    for pattern_no, trial_results_for_one_series in enumerate(list_of_trial_results_for_one_series, 1):

        score_board = ScoreBoard.make_score_board(
                pattern_no=pattern_no,
                spec=series_rule.spec,
                series_rule=series_rule,
                path_of_face_of_coin=trial_results_for_one_series.path_of_face_of_coin)


        on_score_board_created(score_board=score_board)


        all_patterns_p += score_board.pattern_p

        # 満点で,Ａさんの勝ち
        # 勝ち点差で,Ａさんの勝ち
        if score_board.game_results == ALICE_FULLY_WON or score_board.game_results == ALICE_POINTS_WON:
            a_win_rate_with_draw += score_board.pattern_p

        # 満点で,Ｂさんの勝ち
        # 勝ち点差で,Ｂさんの勝ち
        #
        #   NOTE ［Ａさんの勝ち］が分かれば［Ｂさんの勝ち］は調べなくていいが、一応、検算のために取っておく
        #
        elif score_board.game_results == BOB_FULLY_WON or score_board.game_results == BOB_POINTS_WON:
            b_win_rate_with_draw += score_board.pattern_p
        
        # 勝者なし
        elif score_board.game_results == NO_WIN_MATCH:
            no_win_match_rate += score_board.pattern_p
        
        else:
            raise ValueError(f"{score_board.game_results=}")

    
    # ＡさんとＢさんの勝率は、足しても１００％にならない。勝者なしの勝率を取り除いた分だから。
    # 足して１００％になるように、引き延ばす必要がある
    win_match_rate = 1 - no_win_match_rate
    # 以下の数を［Ａさんの勝率］、［Ｂさんの勝率］に掛けると、１００％に引き延ばされる
    # FIXME 0除算にならないように注意
    zoom = 1 / win_match_rate

    a_win_rate = zoom * a_win_rate_with_draw
    b_win_rate = zoom * b_win_rate_with_draw
    if a_win_rate == 0 or b_win_rate == 0:
        raise ValueError(f"勝率が両者０％なのはおかしい {all_patterns_p=}  {a_win_rate_with_draw=}  {b_win_rate_with_draw=}  {no_win_match_rate=}  {zoom=}")

    three_rates = ThreeRates.create_three_rates(
            a_win_rate=a_win_rate,
            b_win_rate=b_win_rate,
            no_win_match_rate=no_win_match_rate)
    return three_rates, all_patterns_p
