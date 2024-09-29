#
# 表示
# python create_a_csv_to_view_evenizer_in_excel.py
#
#   Excel で［かくきんシステムの表］を表示するための CSV を作成する
#
#   NOTE 書式のような仕様は頻繁に変更することがあります
#

import traceback
import re

from library import HEAD, TAIL, ALICE, BOB, SUCCESSFUL, FAILED, FACE_OF_COIN, PLAYERS, FROZEN_TURN, ALTERNATING_TURN, BRUTE_FORCE, THEORETICAL, IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO, Converter, round_letro, Specification, SeriesRule, judge_series, LargeSeriesTrialSummary, SequenceOfFaceOfCoin
from library.file_paths import get_even_view_csv_file_path
from library.database import get_df_selection_series_rule, get_df_even, EvenTable, SelectionSeriesRuleTable


def stringify_header():
    """\
    データの構造
    +------------------------------------------------+---------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Specification                                  | Series rule                                                               | Large Series Trial Summary                                                                                                                                                                                                                              |
    | 前提条件                                        | 大会のルール設定                                                           | シミュレーション結果                                                                                                                                                                                                                                      |
    +---------------+------------------+-------------+-------------+-------------+-----------+---------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | p             | failure_rate     | turn_system | head_step   | tail_step   | span     | shortest_coins | upper_limit_coins | trials_series    series_shortest_coins  series_longest_coins                                                                                                                                                                                            |
    | 将棋の先手勝率 | 将棋の引分け率    | 先後の決め方 | 先手で勝った  | 後手で勝った | シリーズ  | 最短対局数     | 上限対局数         | 試行シリーズ総数  シリーズ最短対局数      シリーズ最長対局数                                                                                                                                                                                                 |
    | ％            | ％               |             | ときの勝ち点  | ときの勝ち点 | 勝利条件  |               |                   |                                                                                            ______________________________________________________________________________________________________________________________________________________________|
    |               |                  |             |              |             |          |               |                   |                                                                                           | succucessful_series                                                   | failed_series                                                                       |
    |               |                  |             |              |             |          |               |                   |                                                                                           | 引分けが起こらなかったシリーズ数                                         | 引分けが含まれたシリーズ数                                                            |
    |               |                  |             |              |             |          |               |                   |                                                                総数                       |                                                                       |                                                                                      |
    |               |                  |             |              |             |          |               |                   |                                                                ___________________________|                                                                       |                                                                        _____________|
    |               |                  |             |              |             |          |               |                   |                                                               | wins_a      | wins_b      |                                                                       |                                                                        | no_wins_ab |
    |               |                  |             |              |             |          |               |                   |                                                               | Ａさんの勝ち | Ｂさんの勝ち |             勝利条件達成                   点数差による判定勝ち          |             勝利条件達成                   点数差による判定勝ち           | 勝敗付かず  |
    |               |                  |             |              |             |          |               |                   |                                                               | シリーズ数   | シリーズ数   |            ___________________________________________________________|           _____________________________________________________________| シリーズ数  |
    |               |                  |             |              |             |          |               |                   |                                                               |             |             |           | s_ful_wins_a | s_ful_wins_b | s_pts_wins_a | s_pts_wins_b |           | f_ful_wins_a  | f_ful_wins_b | f_pts_wins_a | f_pts_wins_b |            |
    |               |                  |             |              |             |          |               |                   |                                                               |             |             |           | Ａさんの勝ち  | Ｂさんの勝ち  | Ａさんの勝ち  | Ｂさんの勝ち  |            | Ａさんの勝ち  | Ｂさんの勝ち  | Ａさんの勝ち  | Ｂさんの勝ち  |             |
    |               |                  |             |              |             |          |               |                   |                                                               |             |             |           | シリーズ数    | シリーズ数    | シリーズ数    | シリーズ数    |           | シリーズ数    | シリーズ数    | シリーズ数    | シリーズ数    |             |
    |               |                  |             |              |             |          |               |                   |                                                               |             |             |           |              |              |              |              |            |              |              |              |              |             |
    +---------------+------------------+-------------+--------------+-------------+----------+---------------+-------------------+---------------------------------------------------------------+-------------+-------------+-----------+--------------+--------------+--------------+--------------+------------+--------------+--------------+--------------+--------------+-------------+
    """

    # CSV
    return f"p,failure_rate,turn_system,head_step,tail_step,span,shortest_coins,upper_limit_coins,trials_series,series_shortest_coins,series_longest_coins,wins_a,wins_b,succucessful_series,s_ful_wins_a,s_ful_wins_b,s_pts_wins_a,s_pts_wins_b,failed_series,f_ful_wins_a,f_ful_wins_b,f_pts_wins_a,f_pts_wins_b,no_wins_ab"


