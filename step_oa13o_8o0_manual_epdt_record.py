#
# python step_oa13o_8o0_manual_epdt_record.py
#
# EPDTレコード１行分の探索
#

import traceback
import datetime

from library import HEAD, TAIL, FROZEN_TURN, ALTERNATING_TURN, SMALL_P_ABS_ERROR, Converter, Specification
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths
from library.database import EmpiricalProbabilityDuringTrialsRecord, EmpiricalProbabilityDuringTrialsTable
from library.views import PromptCatalog
from scripts import ForEachSeriesRule, SaveOrIgnore
from scripts.step_oa13o_8o0_each_epdt_record import SearchRecordOfEDPT
from config import DEFAULT_UPPER_LIMIT_SPAN



class Manual():


    def __init__(self, epdt_table):
        self._epdt_table = epdt_table


    def on_callback_each_epdt_record(self, context, is_update):
        # 変数名を縮める
        B = context.best_series_rule_cursor
        L = context.latest_series_rule_cursor


        # アップデート
        if is_update:

            # データフレーム更新
            is_dirty_record = self._epdt_table.upsert_record(
                    welcome_record=EmpiricalProbabilityDuringTrialsRecord(
                            p=B.series_rule.spec.p,
                            best_p=B.p,
                            best_p_error=B.p_error,
                            best_h_step=B.series_rule.h_step,
                            best_t_step=B.series_rule.t_step,
                            best_span=B.series_rule.span,
                            latest_p=L.p,
                            latest_p_error=L.p_error,
                            latest_h_step=L.series_rule.h_step,
                            latest_t_step=L.series_rule.t_step,
                            latest_span=L.series_rule.span,
                            candidate_history_text=context.candidate_history_text))

            # すぐ保存
            SaveOrIgnore.execute(
                    log_file_path=EmpiricalProbabilityDuringTrialsFilePaths.as_log(
                            trial_series=context.specified_trial_series,
                            turn_system_id=context.specified_turn_system_id,
                            failure_rate=context.specified_failure_rate),
                    on_save_and_get_file_name=self._epdt_table.to_csv)


        # 探索は十分か？
        if abs(B.p_error) < SMALL_P_ABS_ERROR:
            return True     # break

        return False    # continue


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［試行シリーズ数］を尋ねます
        specified_trial_series, specified_abs_small_error = PromptCatalog.how_many_times_do_you_want_to_try_the_series()


        # ［先後の決め方］を尋ねます
        specified_turn_system_id = PromptCatalog.which_method_do_you_use_to_determine_sente_and_gote()


        # ［将棋の引分け率］を尋ねます
        specified_failure_rate = PromptCatalog.what_is_the_failure_rate()


        # ［将棋の先手勝率］を尋ねます
        specified_p = PromptCatalog.what_is_the_probability_of_flipping_a_coin_and_getting_heads()


        # EPDTファイル読取り。無ければスキップ
        epdt_table, epdt_file_read_result = EmpiricalProbabilityDuringTrialsTable.from_csv(
                trial_series=specified_trial_series,
                turn_system_id=specified_turn_system_id,
                failure_rate=specified_failure_rate,
                new_if_it_no_exists=False)

        if epdt_file_read_result.is_file_not_found and epdt_table is None:
            print(f"[{datetime.datetime.now()}] ファイルが無いのでスキップします")
        
        else:
            manual = Manual(epdt_table=epdt_table)

            # ［仕様］
            spec = Specification(
                    turn_system_id=specified_turn_system_id,
                    failure_rate=specified_failure_rate,
                    p=specified_p)


            search_record_of_edpt = SearchRecordOfEDPT(
                    specified_trial_series=specified_trial_series,
                    specified_turn_system_id=specified_turn_system_id,
                    specified_failure_rate=specified_failure_rate,
                    on_callback=manual.on_callback_each_epdt_record)


            ForEachSeriesRule.execute(
                    spec=spec,
                    start_span=1,
                    start_t_step=1,
                    start_h_step=1,
                    end_span=DEFAULT_UPPER_LIMIT_SPAN,
                    on_each=search_record_of_edpt.execute)


        print("完了")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
