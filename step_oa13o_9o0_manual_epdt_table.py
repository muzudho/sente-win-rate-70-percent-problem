#
# python step_oa13o_9o0_manual_epdt_table.py
#
# EPDTテーブル１つ分の探索
#

import traceback
import datetime

from library import HEAD, TAIL, FROZEN_TURN, ALTERNATING_TURN, SMALL_P_ABS_ERROR, Converter, Specification
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths
from library.database import EmpiricalProbabilityDuringTrialsRecord, EmpiricalProbabilityDuringTrialsTable
from library.views import PromptCatalog
from scripts import ForEachSeriesRule, SaveOrIgnore
from scripts.step_o1o_9o0_each_epdt_table import Automation as StepO1o09o0EachEdptTable
from config import DEFAULT_UPPER_LIMIT_SPAN


# １つのテーブルに割り当てる最大処理時間（秒）
INTERVAL_SECONDS_ON_TABLE = 60


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


        # EPDTファイル読取り。無ければスキップ
        epdt_table, is_new = EmpiricalProbabilityDuringTrialsTable.read_csv(
                trial_series=specified_trial_series,
                turn_system_id=specified_turn_system_id,
                failure_rate=specified_failure_rate,
                new_if_it_no_exists=False)

        if is_new and epdt_table is None:
            print(f"[{datetime.datetime.now()}] ファイルが無いのでスキップします")
        
        else:
            automation = StepO1o09o0EachEdptTable(
                    specified_trial_series=specified_trial_series,
                    specified_turn_system_id=specified_turn_system_id,
                    specified_failure_rate=specified_failure_rate,
                    smaller_abs_error=SMALL_P_ABS_ERROR,
                    interval_seconds=INTERVAL_SECONDS_ON_TABLE,
                    epdt_table=epdt_table)


            # 各レコード
            epdt_table.for_each(on_each=automation.execute_by_epdt_record)


        print("完了")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
