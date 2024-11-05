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

from library import get_list_of_basename
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
            csv_file_path = os.path.join(dir_path, basename)
            print(f"[{datetime.datetime.now()}] convert_tp {csv_file_path=}")

            # CSVファイル読込
            df = pd.read_csv(csv_file_path)

            if 't_time' not in df.index:
                df['t_time'] = None

            if 'h_time' not in df.index:
                df['h_time'] = None
            
            df.to_csv(csv_file_path)

            break


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
