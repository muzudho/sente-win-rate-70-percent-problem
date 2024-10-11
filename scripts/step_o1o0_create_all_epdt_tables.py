#
# 全ての経験的確率テーブルを生成する
#
#

import time
import datetime
import pandas as pd

from library import ABS_OUT_OF_ERROR
from library.database import EmpiricalProbabilityDuringTrialsTable
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths
from library.views import DebugWrite
from scripts import ForEachTsFr
from scripts.step_o1o_9o0_each_epdt_table import Automation as StepO1o09o0EachEpdtTable


class Automation():
    """自動化"""


    def __init__(self, trial_series, abs_small_error, interval_seconds):
        self._specified_trial_series = trial_series
        self._specified_abs_small_error = abs_small_error

        # 反復深化探索
        self._interval_seconds = interval_seconds   # タイムアップ間隔
        self._specified_abs_smaller_error = None    # 閾値
        self._number_of_remaining = None            # 処理が残っているテーブル数
        self._passage_occurred = None               # 処理が残っているのに時間が足りなくて１件も更新できないということが発生したか？


    def execute_all_epdt_tables(self):
        """実行
        
        Returns
        -------
        None
        """

        # 反復深化探索
        # ===========
        #
        #   ［エラー］が 0 になることを目指していますが、最初から 0 を目指すと、もしかするとエラーは 0 にならなくて、
        #   処理が永遠に終わらないかもしれません。
        #   そこで、［エラー］列は、一気に 0 を目指すのではなく、手前の目標を設定し、その目標を徐々に小さくしていきます。
        #   リミットを指定して、リミットより［エラー］が下回ったら、処理を打ち切ることにします
        #

        self._specified_abs_smaller_error = ABS_OUT_OF_ERROR

        while True:
            # リセット
            self._number_of_remaining = 0
            self._passage_occurred = False

            # どんどん減っていく
            self._specified_abs_smaller_error = self._specified_abs_smaller_error * 0.75

            ForEachTsFr.execute(on_each_tsfr=self.on_each_tsfr)

            if self._number_of_remaining < 1:
                break

            # タイムシェアリングのために、処理時間が足りなくて更新が起こらず、処理を譲ることがオーバーヘッドになってきそうなら        
            if self._passage_occurred:
                # 間隔をどんどん長くしていく
                self._interval_seconds = int((self._interval_seconds + 10) * 1.1)


        print("完了しました")


    def on_each_tsfr(self, turn_system_id, failure_rate):

        # TODO ここでファイル作成してもいいんじゃないか？ --> 空ファイルになるからいやだということ？
        # EPDTファイル読取り。無ければスキップ
        epdt_table, epdt_file_read_result = EmpiricalProbabilityDuringTrialsTable.from_csv(
                trial_series=self._specified_trial_series,
                turn_system_id=turn_system_id,
                failure_rate=failure_rate,
                new_if_it_no_exists=False)


        # 対象外のテーブル
        # ===============

        # ファイルが無い
        if epdt_file_read_result.is_file_not_found and epdt_table is None:
            print(f"[{datetime.datetime.now()}] ファイルが無いのでスキップします")
            return

        # レコードが無い
        # NOTE ０件だと、 .min() や .max() が nan になってしまう
        if len(epdt_table.df) < 1:
            print(f"[{datetime.datetime.now()}] レコードが無いのでスキップします")
            return


        best_p_error_min = epdt_table.df['best_p_error'].min()
        best_p_error_max = epdt_table.df['best_p_error'].max()
        worst_abs_best_p_error = max(abs(best_p_error_min), abs(best_p_error_max))  # 絶対値の最大

        # ［小さな値］を下回っている
        if worst_abs_best_p_error <= self._specified_abs_small_error:
            print(f"[{datetime.datetime.now()}] 処理が完了しているのでスキップします")
            return


        # ［小さ目の値］を下回っている
        if worst_abs_best_p_error <= self._specified_abs_smaller_error:
            print(f"[{datetime.datetime.now()}] 処理が進んでいるので、他の処理へ譲るためにスキップします  {worst_abs_best_p_error=}  {self._specified_abs_smaller_error=}")
            return


        # 対象のテーブル
        # =============

        # とりあえず、［調整後の表が出る確率］が［最大エラー］値の半分未満になるよう目指す
        #
        #   NOTE P=0.99 の探索は、 p=0.50～0.98 を全部合わせた処理時間よりも、時間がかかるかも。だから p=0.99 のケースだけに合わせて時間調整するといいかも。
        #   NOTE エラー値を下げるときに、８本勝負の次に９本勝負を見つけられればいいですが、そういうのがなく次が１５本勝負だったりするような、跳ねるケースでは処理が長くなりがちです。リミットをゆっくり下げればいいですが、どれだけ気を使っても避けようがありません
        #
        #   TODO 探索をタイムシェアリングのために途中で譲ったのか、更新が終わってるのかを区別したい
        #
        o1o09o0_edpt_table = StepO1o09o0EachEpdtTable(
                specified_trial_series=self._specified_trial_series,
                specified_turn_system_id=turn_system_id,
                specified_failure_rate=failure_rate,
                smaller_abs_error=self._specified_abs_small_error,
                interval_seconds=self._interval_seconds,
                epdt_table=epdt_table)
        epdt_table.for_each(on_each=o1o09o0_edpt_table.execute_by_epdt_record)


        #
        # NOTE 小数点以下の桁を長く出しても見づらい
        #
        print(f"{DebugWrite.stringify(failure_rate=failure_rate)} is_smalled={o1o09o0_edpt_table.is_smalled}  target={o1o09o0_edpt_table.number_of_target}  smalled={o1o09o0_edpt_table.number_of_smalled}  yield={o1o09o0_edpt_table.number_of_yield}  passaged={o1o09o0_edpt_table.number_of_passaged}  interval_seconds={self._interval_seconds}  worst_error={worst_abs_best_p_error:.7f}(min={best_p_error_min}  max={best_p_error_max})  small_error={self._specified_abs_small_error:.7f}")


        # 処理が完了したから、ループを抜ける
        if o1o09o0_edpt_table.is_smalled:
            print(f"すべてのデータについて、誤差が {self._specified_abs_small_error} 以下になるよう作成完了。 {worst_abs_best_p_error=}")
            return
        

        # 処理が残っているテーブル数
        self._number_of_remaining += 1


        # タイムシェアリングのために、処理時間が足りなくて更新が起こらず、処理を譲ることがオーバーヘッドになってきそうなら        
        if 0 < o1o09o0_edpt_table.number_of_passaged:
            self._passage_occurred = True

