#
# 表示
# python create_a_csv_to_view_evenizer_in_excel_ver2.py
#
#   Excel で［かくきんシステムの表］を表示するための CSV を作成する
#
#   NOTE 書式のような仕様は頻繁に変更することがあります
#

import traceback
import datetime

from library import HEAD, TAIL, ALICE, BOB, SUCCESSFUL, FAILED, FROZEN_TURN, ALTERNATING_TURN, BRUTE_FORCE, THEORETICAL, IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO, Converter, Specification, SeriesRule, judge_series, LargeSeriesTrialSummary, SequenceOfFaceOfCoin, simulate_series
from library.file_paths import get_even_view_csv_file_path, get_score_board_data_best_csv_file_path
from library.database import ScoreBoardDataBestRecord, ScoreBoardDataBestTable
from library.views import KakukinViewerInExcel


class Automation():


    def __init__(self, specified_failure_rate, specified_turn_system, specified_trials_series):
        self._specified_failure_rate=specified_failure_rate
        self._specified_turn_system=specified_turn_system
        self._specified_trials_series=specified_trials_series


    def on_each(self, best_record):

        # 対象外のものはスキップ　［将棋の引分け率］
        if self._specified_failure_rate != best_record.failure_rate:
            return

        # 対象外のものはスキップ　［先後の決め方］
        if self._specified_turn_system != Converter.code_to_turn_system(best_record.turn_system_str):
            return

        # # 対象外のものはスキップ　［試行シリーズ数］
        # if self._specified_trials_series != best_record.trials_series:
        #     return

        # if best_record.best_h_step == IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO:
        #     print(f"[p={best_record.p}  failure_rate={best_record.failure_rate}] ベスト値が設定されていません。スキップします")
        #     return


        # 仕様
        spec = Specification(
                p=best_record.p,
                failure_rate=best_record.failure_rate,
                turn_system=self._specified_turn_system)


        # ［シリーズ・ルール］
        series_rule = SeriesRule.make_series_rule_base(
                spec=spec,
                trials_series=self._specified_trials_series,
                h_step=best_record.h_step,
                t_step=best_record.t_step,
                span=best_record.span)


        # シミュレーションします
        large_series_trial_summary = simulate_series(
                spec=spec,
                series_rule=series_rule,
                specified_trials_series=self._specified_trials_series)


        # CSV作成
        csv = KakukinViewerInExcel.stringify_csv_of_body(
                spec=spec,
                series_rule=series_rule,
                presentable='',
                comment='',
                large_series_trial_summary=large_series_trial_summary)


        print(csv) # 表示

        # ログ出力
        csv_file_path_of_view = get_even_view_csv_file_path(spec=spec, trials_series=self._specified_trials_series)
        print(f"[{datetime.datetime.now()}] write view to `{csv_file_path_of_view}` file ...")
        with open(csv_file_path_of_view, 'a', encoding='utf8') as f:
            f.write(f"{csv}\n")    # ファイルへ出力


    # automatic
    def execute(self):
        header_csv = KakukinViewerInExcel.stringify_header()

        print(header_csv) # 表示

        # 仕様
        spec = Specification(
                p=None,
                failure_rate=self._specified_failure_rate,
                turn_system=self._specified_turn_system)


        # ヘッダー出力（ファイルは上書きします）
        #
        #   NOTE ビューは既存ファイルの内容は破棄して、毎回、１から作成します
        #
        csv_file_path_of_view = get_even_view_csv_file_path(spec=spec, trials_series=self._specified_trials_series)
        with open(csv_file_path_of_view, 'w', encoding='utf8') as f:
            f.write(f"{header_csv}\n")


        generation_algorythm = Converter.make_generation_algorythm(failure_rate=self._specified_failure_rate, turn_system=self._specified_turn_system)
        if generation_algorythm == BRUTE_FORCE:
            print("力任せ探索で行われたデータです")
        elif generation_algorythm == THEORETICAL:
            print("理論値で求められたデータです")
        else:
            raise ValueError(f"{generation_algorythm=}")


        # ベスト・テーブルを読込
        df_b, is_new = ScoreBoardDataBestTable.read_df(new_if_it_no_exists=False)

        # ファイルが存在しなければスキップ
        if is_new==True:
            return


        ScoreBoardDataBestTable.for_each(df=df_b, on_each=self.on_each)



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


        automation = Automation(
                specified_failure_rate=specified_failure_rate,
                specified_turn_system=specified_turn_system,
                specified_trials_series=specified_trials_series)

        automation.execute()


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