def stringify_csv_of_body(spec, series_rule, presentable, comment, large_series_trial_summary):
    """データ部を文字列化

    Parameters
    ----------
    spec : Specification
        ［仕様］
    """

    # 変数名を縮める（Summary）
    S = large_series_trial_summary


    s_wins_a = S.wins(challenged=SUCCESSFUL, winner=ALICE)
    f_wins_a = S.wins(challenged=FAILED, winner=ALICE)
    s_wins_b = S.wins(challenged=SUCCESSFUL, winner=BOB)
    f_wins_b = S.wins(challenged=FAILED, winner=BOB)


    # ［前提条件］
    str_p = f"{spec.p*100:.4f}"                                                 # ［将棋の先手勝率］ p （Probability）
    str_failure_rate = f"{spec.failure_rate*100:.4f}"                           # ［将棋の引分け率］
    str_turn_system = f"{Converter.turn_system_to_code(spec.turn_system)}"      # ［手番の決め方］

    # ［大会のルール設定］
    str_head_step = f"{series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)}"   # ［先手で勝ったときの勝ち点］
    str_tail_step = f"{series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)}"   # ［後手で勝ったときの勝ち点］
    str_span = f"{series_rule.step_table.span}"                                 # ［シリーズ勝利条件］
    str_shortest_coins = f"{series_rule.shortest_coins}"                        # ［最短対局数］
    str_upper_limit_coins = f"{series_rule.upper_limit_coins}"                  # ［上限対局数］
                                                                                # NOTE ルール設定を求めたときの試行回数も記録しようかと思ったが、作り方についてそんなに信用できる記録でもないので止めた

    # ［シミュレーション結果］
    str_trials_series = f"{S.total}"                                             # ［試行シリーズ総数］
    str_series_shortest_coins = f"{S.series_shortest_coins}"                    # ［シリーズ最短局数］
    str_series_longest_coins = f"{S.series_longest_coins}"                      # ［シリーズ最長局数］
    str_wins_a = f"{s_wins_a + f_wins_a}"                                       # ［Ａさんの勝ちシリーズ数］
    str_wins_b = f"{s_wins_b + f_wins_b}"                                       # ［Ｂさんの勝ちシリーズ数］
    str_succucessful_series = f"{S.successful_series}"                          # ［引分けが起こらなかったシリーズ数］
    str_s_ful_wins_a = f"{S.ful_wins(challenged=SUCCESSFUL, winner=ALICE)}"     # ［引分けが起こらなかったシリーズ＞勝利条件達成＞Ａさんの勝ち］
    str_s_ful_wins_b = f"{S.ful_wins(challenged=SUCCESSFUL, winner=BOB)}"       # ［引分けが起こらなかったシリーズ＞勝利条件達成＞Ｂさんの勝ち］
    str_s_pts_wins_a = f"{S.pts_wins(challenged=SUCCESSFUL, winner=ALICE)}"     # ［引分けが起こらなかったシリーズ＞点数差による判定勝ち＞Ａさんの勝ち］
    str_s_pts_wins_b = f"{S.pts_wins(challenged=SUCCESSFUL, winner=BOB)}"       # ［引分けが起こらなかったシリーズ＞点数差による判定勝ち＞Ｂさんの勝ち］
    str_failed_series = f"{S.failed_series}"                                    # ［引分けが含まれたシリーズ数］
    str_f_ful_wins_a = f"{S.ful_wins(challenged=FAILED, winner=ALICE)}"         # ［引分けが含まれたシリーズ＞勝利条件達成＞Ａさんの勝ち］
    str_f_ful_wins_b = f"{S.ful_wins(challenged=FAILED, winner=BOB)}"           # ［引分けが含まれたシリーズ＞勝利条件達成＞Ｂさんの勝ち］
    str_f_pts_wins_a = f"{S.pts_wins(challenged=FAILED, winner=ALICE)}"         # ［引分けが含まれたシリーズ＞点数差による判定勝ち＞Ａさんの勝ち］
    str_f_pts_wins_b = f"{S.pts_wins(challenged=FAILED, winner=BOB)}"           # ［引分けが含まれたシリーズ＞点数差による判定勝ち＞Ｂさんの勝ち］
    str_no_wins_ab = f"{S.no_wins}"                                             # ［勝敗付かずシリーズ数］


    # CSV
    return f"{str_p},{str_failure_rate},{str_turn_system},{str_head_step},{str_tail_step},{str_span},{str_shortest_coins},{str_upper_limit_coins},{str_trials_series},{str_series_shortest_coins},{str_series_longest_coins},{str_wins_a},{str_wins_b},{str_succucessful_series},{str_s_ful_wins_a},{str_s_ful_wins_b},{str_s_pts_wins_a},{str_s_pts_wins_b},{str_failed_series},{str_f_ful_wins_a},{str_f_ful_wins_b},{str_f_pts_wins_a},{str_f_pts_wins_b},{str_no_wins_ab}"


