#
# シミュレーション
# python simulation_large_series.py
#
#   ［コインの表が出る確率］ p=0.50 ～ 0.99 までのデータを一覧する
#

import traceback

from library import WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN, BRUTE_FORCE, THEORETICAL, IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO, round_letro, Specification, SeriesRule, judge_series, LargeSeriesTrialSummary, ElementaryEventSequence, SequenceOfFaceOfCoin, ArgumentOfSequenceOfPlayout, make_generation_algorythm
from library.file_paths import get_simulation_large_series_log_file_path
from library.database import get_df_selection_series_rule, get_df_even
from library.views import stringify_simulation_log


def simulate_series_rule(p, failure_rate, number_of_series, p_step, q_step, span, presentable, comment, turn_system):
    """［シリーズ・ルール］をシミュレーションします"""
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

    series_result_list = []

    for round in range(0, number_of_series):

        # 引数作成
        argument_of_sequence_of_playout = ArgumentOfSequenceOfPlayout(
                p=p,
                failure_rate=spec.failure_rate,
                number_of_longest_time=series_rule.number_of_longest_time)

        # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
        list_of_face_of_coin = SequenceOfFaceOfCoin.make_sequence_of_playout(
                argument_of_sequence_of_playout=argument_of_sequence_of_playout)

        # ［シリーズ］１つ分の試行結果を返す
        trial_results_for_one_series = judge_series(
                argument_of_sequence_of_playout=argument_of_sequence_of_playout,
                list_of_face_of_coin=list_of_face_of_coin,
                series_rule=series_rule)
        #print(f"{trial_results_for_one_series.stringify_dump()}")

        
        if trial_results_for_one_series.number_of_times < series_rule.number_of_shortest_time:
            text = f"{spec.p=} 最短対局数の実際値 {trial_results_for_one_series.number_of_times} が理論値 {series_rule.number_of_shortest_time} を下回った"
            print(f"""{text}
{series_rule.number_of_longest_time=}
{trial_results_for_one_series.stringify_dump('   ')}
""")
            raise ValueError(text)

        if series_rule.number_of_longest_time < trial_results_for_one_series.number_of_times:
            text = f"{spec.p=} 最長対局数の実際値 {trial_results_for_one_series.number_of_times} が理論値 {series_rule.number_of_longest_time} を上回った"
            print(f"""{text}
{series_rule.number_of_shortest_time=}
{trial_results_for_one_series.stringify_dump('   ')}
""")
            raise ValueError(text)


        series_result_list.append(trial_results_for_one_series)


    # シミュレーションの結果
    large_series_trial_summary = LargeSeriesTrialSummary(
            series_result_list=series_result_list)


    text = stringify_simulation_log(
            # ［表が出る確率］（指定値）
            p=spec.p,
            # ［表も裏も出ない率］
            failure_rate=spec.failure_rate,
            # ［先後運用制度］
            turn_system=turn_system,
            # ［かくきんシステムのｐの構成］
            series_rule=series_rule,
            # シミュレーションの結果
            large_series_trial_summary=large_series_trial_summary,
            # タイトル
            title=title)


    print(text) # 表示


    # ログ出力
    with open(get_simulation_large_series_log_file_path(
            failure_rate=spec.failure_rate,
            turn_system=turn_system), 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


    # 表示とログ出力を終えた後でテスト
    if large_series_trial_summary.shortest_time_th < series_rule.number_of_shortest_time:
        raise ValueError(f"{spec.p=} 最短対局数の実際値 {large_series_trial_summary.shortest_time_th} が理論値 {series_rule.number_of_shortest_time} を下回った")

    if series_rule.number_of_longest_time < large_series_trial_summary.longest_time_th:
        raise ValueError(f"{spec.p=} 最長対局数の実際値 {large_series_trial_summary.longest_time_th} が理論値 {series_rule.number_of_longest_time} を上回った")


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        print(f"""\
(1) Frozen turn
(2) Alternating turn
Which one(1-2)? """)

        choice = input()

        if choice == '1':
            specified_turn_system = WHEN_FROZEN_TURN

        elif choice == '2':
            specified_turn_system = WHEN_ALTERNATING_TURN

        else:
            raise ValueError(f"{choice=}")


        print(f"""\
What is the failure rate?
Example: 10% is 0.1
? """)
        specified_failure_rate = float(input())


        # 試行回数を尋ねる
        print(f"""\
How many times do you want to try the series?
Example: 2000000
? """)
        number_of_series = int(input())


        data_source = int(input(f"""\
(1) even series rule
(2) selection series rule
Which data source should I use?
> """))


        # TODO
        if data_source == 1:
            title='イーブン［シリーズ・ルール］'

            generation_algorythm = make_generation_algorythm(failure_rate=specified_failure_rate, turn_system=specified_turn_system)
            if generation_algorythm == BRUTE_FORCE:
                print("力任せ探索を行います")
            elif generation_algorythm == THEORETICAL:
                print("理論値を求めます")
            else:
                raise ValueError(f"{generation_algorythm=}")

            df_ev = get_df_even(turn_system=specified_turn_system, generation_algorythm=generation_algorythm)

            for            p,          failure_rate,          best_p,          best_p_error,          best_number_of_series,          best_p_step,          best_q_step,          best_span,          latest_p,          latest_p_error,          latest_number_of_series,          latest_p_step,          latest_q_step,          latest_span,          candidates in\
                zip(df_ev['p'], df_ev['failure_rate'], df_ev['best_p'], df_ev['best_p_error'], df_ev['best_number_of_series'], df_ev['best_p_step'], df_ev['best_q_step'], df_ev['best_span'], df_ev['latest_p'], df_ev['latest_p_error'], df_ev['latest_number_of_series'], df_ev['latest_p_step'], df_ev['latest_q_step'], df_ev['latest_span'], df_ev['candidates']):

                # 対象外のものはスキップ
                if specified_failure_rate != failure_rate:
                    continue

                if best_p_step == IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO:
                    print(f"[P={p} failure_rate={failure_rate}] ベスト値が設定されていません。スキップします")
                    continue

                # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
                p_step = round_letro(best_p_step)
                q_step = round_letro(best_q_step)
                span = round_letro(best_span)

                simulate_series_rule(p, failure_rate, p_step, q_step, span, '', '', turn_system=specified_turn_system)


        elif data_source == 2:
            title='セレクション［シリーズ・ルール］'

            df_ssr = get_df_selection_series_rule(turn_system=specified_turn_system)

            for             p,           failure_rate,           p_step,           q_step,           span,           presentable,           comment,           candidates in\
                zip(df_ssr['p'], df_ssr['failure_rate'], df_ssr['p_step'], df_ssr['q_step'], df_ssr['span'], df_ssr['presentable'], df_ssr['comment'], df_ssr['candidates']):

                # 対象外のものはスキップ
                if specified_failure_rate != failure_rate:
                    continue

                # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
                p_step = round_letro(p_step)
                q_step = round_letro(q_step)
                span = round_letro(span)

                if p_step < 1:
                    print(f"データベースの値がおかしいのでスキップ  {p=}  {failure_rate=}  {p_step=}")
                    continue


                simulate_series_rule(p, failure_rate, number_of_series, p_step, q_step, span, presentable, comment, turn_system=specified_turn_system)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
