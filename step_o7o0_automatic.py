#
# python step_o7o0_automatic.py
#

import traceback
import time
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, Converter, Specification
from library.file_paths import TheoreticalProbabilityBestFilePaths
from library.database import TheoreticalProbabilityBestTable
from library.views import DebugWrite
from config import DEFAULT_MAX_DEPTH, DEFAULT_UPPER_LIMIT_FAILURE_RATE
from scripts import SaveWithRetry
from scripts.step_o7o0_upsert_record_in_tpb import AutomationOne as StepO7o0UpsertRecordInTPBOne


# CSV保存間隔（秒）
INTERVAL_SECONDS_FOR_SAVE_CSV = 30


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """Step o7o0 ［理論的確率ベスト］表へレコードの挿入または更新

    TODO 先に TP表の theoretical_a_win_rate列、 theoretical_no_win_match_rate列が更新されている必要があります
    """

    try:
        # 書込み先の［理論的確率ベストデータ］ファイルが存在しなかったなら、空データフレーム作成
        tpb_table, is_new = TheoreticalProbabilityBestTable.read_csv(new_if_it_no_exists=True)

        if tpb_table is None:
            raise ValueError("ここで tpb_table がナンなのはおかしい")


        automation_one = StepO7o0UpsertRecordInTPBOne(tpb_table=tpb_table)


        # TODO 自動調整のいい方法が思い浮かばない。とりあえず、 depth が どんどん増えていくものとする。
        for depth in range(1, DEFAULT_MAX_DEPTH):

            # リセット
            number_of_dirty_rows = 0
            number_of_bright_rows = 0

            # ［先後の決め方］
            for turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:
                turn_system_name = Converter.turn_system_id_to_name(turn_system_id)

                # ［将棋の引分け率］
                for failure_rate_percent in range(0, int(DEFAULT_UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5): # 5％刻み。 100%は除く。0除算が発生するので
                    failure_rate = failure_rate_percent / 100

                    # ［将棋の先手勝率］
                    for p_percent in range(50, 96):
                        p = p_percent / 100

                        # 仕様
                        spec = Specification(
                                turn_system_id=turn_system_id,
                                failure_rate=failure_rate,
                                p=p)


                        #print(f"{DebugWrite.stringify(depth=depth, spec=spec)}step o7o0 upsert record of tpb...  {number_of_dirty_rows=}  {number_of_bright_rows=}")
                        # ［理論的確率ベストデータ］新規作成または更新
                        is_dirty_temp = automation_one.execute_a_spec(spec=spec)

                        if is_dirty_temp:
                            number_of_dirty_rows += 1
                        
                        else:
                            number_of_bright_rows += 1
                        

                        if 0 < number_of_dirty_rows:
                            # 指定間隔（秒）でファイル保存
                            end_time_for_save = time.time()
                            if INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - start_time_for_save:
                                SaveWithRetry.execute(
                                        log_file_path=TheoreticalProbabilityBestFilePaths.as_log(),
                                        on_save_and_get_file_name=tpb_table.to_csv)

                                # コンソール表示
                                print(f"{DebugWrite.stringify(depth=depth, spec=spec)}{number_of_dirty_rows} row(s) changed. {number_of_bright_rows} row(s) unchanged.")

                                # リセット
                                start_time_for_save = time.time()
                                number_of_dirty_rows = 0
                                number_of_bright_rows = 0


            # 忘れずに flush
            if 0 < number_of_dirty_rows:
                # ファイル保存
                SaveWithRetry.execute(
                        log_file_path=TheoreticalProbabilityBestFilePaths.as_log(),
                        on_save_and_get_file_name=tpb_table.to_csv)

                # コンソール表示
                print(f"{DebugWrite.stringify(depth=depth)}{number_of_dirty_rows} row(s) changed. {number_of_bright_rows} row(s) unchanged.")

                # リセット
                start_time_for_save = time.time()


        # 現実的に、完了しない想定
        print("完了")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
