#
# 経験的確率CSVを生成する
#
#

import traceback
import datetime

from library import ABS_OUT_OF_ERROR, EVEN, Converter, Specification
from library.database import EmpiricalProbabilityDuringTrialsTable, EmpiricalProbabilityDuringTrialsRecord
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths
from library.views import DebugWrite
from scripts import SaveOrIgnore
from config import DEFAULT_UPPER_LIMIT_OF_P


class Automation():
    """自動化"""


    def __init__(self, specified_trial_series, specified_turn_system_id, specified_failure_rate, smaller_abs_error):
        self._specified_trial_series = specified_trial_series
        self._specified_turn_system_id = specified_turn_system_id
        self._specified_failure_rate = specified_failure_rate
        self._smaller_abs_error = smaller_abs_error

        self._epdt_table = None


    def execute(self):
        """実行
        
        Returns
        -------
        file_update : bool
            ファイルの更新があったか？
        """

        is_dirty = False

        # ファイル読取り。無ければ空テーブル新規作成して保存
        self._epdt_table, epdt_file_read_result = EmpiricalProbabilityDuringTrialsTable.from_csv(
                trial_series=self._specified_trial_series,
                turn_system_id=self._specified_turn_system_id,
                failure_rate=self._specified_failure_rate,
                new_if_it_no_exists=True)
        #print(self._epdt_table.df)


        # 対象外のテーブルは無視します
        # --------------------------
        if epdt_file_read_result.is_file_not_found:
            is_dirty = True

        # NOTE １件以上ないと、 .min() や .max() が nan になってしまう。１件以上あるときに判定する
        elif 0 < len(self._epdt_table.df):
            best_p_error_min = self._epdt_table.df['best_p_error'].min()
            best_p_error_max = self._epdt_table.df['best_p_error'].max()
            # 絶対値にする
            worst_abs_best_p_error = max(abs(best_p_error_min), abs(best_p_error_max))

            # ［小さな値］を下回っていれば、完了しているので、対象外です
            if worst_abs_best_p_error <= self._smaller_abs_error:
                return False
        

        # ［コインを投げて表が出る確率］
        for p_parcent in range(int(EVEN * 100), int(DEFAULT_UPPER_LIMIT_OF_P * 100) + 1):
            p = p_parcent / 100

            # 行の存在チェック。無ければ追加
            is_insert_record_temp = self.ready_disable_record(p=p)

            if is_insert_record_temp:
                is_dirty = True


        if is_dirty:
            # CSV保存
            SaveOrIgnore.execute(
                    log_file_path=EmpiricalProbabilityDuringTrialsFilePaths.as_log(
                            trial_series=self._specified_trial_series,
                            turn_system_id=self._specified_turn_system_id,
                            failure_rate=self._specified_failure_rate),
                    on_save_and_get_file_name=self._epdt_table.to_csv)

            turn_system_name = Converter.turn_system_id_to_name(self._specified_turn_system_id)
            print(f"{DebugWrite.stringify(trial_series=self._specified_trial_series, turn_system_name=turn_system_name, failure_rate=self._specified_failure_rate)}EMDT file saved")
            return True


        return False


    def ready_disable_record(self, p):
        """EPDTテーブルについて、まず、行の存在チェック。無ければ追加"""
            
        # 指定の p のレコードが１件も存在しなければデフォルトのレコード追加
        if not self._epdt_table.exists_index(p=p):

            # ［仕様］
            spec = Specification(
                    turn_system_id=self._specified_turn_system_id,
                    failure_rate=self._specified_failure_rate,
                    p=p)

            # レコードの挿入
            self._epdt_table.upsert_record(
                    welcome_record=EmpiricalProbabilityDuringTrialsRecord(
                            p=spec.p,
                            best_p=0,
                            best_p_error=ABS_OUT_OF_ERROR,
                            best_h_step=1,
                            best_t_step=1,
                            best_span=1,
                            latest_p=0,
                            latest_p_error=ABS_OUT_OF_ERROR,
                            latest_h_step=1,
                            latest_t_step=1,
                            latest_span=1,
                            candidate_history_text=''))

            return True
        

        return False
