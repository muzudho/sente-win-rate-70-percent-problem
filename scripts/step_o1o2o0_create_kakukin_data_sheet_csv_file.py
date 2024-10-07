#
# ［かくきんデータ］Excel ファイルのシート１個分の CSV ファイルを作ろう
#
import datetime

from library import OUT_OF_P, Converter, Specification, SeriesRule, try_series
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


    def on_each_tpb_record(self, tpb_record):

        # 対象外のものはスキップ　［試行シリーズ数］
        if self._specified_trial_series != tpb_record.trial_series:
            return

        # 対象外のものはスキップ　［先後の決め方］
        if self._specified_turn_system_id != Converter.turn_system_code_to_id(tpb_record.turn_system_name):
            return

        # 対象外のものはスキップ　［将棋の引分け率］
        if self._specified_failure_rate != tpb_record.failure_rate:
            return

        if tpb_record.theoretical_a_win_rate == OUT_OF_P:
            print(f"[trial_series={self._specified_trial_series}  failure_rate={tpb_record.failure_rate}  p={tpb_record.p}] ベスト値が設定されていません。スキップします")
            return


        # 仕様
        spec = Specification(
                turn_system_id=self._specified_turn_system_id,
                failure_rate=self._specified_failure_rate,
                p=tpb_record.p)


        # 理論値による［シリーズ・ルール］
        theoretical_series_rule = SeriesRule.make_series_rule_base(
                spec=spec,
                h_step=tpb_record.h_step,
                t_step=tpb_record.t_step,
                span=tpb_record.span)


        # シリーズを試行します
        large_series_trial_summary = try_series(
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
                turn_system_id=self._specified_turn_system_id,
                failure_rate=self._specified_failure_rate,
                p=None)


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


        # ［理論的確率ベスト］表を読込。無ければナン
        tpb_table, is_new = TheoreticalProbabilityBestTable.read_csv(new_if_it_no_exists=False)

        # ファイルが存在しなければスキップ
        if tpb_table==None:
            return


        tpb_table.for_each(on_each=self.on_each_tpb_record)
