#
# ［かくきんデータ］Excel ファイルのシート１個分の CSV ファイルを作ろう
#
import datetime

from library import OUT_OF_P, Converter, Specification, SeriesRule, simulate_series
from library.file_paths import KakukinDataFilePaths
from library.database import TheoreticalProbabilityBestTable
from library.views import KakukinDataSheetTableCsv


class Automation():


    def __init__(self, specified_trial_series, specified_turn_system_id, specified_failure_rate):
        """初期化
        
        Parameters
        ----------
        specified_trial_series : float
            ［試行シリーズ数］
        specified_turn_system_id : float
            ［先後の決め方］
        specified_failure_rate : float
            ［コインの表も裏も出ない確率］
        """
        self._specified_trial_series=specified_trial_series
        self._specified_turn_system_id=specified_turn_system_id
        self._specified_failure_rate=specified_failure_rate


    def on_each_tpb_record(self, record_best_tp):

        # 対象外のものはスキップ　［試行シリーズ数］
        if self._specified_trial_series != record_best_tp.trial_series:
            return

        # 対象外のものはスキップ　［先後の決め方］
        if self._specified_turn_system_id != Converter.turn_system_code_to_id(record_best_tp.turn_system_name):
            return

        # 対象外のものはスキップ　［将棋の引分け率］
        if self._specified_failure_rate != record_best_tp.failure_rate:
            return

        if record_best_tp.theoretical_a_win_rate == OUT_OF_P:
            print(f"[trial_series={self._specified_trial_series}  failure_rate={record_best_tp.failure_rate}  p={record_best_tp.p}] ベスト値が設定されていません。スキップします")
            return


        # 仕様
        spec = Specification(
                p=record_best_tp.p,
                failure_rate=record_best_tp.failure_rate,
                turn_system_id=self._specified_turn_system_id)


        # ［シリーズ・ルール］
        # TODO これは理論値にしたい
        theoretical_series_rule = SeriesRule.make_series_rule_base(
                spec=spec,
                trial_series=self._specified_trial_series,
                h_step=record_best_tp.h_step,  # TODO これは理論値にしたい
                t_step=record_best_tp.t_step,  # TODO これは理論値にしたい
                span=record_best_tp.span)      # TODO これは理論値にしたい


        # シミュレーションします
        large_series_trial_summary = simulate_series(
                spec=spec,
                series_rule=theoretical_series_rule,
                specified_trial_series=self._specified_trial_series)


        # CSV作成
        csv = KakukinDataSheetTableCsv.stringify_csv_of_body(
                spec=spec,
                theoretical_series_rule=theoretical_series_rule,    # TODO ここは理論値にしたい
                presentable='',
                comment='',
                large_series_trial_summary=large_series_trial_summary)


        #print(csv) # 表示

        # CSVファイル出力
        csv_file_path = KakukinDataFilePaths.as_sheet_csv(
                failure_rate=spec.failure_rate,
                turn_system_id=spec.turn_system_id,
                trial_series=self._specified_trial_series)
        print(f"[{datetime.datetime.now()}] step_o1o2o0_create_kakukin_data_sheet_csv_file. write view to `{csv_file_path}` file ...")
        with open(csv_file_path, 'a', encoding='utf8') as f:
            f.write(f"{csv}\n")    # ファイルへ出力


    # automatic
    def execute(self):
        header_csv = KakukinDataSheetTableCsv.stringify_header()

        #print(header_csv) # 表示

        # 仕様
        spec = Specification(
                p=None,
                failure_rate=self._specified_failure_rate,
                turn_system_id=self._specified_turn_system_id)


        # ヘッダー出力（ファイルは上書きします）
        #
        #   NOTE ビューは既存ファイルの内容は破棄して、毎回、１から作成します
        #
        csv_file_path = KakukinDataFilePaths.as_sheet_csv(
                failure_rate=spec.failure_rate,
                turn_system_id=spec.turn_system_id,
                trial_series=self._specified_trial_series)
        with open(csv_file_path, 'w', encoding='utf8') as f:
            f.write(f"{header_csv}\n")


        # ベスト・テーブルを読込
        tpb_table, is_new = TheoreticalProbabilityBestTable.read_csv(new_if_it_no_exists=False)

        # ファイルが存在しなければスキップ
        if tpb_table==None:
            return


        tpb_table.for_each(on_each=self.on_each_tpb_record)
