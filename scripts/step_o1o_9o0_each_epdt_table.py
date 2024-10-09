import time
import datetime

from library import HEAD, TAIL, ABS_OUT_OF_ERROR, SeriesRule, Specification
from library.database import EmpiricalProbabilityDuringTrialsRecord
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths
from scripts import SaveOrIgnore, ForEachSeriesRule
from scripts.step_o1o_8o0_each_epdt_record import Automation as StepO1o08o0EachEdptRecord, SeriesRuleCursor
from config import DEFAULT_LIMIT_SPAN


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

        self._best_series_rule_cursor = None
        self._latest_series_rule_cursor = None
        self._candidate_history_text = None

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

        # ［仕様］
        spec = Specification(
                turn_system_id=self._specified_turn_system_id,
                failure_rate=self._specified_failure_rate,
                p=epdt_record.p)

        # 探索開始時のベストとラテスト、候補の履歴
        self._best_series_rule_cursor = SeriesRuleCursor(
                p=epdt_record.best_p,
                p_error=epdt_record.best_p_error,
                series_rule=SeriesRule.make_series_rule_base(
                        spec=spec,
                        span=epdt_record.best_span,
                        t_step=epdt_record.best_t_step,
                        h_step=epdt_record.best_h_step))
        self._latest_series_rule_cursor = SeriesRuleCursor(
                p=epdt_record.latest_p,
                p_error=epdt_record.latest_p_error,
                series_rule=SeriesRule.make_series_rule_base(
                        spec=spec,
                        span=epdt_record.latest_span,
                        t_step=epdt_record.latest_t_step,
                        h_step=epdt_record.latest_h_step))
        self._candidate_history_text = epdt_record.candidate_history_text


        # ここから先、処理対象行
        self._number_of_target += 1

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


            stepo1o08o0_series_rule = StepO1o08o0EachEdptRecord(
                    specified_trial_series=self._specified_trial_series,
                    specified_turn_system_id=self._specified_turn_system_id,
                    specified_failure_rate=self._specified_failure_rate,
                    on_callback=self.on_callback_each_series_rule)


            ForEachSeriesRule.execute(
                    spec=spec,
                    span=start_span,
                    t_step=start_t_step,
                    h_step=start_h_step,
                    upper_limit_span=DEFAULT_LIMIT_SPAN,
                    on_each=stepo1o08o0_series_rule.execute)


            # self._is_sufficient_series_rule = False
            # self._is_multiple_update = False
            # # TODO 十分な［シリーズ・ルール］が出たか、複数回の更新があったとき
            # self._is_sufficient_series_rule = abs(self._best_p_error) < self._current_abs_lower_limit_of_error
            # self._is_multiple_update = 2 < self._update_count
            # @property
            # def is_sufficient_series_rule(self):
            #     """十分な［シリーズ・ルール］だ"""
            #     return self._is_sufficient_series_rule


            # @property
            # def is_multiple_update(self):
            #     """複数回更新があったか？"""
            #     return self._is_multiple_update


            if stepo1o08o0_series_rule.is_sufficient_series_rule:
                self._number_of_smalled += 1


            elif stepo1o08o0_series_rule.is_multiple_update:
                self._number_of_yield += 1
                # # 進捗バー
                # print('cutoff (good)', flush=True)

            # 処理はしたが更新は無かった
            elif stepo1o08o0_series_rule.is_passaged:
                self._number_of_passaged += 1


            # 保存判定
            if stepo1o08o0_series_rule._is_record_update:
                self._start_time_for_save = end_time_for_save

                # CSV保存
                SaveOrIgnore.execute(
                        log_file_path=EmpiricalProbabilityDuringTrialsFilePaths.as_log(
                                trial_series=self._specified_trial_series,
                                turn_system_id=self._specified_turn_system_id,
                                failure_rate=self._specified_failure_rate),
                        on_save_and_get_file_name=self._epdt_table.to_csv)

            # # 空振りが多いとき、探索を打ち切ります
            # if self._passage_upper_limit < self._passage_count:
            #     self._is_cutoff = True
            #     self._number_of_passaged += 1

            #     # # 進捗バー
            #     # print('cutoff (procrastinate)', flush=True)
            #     return True     # break

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
                            candidate_history_text=self._candidate_history_text))
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


    def on_callback_each_series_rule(self, context, is_update):
        # 変数名を縮める
        B = context.best_series_rule_cursor
        L = context.latest_series_rule_cursor

        self._latest_series_rule = L.series_rule


        # アップデート
        if is_update:

            # データフレーム更新
            self._is_dirty_record = self._epdt_table.upsert_record(
                    welcome_record=EmpiricalProbabilityDuringTrialsRecord(
                            p=B.series_rule.spec.p,
                            best_p=B.p,
                            best_p_error=B.p_error,
                            best_h_step=B.series_rule.step_table.get_step_by(face_of_coin=HEAD),
                            best_t_step=B.series_rule.step_table.get_step_by(face_of_coin=TAIL),
                            best_span=B.series_rule.step_table.span,
                            latest_p=L.p,
                            latest_p_error=L.p_error,
                            latest_h_step=L.series_rule.step_table.get_step_by(face_of_coin=HEAD),
                            latest_t_step=L.series_rule.step_table.get_step_by(face_of_coin=TAIL),
                            latest_span=L.series_rule.series_rule.step_table.span,
                            candidate_history_text=context.candidate_history_text))
            

            # 指定間隔（秒）
            end_time_for_save = time.time()
            is_timeup = INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - self._start_time_for_save

            # 探索打切り判定
            # FIXME タイムシェアリング書くの、めんどくさいんで、ループから抜けるのに使う
            self._is_cutoff = self._is_sufficient_series_rule or self._is_multiple_update or is_timeup


            # 探索を打ち切ります
            if self._is_cutoff:
                return True     # break

        else:
            self._is_passaged = True
            candidate_history_text = self._candidate_history_text



        is_break = False
        return is_break
