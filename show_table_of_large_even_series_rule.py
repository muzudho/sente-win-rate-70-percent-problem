#
# 表示
# python show_table_of_large_even_series_rule.py
#
#   テーブル形式でただ表示するだけ
#

import traceback
import re

from library import HEAD, TAIL, ALICE, BOB, SUCCESSFUL, FAILED, FACE_OF_COIN, PLAYERS, WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN, BRUTE_FORCE, THEORETICAL, IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO, turn_system_to_str, round_letro, Specification, SeriesRule, judge_series, LargeSeriesTrialSummary, SequenceOfFaceOfCoin, ArgumentOfSequenceOfPlayout, make_generation_algorythm
from library.file_paths import get_show_table_of_large_even_series_rule_csv_file_path
from library.database import get_df_selection_series_rule, get_df_even, EvenTable, SelectionSeriesRuleTable
from library.views import stringify_simulation_log


def stringify_header():
    """\
    +---------------------------+------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Spec                      | Series rule                                          | Large Series Trial Summary                                                                                                                                                    |
    +-------------+-------------+----------+----------+--------+-----------+-----------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | p           | Failure     | p_step   | q_step   | span   | shortest  | longest   | Total ab (of players)             ____________________________________________________________________________________________________________________________________________|
    |             |             |          |          |        |           |           |           ________________________| Successful series ____________________________________________| Failed series ____________________________________________________________|
    |             |             |          |          |        |           |           |           | wins a    | wins b    |           |            |            |            |            |           |            |            |            |            | no wins ab|
    |             |             |          |          |        |           |           |           |           |           |           |s_ful_wins a|s_ful_wins b|s_pts_wins a|s_pts_wins b|           |f_ful_wins a|f_ful_wins b|f_pts_wins a|f_pts_wins b|           |
    +-------------+-------------+----------+----------+--------+-----------+-----------+-----------+-----------+-----------+-----------+------------+------------+------------+------------+-----------+------------+------------+------------+------------+-----------+
    """

    # CSV
    text = f"""\
p=,p,％ f=,failure_rate,％ 表=,p_step,裏=,q_step,目=,span,最短=,shortest,局 最長=,longest,局 計=,total_ab,シリ Ａ勝=,wins_a,シリ Ｂ勝=,wins_b,シリ 成功=,succ,シリ 成Ａ満点=,s_ful_wins_a,シリ 成Ｂ満点=,s_ful_wins_b,シリ 成Ａ点差勝=,s_pts_wins_a,シリ 成Ｂ点差勝=,s_pts_wins_b,シリ 失敗=,fail,シリ 失Ａ満点=,f_ful_wins_a,シリ 失Ｂ満点=,f_ful_wins_b,シリ  失Ａ点差勝=,f_pts_wins_a,シリ 失Ｂ点差勝=,f_pts_wins_b,シリ 無勝負=,no_wins_ab,シリ\
"""

    return text


def stringify_csv_of_body(p, spec, series_rule, presentable, comment, large_series_trial_summary):
    """データ部を文字列化

    Parameters
    ----------

    """

#+-------------+-------------+----------+----------+--------+-----------+-----------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
#| t1          | t2          | t3       | t4       | t5     | t6a       | t6b       | t17                               ____________________________________________________________________________________________________________________________________|
#|             |             |          |          |        |           |           |           ________________________| t8        ________________________________________________| t9        ____________________________________________________________|
#|             |             |          |          |        |           |           |           | t18       | t19       |           |           |           |           |           |           |           |           |           |           | t24       |
#|             |             |          |          |        |           |           |           |           |           |           | t20       | t21       | t20b      | t21b      |           | t22a      | t23b      | t22       | t23       |           |
#+-------------+-------------+----------+----------+--------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+

    # 変数名を縮める（Summary）
    S = large_series_trial_summary


    t1 = f"{p*100:.4f}"                                         # p
    t2 = f"{spec.failure_rate*100:.4f}"                         # failure_rate
    t3 = f"{series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)}"   # p_step
    t4 = f"{series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)}"   # q_step
    t5 = f"{series_rule.step_table.span}"                       # span
    t6a = f"{series_rule.shortest_coins}" # shortest
    t6b = f"{series_rule.longest_coins}" # longest
    t8 = f"{S.successful_series}"   # Successful series
    t9 = f"{S.failed_series}"       # Failed series

    t17 = f"{S.total}"                   # Total (of players)

    t18 = f"{S.wins(challenged=SUCCESSFUL, winner=ALICE)}"                             # s_wins a
    t19 = f"{S.wins(challenged=SUCCESSFUL, winner=BOB)}"                               # s_wins b
    t18b = f"{S.wins(challenged=FAILED, winner=ALICE)}"                             # f_wins a
    t19b = f"{S.wins(challenged=FAILED, winner=BOB)}"                               # f_wins b

    t20 = f"{S.ful_wins(challenged=SUCCESSFUL, winner=ALICE)}"                         # s_ful_wins a
    t21 = f"{S.ful_wins(challenged=SUCCESSFUL, winner=BOB)}"                           # s_ful_wins b
    t20b = f"{S.pts_wins(challenged=SUCCESSFUL, winner=ALICE)}"                         # FIXME pts_wins a
    t21b = f"{S.pts_wins(challenged=SUCCESSFUL, winner=BOB)}"                           # FIXME pts_wins b

    t22b = f"{S.ful_wins(challenged=FAILED, winner=ALICE)}"
    t23b = f"{S.ful_wins(challenged=FAILED, winner=BOB)}"
    t22 = f"{S.pts_wins(challenged=FAILED, winner=ALICE)}"                         # FIXME pts_wins a
    t23 = f"{S.pts_wins(challenged=FAILED, winner=BOB)}"                           # FIXME pts_wins b

    t24 = f"{S.no_wins}"                 # no wins ab




