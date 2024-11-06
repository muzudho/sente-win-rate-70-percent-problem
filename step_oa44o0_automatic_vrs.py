#
# python step_oa44o0_automatic_vrs.py
#

import traceback
import os
import time
import datetime
import random
import openpyxl as xl
import pandas as pd
from library import TAIL, HEAD, Converter, get_list_of_basename
from library.file_basename import BasenameOfVictoryRateDetailFile
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

            # victory_rate_detail フォルダーを見る
            basename_list = get_list_of_basename(dir_path=VictoryRateDetailFilePaths.get_temp_directory_path())

            # シャッフル
            random.shuffle(basename_list)


            for basename in basename_list:

                # print(f"[{datetime.datetime.now()}] step_oa44o0 {basename=}")

                # # １秒休む
                # time.sleep(1)

                # ファイル名から［仕様］を取得する
                spec = BasenameOfVictoryRateDetailFile.to_spec(basename=basename)

                if spec is None:
                    continue


                try:

                    # TODO ファイルパス指定
                    detail_csv_file_name = f'./{VictoryRateDetailFilePaths.get_temp_directory_path()}/{basename}'
                    summary_csv_file_name = VictoryRateSummaryFilePaths.as_csv()
                    print(f"[{datetime.datetime.now()}] step_oa44o0 {detail_csv_file_name=} {summary_csv_file_name=}")

                    # １秒休む
                    time.sleep(1)

                    # CSVファイルを開く
                    detail_df = pd.read_csv(detail_csv_file_name, encoding='utf-8')

                    if os.path.isfile(summary_csv_file_name):
                        summary_df = pd.read_csv(summary_csv_file_name, encoding='utf-8')
                    else:
                        summary_df = pd.DataFrame(columns=['turn_system_name', 'failure_rate', 'p', 'span', 't_step', 'h_step', 'a_victory_rate_by_trio', 'b_victory_rate_by_trio', 'no_victory_rate'])


                    detail_dtypes = {
                        'span':'int64',
                        't_step':'int64',
                        'h_step':'int64',
                        'a_victory_rate_by_trio':'float64',
                        'b_victory_rate_by_trio':'float64',
                        'no_victory_rate':'float64'}

                    summary_dtypes = {
                        'turn_system_name':'object',
                        'failure_rate':'float64',
                        'p':'float64',
                        'span':'int64',
                        't_step':'int64',
                        'h_step':'int64',
                        'a_victory_rate_by_trio':'float64',
                        'b_victory_rate_by_trio':'float64',
                        'no_victory_rate':'float64'}

                    # 型設定
                    detail_df.astype(detail_dtypes)
                    summary_df.astype(summary_dtypes)

    #                     print(f"""\
# detail_df o_8o0:
# {detail_df}

# summary_df o_8o0:
# {summary_df}""")

                    # インデックス設定
                    summary_df.set_index(['turn_system_name', 'failure_rate', 'p'], inplace=True)

#                     print(f"""\
# summary_df o_9o0:
# {summary_df}""")


                    # FIXME by_trio ではなく、 by_duet の方で 0.5 に近いものを選ばないといけない
                    # a_victory_rate が一番 0.5 に近いものを選ぶ
                    detail_df = detail_df[(detail_df['a_victory_rate_by_trio'] - 0.5).abs() == (detail_df['a_victory_rate_by_trio'] - 0.5).abs().min()]

#                     print(f"""\
# detail_df o0o0:
# {detail_df}""")

                    # ソートする。 no_victory_rate が 0 に近く、span が小さく、t_step が小さく、 h_step が小さいものを選ぶ
                    detail_df.sort_values(by=['no_victory_rate', 'span', 't_step', 'h_step'], inplace=True)

#                     print(f"""\
# detail_df o0o1o0:
# {detail_df}""")

                    head_detail_df = detail_df.head(1)

#                     print(f"""\
# head_detail_df o0o2o0:
# {head_detail_df}""")


                    # 行追加
                    detail_index = detail_df.index[0]
                    summary_index = (Converter.turn_system_id_to_name(spec.turn_system_id), spec.failure_rate, spec.p)
                    summary_df.loc[summary_index] = {
                        'span':detail_df.at[detail_index, 'span'],
                        't_step':detail_df.at[detail_index, 't_step'],
                        'h_step':detail_df.at[detail_index, 'h_step'],
                        'a_victory_rate_by_trio':detail_df.at[detail_index, 'a_victory_rate_by_trio'],
                        'b_victory_rate_by_trio':detail_df.at[detail_index, 'b_victory_rate_by_trio'],
                        'no_victory_rate':detail_df.at[detail_index, 'no_victory_rate']}


#                     print(f"""\
# summary_df o1o0:
# {summary_df}""")

                    
                    # インデックスを解除する
                    summary_df.reset_index(inplace=True)
#                     print(f"""\
# summary_df o2o0:
# {summary_df}""")

                    # ソートする
                    summary_df.sort_values(by=['turn_system_name', 'failure_rate', 'p'], inplace=True)

                    # ファイル保存
                    summary_df.to_csv(
                            summary_csv_file_name,
                            columns=['turn_system_name', 'failure_rate', 'p', 'span', 't_step', 'h_step', 'a_victory_rate_by_trio', 'b_victory_rate_by_trio', 'no_victory_rate'],
                            index=False)
                    print(f"[{datetime.datetime.now()}] please look `{summary_csv_file_name}`")


                except KeyError as e:
                    message = f"[{datetime.datetime.now()}] ファイルが壊れているかも？ {detail_csv_file_name=} {summary_csv_file_name=} {e=}"
                    print(message)

                    log_file_path = VictoryRateSummaryFilePaths.as_log()
                    with open(log_file_path, 'a', encoding='utf-8') as f:
                        f.write(f"{message}\n")    # ファイルへ出力

                    # １分休む
                    seconds = 60
                    print(f"[{datetime.datetime.now()}] retry after {seconds} seconds")
                    time.sleep(seconds)


                except PermissionError as e:
                    message = f"[{datetime.datetime.now()}] ファイルが他で開かれているのかも？ {detail_csv_file_name=} {summary_csv_file_name=} {e=}"
                    print(message)

                    log_file_path = VictoryRateSummaryFilePaths.as_log()
                    with open(log_file_path, 'a', encoding='utf-8') as f:
                        f.write(f"{message}\n")    # ファイルへ出力

                    # １分休む
                    seconds = 60
                    print(f"[{datetime.datetime.now()}] retry after {seconds} seconds")
                    time.sleep(seconds)


                except Exception as e:
                    message = f"[{datetime.datetime.now()}] 予期せぬ例外 {detail_csv_file_name=} {summary_csv_file_name=} {e=}"
                    print(message)

                    log_file_path = VictoryRateSummaryFilePaths.as_log()
                    with open(log_file_path, 'a', encoding='utf-8') as f:
                        f.write(f"{message}\n")    # ファイルへ出力

                    # １分休む
                    seconds = 60
                    print(f"[{datetime.datetime.now()}] retry after {seconds} seconds")
                    time.sleep(seconds)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
