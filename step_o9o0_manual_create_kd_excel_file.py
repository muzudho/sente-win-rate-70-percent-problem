#
# python step_o9o0_manual_create_kd_excel_file.py
#
#

import traceback
import datetime

from library import Converter
from library.views import PromptCatalog
from scripts.step_o9o0_create_kakukin_data_excel_file import Automation as StepO9o0CreateKakukinDataExcelFileAutomation


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    try:
        # ［試行シリーズ数］を尋ねます
        specified_trial_series, specified_abs_small_error = PromptCatalog.how_many_times_do_you_want_to_try_the_series()


        # ［先後の決め方］を尋ねます
        specified_turn_system_id = PromptCatalog.which_method_do_you_use_to_determine_sente_and_gote()
        turn_system_name = Converter.turn_system_id_to_name(specified_turn_system_id)


        # ［将棋の引分け率］を尋ねます
        specified_failure_rate = PromptCatalog.what_is_the_failure_rate()



        print(f"[{datetime.datetime.now()}][turn_system_name={Converter.turn_system_id_to_name(specified_turn_system_id)}  failure_rete={specified_failure_rate * 100:.1f}%] create kakukin data excel file ...")

        # ［かくきんデータ］エクセル・ファイルの作成
        #
        #   NOTE 先にKDSファイルを作成しておく必要があります
        #
        automation = StepO9o0CreateKakukinDataExcelFileAutomation(
                specified_trial_series=specified_trial_series,
                specified_turn_system_id=specified_turn_system_id,
                specified_failure_rate=specified_failure_rate)

        automation.execute()

        print(f"""\
でーきたっ！""")


    except Exception as err:
        print(f"""\
おお、残念！　例外が投げられてしまった！
{type(err)=}  {err=}

以下はスタックトレース表示じゃ。
{traceback.format_exc()}
""")
