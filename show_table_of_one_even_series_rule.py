#
# 表示
# python show_table_of_one_even_series_rule.py
#
#   テーブル形式でただ表示するだけ
#

import traceback

from library import HEAD, TAIL, ALICE, BOB, SUCCESSFUL, FAILED, FROZEN_TURN, ALTERNATING_TURN, BRUTE_FORCE, THEORETICAL, IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO, Converter, round_letro, Specification, SeriesRule, judge_series, LargeSeriesTrialSummary, SequenceOfFaceOfCoin
from library.file_paths import get_simulation_large_series_log_file_path
from library.database import EvenTable, EvenRecord


def stringify_header(turn_system):
    return f"""\
turn system={Converter.turn_system_to_readable(turn_system)}

+---------------------------+------------------------------------------+--------------------------------+
| Spec                      | Series rule                              | 1 Trial                        |
+-------------+-------------+----------+----------+--------+-----------+-----------+-----------+--------+
| p           | Failure     | h_step   | t_step   | span   | upr_limit | n_times   | f_times   | Won    |
+-------------+-------------+----------+----------+--------+-----------+-----------+-----------+--------+
"""


def stringify_body(p, spec, series_rule, presentable, comment, trial_results_for_one_series):
    """データ部を文字列化

    Parameters
    ----------

    """
    t1 = f"{p * 100:>7.4f}"
    t2 = f"{spec.failure_rate * 100:>7.4f}"
    t3 = f"{series_rule.step_table.get_step_by(face_of_coin=HEAD):>6}"
    t4 = f"{series_rule.step_table.get_step_by(face_of_coin=TAIL):>6}"
    t5 = f"{series_rule.step_table.span:>4}"
    t6 = f"{series_rule.upper_limit_coins:>7}"
    t7 = f"{trial_results_for_one_series.number_of_coins:>7}"  # ［行われた対局数］
    t8 = f"{trial_results_for_one_series.failed_coins:>7}"  # ［表も裏も出なかった対局数］

    if trial_results_for_one_series.is_won(winner=ALICE):
        t9 = f"Ａさん"  # ［先後交互制のシリーズでＡさんが勝ったか？］
    elif trial_results_for_one_series.is_won(winner=BOB):
        t9 = f"Ｂさん"  # ［先後交互制のシリーズでＢさんが勝ったか？］
    else:
        t9 = f"引分  "  # ［先後交互制のシリーズで引分けだったか？］


# --------------------------+------------------------------------------+--------------------------------+
# Spec                      | Series rule                              | 1 Trial                        |
# ------------+-------------+----------+----------+--------+-----------+-----------+-----------+--------+
# p           | Failure     | h_step   | t_step   | span   | upr_limit | n_times   | f_times   | Won    |
# ------------+-------------+----------+----------+--------+-----------+-----------+-----------+--------+

    return f"""\
  p={t1   }％   f={t2   }％   {t3  }表   {t4  }裏   {t5}目   {t6   }局   {t7   }回   {t8   }回   {t9  }\
"""


def show_series_rule(spec, trials_series, h_step, t_step, span, presentable, comment):
    """［シリーズ・ルール］を表示します"""

    # ［シリーズ・ルール］。任意に指定します
    series_rule = SeriesRule.make_series_rule_base(
            spec=spec,
            trials_series=trials_series,
            h_step=h_step,
            t_step=t_step,
            span=span)

    # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
    path_of_face_of_coin = SequenceOfFaceOfCoin.make_sequence_of_playout(
            spec=spec,
            upper_limit_coins=series_rule.upper_limit_coins)

    # FIXME 検証
    if len(path_of_face_of_coin) < series_rule.shortest_coins:
        text = f"{spec.p=} 指定の対局シートの長さ {len(path_of_face_of_coin)} は、最短対局数の理論値 {series_rule.shortest_coins} を下回っています。このような対局シートを指定してはいけません"
        print(f"""{text}
{path_of_face_of_coin=}
{series_rule.upper_limit_coins=}
""")
        raise ValueError(text)


    # ［シリーズ］１つ分の試行結果を返す
    trial_results_for_one_series = judge_series(
            spec=spec,
            series_rule=series_rule,
            path_of_face_of_coin=path_of_face_of_coin)


    text = stringify_body(
            p=p,
            spec=spec,
            series_rule=series_rule,
            presentable=presentable,
            comment=comment,
            trial_results_for_one_series=trial_results_for_one_series)

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
        # ［将棋の引分け率］を尋ねる
        prompt = f"""\
What is the failure rate?
Example: 10% is 0.1
? """
        specified_failure_rate = float(input(prompt))


        # ［先後の決め方］を尋ねる
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


        text = stringify_header(specified_turn_system)

        print(text) # 表示

        # ログ出力
        log_file_path = get_simulation_large_series_log_file_path(
                failure_rate=specified_failure_rate,
                turn_system=specified_turn_system)
        with open(log_file_path, 'a', encoding='utf8') as f:
            f.write(f"{text}\n")    # ファイルへ出力


        generation_algorythm = Converter.make_generation_algorythm(failure_rate=specified_failure_rate, turn_system=specified_turn_system)
        if generation_algorythm == BRUTE_FORCE:
            print("力任せ探索で行われたデータです")
        elif generation_algorythm == THEORETICAL:
            print("理論値で求められたデータです")
        else:
            raise ValueError(f"{generation_algorythm=}")

        df_ev = EvenTable.read_df(failure_rate=specified_failure_rate, turn_system=specified_turn_system, generation_algorythm=generation_algorythm)

        for            p,          failure_rate,          turn_system,          trials_series,          best_p,          best_p_error,          best_h_step,          best_t_step,          best_span,          latest_p,          latest_p_error,          latest_h_step,          latest_t_step,          latest_span,          candidates in\
            zip(df_ev['p'], df_ev['failure_rate'], df_ev['turn_system'], df_ev['trials_series'], df_ev['best_p'], df_ev['best_p_error'], df_ev['best_h_step'], df_ev['best_t_step'], df_ev['best_span'], df_ev['latest_p'], df_ev['latest_p_error'], df_ev['latest_h_step'], df_ev['latest_t_step'], df_ev['latest_span'], df_ev['candidates']):

            # 対象外のものはスキップ
            if specified_failure_rate != failure_rate:
                continue

            if best_h_step == IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO:
                print(f"[p={p} failure_rate={failure_rate}] ベスト値が設定されていません。スキップします")
                continue

            even_record = EvenRecord(
                    p=p,
                    failure_rate=failure_rate,
                    turn_system_str=turn_system,
                    trials_series=trials_series,
                    best_p=best_p,
                    best_p_error=best_p_error,
                    best_h_step=best_h_step,
                    best_t_step=best_t_step,
                    best_span=best_span,
                    latest_p=latest_p,
                    latest_p_error=latest_p_error,
                    latest_h_step=latest_h_step,
                    latest_t_step=latest_t_step,
                    latest_span=latest_span,
                    candidates=candidates)

            # 仕様
            spec = Specification(
                    p=p,
                    failure_rate=failure_rate,
                    turn_system=specified_turn_system)

            show_series_rule(
                    spec=spec,
                    trials_series=trials_series,
                    h_step=even_record.best_h_step,
                    t_step=even_record.best_t_step,
                    span=even_record.best_span,
                    presentable='',
                    comment='')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
