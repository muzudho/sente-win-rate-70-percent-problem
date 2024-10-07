#
# シミュレーション
# python simulation_large_series.py
#
#   ［コインの表が出る確率］ p=0.50 ～ 0.99 までのデータを一覧する
#

import traceback

from library import FROZEN_TURN, ALTERNATING_TURN, IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO, Converter, round_letro, Specification, SeriesRule, judge_series, LargeSeriesTrialSummary, SequenceOfFaceOfCoin, simulate_series
from library.file_paths import SimulationLargeSeriesFilePaths
from library.database import EmpiricalProbabilityDuringTrialsTable
from library.views import stringify_simulation_log, PromptCatalog


def simulate_series_rule(spec, trials_series, h_step, t_step, span, presentable, comment):
    """［シリーズ・ルール］をシミュレーションします"""

    # ［シリーズ・ルール］。任意に指定します
    series_rule = SeriesRule.make_series_rule_base(
            spec=spec,
            trials_series=trials_series,
            h_step=h_step,
            t_step=t_step,
            span=span)


    if not series_rule.is_enabled:
        print("この［シリーズ・ルール］は有効な内容ではないので、スキップします")
        return


    # シミュレーションします
    large_series_trial_summary = simulate_series(
            spec=spec,
            series_rule=series_rule,
            specified_trials_series=trials_series)


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
    log_file_path = SimulationLargeSeriesFilePaths.as_log(
            failure_rate=spec.failure_rate,
            turn_system_id=spec.turn_system_id)
    with open(log_file_path, 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


    # 表示とログ出力を終えた後でテスト
    if large_series_trial_summary.series_shortest_coins < series_rule.shortest_coins:
        raise ValueError(f"{spec.p=} シリーズ最短対局数の実際値 {large_series_trial_summary.series_shortest_coins} が理論値 {series_rule.shortest_coins} を下回った")

    if series_rule.upper_limit_coins < large_series_trial_summary.series_longest_coins:
        raise ValueError(f"{spec.p=} シリーズ最長対局数の実際値 {large_series_trial_summary.series_longest_coins} が理論値 {series_rule.upper_limit_coins} を上回った")


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［試行シリーズ数］を尋ねます
        specified_trials_series, specified_abs_small_error = PromptCatalog.how_many_times_do_you_want_to_try_the_series()


        # ［先後の決め方］を尋ねます
        specified_turn_system_id = PromptCatalog.which_method_do_you_use_to_determine_sente_and_gote()


        # ［将棋の引分け率］を尋ねます
        specified_failure_rate = PromptCatalog.what_is_the_failure_rate()


        title='イーブン［シリーズ・ルール］'


        ep_table = EmpiricalProbabilityDuringTrialsTable.read_csv(failure_rate=specified_failure_rate, turn_system_id=specified_turn_system_id)
        df_ep = ep_table.df

        for            p,          failure_rate,          turn_system_name,          trials_series,          best_p,          best_p_error,          best_h_step,          best_t_step,          best_span,          latest_p,          latest_p_error,          latest_h_step,          latest_t_step,          latest_span,          candidates in\
            zip(df_ep['p'], df_ep['failure_rate'], df_ep['turn_system_name'], df_ep['trials_series'], df_ep['best_p'], df_ep['best_p_error'], df_ep['best_h_step'], df_ep['best_t_step'], df_ep['best_span'], df_ep['latest_p'], df_ep['latest_p_error'], df_ep['latest_h_step'], df_ep['latest_t_step'], df_ep['latest_span'], df_ep['candidates']):

            # 対象外のものはスキップ
            if specified_failure_rate != failure_rate:
                continue

            if best_h_step == IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO:
                print(f"[P={p} failure_rate={failure_rate}] ベスト値が設定されていません。スキップします")
                continue

            # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
            h_step = round_letro(best_h_step)
            t_step = round_letro(best_t_step)
            span = round_letro(best_span)

            # 仕様
            spec = Specification(
                    p=p,
                    failure_rate=failure_rate,
                    turn_system_id=specified_turn_system_id)

            simulate_series_rule(
                    spec=spec,
                    trials_series=specified_trials_series,
                    h_step=h_step,
                    t_step=t_step,
                    span=span,
                    presentable='',
                    comment='')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
