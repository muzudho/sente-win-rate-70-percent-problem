#
# 表示
# python create_a_csv_to_view_evenizer_in_excel.py
#
#   Excel で［かくきんシステムの表］を表示するための CSV を作成する
#
#   NOTE 書式のような仕様は頻繁に変更することがあります
#

import traceback
import datetime

from library import HEAD, TAIL, ALICE, BOB, SUCCESSFUL, FAILED, FROZEN_TURN, ALTERNATING_TURN, BRUTE_FORCE, THEORETICAL, IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO, Converter, Specification, SeriesRule, judge_series, LargeSeriesTrialSummary, SequenceOfFaceOfCoin
from library.file_paths import get_even_view_csv_file_path
from library.database import get_df_even, EvenRecord
from library.views import KakukinViewerInExcel


def simulate_series(spec, series_rule, specified_trials_series):
    """シリーズをシミュレーションします
    
    Returns
    -------
    large_series_trial_summary : LargeSeriesTrialSummary
        シミュレーション結果
    """
    list_of_trial_results_for_one_series = []

    # シミュレーション
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

    return large_series_trial_summary


def automatic(specified_failure_rate, specified_turn_system, specified_trials_series):
    header_csv = KakukinViewerInExcel.stringify_header()

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


    generation_algorythm = Converter.make_generation_algorythm(failure_rate=specified_failure_rate, turn_system=specified_turn_system)
    if generation_algorythm == BRUTE_FORCE:
        print("力任せ探索で行われたデータです")
    elif generation_algorythm == THEORETICAL:
        print("理論値で求められたデータです")
    else:
        raise ValueError(f"{generation_algorythm=}")


    df_ev = get_df_even(failure_rate=specified_failure_rate, turn_system=specified_turn_system, generation_algorythm=generation_algorythm, trials_series=specified_trials_series)

    for            p,          failure_rate,          turn_system,          trials_series,          best_p,          best_p_error,          best_h_step,          best_t_step,          best_span,          latest_p,          latest_p_error,          latest_h_step,          latest_t_step,          latest_span,          candidates in\
        zip(df_ev['p'], df_ev['failure_rate'], df_ev['turn_system'], df_ev['trials_series'], df_ev['best_p'], df_ev['best_p_error'], df_ev['best_h_step'], df_ev['best_t_step'], df_ev['best_span'], df_ev['latest_p'], df_ev['latest_p_error'], df_ev['latest_h_step'], df_ev['latest_t_step'], df_ev['latest_span'], df_ev['candidates']):

        # 対象外のものはスキップ　［将棋の引分け率］
        if specified_failure_rate != failure_rate:
            continue

        # 対象外のものはスキップ　［試行シリーズ数］
        if specified_trials_series != trials_series:
            continue

        if best_h_step == IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO:
            print(f"[{p=} {failure_rate=}] ベスト値が設定されていません。スキップします")
            continue


        # レコード作成
        even_record = EvenRecord(
                p=p,
                failure_rate=failure_rate,
                turn_system=turn_system,
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


        # ［シリーズ・ルール］
        series_rule = SeriesRule.make_series_rule_base(
                spec=spec,
                trials_series=specified_trials_series,
                h_step=even_record.best_h_step,
                t_step=even_record.best_t_step,
                span=even_record.best_span)


        # シミュレーションします
        large_series_trial_summary = simulate_series(
                spec=spec,
                series_rule=series_rule,
                specified_trials_series=specified_trials_series)


        # CSV作成
        csv = KakukinViewerInExcel.stringify_csv_of_body(
                spec=spec,
                series_rule=series_rule,
                presentable='',
                comment='',
                large_series_trial_summary=large_series_trial_summary)

        print(csv) # 表示

        # ログ出力
        csv_file_path = get_even_view_csv_file_path(spec=spec, trials_series=specified_trials_series)
        print(f"[{datetime.datetime.now()}] write view to `{csv_file_path}` file ...")
        with open(csv_file_path, 'a', encoding='utf8') as f:
            f.write(f"{csv}\n")    # ファイルへ出力




########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［将棋の先手勝率］を尋ねます
        prompt = f"""\
What is the failure rate?
Example: 10% is 0.1
? """
        specified_failure_rate = float(input(prompt))


        # ［先後の決め方］を尋ねます
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


        automatic(
                specified_failure_rate=specified_failure_rate,
                specified_turn_system=specified_turn_system,
                specified_trials_series=specified_trials_series)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
