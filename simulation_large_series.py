#
# シミュレーション
# python simulation_large_series.py
#
#   ［コインの表が出る確率］ p=0.50 ～ 0.99 までのデータを一覧する
#

import traceback

from library import FROZEN_TURN, ALTERNATING_TURN, BRUTE_FORCE, THEORETICAL, IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO, Converter, round_letro, Specification, SeriesRule, judge_series, LargeSeriesTrialSummary, SequenceOfFaceOfCoin
from library.file_paths import get_simulation_large_series_log_file_path
from library.database import get_df_selection_series_rule, get_df_even
from library.views import stringify_simulation_log


def simulate_series_rule(spec, number_of_series, p_step, q_step, span, presentable, comment):
    """［シリーズ・ルール］をシミュレーションします"""

    # ［シリーズ・ルール］。任意に指定します
    series_rule = SeriesRule.make_series_rule_base(
            spec=spec,
            p_step=p_step,
            q_step=q_step,
            span=span)


    if not series_rule.is_enabled:
        print("この［シリーズ・ルール］は有効な内容ではないので、スキップします")
        return


    list_of_trial_results_for_one_series = []

    for round in range(0, number_of_series):

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
        #print(f"{trial_results_for_one_series.stringify_dump()}")

        
        if trial_results_for_one_series.number_of_coins < series_rule.shortest_coins:
            text = f"{spec.p=} 最短対局数の実際値 {trial_results_for_one_series.number_of_coins} が理論値 {series_rule.shortest_coins} を下回った"
            print(f"""{text}
{list_of_face_of_coin=}
{series_rule.upper_limit_coins=}
{trial_results_for_one_series.stringify_dump('   ')}
""")
            raise ValueError(text)

        if series_rule.upper_limit_coins < trial_results_for_one_series.number_of_coins:
            text = f"{spec.p=} 上限対局数の実際値 {trial_results_for_one_series.number_of_coins} が理論値 {series_rule.upper_limit_coins} を上回った"
            print(f"""{text}
{list_of_face_of_coin=}
{series_rule.shortest_coins=}
{trial_results_for_one_series.stringify_dump('   ')}
""")
            raise ValueError(text)


        list_of_trial_results_for_one_series.append(trial_results_for_one_series)


    # ［大量のシリーズを試行した結果］
    large_series_trial_summary = LargeSeriesTrialSummary(
            list_of_trial_results_for_one_series=list_of_trial_results_for_one_series)


    text = stringify_simulation_log(
            spec=spec,
            # ［かくきんシステムのｐの構成］
            series_rule=series_rule,
            # シミュレーションの結果
            large_series_trial_summary=large_series_trial_summary,
            # タイトル
            title=title)


    print(text) # 表示


    # ログ出力
    log_file_path = get_simulation_large_series_log_file_path(
            failure_rate=spec.failure_rate,
            turn_system=spec.turn_system)
    with open(log_file_path, 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


    # 表示とログ出力を終えた後でテスト
    if large_series_trial_summary.trial_shortest_coins < series_rule.shortest_coins:
        raise ValueError(f"{spec.p=} 最短対局数の実際値 {large_series_trial_summary.trial_shortest_coins} が理論値 {series_rule.shortest_coins} を下回った")

    if series_rule.upper_limit_coins < large_series_trial_summary.trial_upper_limit_coins:
        raise ValueError(f"{spec.p=} 上限対局数の実際値 {large_series_trial_summary.trial_upper_limit_coins} が理論値 {series_rule.upper_limit_coins} を上回った")


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
            specified_turn_system = FROZEN_TURN

        elif choice == '2':
            specified_turn_system = ALTERNATING_TURN

        else:
            raise ValueError(f"{choice=}")


        prompt = f"""\
What is the failure rate?
Example: 10% is 0.1
? """
        specified_failure_rate = float(input(prompt))


        # 試行回数を尋ねる
        prompt = f"""\
How many times do you want to try the series?
Example: 2000000
? """
        specified_number_of_series = int(input(prompt))


        prompt = f"""\
(1) even series rule
(2) selection series rule
Which data source should I use?
> """
        data_source = int(input(prompt))


        # TODO
        if data_source == 1:
            title='イーブン［シリーズ・ルール］'

            generation_algorythm = Converter.make_generation_algorythm(failure_rate=specified_failure_rate, turn_system=specified_turn_system)
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

                # 仕様
                spec = Specification(
                        p=p,
                        failure_rate=failure_rate,
                        turn_system=specified_turn_system)

                simulate_series_rule(
                        spec=spec,
                        number_of_series=specified_number_of_series,
                        p_step=p_step,
                        q_step=q_step,
                        span=span,
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

                # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
                p_step = round_letro(p_step)
                q_step = round_letro(q_step)
                span = round_letro(span)

                if p_step < 1:
                    print(f"データベースの値がおかしいのでスキップ  {p=}  {failure_rate=}  {p_step=}")
                    continue

                # 仕様
                spec = Specification(
                        p=p,
                        failure_rate=failure_rate,
                        turn_system=specified_turn_system)

                simulate_series_rule(
                        spec=spec,
                        number_of_series=specified_number_of_series,
                        p_step=p_step,
                        q_step=q_step,
                        span=span,
                        presentable=presentable,
                        comment=comment)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
