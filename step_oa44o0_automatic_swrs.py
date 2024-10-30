#
# TODO 作成中
#
# python step_oa44o0_automatic_swrs.py
#

import traceback
import os
import time
import datetime
import random
import openpyxl as xl
import pandas as pd
from library import TAIL, HEAD, get_list_of_basename
from library.file_basename import BasenameOfVictoryRateDetailFile, BasenameOfVictoryRateSummaryFile
from library.file_paths import VictoryRateDetailFilePaths, VictoryRateSummaryFilePaths


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        while True:

            # １秒休む
            time.sleep(1)

            # TODO victory_rate_detail フォルダーを見る
            basename_list = get_list_of_basename(dir_path=VictoryRateDetailFilePaths.get_directory_path())

            # シャッフル
            random.shuffle(basename_list)


            for basename in basename_list:

                print(f"[{datetime.datetime.now()}] step_oa44o0 {basename=}")

                # １秒休む
                time.sleep(1)

                # ファイル名から［仕様］を取得する
                spec = BasenameOfVictoryRateDetailFile.to_spec(basename=basename)

                if spec is not None:

                    # TODO ファイルパス指定
                    detail_csv_file_name = f'./{VictoryRateDetailFilePaths.get_directory_path()}/{basename}'
                    summary_csv_file_name = f'./{VictoryRateSummaryFilePaths.get_directory_path()}/{basename}'
                    print(f"[{datetime.datetime.now()}] step_oa44o0 {detail_csv_file_name=} {summary_csv_file_name=}")

                    # TODO CSVファイルを開く
                    detail_df = pd.read_csv(detail_csv_file_name, encoding='utf-8')

                    if os.path.isfile(summary_csv_file_name):
                        summary_df = pd.read_csv(summary_csv_file_name, encoding='utf-8')
                    else:
                        summary_df = pd.DataFrame(columns=['span', 't_step', 'h_step', 'a_victory_rate', 'b_victory_rate', 'no_victory_rate'])


                    detail_dtypes = {
                        'span':'int64',
                        't_step':'int64',
                        'h_step':'int64',
                        'a_victory_rate':'float64',
                        'b_victory_rate':'float64',
                        'no_victory_rate':'float64'}

                    summary_dtypes = {
                        'span':'int64',
                        't_step':'int64',
                        'h_step':'int64',
                        'a_victory_rate':'float64',
                        'b_victory_rate':'float64',
                        'no_victory_rate':'float64'}

                    # 型設定
                    detail_df.astype(detail_dtypes)
                    summary_df.astype(summary_dtypes)

                    print(f"""\
detail_df o_8o0:
{detail_df}

summary_df o_8o0:
{summary_df}""")

                    # インデックス設定
                    summary_df.set_index(['span', 't_step', 'h_step'], inplace=True)

                    print(f"""\
summary_df o_9o0:
{summary_df}""")


                    # TODO a_victory_rate が一番 0.5 に近いものを選ぶ
                    detail_df = detail_df[(detail_df['a_victory_rate'] - 0.5).abs() == (detail_df['a_victory_rate'] - 0.5).abs().min()]

                    print(f"""\
detail_df o0o0:
{detail_df}""")

                    # TODO ソートする。 no_victory_rate が 0 に近く、span が小さく、t_step が小さく、 h_step が小さいものを選ぶ
                    detail_df.sort_values(by=['no_victory_rate', 'span', 't_step', 'h_step'], inplace=True)

                    print(f"""\
detail_df o0o1o0:
{detail_df}""")

                    head_detail_df = detail_df.head(1)

                    print(f"""\
head_detail_df o0o2o0:
{head_detail_df}""")


                    # TODO 行追加
                    detail_index = detail_df.index[0]
                    summary_index = (detail_df.at[detail_index, 'span'], detail_df.at[detail_index, 't_step'], detail_df.at[detail_index, 'h_step'])
                    summary_df.loc[summary_index] = {
                        'a_victory_rate':detail_df.at[detail_index, 'a_victory_rate'],
                        'b_victory_rate':detail_df.at[detail_index, 'b_victory_rate'],
                        'no_victory_rate':detail_df.at[detail_index, 'no_victory_rate']}


                    print(f"""\
summary_df o1o0:
{summary_df}""")

                    
                    # インデックスを解除する
                    summary_df.reset_index(inplace=True)
                    print(f"""\
summary_df o2o0:
{summary_df}""")

                    # ソートする
                    summary_df.sort_values(by=['span', 't_step', 'h_step'], inplace=True)

                    # ファイル保存
                    summary_df.to_csv(
                            summary_csv_file_name,
                            columns=['span', 't_step', 'h_step', 'a_victory_rate', 'b_victory_rate', 'no_victory_rate'],
                            index=False)
                    print(f"[{datetime.datetime.now()}] please look `{summary_csv_file_name}`")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
