#
# python step_oa31o0_manual_create_kds_table.py
#
#   ［かくきんデータ・シート］を作成する。
#   ［かくきんデータ・シート］とは、Excel で［かくきんシステムの表］を表示するための CSV
#

import traceback

from library import FROZEN_TURN, ALTERNATING_TURN, Converter
from library.views import PromptCatalog
from scripts.step_oa31o0_create_kds_table import Automation as StepO31o0CreateKDSTable


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


        # FIXME ［理論値の確率ベスト］表は先に更新されている必要があります


        automation = StepO31o0CreateKDSTable(
                specified_trial_series=specified_trial_series,
                specified_turn_system_id=specified_turn_system_id,
                specified_failure_rate=specified_failure_rate)

        automation.execute()


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
