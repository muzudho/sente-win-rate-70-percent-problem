#
# NOTE こちらは古い方
#
#
# 表示
# python create_a_csv_to_view_ep_in_excel.py
#
#   Excel で［かくきんシステムの表］を表示するための CSV を作成する
#
#   NOTE 書式のような仕様は頻繁に変更することがあります
#

import traceback
import datetime

from library import HEAD, TAIL, ALICE, BOB, SUCCESSFUL, FAILED, FROZEN_TURN, ALTERNATING_TURN, IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO, Converter, Specification, SeriesRule, judge_series, LargeSeriesTrialSummary, SequenceOfFaceOfCoin, simulate_series
from library.file_paths import get_kakukin_data_sheet_csv_file_path
from library.database import EmpiricalProbabilityTable, EmpiricalProbabilityRecord
from library.views import KakukinDataSheetTableCsv


def automatic(specified_failure_rate, specified_turn_system, specified_trials_series):
    header_csv = KakukinDataSheetTableCsv.stringify_header()

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
    csv_file_path = get_kakukin_data_sheet_csv_file_path(
            failure_rate=spec.failure_rate,
            turn_system=spec.turn_system,
            trials_series=specified_trials_series)
    with open(csv_file_path, 'w', encoding='utf8') as f:
        f.write(f"{header_csv}\n")


    df_ep = EmpiricalProbabilityTable.read_df(failure_rate=specified_failure_rate, turn_system=specified_turn_system, trials_series=specified_trials_series)


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
                turn_system=specified_turn_system)


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
                series_rule=series_rule,
                presentable='',
                comment='',
                large_series_trial_summary=large_series_trial_summary)

        print(csv) # 表示

        # ログ出力
        csv_file_path = get_kakukin_data_sheet_csv_file_path(
                failure_rate=spec.failure_rate,
                turn_system=spec.turn_system,
                trials_series=specified_trials_series)
        print(f"[{datetime.datetime.now()}] write view to `{csv_file_path}` file ...")
        with open(csv_file_path, 'a', encoding='utf8') as f:
            f.write(f"{csv}\n")    # ファイルへ出力


    EmpiricalProbabilityTable.for_each(df=df_ep, on_each=on_each)



########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［将棋の先手勝率］を尋ねます
        prompt = f"""\

Example: 10% is 0.1
What is the failure rate? """
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

(0) Try       2 series
(1) Try      20 series
(2) Try     200 series
(3) Try    2000 series
(4) Try   20000 series
(5) Try  200000 series
(6) Try 2000000 series

Example: 3
How many times do you want to try the series(0-6)? """
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