import time
import datetime

from library import HEAD, TAIL, ABS_OUT_OF_ERROR, EVEN, SeriesRule, Specification
from library.database import EmpiricalProbabilityDuringTrialsRecord
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths
from scripts import SaveOrIgnore, ForEachSeriesRule
from scripts.step_o1o_8o0_each_epdt_record import Automation as StepO1o08o0EachEdptRecord, SeriesRuleCursor
from config import DEFAULT_UPPER_LIMIT_SPAN


# １つのテーブルに割り当てる最大処理時間（秒）
INTERVAL_SECONDS_ON_TABLE = 60


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

        self._start_time_on_table = time.time()    # １つのテーブルの処理開始タイム
        self._is_dirty_csv = False

        self._is_smalled = False
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


    @property
    def number_of_target(self):
        """処理対象の数"""
        return self._number_of_target


    @property
    def is_smalled(self):
        """このテーブルは処理完了しているか？"""
        return self._is_smalled


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


    def execute_by_epdt_record(self, epdt_record):
        """実行
        
        TODO 更新が無かったとき、全て終わってるのか、何も進まなかったのかを分けたい。全部のレコードがスキップされたとき、無限ループに陥るのを防ぎたい
        """

        # 更新が終わってるか確認
        min_best_abs_p_error = (self._epdt_table.df['best_p_error'] - EVEN).abs().min()
        if min_best_abs_p_error < self._specified_abs_small_error:
            print(f"[{datetime.datetime.now()}] it was over")
            self._is_smalled = True
            return


        # 以下、このテーブルは処理対象。


        # ［仕様］
        spec = Specification(
                turn_system_id=self._specified_turn_system_id,
                failure_rate=self._specified_failure_rate,
                p=epdt_record.p)
        print(f"[{datetime.datetime.now()}][p={spec.p}]", flush=True)


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
                on_callback=self.on_callback_each_epdt_record)


        ForEachSeriesRule.execute(
                spec=spec,
                start_span=start_span,
                start_t_step=start_t_step,
                start_h_step=start_h_step,
                end_span=DEFAULT_UPPER_LIMIT_SPAN,
                on_each=stepo1o08o0_series_rule.execute)


    def on_callback_each_epdt_record(self, context, is_update):
        # 変数名を縮める
        B = context.best_series_rule_cursor
        L = context.latest_series_rule_cursor

        self._best_series_rule_cursor = B
        self._latest_series_rule_cursor = L
        self._candidate_history_text = context.candidate_history_text

        # 処理対象行。集計の分母に使う
        self._number_of_target += 1


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
                            latest_span=L.series_rule.step_table.span,
                            candidate_history_text=context.candidate_history_text))


        # 探索は十分か？
        is_sufficient = (abs(B.p_error) < self._specified_abs_small_error)

        # 探索打切り判定
        is_cutoff = any([
                # タイムアップ判定
                (INTERVAL_SECONDS_ON_TABLE < time.time() - self._start_time_on_table),
                is_sufficient,
        ])


        # 打切りなら
        if is_cutoff:
            # テーブルをCSV形式で保存する
            SaveOrIgnore.execute(
                    log_file_path=EmpiricalProbabilityDuringTrialsFilePaths.as_log(
                            trial_series=self._specified_trial_series,
                            turn_system_id=self._specified_turn_system_id,
                            failure_rate=self._specified_failure_rate),
                    on_save_and_get_file_name=self._epdt_table.to_csv)

            # 集計
            # ----

            # 処理完了
            if is_sufficient:
                self._number_of_smalled += 1

            # 処理中で、更新はあり、打ち切った
            elif is_update:
                self._number_of_yield += 1
            
            # 処理中だが、更新は無く、打ち切った
            else:
                self._number_of_passaged += 1


        # 真なら探索打切り、偽なら探索続行
        return is_cutoff
