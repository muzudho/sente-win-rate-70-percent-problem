#
# やっつけプログラム１号
# python step_o1o0_automatic.py
#
#

import traceback
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, UPPER_LIMIT_FAILURE_RATE, ABS_SMALL_P_ERROR
from library.file_paths import StepO1o0AutomaticFilePaths
from config import DEFAULT_TRIAL_SERIES
from scripts.step_o1o1o0_create_a_csv_to_epdt import Automation as StepO1o1o0CreateCsvToEPDT
from scripts.step_o8o0_create_kds_table import Automation as StepO8o0CreateKDSTable


# 実行間隔タイマー
start_time_for_save = None
INTERVAL_SECONDS = 5 * 60   # ５分


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # リセット
        start_time_for_save = time.time()       # CSV保存用タイマー

        # ［試行シリーズ回数］
        specified_trial_series = DEFAULT_TRIAL_SERIES

        # ［先後の決め方］
        for specified_turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:

            # ［将棋の引分け率］
            #  0％～上限、5%刻み
            for specified_failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5):
                specified_failure_rate = specified_failure_rate_percent / 100


                # 指定間隔（秒）
                end_time_for_save = time.time()
                if INTERVAL_SECONDS <= end_time_for_save - self._start_time_for_save:
                    # リセット
                    start_time_for_save = time.time()       # CSV保存用タイマー

                    ###############################
                    # Step.o1o2o0 かくきんデータ作成
                    ###############################

                    # TODO ロギング

                    # CSV作成 ［かくきんデータ・エクセル・ファイルの各シートの元データ］
                    step_o8o0_create_kds_table = StepO8o0CreateKDSTable(
                            specified_failure_rate=specified_failure_rate,
                            specified_turn_system_id=specified_turn_system_id,
                            specified_trial_series=specified_trial_series)

                    step_o8o0_create_kds_table.execute()



        progress = f"[{datetime.datetime.now()}] 完了"

        # 表示
        print(progress)
  
        # ファイルへログ出力
        log_file_path = StepO1o0AutomaticFilePaths.as_log()
        with open(log_file_path, 'a', encoding='utf8') as f:
            f.write(f"{progress}\n")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
