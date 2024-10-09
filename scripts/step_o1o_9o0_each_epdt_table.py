import time
import datetime

from library import HEAD, TAIL, ALICE, SUCCESSFUL, FAILED, ABS_OUT_OF_ERROR, Converter, judge_series, SeriesRule, LargeSeriesTrialSummary, Specification, SequenceOfFaceOfCoin, Candidate
from library.database import EmpiricalProbabilityDuringTrialsRecord
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths
from scripts import SaveOrIgnore, ForEachSeriesRule


# 探索の上限
LIMIT_SPAN = 1001

# CSV保存間隔（秒）
INTERVAL_SECONDS_FOR_SAVE_CSV = 60


class Automation():
    """自動化"""


    def __init__(self, specified_trial_series, specified_turn_system_id, specified_failure_rate, specified_abs_small_error, epdt_table):
        self._specified_trial_series = specified_trial_series
        self._specified_turn_system_id = specified_turn_system_id
        self._specified_failure_rate = specified_failure_rate
        self._specified_abs_small_error = specified_abs_small_error

        self._epdt_table = epdt_table

        self._current_abs_lower_limit_of_error = None
        self._passage_upper_limit = None

        self._start_time_for_save = None    # CSV保存用タイマー
        self._is_dirty_csv = False

        self._number_of_target = 0       # 処理対象の数
        self._number_of_smalled = 0      # 処理完了の数
        self._number_of_yield = 0        # 処理を途中で譲った数
        self._number_of_passaged = 0     # 空振りで終わったレコード数

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


    @property
    def number_of_target(self):
        """処理対象の数"""
        return self._number_of_target


    @property
    def number_of_smalled(self):
        """処理完了の数"""
        return self._number_of_smalled


    @property
    def number_of_yield(self):
        """処理を途中で譲った数"""
        return self._number_of_yield


    @property
    def number_of_passaged(self):
        """空振りで終わったレコード数"""
        return self._number_of_passaged


    def execute(self, epdt_record):

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
            # データフレーム更新
            self._epdt_table.upsert_record(
                    welcome_record=EmpiricalProbabilityDuringTrialsRecord(
                            p=spec.p,
                            best_p=self._best_p,
                            best_p_error=self._best_p_error,
                            best_h_step=best_series_rule_if_it_exists.step_table.get_step_by(face_of_coin=HEAD),
                            best_t_step=best_series_rule_if_it_exists.step_table.get_step_by(face_of_coin=TAIL),
                            best_span=best_series_rule_if_it_exists.step_table.span,
                            latest_p=self._latest_p,
                            latest_p_error=self._latest_p_error,
                            latest_h_step=self._latest_series_rule.step_table.get_step_by(face_of_coin=HEAD),
                            latest_t_step=self._latest_series_rule.step_table.get_step_by(face_of_coin=TAIL),
                            latest_span=self._latest_series_rule.step_table.span,
                            candidates=self._latest_candidates))
            self._is_dirty_csv = True


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

            # データフレーム更新
            self._epdt_table.upsert_record(
                    welcome_record=EmpiricalProbabilityDuringTrialsRecord(
                            p=series_rule.spec.p,
                            best_p=self._best_p,
                            best_p_error=self._best_p_error,
                            best_h_step=best_series_rule_if_it_exists.step_table.get_step_by(face_of_coin=HEAD),
                            best_t_step=best_series_rule_if_it_exists.step_table.get_step_by(face_of_coin=TAIL),
                            best_span=best_series_rule_if_it_exists.step_table.span,
                            latest_p=self._latest_p,
                            latest_p_error=self._latest_p_error,
                            latest_h_step=series_rule.step_table.get_step_by(face_of_coin=HEAD),
                            latest_t_step=series_rule.step_table.get_step_by(face_of_coin=TAIL),
                            latest_span=series_rule.step_table.span,
                            candidates=self._latest_candidates))
            self._is_dirty_csv = True
            

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
