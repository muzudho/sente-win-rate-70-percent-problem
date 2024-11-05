#
# python convert_tpr.py
#
#   t_time, h_time 列を追加する
#

import traceback
import datetime
import os
import random
import math
import pandas as pd

from library import SeriesRule, get_list_of_basename
from library.file_basename import BasenameOfTheoreticalProbabilityRates
from library.file_paths import TheoreticalProbabilityRatesFilePaths


def let_uppler_limit_coins(spec, span, t_step, h_step):
    # ［シリーズ・ルール］
    series_rule = SeriesRule.make_series_rule_base(
            spec=spec,
            span=int(span),
            t_step=int(t_step),
            h_step=int(h_step))

    return series_rule.upper_limit_coins


def execute():

    try:
        # victory_rate_detail フォルダーを見る
        dir_path = TheoreticalProbabilityRatesFilePaths.get_temp_directory_path()
        basename_list = get_list_of_basename(dir_path=dir_path)

        # シャッフル
        random.shuffle(basename_list)

        for basename in basename_list:

            try:
                csv_file_path = os.path.join(dir_path, basename)
                print(f"[{datetime.datetime.now()}] convert_tpr {csv_file_path=}")

                spec = BasenameOfTheoreticalProbabilityRates.to_spec(basename=basename)

                # CSVファイル読込
                df = pd.read_csv(csv_file_path)

                dirty = False

                # TODO
                if 'upper_limit_coins' not in df.index:
                    df.astype({
                        'span':'int64',
                        't_step':'int64',
                        'h_step':'int64',
                        'expected_a_victory_rate_by_duet':'float64',
                        'expected_no_win_match_rate':'float64'})
                    df['upper_limit_coins'] = df[['span', 't_step', 'h_step']].apply(lambda X:let_uppler_limit_coins(spec=spec, span=X[0], t_step=X[1], h_step=X[2]), axis=1)
                    dirty = True

                if 't_time' not in df.index:
                    # t_time の計算方法は、 span / t_step ※小数点切り上げ
                    a_series = df['span'] / df['t_step']
                    #print(f"{type(a_series)=}")
                    # Series クラスの map() 関数は処理が遅いが、独自関数を使える
                    df['t_time'] = a_series.map(math.ceil)
                    dirty = True

                if 'h_time' not in df.index:
                    # h_time の計算方法は、 span / h_step ※小数点切り上げ
                    df['h_time'] = (df['span'] / df['h_step']).map(math.ceil)
                    dirty = True

                if dirty:
                    df.sort_values(['t_time', 'h_time', 'expected_a_victory_rate_by_duet'], inplace=True)
                    df.to_csv(csv_file_path, index=False)


            # .gitkeep ファイルなど、CSVでないファイルも含まれているのでスキップ
            except pd.errors.EmptyDataError as e:
                print(f"[{datetime.datetime.now()} skip no csv file. {e}")
                pass

            break


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
