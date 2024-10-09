#
# 経験的確率CSVを生成する
#
#

import time
import datetime

from library import ABS_OUT_OF_ERROR
from library.database import EmpiricalProbabilityDuringTrialsTable
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths
from scripts import SaveOrIgnore
from scripts.step_o1o_9o0_each_epdt_table import Automation as StepO1o09o0EachEpdtTable


class Automation():
    """自動化"""


    def __init__(self, specified_trial_series, specified_turn_system_id, specified_failure_rate, specified_abs_small_error):
        self._specified_trial_series=specified_trial_series
        self._specified_turn_system_id=specified_turn_system_id
        self._specified_failure_rate=specified_failure_rate
        self._specified_abs_small_error=specified_abs_small_error

        self._epdt_table = None

        self._current_abs_lower_limit_of_error = None
        self._passage_upper_limit = None

        self._start_time_for_save = None    # CSV保存用タイマー
        self._is_dirty_csv = False

        self._cut_off = False   # FIXME 打ち切りフラグ。本当はタイムシェアリング書くべき

        self._best_p = None
        self._best_p_error = None


    def execute(self):
        """実行
        
        Returns
        -------
        None
        """

        # ファイル読取り。無ければスキップ
        self._epdt_table, is_new = EmpiricalProbabilityDuringTrialsTable.read_csv(
                trial_series=self._specified_trial_series,
                turn_system_id=self._specified_turn_system_id,
                failure_rate=self._specified_failure_rate,
                new_if_it_no_exists=False)

        if is_new and self._epdt_table is None:
            print(f"[{datetime.datetime.now()}] ファイルが無いのでスキップします")
            return


        # 対象外のケース
        # =============

        # NOTE ０件だと、 .min() や .max() が nan になってしまう
        if len(self._epdt_table.df) < 1:
            best_p_error_min = - ABS_OUT_OF_ERROR
            best_p_error_max = ABS_OUT_OF_ERROR
            # ループに最初に１回入るためだけの設定
            worst_abs_best_p_error = ABS_OUT_OF_ERROR

        else:
            best_p_error_min = self._epdt_table.df['best_p_error'].min()
            best_p_error_max = self._epdt_table.df['best_p_error'].max()
            # 絶対値にする
            worst_abs_best_p_error = max(abs(best_p_error_min), abs(best_p_error_max))

            # ［小さな値］を下回っていれば、対象外です
            if worst_abs_best_p_error <= self._specified_abs_small_error:
                return
        

        self._start_time_for_save = time.time()
        self._is_dirty_csv = False


        # 反復深化探索
        # ===========
        #
        #   ［エラー］が 0 になることを目指していますが、最初から 0 を目指すと、もしかするとエラーは 0 にならなくて、
        #   処理が永遠に終わらないかもしれません。
        #   そこで、［エラー］列は、一気に 0 を目指すのではなく、手前の目標を設定し、その目標を徐々に小さくしていきます。
        #   リミットを指定して、リミットより［エラー］が下回ったら、処理を打ち切ることにします
        #

        speed = 10
        self._current_abs_lower_limit_of_error = ABS_OUT_OF_ERROR
        self._passage_upper_limit = 10


        # FIXME どこかのタイミングで抜けたい。タイムシェアリングのコードをきちんと書くべきだが
        while not self._cut_off and (len(self._epdt_table.df) < 1 or self._specified_abs_small_error < worst_abs_best_p_error):

            # データが１件も入っていないとき、 nan になってしまう。とりあえずワースト誤差を最大に設定する
            if pd.isnull(worst_abs_best_p_error):
                worst_abs_best_p_error = ABS_OUT_OF_ERROR


            # とりあえず、［調整後の表が出る確率］が［最大エラー］値の半分未満になるよう目指す
            #
            #   NOTE P=0.99 の探索は、 p=0.50～0.98 を全部合わせた処理時間よりも、時間がかかるかも。だから p=0.99 のケースだけに合わせて時間調整するといいかも。
            #   NOTE エラー値を下げるときに、８本勝負の次に９本勝負を見つけられればいいですが、そういうのがなく次が１５本勝負だったりするような、跳ねるケースでは処理が長くなりがちです。リミットをゆっくり下げればいいですが、どれだけ気を使っても避けようがありません
            #
            #   TODO 探索をタイムシェアリングのために途中で譲ったのか、更新が終わってるのかを区別したい
            #
            is_update_table = False

            o1o09o0_edpt_table = StepO1o09o0EachEpdtTable(
                    specified_trial_series=self._specified_trial_series,
                    specified_turn_system_id=self._specified_turn_system_id,
                    specified_failure_rate=self._specified_failure_rate,
                    specified_abs_small_error=self._specified_abs_small_error,
                    epdt_table=self._epdt_table)
            self._epdt_table.for_each(on_each=o1o09o0_edpt_table.execute)


            #
            # NOTE 小数点以下の桁を長く出しても見づらい
            #
            print(f"[{datetime.datetime.now()}][failure_rate={self._specified_failure_rate}]  update={is_update_table}  target={o1o09o0_edpt_table.number_of_target}  smalled={o1o09o0_edpt_table.number_of_smalled}  yield={o1o09o0_edpt_table.number_of_yield}  passaged={o1o09o0_edpt_table.number_of_passaged}  {speed=}  worst_error={worst_abs_best_p_error:.7f}(min={best_p_error_min}  max={best_p_error_max})  current_error={self._current_abs_lower_limit_of_error:.7f}  small_error={self._specified_abs_small_error:.7f}  {self._passage_upper_limit=}")


            # 処理が完了したから、ループを抜ける
            if o1o09o0_edpt_table.number_of_target == o1o09o0_edpt_table.number_of_smalled:
                print(f"すべてのデータについて、誤差が {self._specified_abs_small_error} 以下になるよう作成完了。 {worst_abs_best_p_error=}")
                break


            # タイムシェアリングのために、処理を譲ることがオーバーヘッドになってきそうなら        
            if 0 < o1o09o0_edpt_table.number_of_passaged:
                # 初期値が 10 なら 1.1 倍で必ず 1 は増える
                self._passage_upper_limit = int(self._passage_upper_limit * 1.1)

            else:
                self._passage_upper_limit = int(self._passage_upper_limit * 0.9)
                if  self._passage_upper_limit < 10:
                    self._passage_upper_limit = 10

                # タイムシェアリングのために、処理を譲っているというわけでもないとき
                if o1o09o0_edpt_table.number_of_yield < 1:
                    # スピードがどんどん上がっていく
                    if not is_update_table:
                        speed += 1

                        # 半分、半分でも速そうなので、１０分の９を繰り返す感じで。
                        if self._current_abs_lower_limit_of_error is None:
                            self._current_abs_lower_limit_of_error = worst_abs_best_p_error * 9/speed
                        else:
                            self._current_abs_lower_limit_of_error *= 9/speed
                        
                        if self._current_abs_lower_limit_of_error < self._specified_abs_small_error:
                            self._current_abs_lower_limit_of_error = self._specified_abs_small_error


            # ［エラー］列で一番大きい値を取得します
            #
            #   ［調整後の表が出る確率］を 0.5 になるように目指します。［エラー］列は、［調整後の表が出る確率］と 0.5 の差の絶対値です
            #
            best_p_error_min = self._epdt_table.df['best_p_error'].min()
            best_p_error_max = self._epdt_table.df['best_p_error'].max()
            worst_abs_best_p_error = max(abs(best_p_error_min), abs(best_p_error_max))


        print(f"ループから抜けました")


        if self._is_dirty_csv:
            self._is_dirty_csv = False

            # 最後に CSV保存
            SaveOrIgnore.execute(
                    log_file_path=EmpiricalProbabilityDuringTrialsFilePaths.as_log(
                            trial_series=self._specified_trial_series,
                            turn_system_id=self._specified_turn_system_id,
                            failure_rate=self._specified_failure_rate),
                    on_save_and_get_file_name=self._epdt_table.to_csv)
