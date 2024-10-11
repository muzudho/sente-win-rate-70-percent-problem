#
# TODO 作成中
#
# python create_a_kakukin_data_excel_file.py
#
# Excel ファイルを作ろう
#
import traceback

from library import FROZEN_TURN, ALTERNATING_TURN, Converter
from library.views import PromptCatalog
from scripts.step_oa32o0_create_kd_excel import Automation as StepOa32o0CreateKDExcelAutomation


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    try:
        # ［試行シリーズ数］を尋ねます
        specified_trial_series, specified_abs_small_error = PromptCatalog.how_many_times_do_you_want_to_try_the_series()


        # ［先後の決め方］を尋ねます
        specified_turn_system_id = PromptCatalog.which_method_do_you_use_to_determine_sente_and_gote()


        # ［将棋の引分け率］を尋ねます
        specified_failure_rate = PromptCatalog.what_is_the_failure_rate()


        automation = StepOa32o0CreateKDExcelAutomation(
                specified_trial_series=specified_trial_series,
                specified_turn_system_id=specified_turn_system_id,
                specified_failure_rate=specified_failure_rate)

        automation.execute()


    except Exception as err:
        print(f"""\
おお、残念！　例外が投げられてしまった！
{type(err)=}  {err=}

以下はスタックトレース表示じゃ。
{traceback.format_exc()}
""")
