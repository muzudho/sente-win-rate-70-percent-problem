#
# ［かくきんデータ］Excel ファイルのシート１個分の CSV ファイルを作ろう
#
import datetime

from library import ALICE, BOB, SUCCESSFUL, FAILED, HEAD, TAIL, UPPER_OUT_OF_P, Converter, Specification, SeriesRule
from library.eco import try_series
from library.file_paths import KakukinDataWorkbookFilePaths, KakukinDataSheetFilePaths
from library.database import TheoreticalProbabilityBestTable, KakukinDataSheetRecord, KakukinDataSheetTable
from scripts import SaveOrIgnore


class GeneratorOfKDS():


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
        self._kds_table = None


    def on_each_tpb_record(self, row_number, tpb_record):

        # 対象外のものはスキップ　［先後の決め方］
        if self._specified_turn_system_id != Converter.turn_system_code_to_id(tpb_record.turn_system_name):
            return

        # 対象外のものはスキップ　［将棋の引分け率］
        if self._specified_failure_rate != tpb_record.failure_rate:
            return

        if tpb_record.expected_a_victory_rate_by_duet == UPPER_OUT_OF_P:
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
                span=tpb_record.span,
                t_step=tpb_record.t_step,
                h_step=tpb_record.h_step)


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


        # データフレーム更新。レコードの挿入または更新
        self._kds_table.upsert_record(
                welcome_record=KakukinDataSheetRecord(
                        turn_system_name=Converter.turn_system_id_to_name(self._specified_turn_system_id),  # ［先後の決め方］
                        failure_rate=self._specified_failure_rate,                                  # ［将棋の引分け率］
                        p=spec.p,                                                                   # ［将棋の先手勝率］ p （Probability）
                        span=theoretical_series_rule.span,                               # ［シリーズ勝利条件］
                        t_step=theoretical_series_rule.t_step,   # ［後手で勝ったときの勝ち点］
                        h_step=theoretical_series_rule.h_step,   # ［先手で勝ったときの勝ち点］
                        shortest_coins=theoretical_series_rule.shortest_coins,                      # ［最短対局数］
                        upper_limit_coins=theoretical_series_rule.upper_limit_coins,                # ［上限対局数］
                        expected_a_victory_rate_by_duet=tpb_record.expected_a_victory_rate_by_duet,   # ［Ａさんの勝率の理論値］
                        expected_no_win_match_rate=tpb_record.expected_no_win_match_rate,           # ［コインを投げて表も裏も出ない確率の理論値］
                        trial_series=self._specified_trial_series,                                  # ［シリーズ試行回数］
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


    # automatic
    def execute(self):
        """実行"""


        # ［理論的確率ベスト］表を読込。無ければナン
        tpb_table, tpb_file_read_result = TheoreticalProbabilityBestTable.from_csv(new_if_it_no_exists=False)

        # ［理論的確率ベスト］ファイルが存在しなければスキップ
        if tpb_table==None:
            return


        # ［かくきんデータ・シート］テーブル作成
        self._kds_table, kds_file_read_result = KakukinDataSheetTable.from_csv(
                trial_series=self._specified_trial_series,
                turn_system_id=self._specified_turn_system_id,
                failure_rate=self._specified_failure_rate,
                new_if_it_no_exists=True)


        # ［かくきんデータ・シート］のデータ行出力
        tpb_table.for_each(on_each=self.on_each_tpb_record)


        # ［かくきんデータ・シート］のCSVファイル出力
        SaveOrIgnore.execute(
                log_file_path=KakukinDataSheetFilePaths.as_log(),
                on_save_and_get_file_name=self._kds_table.to_csv)
