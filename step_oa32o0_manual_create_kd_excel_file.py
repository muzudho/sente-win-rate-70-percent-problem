#
# python step_oa32o0_manual_create_kd_excel_file.py
#
#

import traceback
import datetime

from library.views import PromptCatalog, DebugWrite
from scripts.step_oa32o0_create_kd_excel import Automation as StepOa32o0CreateKDExcel


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    try:
        # ［試行シリーズ数］を尋ねます
        specified_trial_series, specified_abs_small_error = PromptCatalog.how_many_times_do_you_want_to_try_the_series()
        print(f"{DebugWrite.stringify(trial_series=specified_trial_series)}create kakukin data excel file ...")

        # ［かくきんデータ］エクセル・ファイルの作成
        #
        #   NOTE 先にKDSファイルを作成しておく必要があります
        #
        automation = StepOa32o0CreateKDExcel(
                trial_series=specified_trial_series)
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