#-------------+-------------+----------+----------+--------+-----------+-----------+-----------------------------------------------------------------------------------------------------------------------------------------------+
# t1          | t2          | t3       | t4       | t5     | t6a       | t6b       | t17                               ____________________________________________________________________________________________________________|
#             |             |          |          |        |           |           |           ________________________| t8        ________________________________________________| t9        ____________________________________|
#             |             |          |          |        |           |           |           | t18       | t19       |           |           |           |           |           |           |           |           | t24       |
#             |             |          |          |        |           |           |           |           |           |           | t20       | t21       | t20b      | t21b      |           | t22       | t23       |           |
#-------------+-------------+----------+----------+--------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+

    # CSV
    text = f"""\
p=,{ t1},％ f=,{ t2},％ 表=,{ t3},裏=,{ t4},目=,{ t5},最短=,{t6a},局 最長=,{t6b},局 計=,{t17},シリ Ａ勝=,{t18},シリ Ｂ勝=,{t19},シリ 成功=,{ t8},シリ Ａ満点=,{t20},シリ Ｂ満点=,{t21},シリ Ａ点差勝=,{t20b},シリ Ｂ点差勝=,{t21b},シリ 失敗=,{ t9},シリ Ａ点差勝=,{t22},シリ Ｂ点差勝=,{t23},シリ 無勝負=,{t24},シリ\
"""


    # 空白だけのセルは詰める
    text = re.sub(r",\s+,", ",,", text)

    return text


