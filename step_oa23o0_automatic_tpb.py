#
# python step_oa23o0_automatic_tpb.py
#
# ［理論的確率ベスト］（TPB）表へのレコードの挿入または更新。
#

import traceback
import time
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, Converter, Specification
from library.file_paths import TheoreticalProbabilityBestFilePaths
from library.database import TheoreticalProbabilityBestTable
from library.views import DebugWrite
from scripts import SaveWithRetry, IntervalForRetry, ForEachSpec
from scripts.step_oa23o0_upsert_record_in_tpb import GeneratorOneOfTPB
from config import DEFAULT_MAX_DEPTH, DEFAULT_UPPER_LIMIT_FAILURE_RATE


# 実行間隔タイマー
#INTERVAL_SECONDS = 5   # ５秒
INTERVAL_SECONDS = 3 * 60   # ３分。［素数ゼミ］参考


# CSV保存間隔（秒）
INTERVAL_SECONDS_FOR_SAVE_CSV = 30


class Automation():


    def __init__(self, automation_one):
        self._automation_one = automation_one

        self._depth = None
        self._start_time_for_save = time.time()
        self._number_of_target_rows = None
        self._number_of_not_found_rows = None
        self._number_of_dirty_rows = None
        self._number_of_bright_rows = None


    @property
    def number_of_target_rows(self):
        return self._number_of_target_rows


    @property
    def number_of_not_found_rows(self):
        return self._number_of_not_found_rows


    @property
    def number_of_dirty_rows(self):
        return self._number_of_dirty_rows


    @property
    def number_of_bright_rows(self):
        return self._number_of_bright_rows


    def reset_by_depth(self, depth):
        self._depth = depth
        self._number_of_target_rows = 0
        self._number_of_not_found_rows = 0
        self._number_of_dirty_rows = 0
        self._number_of_bright_rows = 0


    def on_each_spec(self, spec):
        self._number_of_target_rows += 1

        #print(f"{DebugWrite.stringify(depth=depth, spec=spec)}step o7o0 upsert record of tpb...  {number_of_dirty_rows=}  {number_of_bright_rows=}")
        # ［理論的確率ベストデータ］新規作成または更新
        is_dirty_temp, is_not_found = automation_one.execute_a_spec(spec=spec)

        if is_not_found:
            print(f"{DebugWrite.stringify(depth=depth,spec=spec)}ファイルが見つかりません")
            self._number_of_not_found_rows += 1

        elif is_dirty_temp:
            self._number_of_dirty_rows += 1
        
        else:
            self._number_of_bright_rows += 1
        

        if 0 < self._number_of_dirty_rows:
            # 指定間隔（秒）でファイル保存
            end_time_for_save = time.time()
            if INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - self._start_time_for_save:
                SaveWithRetry.execute(
                        log_file_path=TheoreticalProbabilityBestFilePaths.as_log(),
                        on_save_and_get_file_name=self._automation_one.tpb_table.to_csv)

                # コンソール表示
                print(f"{DebugWrite.stringify(depth=depth, spec=spec)}{self._number_of_dirty_rows} row(s) changed. {self._number_of_bright_rows} row(s) unchanged.")

                # リセット
                self._start_time_for_save = time.time()
                self._number_of_target = 0
                self._number_of_not_found_rows = 0
                self._number_of_dirty_rows = 0
                self._number_of_bright_rows = 0


    def on_file_saved():
        self._start_time_for_save = time.time()


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """Step o7o0 ［理論的確率ベスト］表へレコードの挿入または更新

    TODO 先に TPR表の expected_a_victory_rate_by_duet 列、 expected_no_win_match_rate列が更新されている必要があります
    """

    try:

        # 書込み先の［理論的確率ベストデータ］ファイルが存在しなかったなら、空データフレーム作成
        tpb_table, tpb_file_read_result = TheoreticalProbabilityBestTable.from_csv(new_if_it_no_exists=True)

        if tpb_table is None:
            raise ValueError("ここで tpb_table がナンなのはおかしい")


        generator_one_of_tpb = GeneratorOneOfTPB(tpb_table=tpb_table)

        automation_1 = Automation(automation_one=generator_one_of_tpb)


        # TODO 自動調整のいい方法が思い浮かばない。とりあえず、 depth が どんどん増えていくものとする。
        depth = 1
        while depth < DEFAULT_MAX_DEPTH:

            print(f"[{datetime.datetime.now()}] {depth=}  wait for {INTERVAL_SECONDS} seconds")
            time.sleep(INTERVAL_SECONDS)

            # リセット
            automation_1.reset_by_depth(depth=depth)


            ForEachSpec.execute(on_each_spec=automation_1.on_each_spec)


            # 深さの結果
            print(f"{DebugWrite.stringify(depth=depth)}loop end. There are {automation_1.number_of_target_rows} rows. {automation_1.number_of_dirty_rows} row(s) changed. {automation_1.number_of_bright_rows} row(s) unchanged.")


            # 忘れずに flush
            if 0 < automation_1.number_of_dirty_rows:
                # ファイル保存
                SaveWithRetry.execute(
                        log_file_path=TheoreticalProbabilityBestFilePaths.as_log(),
                        on_save_and_get_file_name=tpb_table.to_csv)

                # コンソール表示
                print(f"{DebugWrite.stringify(depth=depth)}{automation_1.number_of_dirty_rows} row(s) changed. {automation_1.number_of_bright_rows} row(s) unchanged.")

                # リセット
                automation_1.on_file_saved()


            # ファイルが見つからない場合、作成中かもしれません。それが作られることを期待します
            elif 0 < automation_1.number_of_not_found_rows:
                IntervalForRetry.sleep(min_secs=30, max_secs=5*60, shall_print=True)
                # 深さは継続


            # 更新完了
            elif automation_1.number_of_target_rows == automation_1.number_of_bright_rows:
                print(f"{DebugWrite.stringify(depth=depth)}it was over")
                # あとから新しいTPデータが追加されてくるから、終了はさせない
                #break
                # 深さのリセット
                depth = 1


            # 次の深さへ
            else:
                depth += 1


        # 現実的に、完了しない想定
        print("完了")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
