#
# 表示
# python show_log_of_one_epdt_series_rule.py
#
#   ログ表示するだけ。CSV編集してない
#

import traceback

from library import HEAD, TAIL, ALICE, BOB, SUCCESSFUL, FAILED, FROZEN_TURN, ALTERNATING_TURN, IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO, Converter, round_letro, Specification, SeriesRule, judge_series, LargeSeriesTrialSummary, SequenceOfFaceOfCoin
from library.file_paths import SimulationLargeSeriesFilePaths
from library.database import EmpiricalProbabilityDuringTrialsTable, EmpiricalProbabilityDuringTrialsRecord
from library.views import PromptCatalog


def stringify_header(turn_system_id):
    return f"""\
turn system={Converter.turn_system_id_to_readable(turn_system_id)}

+---------------------------+------------------------------------------+--------------------------------+
| Spec                      | Series rule                              | 1 Trial                        |
+-------------+-------------+----------+----------+--------+-----------+-----------+-----------+--------+
| p           | Failure     | h_step   | t_step   | span   | upr_limit | n_times   | f_times   | Won    |
+-------------+-------------+----------+----------+--------+-----------+-----------+-----------+--------+
"""


def stringify_log_body(p, spec, series_rule, presentable, comment, trial_results_for_one_series):
    """データ部を文字列化

    TODO pandas に書き直せるか？

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


def show_log_of_series_rule(spec, trial_series, h_step, t_step, span, presentable, comment):
    """［シリーズ・ルール］を表示します
    
    FIXME ログ出力してるだけ？要らない？ 試行結果をCSVに保存してない？
    """

    # ［シリーズ・ルール］。任意に指定します
    series_rule = SeriesRule.make_series_rule_base(
            spec=spec,
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


    # ログ出力
    # -------
    log_text = stringify_log_body(
            p=p,
            spec=spec,
            series_rule=series_rule,
            presentable=presentable,
            comment=comment,
            trial_results_for_one_series=trial_results_for_one_series)
    print(log_text) # 表示
    with open(SimulationLargeSeriesFilePaths.as_log(
            failure_rate=spec.failure_rate,
            turn_system_id=turn_system_id), 'a', encoding='utf8') as f:
        f.write(f"{log_text}\n")    # ファイルへ出力


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［試行シリーズ数］を尋ねます
        specified_trial_series, specified_abs_small_error = PromptCatalog.how_many_times_do_you_want_to_try_the_series()


        # ［先後の決め方］を尋ねます
        specified_turn_system_id = PromptCatalog.which_method_do_you_use_to_determine_sente_and_gote()


        # ［将棋の引分け率］を尋ねます
        specified_failure_rate = PromptCatalog.what_is_the_failure_rate()


        # ヘッダー
        text = stringify_header(specified_turn_system_id)

        print(text) # 表示

        # ログ出力
        log_file_path = SimulationLargeSeriesFilePaths.as_log(
                failure_rate=specified_failure_rate,
                turn_system_id=specified_turn_system_id)
        with open(log_file_path, 'a', encoding='utf8') as f:
            f.write(f"{text}\n")    # ファイルへ出力


        ep_table = EmpiricalProbabilityDuringTrialsTable.read_csv(
                failure_rate=specified_failure_rate,
                turn_system_id=specified_turn_system_id,
                trial_series=specified_trial_series,
                new_if_it_no_exists=True)
        df_ep = ep_table.df


        def on_each(epdt_record):

            # 対象外のものはスキップ
            if specified_failure_rate != failure_rate:
                return

            if best_h_step == IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO:
                print(f"[p={p} failure_rate={failure_rate}] ベスト値が設定されていません。スキップします")
                return

            # 仕様
            spec = Specification(
                    p=epdt_record.p,
                    failure_rate=specified_failure_rate,
                    turn_system_id=specified_turn_system_id)

            show_log_of_series_rule(
                    spec=spec,
                    trial_series=specified_trial_series,
                    h_step=epdt_record.best_h_step,
                    t_step=epdt_record.best_t_step,
                    span=epdt_record.best_span,
                    presentable='',
                    comment='')


        EmpiricalProbabilityDuringTrialsTable.for_each(on_each=on_each)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
