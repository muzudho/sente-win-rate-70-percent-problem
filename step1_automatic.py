#
# やっつけプログラム１号
# python step1_automatic.py
#
#

import traceback
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, UPPER_LIMIT_FAILURE_RATE
from library.file_paths import Step1AutomaticFilePaths
from library.logging import Step1AutomaticLogging
from scripts.create_a_csv_to_epdt import Automation as CreateCsvToEPDT
from scripts.create_kakukin_data_sheet_csv_file import Automation as CreateKakukinDataSheetCsvFile


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［試行シリーズ回数］
        specified_trials_series = 2000

        # ［先後の決め方］
        for specified_turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:

            # ［将棋の引分け率］
            #  0％～上限、5%刻み
            for specified_failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5):
                specified_failure_rate = specified_failure_rate_percent / 100

                # 進捗記録
                Step1AutomaticLogging.log_progress(
                        failure_rate=specified_failure_rate,
                        shall_print=True)

                # CSV作成 ［試行中の経験的確率データファイル］
                #
                #   NOTE ここ、時間がかかりすぎじゃないか？
                #
                create_csv_to_epdt = CreateCsvToEPDT(
                        specified_failure_rate=specified_failure_rate,
                        specified_turn_system_id=specified_turn_system_id,
                        specified_trials_series=specified_trials_series,
                        specified_abs_small_error=0.0009)
                
                create_csv_to_epdt.execute()


                # CSV作成 ［かくきんデータ・エクセル・ファイルの各シートの元データ］
                create_kakukin_data_sheet_csv_file = CreateKakukinDataSheetCsvFile(
                        specified_failure_rate=specified_failure_rate,
                        specified_turn_system_id=specified_turn_system_id,
                        specified_trials_series=specified_trials_series)

                create_kakukin_data_sheet_csv_file.execute()


        progress = f"[{datetime.datetime.now()}] 完了"

        # 表示
        print(progress)
  
        # ファイルへログ出力
        log_file_path = Step1AutomaticFilePaths.as_log()
        with open(log_file_path, 'a', encoding='utf8') as f:
            f.write(f"{progress}\n")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
