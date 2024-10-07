#
# 生成
# python step_o1o1o0_manual_create_a_csv_to_data_epdt.py
#
#   ［表勝ちだけでの対局数］と、［裏勝ちだけでの対局数］を探索する。
#

import traceback

from library import FROZEN_TURN, ALTERNATING_TURN, Converter
from library.views import PromptCatalog
from scripts.step_o1o1o0_create_a_csv_to_epdt import CreateCsvToEPDT


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［試行シリーズ数］を尋ねます
        specified_trials_series, specified_abs_small_error = PromptCatalog.how_many_times_do_you_want_to_try_the_series()


        # ［先後の決め方］を尋ねます
        specified_turn_system_id = PromptCatalog.which_method_do_you_use_to_determine_sente_and_gote()


        # ［将棋の引分け率］を尋ねます
        specified_failure_rate = PromptCatalog.what_is_the_failure_rate()


        create_csv_to_epdt = CreateCsvToEPDT(
                specified_failure_rate=specified_failure_rate,
                specified_turn_system_id=specified_turn_system_id,
                specified_trials_series=specified_trials_series,
                specified_abs_small_error=specified_abs_small_error)
        
        create_csv_to_epdt.execute()


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
