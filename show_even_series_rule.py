#
# 表示
# python show_even_series_rule.py
#
#   テーブルをただ表示するだけ
#

import traceback

from library import HEAD, TAIL, SUCCESSFUL, FAILED, WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN, BRUTE_FORCE, THEORETICAL, IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO, turn_system_to_str, round_letro, Specification, SeriesRule, judge_series, LargeSeriesTrialSummary, ElementaryEventSequence, SequenceOfFaceOfCoin, ArgumentOfSequenceOfPlayout, make_generation_algorythm
from library.file_paths import get_simulation_large_series_log_file_path
from library.database import get_df_selection_series_rule, get_df_even
from library.views import stringify_simulation_log


def stringify_header(turn_system):
    return f"""\
turn system={turn_system_to_str(turn_system)}

p           Failure     p_step   q_step   span   longest   n_times   f_times
----------- ----------- -------- -------- ------ --------- --------- ---------
"""


def stringify_body(p, spec, series_rule, presentable, comment, argument_of_sequence_of_playout, series_result):
    """データ部を文字列化

    Parameters
    ----------

    """
    t1 = f"{p * 100:>7.4f}"
    t2 = f"{spec.failure_rate * 100:>7.4f}"
    t3 = f"{series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD):>6}"
    t4 = f"{series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL):>6}"
    t5 = f"{series_rule.step_table.span:>4}"
    t6 = f"{argument_of_sequence_of_playout.number_of_longest_time:>7}"
    t7 = f"{series_result.number_of_times:>7}"  # ［行われた対局数］
    t8 = f"{series_result.number_of_failed:>7}"  # ［表も裏も出なかった対局数］

# P         Failure     p_step   q_step   span   longest   n_times   f_times
# --------- ----------- -------- -------- ------ --------- --------- ---------

    return f"""\
p={t1   }％ f={t2   }％ {t3  }表 {t4  }裏 {t5}目 {t6   }局 {t7   }回 {t8   }回
"""


def show_series_rule(p, failure_rate, p_step, q_step, span, presentable, comment, turn_system):
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


    # 引数作成
    argument_of_sequence_of_playout = ArgumentOfSequenceOfPlayout(
            p=p,
            failure_rate=spec.failure_rate,
            number_of_longest_time=series_rule.number_of_longest_time)

    # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
    list_of_face_of_coin = SequenceOfFaceOfCoin.make_sequence_of_playout(
            argument_of_sequence_of_playout=argument_of_sequence_of_playout)

    # シリーズの結果を返す
    series_result = judge_series(
            argument_of_sequence_of_playout=argument_of_sequence_of_playout,
            list_of_face_of_coin=list_of_face_of_coin,
            series_rule=series_rule)


    text = stringify_body(
            p=p,
            spec=spec,
            series_rule=series_rule,
            presentable=presentable,
            comment=comment,
            argument_of_sequence_of_playout=argument_of_sequence_of_playout,
            series_result=series_result)

    print(text) # 表示

    # ログ出力
    with open(get_simulation_large_series_log_file_path(
            failure_rate=spec.failure_rate,
            turn_system=turn_system), 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


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


        data_source = int(input(f"""\
(1) even series rule
(2) selection series rule
Which data source should I use?
> """))


        text = stringify_header(specified_turn_system)

        print(text) # 表示

        # ログ出力
        log_file_path = get_simulation_large_series_log_file_path(
                failure_rate=specified_failure_rate,
                turn_system=specified_turn_system)
        with open(log_file_path, 'a', encoding='utf8') as f:
            f.write(f"{text}\n")    # ファイルへ出力


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
                    print(f"[P={p} failure_rate={failure_rate}] ベスト値が設定されていません。スキップします")
                    continue

                # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
                p_step = round_letro(best_p_step)
                q_step = round_letro(best_q_step)
                span = round_letro(best_span)

                show_series_rule(p, failure_rate, p_step, q_step, span, '', '', turn_system=specified_turn_system)


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


                show_series_rule(p, failure_rate, p_step, q_step, span, presentable, comment, turn_system=specified_turn_system)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