def show_series_rule(p, failure_rate, specified_number_of_series, p_step, q_step, span, presentable, comment, turn_system):
    """［シリーズ・ルール］を表示します"""
    # 仕様
    spec = Specification(
            p=p,
            failure_rate=failure_rate,
            turn_system=turn_system)

    # ［シリーズ・ルール］。任意に指定します
    series_rule = SeriesRule.make_series_rule_base(
            failure_rate=spec.failure_rate,
            p_step=p_step,
            q_step=q_step,
            span=span,
            turn_system=turn_system)


    list_of_trial_results_for_one_series = []

    for round in range(0, specified_number_of_series):

        # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
        list_of_face_of_coin = SequenceOfFaceOfCoin.make_sequence_of_playout(
                spec=spec,
                longest_coins=series_rule.longest_coins)

        # FIXME 検証
        if len(list_of_face_of_coin) < series_rule.shortest_coins:
            text = f"{spec.p=} 指定の対局シートの長さ {len(list_of_face_of_coin)} は、最短対局数の理論値 {series_rule.shortest_coins} を下回っています。このような対局シートを指定してはいけません"
            print(f"""{text}
{list_of_face_of_coin=}
{series_rule.longest_coins=}
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
            p=p,
            spec=spec,
            series_rule=series_rule,
            presentable=presentable,
            comment=comment,
            large_series_trial_summary=large_series_trial_summary)


    print(csv) # 表示

    # ログ出力
    with open(get_show_table_of_large_even_series_rule_csv_file_path(
            failure_rate=spec.failure_rate,
            turn_system=turn_system), 'a', encoding='utf8') as f:
        f.write(f"{csv}\n")    # ファイルへ出力


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        prompt = f"""\
(1) Frozen turn
(2) Alternating turn
Which one(1-2)? """
        choice = input(prompt)

        if choice == '1':
            specified_turn_system = WHEN_FROZEN_TURN

        elif choice == '2':
            specified_turn_system = WHEN_ALTERNATING_TURN

        else:
            raise ValueError(f"{choice=}")


        prompt = f"""\
What is the failure rate?
Example: 10% is 0.1
? """
        specified_failure_rate = float(input(prompt))


        prompt = f"""\
(1) even series rule
(2) selection series rule
Which data source should I use?
> """
        data_source = int(input(prompt))


        # ［試行シリーズ回数］を尋ねる
        prompt = f"""\
How many times do you want to try the series?
Example: 2000000
? """
        specified_number_of_series = int(input(prompt))


        header_csv = stringify_header()

        print(header_csv) # 表示

        # ログ出力
        csv_file_path = get_show_table_of_large_even_series_rule_csv_file_path(
                failure_rate=specified_failure_rate,
                turn_system=specified_turn_system)
        with open(csv_file_path, 'a', encoding='utf8') as f:
            f.write(f"{header_csv}\n")    # ファイルへ出力


        # TODO
        if data_source == 1:
            title='イーブン［シリーズ・ルール］'

            generation_algorythm = make_generation_algorythm(failure_rate=specified_failure_rate, turn_system=specified_turn_system)
            if generation_algorythm == BRUTE_FORCE:
                print("力任せ探索で行われたデータです")
            elif generation_algorythm == THEORETICAL:
                print("理論値で求められたデータです")
            else:
                raise ValueError(f"{generation_algorythm=}")

            df_ev = get_df_even(turn_system=specified_turn_system, generation_algorythm=generation_algorythm)

            for            p,          failure_rate,          best_p,          best_p_error,          best_number_of_series,          best_p_step,          best_q_step,          best_span,          latest_p,          latest_p_error,          latest_number_of_series,          latest_p_step,          latest_q_step,          latest_span,          candidates in\
                zip(df_ev['p'], df_ev['failure_rate'], df_ev['best_p'], df_ev['best_p_error'], df_ev['best_number_of_series'], df_ev['best_p_step'], df_ev['best_q_step'], df_ev['best_span'], df_ev['latest_p'], df_ev['latest_p_error'], df_ev['latest_number_of_series'], df_ev['latest_p_step'], df_ev['latest_q_step'], df_ev['latest_span'], df_ev['candidates']):

                # 対象外のものはスキップ
                if specified_failure_rate != failure_rate:
                    continue

                if best_p_step == IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO:
                    print(f"[P={even_table.p} failure_rate={even_table.failure_rate}] ベスト値が設定されていません。スキップします")
                    continue

                even_table = EvenTable(
                        p=p,
                        failure_rate=failure_rate,
                        best_p=best_p,
                        best_p_error=best_p_error,
                        best_number_of_series=best_number_of_series,
                        best_p_step=best_p_step,
                        best_q_step=best_q_step,
                        best_span=best_span,
                        latest_p=latest_p,
                        latest_p_error=latest_p_error,
                        latest_number_of_series=latest_number_of_series,
                        latest_p_step=latest_p_step,
                        latest_q_step=latest_q_step,
                        latest_span=latest_span,
                        candidates=candidates)

                show_series_rule(
                        p=p,
                        failure_rate=failure_rate,
                        specified_number_of_series=specified_number_of_series,
                        p_step=even_table.best_p_step,
                        q_step=even_table.best_q_step,
                        span=even_table.best_span,
                        presentable='',
                        comment='',
                        turn_system=specified_turn_system)


        elif data_source == 2:
            title='セレクション［シリーズ・ルール］'

            df_ssr = get_df_selection_series_rule(turn_system=specified_turn_system)

            for             p,           failure_rate,           p_step,           q_step,           span,           presentable,           comment,           candidates in\
                zip(df_ssr['p'], df_ssr['failure_rate'], df_ssr['p_step'], df_ssr['q_step'], df_ssr['span'], df_ssr['presentable'], df_ssr['comment'], df_ssr['candidates']):

                # 対象外のものはスキップ
                if specified_failure_rate != failure_rate:
                    continue

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


                show_series_rule(
                        p=ssr_table.p,
                        failure_rate=ssr_table.failure_rate,
                        specified_number_of_series=specified_number_of_series,
                        p_step=ssr_table.p_step,
                        q_step=ssr_table.q_step,
                        span=ssr_table.span,
                        presentable=ssr_table.presentable,
                        comment=ssr_table.comment,
                        turn_system=specified_turn_system)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
