#
# python convert_tp.py
#
#   t_time, h_time 列を追加する
#

import traceback
import datetime
import os
import random
import math
import pandas as pd

from library.eco import get_list_of_basename
from library.file_paths import TheoreticalProbabilityFilePaths


########################################
# コマンドから実行時
########################################

def execute():

    try:
        # victory_rate_detail フォルダーを見る
        dir_path = TheoreticalProbabilityFilePaths.get_temp_directory_path()
        basename_list = get_list_of_basename(dir_path=dir_path)

        # シャッフル
        random.shuffle(basename_list)

        for basename in basename_list:

            try:
                csv_file_path = os.path.join(dir_path, basename)
                print(f"[{datetime.datetime.now()}] convert_tp {csv_file_path=}")

                # CSVファイル読込
                df = pd.read_csv(csv_file_path)

                dirty = False

                if True: #'t_time' not in df.columns.values:
                    # t_time の計算方法は、 span / t_step ※小数点切り上げ
                    a_series = df['span'] / df['t_step']
                    #print(f"{type(a_series)=}")
                    # Series クラスの map() 関数は処理が遅いが、独自関数を使える
                    df['t_time'] = a_series.map(math.ceil)
                    dirty = True

                if True: #'h_time' not in df.columns.values:
                    # h_time の計算方法は、 span / h_step ※小数点切り上げ
                    df['h_time'] = (df['span'] / df['h_step']).map(math.ceil)
                    dirty = True

                if dirty:
                    df.sort_values(['t_time', 'h_time', 'upper_limit_coins'], inplace=True)
                    df.to_csv(csv_file_path, index=False)


            # .gitkeep ファイルなど、CSVでないファイルも含まれているのでスキップ
            except pd.errors.EmptyDataError as e:
                print(f"[{datetime.datetime.now()} skip no csv file. {e}")
                pass


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
