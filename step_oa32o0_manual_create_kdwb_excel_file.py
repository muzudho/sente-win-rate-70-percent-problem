#
# python step_oa32o0_manual_create_kdwb_excel_file.py
#
#

import traceback
import datetime

from library.views import PromptCatalog, DebugWrite
from scripts.step_oa32o0_create_kdwb_excel import GeneratorOfKDWB


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
        generator_of_kdwb = GeneratorOfKDWB(
                trial_series=specified_trial_series)
        generator_of_kdwb.execute()

        print(f"""\
でーきたっ！""")


    except Exception as err:
        print(f"""\
おお、残念！　例外が投げられてしまった！
{type(err)=}  {err=}

以下はスタックトレース表示じゃ。
{traceback.format_exc()}
""")
