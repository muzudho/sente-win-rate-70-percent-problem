#
# ［かくきんデータ］Excel ファイルのシート１個分の CSV ファイルを作ろう
#
import datetime

from library import ALICE, BOB, SUCCESSFUL, FAILED, HEAD, TAIL, OUT_OF_P, Converter, Specification, SeriesRule, try_series
from library.file_paths import KakukinDataFilePaths
from library.database import TheoreticalProbabilityBestTable, KakukinDataSheetRecord, KakukinDataSheetTable
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

        # 変数名を縮める（Summary）
        S = large_series_trial_summary

        s_wins_a = S.wins(challenged=SUCCESSFUL, winner=ALICE)
        f_wins_a = S.wins(challenged=FAILED, winner=ALICE)
        s_wins_b = S.wins(challenged=SUCCESSFUL, winner=BOB)
        f_wins_b = S.wins(challenged=FAILED, winner=BOB)


        # テーブル作成
        kds_table, is_new = KakukinDataSheetTable.read_csv(
                trial_series=self._specified_trial_series,
                turn_system_id=self._specified_turn_system_id,
                failure_rate=self._specified_failure_rate,
                new_if_it_no_exists=True)


        # TODO データフレーム更新。レコード挿入
        kds_table.insert_record(
                welcome_record=KakukinDataSheetRecord(
                        p=spec.p,                                                                   # ［将棋の先手勝率］ p （Probability）
                        span=theoretical_series_rule.step_table.span,                               # ［シリーズ勝利条件］
                        t_step=theoretical_series_rule.step_table.get_step_by(face_of_coin=TAIL),   # ［後手で勝ったときの勝ち点］
                        h_step=theoretical_series_rule.step_table.get_step_by(face_of_coin=HEAD),   # ［先手で勝ったときの勝ち点］
                        shortest_coins=theoretical_series_rule.shortest_coins,                      # ［最短対局数］
                        upper_limit_coins=theoretical_series_rule.upper_limit_coins,                # ［上限対局数］
                        series_shortest_coins=S.series_shortest_coins,                              # ［シリーズ最短局数］
                        series_longest_coins=S.series_longest_coins,                                # ［シリーズ最長局数］
                        wins_a=s_wins_a + f_wins_a,                                                 # ［Ａさんの勝ちシリーズ数］
                        wins_b=s_wins_b + f_wins_b,                                                 # ［Ｂさんの勝ちシリーズ数］
                        succucessful_series=S.successful_series,                                    # ［引分けが起こらなかったシリーズ数］
                        s_ful_wins_a=S.ful_wins(challenged=SUCCESSFUL, winner=ALICE),               # ［引分けが起こらなかったシリーズ＞勝利条件達成＞Ａさんの勝ち］
                        s_ful_wins_b=S.ful_wins(challenged=SUCCESSFUL, winner=BOB),                 # ［引分けが起こらなかったシリーズ＞勝利条件達成＞Ｂさんの勝ち］
                        s_pts_wins_a=S.pts_wins(challenged=SUCCESSFUL, winner=ALICE),               # ［引分けが起こらなかったシリーズ＞点数差による判定勝ち＞Ａさんの勝ち］
                        s_pts_wins_b=S.pts_wins(challenged=SUCCESSFUL, winner=BOB),                 # ［引分けが起こらなかったシリーズ＞点数差による判定勝ち＞Ｂさんの勝ち］
                        failed_series=S.failed_series,                                              # ［引分けが含まれたシリーズ数］
                        f_ful_wins_a=S.ful_wins(challenged=FAILED, winner=ALICE),                   # ［引分けが含まれたシリーズ＞勝利条件達成＞Ａさんの勝ち］
                        f_ful_wins_b=S.ful_wins(challenged=FAILED, winner=BOB),                     # ［引分けが含まれたシリーズ＞勝利条件達成＞Ｂさんの勝ち］
                        f_pts_wins_a=S.pts_wins(challenged=FAILED, winner=ALICE),                   # ［引分けが含まれたシリーズ＞点数差による判定勝ち＞Ａさんの勝ち］
                        f_pts_wins_b=S.pts_wins(challenged=FAILED, winner=BOB),                     # ［引分けが含まれたシリーズ＞点数差による判定勝ち＞Ｂさんの勝ち］
                        no_wins_ab=S.no_wins))                                                      # ［勝敗付かずシリーズ数］


        # # CSV作成
        # csv = KakukinDataSheetTableCsv.stringify_csv_of_body(
        #         spec=spec,
        #         theoretical_series_rule=theoretical_series_rule,
        #         presentable='',
        #         comment='',
        #         large_series_trial_summary=large_series_trial_summary)

        #print(csv) # 表示

        # CSVファイル出力
        #
        #   TODO pandas にすれば、ここでファイル出力は不要（タイムアップ除く）
        #
        csv_file_path = kds_table.to_csv()
        # csv_file_path = KakukinDataFilePaths.as_sheet_csv(
        #         failure_rate=spec.failure_rate,
        #         turn_system_id=spec.turn_system_id,
        #         trial_series=self._specified_trial_series)
        print(f"[{datetime.datetime.now()}] step_o1o2o0_create_kakukin_data_sheet_csv_file. write view to `{csv_file_path}` file ...")
        # with open(csv_file_path, 'a', encoding='utf8') as f:
        #     f.write(f"{csv}\n")    # ファイルへ出力


    # automatic
    def execute(self):
        """実行

        TODO pandas で書き直せないか？
        """


        # ［理論的確率ベスト］表を読込。無ければナン
        tpb_table, is_new = TheoreticalProbabilityBestTable.read_csv(new_if_it_no_exists=False)

        # ［理論的確率ベスト］ファイルが存在しなければスキップ
        if tpb_table==None:
            return


        # 列定義
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
        #   TODO pandas にすれば、CSV出力１回で済むはず
        #
        csv_file_path = KakukinDataFilePaths.as_sheet_csv(
                failure_rate=spec.failure_rate,
                turn_system_id=spec.turn_system_id,
                trial_series=self._specified_trial_series)
        with open(csv_file_path, 'w', encoding='utf8') as f:
            f.write(f"{header_csv}\n")


        # データ部各行出力
        #   TODO pandas にすれば、CSV出力１回で済むはず
        tpb_table.for_each(on_each=self.on_each_tpb_record)