def show_series_rule(spec, specified_trials_series, p_step, q_step, span, presentable, comment):
    """［シリーズ・ルール］を表示します"""

    # ［シリーズ・ルール］。任意に指定します
    series_rule = SeriesRule.make_series_rule_base(
            spec=spec,
            trials_series=specified_trials_series,
            p_step=p_step,
            q_step=q_step,
            span=span)


    list_of_trial_results_for_one_series = []

    for round in range(0, specified_trials_series):

        # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
        list_of_face_of_coin = SequenceOfFaceOfCoin.make_sequence_of_playout(
                spec=spec,
                upper_limit_coins=series_rule.upper_limit_coins)

        # FIXME 検証
        if len(list_of_face_of_coin) < series_rule.shortest_coins:
            text = f"{spec.p=} 指定の対局シートの長さ {len(list_of_face_of_coin)} は、最短対局数の理論値 {series_rule.shortest_coins} を下回っています。このような対局シートを指定してはいけません"
            print(f"""{text}
{list_of_face_of_coin=}
{series_rule.upper_limit_coins=}
""")
            raise ValueError(text)


        # ［シリーズ］１つ分の試行結果を返す
        trial_results_for_one_series = judge_series(
                spec=spec,
                series_rule=series_rule,
                list_of_face_of_coin=list_of_face_of_coin)

        list_of_trial_results_for_one_series.append(trial_results_for_one_series)


    # ［大量のシリーズを試行した結果］
    large_series_trial_summary = LargeSeriesTrialSummary(
            list_of_trial_results_for_one_series=list_of_trial_results_for_one_series)


    csv = stringify_csv_of_body(
            spec=spec,
            series_rule=series_rule,
            presentable=presentable,
            comment=comment,
            large_series_trial_summary=large_series_trial_summary)


    print(csv) # 表示

    # ログ出力
    csv_file_path = get_even_view_csv_file_path(spec=spec, trials_series=specified_trials_series)
    with open(csv_file_path, 'a', encoding='utf8') as f:
        f.write(f"{csv}\n")    # ファイルへ出力


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        prompt = f"""\
What is the failure rate?
Example: 10% is 0.1
? """
        specified_failure_rate = float(input(prompt))


        prompt = f"""\
(1) Frozen turn
(2) Alternating turn
Which one(1-2)? """
        choice = input(prompt)

        if choice == '1':
            specified_turn_system = FROZEN_TURN

        elif choice == '2':
            specified_turn_system = ALTERNATING_TURN

        else:
            raise ValueError(f"{choice=}")


        prompt = f"""\
(1) even series rule
(2) selection series rule
Which data source should I use?
> """
        data_source = int(input(prompt))


        # ［試行シリーズ数］を尋ねる
        prompt = f"""\
How many times do you want to try the series?

(0) Try       2 series
(1) Try      20 series
(2) Try     200 series
(3) Try    2000 series
(4) Try   20000 series
(5) Try  200000 series
(6) Try 2000000 series

Example: 3
(0-6)? """
        precision = int(input(prompt))
        specified_trials_series = Converter.precision_to_trials_series(precision)


        header_csv = stringify_header()

        print(header_csv) # 表示

        # 仕様
        spec = Specification(
                p=None,
                failure_rate=specified_failure_rate,
                turn_system=specified_turn_system)


        # ヘッダー出力（ファイルは上書きします）
        #
        #   NOTE ビューは既存ファイルの内容は破棄して、毎回、１から作成します
        #
        csv_file_path = get_even_view_csv_file_path(spec=spec, trials_series=specified_trials_series)
        with open(csv_file_path, 'w', encoding='utf8') as f:
            f.write(f"{header_csv}\n")


        # TODO
        if data_source == 1:
            title='イーブン［シリーズ・ルール］'

            generation_algorythm = Converter.make_generation_algorythm(failure_rate=specified_failure_rate, turn_system=specified_turn_system)
            if generation_algorythm == BRUTE_FORCE:
                print("力任せ探索で行われたデータです")
            elif generation_algorythm == THEORETICAL:
                print("理論値で求められたデータです")
            else:
                raise ValueError(f"{generation_algorythm=}")


            df_ev = get_df_even(failure_rate=specified_failure_rate, turn_system=specified_turn_system, generation_algorythm=generation_algorythm, trials_series=specified_trials_series)

            for            p,          failure_rate,          turn_system,          trials_series,          best_p,          best_p_error,          best_p_step,          best_q_step,          best_span,          latest_p,          latest_p_error,          latest_p_step,          latest_q_step,          latest_span,          candidates in\
                zip(df_ev['p'], df_ev['failure_rate'], df_ev['turn_system'], df_ev['trials_series'], df_ev['best_p'], df_ev['best_p_error'], df_ev['best_p_step'], df_ev['best_q_step'], df_ev['best_span'], df_ev['latest_p'], df_ev['latest_p_error'], df_ev['latest_p_step'], df_ev['latest_q_step'], df_ev['latest_span'], df_ev['candidates']):

                # 対象外のものはスキップ　［将棋の引分け率］
                if specified_failure_rate != failure_rate:
                    continue

                # 対象外のものはスキップ　［試行シリーズ数］
                if specified_trials_series != trials_series:
                    continue

                if best_p_step == IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO:
                    print(f"[P={even_table.p} failure_rate={even_table.failure_rate}] ベスト値が設定されていません。スキップします")
                    continue

                even_table = EvenTable(
                        p=p,
                        failure_rate=failure_rate,
                        trials_series=trials_series,
                        best_p=best_p,
                        best_p_error=best_p_error,
                        best_p_step=best_p_step,
                        best_q_step=best_q_step,
                        best_span=best_span,
                        latest_p=latest_p,
                        latest_p_error=latest_p_error,
                        latest_p_step=latest_p_step,
                        latest_q_step=latest_q_step,
                        latest_span=latest_span,
                        candidates=candidates)

                # 仕様
                spec = Specification(
                        p=p,
                        failure_rate=failure_rate,
                        turn_system=specified_turn_system)

                show_series_rule(
                        spec=spec,
                        specified_trials_series=specified_trials_series,
                        p_step=even_table.best_p_step,
                        q_step=even_table.best_q_step,
                        span=even_table.best_span,
                        presentable='',
                        comment='')


        elif data_source == 2:
            title='セレクション［シリーズ・ルール］'

            df_ssr = get_df_selection_series_rule(turn_system=specified_turn_system)

            for             p,           failure_rate,           p_step,           q_step,           span,           presentable,           comment,           candidates in\
                zip(df_ssr['p'], df_ssr['failure_rate'], df_ssr['p_step'], df_ssr['q_step'], df_ssr['span'], df_ssr['presentable'], df_ssr['comment'], df_ssr['candidates']):

                # 対象外のものはスキップ
                if specified_failure_rate != failure_rate:
                    continue

                # FIXME セレクションは没機能？
                # # 対象外のものはスキップ　［試行シリーズ数］
                # if specified_trials_series != trials_series:
                #     continue

                if p_step < 1:
                    print(f"データベースの値がおかしいのでスキップ  {p=}  {failure_rate=}  {p_step=}")
                    continue


                ssr_table = SelectionSeriesRuleTable(
                        p=p,
                        failure_rate=failure_rate,
                        p_step=p_step,
                        q_step=q_step,
                        span=span,
                        presentable=presentable,
                        comment=comment,
                        candidates=candidates)

                # 仕様
                spec = Specification(
                        p=ssr_table.p,
                        failure_rate=ssr_table.failure_rate,
                        turn_system=specified_turn_system)

                show_series_rule(
                        spec=spec,
                        specified_trials_series=specified_trials_series,
                        p_step=ssr_table.p_step,
                        q_step=ssr_table.q_step,
                        span=ssr_table.span,
                        presentable=ssr_table.presentable,
                        comment=ssr_table.comment)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
