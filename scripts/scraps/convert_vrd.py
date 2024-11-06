#
# python convert_vrd.py
#
#   a_victory_rate_by_duet, b_victory_rate_by_duet 列を追加する
#

import traceback
import datetime
import os
import random
import math
import pandas as pd

from library import get_list_of_basename
from library.file_paths import VictoryRateDetailFilePaths


########################################
# コマンドから実行時
########################################

def execute():

    try:
        # ファイル名一覧取得
        dir_path = VictoryRateDetailFilePaths.get_temp_directory_path()
        basename_list = get_list_of_basename(dir_path=dir_path)

        # シャッフル
        random.shuffle(basename_list)

        for basename in basename_list:

            try:
                csv_file_path = os.path.join(dir_path, basename)
                print(f"[{datetime.datetime.now()}] convert_vrd {csv_file_path=}")

                # CSVファイル読込
                df = pd.read_csv(csv_file_path)

                dirty = False

                if 'a_victory_rate_by_duet' not in df.columns.values:
                    df['a_victory_rate_by_duet'] = df['a_victory_rate_by_trio'] / (1 - df['no_victory_rate'])
                    dirty = True

                if 'b_victory_rate_by_duet' not in df.columns.values:
                    df['b_victory_rate_by_duet'] = df['b_victory_rate_by_trio'] / (1 - df['no_victory_rate'])
                    dirty = True

                # ＡさんとＢさんの勝率が 0.5 から離れていない順
                if 'unfair_point' not in df.columns.values:
                    df['unfair_point'] = (df['a_victory_rate_by_duet'] - 0.5) ** 2 + (df['b_victory_rate_by_duet'] - 0.5) ** 2
                    dirty = True

                if dirty:
                    # TODO ＡさんとＢさんの勝率が 0.5 から離れていない順に並んでほしい。［勝負なし］は少ないほど好ましい。span も短いほど好ましい。
                    df.sort_values(['unfair_point', 'no_victory_rate', 'span'], inplace=True)
                    df.to_csv(csv_file_path, index=False)


            # .gitkeep ファイルなど、CSVでないファイルも含まれているのでスキップ
            except pd.errors.EmptyDataError as e:
                # FIXME ログに残したい
                print(f"[{datetime.datetime.now()} skipped because no csv file. {e}")
                pass


            # 多分ファイルが壊れているからスキップ
            except KeyError as e:
                # FIXME ログに残したい
                print(f"[{datetime.datetime.now()} skipped because maybe file broken. {e}")
                pass


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
