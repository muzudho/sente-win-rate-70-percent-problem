#
# 経験的確率CSVを生成する
#
#

import traceback
import time
import datetime
import pandas as pd

from library import HEAD, TAIL, ALICE, SUCCESSFUL, FAILED, ABS_OUT_OF_ERROR, Converter, judge_series, SeriesRule, LargeSeriesTrialSummary, Specification, SequenceOfFaceOfCoin, Candidate
from library.database import EmpiricalProbabilityDuringTrialsTable, EmpiricalProbabilityDuringTrialsRecord
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths
from scripts import SaveOrIgnore, ForEachSeriesRule


# 探索の上限
LIMIT_SPAN = 1001

# CSV保存間隔（秒）
INTERVAL_SECONDS_FOR_SAVE_CSV = 60


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

        self._number_of_target = None       # 処理対象の数
        self._number_of_smalled = None      # 処理完了の数
        self._number_of_yield = None        # 処理を途中で譲った数
        self._number_of_passaged = None     # 空振りで終わったレコード数

        self._cut_off = False   # FIXME 打ち切りフラグ。本当はタイムシェアリング書くべき

        self._latest_series_rule = None
        self._best_p = None
        self._best_p_error = None
        self._latest_p = None
        self._latest_p_error = None
        self._latest_candidates = None

        self._update_count = None
        self._passage_count = None
        self._is_cutoff = None
        self._is_good = None


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

            self._number_of_target = 0        # 処理対象の数
            self._number_of_smalled = 0       # 処理完了の数
            self._number_of_yield = 0         # 処理を途中で譲った数
            self._number_of_passaged = 0      # 空振りで終わったレコード数

            self._epdt_table.for_each(on_each=self.on_each_epdt_record)


            #
            # NOTE 小数点以下の桁を長く出しても見づらい
            #
            print(f"[{datetime.datetime.now()}][failure_rate={self._specified_failure_rate}]  update={is_update_table}  target={self._number_of_target}  smalled={self._number_of_smalled}  yield={self._number_of_yield}  passaged={self._number_of_passaged}  {speed=}  worst_error={worst_abs_best_p_error:.7f}(min={best_p_error_min}  max={best_p_error_max})  current_error={self._current_abs_lower_limit_of_error:.7f}  small_error={self._specified_abs_small_error:.7f}  {self._passage_upper_limit=}")


            # 処理が完了したから、ループを抜ける
            if self._number_of_target == self._number_of_smalled:
                print(f"すべてのデータについて、誤差が {self._specified_abs_small_error} 以下になるよう作成完了。 {worst_abs_best_p_error=}")
                break


            # タイムシェアリングのために、処理を譲ることがオーバーヘッドになってきそうなら        
            if 0 < self._number_of_passaged:
                # 初期値が 10 なら 1.1 倍で必ず 1 は増える
                self._passage_upper_limit = int(self._passage_upper_limit * 1.1)

            else:
                self._passage_upper_limit = int(self._passage_upper_limit * 0.9)
                if  self._passage_upper_limit < 10:
                    self._passage_upper_limit = 10

                # タイムシェアリングのために、処理を譲っているというわけでもないとき
                if self._number_of_yield < 1:
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


    def on_each_epdt_record(self, epdt_record):

        # どんどん更新されていく
        self._best_p = epdt_record.best_p
        self._best_p_error = epdt_record.best_p_error
        self._latest_p = epdt_record.latest_p
        self._latest_p_error = epdt_record.latest_p_error
        self._latest_candidates = epdt_record.candidates


        # ここから先、処理対象行
        self._number_of_target += 1


        # 仕様
        spec = Specification(
                turn_system_id=self._specified_turn_system_id,
                failure_rate=self._specified_failure_rate,
                p=epdt_record.p)

        # ダミー値。ベスト値が見つかっていないときは、この値は使えない値です
        best_series_rule_if_it_exists = SeriesRule.make_series_rule_base(
                spec=spec,
                span=epdt_record.best_span,
                t_step=epdt_record.best_t_step,
                h_step=epdt_record.best_h_step)

        self._update_count = 0
        self._passage_count = 0
        self._is_cutoff = False
        self._is_good = False


        # 既存データの方が信用のおけるデータだった場合、スキップ
        # エラーが十分小さければスキップ
        if abs(self._best_p_error) <= self._specified_abs_small_error:
            is_automatic = False

            # FIXME 全部のレコードがスキップされたとき、無限ループに陥る
            self._number_of_smalled += 1

        # アルゴリズムで求めるケース
        else:
            #print(f"[p={spec.p}]", end='', flush=True)
            is_automatic = True


            # まず、最後のカーソルを取得
            start_span = epdt_record.latest_span
            start_t_step = epdt_record.latest_t_step
            start_h_step = epdt_record.latest_h_step      # FIXME h_step の初期値が 0 という仕様を廃止したい。 1 にしたい


            ForEachSeriesRule.assert_sth(
                    span=start_span,
                    t_step=start_t_step,
                    h_step=start_h_step)


            # 最後のカーソルが更新済みなら、カーソルを１つ進めたところから次を始める
            if epdt_record.latest_p_error != ABS_OUT_OF_ERROR:
                start_span, start_t_step, start_h_step = ForEachSeriesRule.increase(
                    span=start_span,
                    t_step=start_t_step,
                    h_step=start_h_step)


            ForEachSeriesRule.assert_sth(
                    span=start_span,
                    t_step=start_t_step,
                    h_step=start_h_step)


            ForEachSeriesRule.execute(
                    spec=spec,
                    span=start_span,
                    t_step=start_t_step,
                    h_step=start_h_step,
                    upper_limit_span=LIMIT_SPAN,
                    on_each=self.on_each_series_rule)

            # print() # 改行


        # 十分な答えが出たので探索打切り
        if self._is_good:
            return
            #continue


        # 空振りが１回でもあれば、最終探索状態を保存
        if 0 < self._passage_count:
            # 表示とデータフレーム更新
            self.update_record(
                    spec=spec,
                    best_p=self._best_p,
                    best_p_error=self._best_p_error,
                    best_series_rule_if_it_exists=best_series_rule_if_it_exists,
                    latest_p=self._latest_p,
                    latest_p_error=self._latest_p_error,
                    latest_series_rule=self._latest_series_rule,
                    candidates=self._latest_candidates)

            # 指定間隔（秒）で保存
            end_time_for_save = time.time()
            if self._is_dirty_csv and INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - self._start_time_for_save:
                self._start_time_for_save = end_time_for_save
                self._is_dirty_csv = False

                # CSV保存
                SaveOrIgnore.execute(
                        log_file_path=EmpiricalProbabilityDuringTrialsFilePaths.as_log(
                                trial_series=self._specified_trial_series,
                                turn_system_id=self._specified_turn_system_id,
                                failure_rate=self._specified_failure_rate),
                        on_save_and_get_file_name=self._epdt_table.to_csv)


    def on_each_series_rule(self, series_rule):

        self._latest_series_rule = series_rule

        # 力任せ探索
        list_of_trial_results_for_one_series = []

        for i in range(0, self._specified_trial_series):

            # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
            path_of_face_of_coin = SequenceOfFaceOfCoin.make_sequence_of_playout(
                    spec=series_rule.spec,
                    upper_limit_coins=series_rule.upper_limit_coins)

            # FIXME 検証
            if len(path_of_face_of_coin) < series_rule.shortest_coins:
                text = f"{spec.p=} 指定の対局シートの長さ {len(path_of_face_of_coin)} は、最短対局数の理論値 {series_rule.shortest_coins} を下回っています。このような対局シートを指定してはいけません"
                print(f"""{text}
{path_of_face_of_coin=}
{series_rule.upper_limit_coins=}
""")
                raise ValueError(text)


            # 疑似のリストをもとに、シリーズとして見てみる
            trial_results_for_one_series = judge_series(
                    spec=series_rule.spec,
                    series_rule=series_rule,
                    path_of_face_of_coin=path_of_face_of_coin)
            
            list_of_trial_results_for_one_series.append(trial_results_for_one_series)
        
        # シミュレーションの結果
        large_series_trial_summary = LargeSeriesTrialSummary(
                specified_trial_series=self._specified_trial_series,
                list_of_trial_results_for_one_series=list_of_trial_results_for_one_series)

        # Ａさんが勝った回数
        s_wins_a = large_series_trial_summary.wins(challenged=SUCCESSFUL, winner=ALICE)
        f_wins_a = large_series_trial_summary.wins(challenged=FAILED, winner=ALICE)
        self._latest_p = (s_wins_a + f_wins_a) / self._specified_trial_series
        self._latest_p_error = self._latest_p - 0.5


        if abs(self._latest_p_error) < abs(self._best_p_error):
            is_update_table = True
            self._update_count += 1
            self._best_p = self._latest_p
            self._best_p_error = self._latest_p_error
            best_series_rule_if_it_exists = series_rule

            # ［シリーズ・ルール候補］
            candidate_obj = Candidate(
                    p_error=self._best_p_error,
                    trial_series=self._specified_trial_series,
                    h_step=best_series_rule_if_it_exists.step_table.get_step_by(face_of_coin=HEAD),   # FIXME FAILED の方は記録しなくていい？
                    t_step=best_series_rule_if_it_exists.step_table.get_step_by(face_of_coin=TAIL),
                    span=best_series_rule_if_it_exists.step_table.span,
                    shortest_coins=best_series_rule_if_it_exists.shortest_coins,             # ［最短対局数］
                    upper_limit_coins=best_series_rule_if_it_exists.upper_limit_coins)       # ［上限対局数］
            candidate_str = candidate_obj.as_str()
            turn_system_name = Converter.turn_system_id_to_name(self._specified_turn_system_id)
            print(f"[{datetime.datetime.now()}][trial_series={self._specified_trial_series}  turn_system_name={turn_system_name}  failure_rate={self._specified_failure_rate * 100:3.0f}％  p={series_rule.spec.p * 100:3.0f}％] {candidate_str}", flush=True) # すぐ表示

            # ［シリーズ・ルール候補］列を更新
            #
            #   途中の計算式。半角空裏区切り
            #
            if isinstance(self._latest_candidates, str):
                self._latest_candidates = f"{self._latest_candidates} {candidate_str}"
            else:
                self._latest_candidates = candidate_str

            # 表示とデータフレーム更新
            self.update_record(
                    spec=series_rule.spec,
                    best_p=self._best_p,
                    best_p_error=self._best_p_error,
                    best_series_rule_if_it_exists=best_series_rule_if_it_exists,
                    latest_p=self._latest_p,
                    latest_p_error=self._latest_p_error,
                    latest_series_rule=series_rule,
                    candidates=self._latest_candidates)

            # 十分な答えが出たか、複数回の更新があったとき
            is_good_temp = abs(self._best_p_error) < self._current_abs_lower_limit_of_error or 2 < self._update_count

            # 指定間隔（秒）
            end_time_for_save = time.time()
            is_timeup = INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - self._start_time_for_save

            # 保存判定
            if self._is_dirty_csv and (is_good_temp or is_timeup):
                self._start_time_for_save = end_time_for_save
                self._is_dirty_csv = False

                # CSV保存
                SaveOrIgnore.execute(
                        log_file_path=EmpiricalProbabilityDuringTrialsFilePaths.as_log(
                                trial_series=self._specified_trial_series,
                                turn_system_id=self._specified_turn_system_id,
                                failure_rate=self._specified_failure_rate),
                        on_save_and_get_file_name=self._epdt_table.to_csv)

                # FIXME タイムシェアリング書くの、めんどくさいんで、ループから抜ける
                self._cut_off = True


            # 探索を打ち切ります
            if is_good_temp:
                self._is_good = True
                self._is_cutoff = True
                self._number_of_yield += 1
                # # 進捗バー
                # print('cutoff (good)', flush=True)
                return True     # break

        else:
            self._passage_count += 1
            latest_candidates = self._latest_candidates

            # # 進捗バー
            # print('.', end='', flush=True)

            # 空振りが多いとき、探索を打ち切ります
            if self._passage_upper_limit < self._passage_count:
                self._is_cutoff = True
                self._number_of_passaged += 1

                # # 進捗バー
                # print('cutoff (procrastinate)', flush=True)
                return True     # break


        return False


    def update_record(self, spec, best_p, best_p_error, best_series_rule_if_it_exists,
            latest_p, latest_p_error, latest_series_rule, candidates):
        """データフレーム更新

        NOTE 新規行の追加は無い

        Parameters
        ----------
        spec : Specification
            ［仕様］
        """

        self._epdt_table.upsert_record(
                welcome_record=EmpiricalProbabilityDuringTrialsRecord(
                        p=spec.p,
                        best_p=best_p,
                        best_p_error=best_p_error,
                        best_h_step=best_series_rule_if_it_exists.step_table.get_step_by(face_of_coin=HEAD),
                        best_t_step=best_series_rule_if_it_exists.step_table.get_step_by(face_of_coin=TAIL),
                        best_span=best_series_rule_if_it_exists.step_table.span,
                        latest_p=latest_p,
                        latest_p_error=latest_p_error,
                        latest_h_step=latest_series_rule.step_table.get_step_by(face_of_coin=HEAD),
                        latest_t_step=latest_series_rule.step_table.get_step_by(face_of_coin=TAIL),
                        latest_span=latest_series_rule.step_table.span,
                        candidates=candidates))

        self._is_dirty_csv = True
