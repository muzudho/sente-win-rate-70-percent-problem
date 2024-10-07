#
# FIXME これは廃止予定
#
#
# 表示
# python query_create_a_csv_to_view_ep_in_excel.py
#
#   Excel で［かくきんシステムの表］を表示するための CSV を作成する
#
#   NOTE 書式のような仕様は頻繁に変更することがあります
#

import traceback
import datetime

from library import HEAD, TAIL, ALICE, BOB, SUCCESSFUL, FAILED, FROZEN_TURN, ALTERNATING_TURN, IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO, Converter, Specification, SeriesRule, judge_series, LargeSeriesTrialSummary, SequenceOfFaceOfCoin, simulate_series
from library.file_paths import KakukinDataFilePaths
from library.database import EmpiricalProbabilityDuringTrialsTable
from library.views import KakukinDataSheetTableCsv, PromptCatalog


def automatic_deprecated(specified_failure_rate, specified_turn_system_id, specified_trials_series):
    header_csv = KakukinDataSheetTableCsv.stringify_header()

    print(header_csv) # 表示

    # 仕様
    spec = Specification(
            p=None,
            failure_rate=specified_failure_rate,
            turn_system_id=specified_turn_system_id)


    # ヘッダー出力（ファイルは上書きします）
    #
    #   NOTE ビューは既存ファイルの内容は破棄して、毎回、１から作成します
    #
    csv_file_path = KakukinDataFilePaths.as_sheet_csv(
            failure_rate=spec.failure_rate,
            turn_system_id=spec.turn_system_id,
            trials_series=specified_trials_series)
    with open(csv_file_path, 'w', encoding='utf8') as f:
        f.write(f"{header_csv}\n")


    ep_table = EmpiricalProbabilityDuringTrialsTable.read_csv(
            failure_rate=specified_failure_rate,
            turn_system_id=specified_turn_system_id,
            trials_series=specified_trials_series,
            new_if_it_no_exists=True)


    def on_each(record):

        # 対象外のものはスキップ　［将棋の引分け率］
        if specified_failure_rate != record.failure_rate:
            return

        # 対象外のものはスキップ　［試行シリーズ数］
        if specified_trials_series != record.trials_series:
            return

        if record.best_h_step == IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO:
            print(f"[p={record.p}  failure_rate={record.failure_rate}] ベスト値が設定されていません。スキップします")
            return


        # 仕様
        spec = Specification(
                p=record.p,
                failure_rate=record.failure_rate,
                turn_system_id=specified_turn_system_id)


        # ［シリーズ・ルール］
        series_rule = SeriesRule.make_series_rule_base(
                spec=spec,
                trials_series=specified_trials_series,
                h_step=record.best_h_step,
                t_step=record.best_t_step,
                span=record.best_span)


        # シミュレーションします
        large_series_trial_summary = simulate_series(
                spec=spec,
                series_rule=series_rule,
                specified_trials_series=specified_trials_series)


        # CSV作成
        csv = KakukinDataSheetTableCsv.stringify_csv_of_body(
                spec=spec,
                theoretical_series_rule=series_rule,    # TODO ここは理論値にしたい
                presentable='',
                comment='',
                large_series_trial_summary=large_series_trial_summary)

        print(csv) # 表示

        # ログ出力
        csv_file_path = KakukinDataFilePaths.as_sheet_csv(
                failure_rate=spec.failure_rate,
                turn_system_id=spec.turn_system_id,
                trials_series=specified_trials_series)
        print(f"[{datetime.datetime.now()}] query_create_a_csv_to_view_ep_in_excel. write view to `{csv_file_path}` file ...")
        with open(csv_file_path, 'a', encoding='utf8') as f:
            f.write(f"{csv}\n")    # ファイルへ出力


    ep_table.for_each(on_each=on_each)



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


        automatic_deprecated(
                specified_failure_rate=specified_failure_rate,
                specified_turn_system_id=specified_turn_system_id,
                specified_trials_series=specified_trials_series)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
