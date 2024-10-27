#
# 生成
# python step_oa13o0_manual_create_epdt_table.py
#
#   ［表勝ちだけでの対局数］と、［裏勝ちだけでの対局数］を探索する。
#

import traceback

from library import FROZEN_TURN, ALTERNATING_TURN, Converter
from library.views import PromptCatalog
from scripts.step_oa13o0_create_all_epdt_tables import GeneratorOfAllTablesOfEPDT


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


        # # ［先後の決め方］を尋ねます
        # specified_turn_system_id = PromptCatalog.which_method_do_you_use_to_determine_sente_and_gote()


        # # ［将棋の引分け率］を尋ねます
        # specified_failure_rate = PromptCatalog.what_is_the_failure_rate()


        generator_of_all_tables_of_epdt = GeneratorOfAllTablesOfEPDT(
                trial_series=specified_trial_series,
                abs_small_error=specified_abs_small_error,
                interval_seconds=INTERVAL_SECONDS_ON_TABLE)
        
        generator_of_all_tables_of_epdt.execute_all_epdt_tables()


        print("完了")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
