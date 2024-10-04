#
# ［かくきんデータ］Excel ファイルのシート１個分の CSV ファイルを作ろう
#
import datetime

from library import IT_IS_NOT_BEST_IF_P_STEP_IS_ZERO, Converter, Specification, SeriesRule, simulate_series
from library.file_paths import KakukinDataFilePaths
from library.database import TheoreticalProbabilityBestTable
from library.views import KakukinDataSheetTableCsv


class Automation():


    def __init__(self, specified_failure_rate, specified_turn_system, specified_trials_series):
        """初期化
        
        Parameters
        ----------
        specified_failure_rate : float
            ［コインの表も裏も出ない確率］
        specified_turn_system : float
            ［先後の決め方］
        specified_trials_series : float
            ［試行シリーズ数］
        """
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
        csv = KakukinDataSheetTableCsv.stringify_csv_of_body(
                spec=spec,
                series_rule=series_rule,
                presentable='',
                comment='',
                large_series_trial_summary=large_series_trial_summary)


        print(csv) # 表示

        # ログ出力
        csv_file_path_of_view = KakukinDataFilePaths.as_sheet_csv(
                failure_rate=spec.failure_rate,
                turn_system=spec.turn_system,
                trials_series=self._specified_trials_series)
        print(f"[{datetime.datetime.now()}] write view to `{csv_file_path_of_view}` file ...")
        with open(csv_file_path_of_view, 'a', encoding='utf8') as f:
            f.write(f"{csv}\n")    # ファイルへ出力


    # automatic
    def execute(self):
        header_csv = KakukinDataSheetTableCsv.stringify_header()

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
        csv_file_path_of_view = KakukinDataFilePaths.as_sheet_csv(
                failure_rate=spec.failure_rate,
                turn_system=spec.turn_system,
                trials_series=self._specified_trials_series)
        with open(csv_file_path_of_view, 'w', encoding='utf8') as f:
            f.write(f"{header_csv}\n")


        # ベスト・テーブルを読込
        df_b, is_new = TheoreticalProbabilityBestTable.read_df(new_if_it_no_exists=False)

        # ファイルが存在しなければスキップ
        if is_new==True:
            return


        TheoreticalProbabilityBestTable.for_each(df=df_b, on_each=self.on_each)
