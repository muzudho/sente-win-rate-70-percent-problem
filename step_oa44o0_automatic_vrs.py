#
# python step_oa44o0_automatic_vrs.py
#

import traceback
import os
import math
import time
import datetime
import random
import pandas as pd
from library import Converter, SeriesRule, get_list_of_basename
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
            detail_basename_list = get_list_of_basename(dir_path=VictoryRateDetailFilePaths.get_temp_directory_path())

            # シャッフル
            random.shuffle(detail_basename_list)


            for detail_basename in detail_basename_list:

                # print(f"[{datetime.datetime.now()}] step_oa44o0 {detail_basename=}")

                # ファイル名から［仕様］を取得する
                spec = BasenameOfVictoryRateDetailFile.to_spec(basename=detail_basename)

                if spec is None:
                    continue


                try:

                    # ファイルパス指定
                    detail_csv_file_path = f'./{VictoryRateDetailFilePaths.get_temp_directory_path()}/{detail_basename}'
                    summary_csv_file_path = VictoryRateSummaryFilePaths.as_csv()

                    print(f"[{datetime.datetime.now()}] step_oa44o0 {detail_csv_file_path=} {summary_csv_file_path=}")
                    time.sleep(1)   # １秒休む


                    # CSV読取
                    # -------
                    detail_df = pd.read_csv(detail_csv_file_path, encoding='utf-8')

                    if os.path.isfile(summary_csv_file_path):
                        summary_df = pd.read_csv(summary_csv_file_path, encoding='utf-8')

                    else:
                        summary_df = pd.DataFrame(columns=[
                            'turn_system_name',
                            'failure_rate',
                            'p',
                            'span',
                            't_step',
                            'h_step',
                            'a_victory_rate_by_trio',
                            'b_victory_rate_by_trio',
                            'no_victory_rate',
                            'a_victory_rate_by_duet',
                            'b_victory_rate_by_duet',
                            'unfair_point'])


                    detail_dtypes = {
                        'span':'int64',
                        't_step':'int64',
                        'h_step':'int64',
                        'a_victory_rate_by_trio':'float64',
                        'b_victory_rate_by_trio':'float64',
                        'no_victory_rate':'float64',
                        'a_victory_rate_by_duet':'float64',
                        'b_victory_rate_by_duet':'float64',
                        'unfair_point':'float64'}

                    summary_dtypes = {
                        'turn_system_name':'object',
                        'failure_rate':'float64',
                        'p':'float64',
                        'span':'int64',
                        't_step':'int64',
                        'h_step':'int64',
                        'a_victory_rate_by_trio':'float64',
                        'b_victory_rate_by_trio':'float64',
                        'no_victory_rate':'float64',
                        'a_victory_rate_by_duet':'float64',
                        'b_victory_rate_by_duet':'float64',
                        'unfair_point':'float64'}

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

                    # 絞り込み
                    # --------
                    #
                    #   unfair_point が一番小さいものを選ぶ
                    #
                    detail_df = detail_df[detail_df['unfair_point'] == detail_df['unfair_point'].min()]

#                     print(f"""\
# detail_df o0o0:
# {detail_df}""")

                    # ソート
                    # ------
                    #
                    #   互角に近いものを絞り込み済み
                    #
                    #   優先度１： no_victory_rate が 0 に近く
                    #   優先度２： span が小さく
                    #   優先度３： h_step が小さく      ※ t_step <= h_step なので、長い方を小さくしたい
                    #   優先度４： t_step が小さい
                    #
                    detail_df.sort_values(by=['a_victory_rate_by_duet', 'no_victory_rate', 'span', 'h_step', 't_step'], inplace=True)

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

                    span = detail_df.at[detail_index, 'span']
                    t_step = detail_df.at[detail_index, 't_step']
                    h_step = detail_df.at[detail_index, 'h_step']
                    summary_df.loc[summary_index] = {
                        'span':span,
                        't_step':t_step,
                        'h_step':h_step,
                        'a_victory_rate_by_trio':detail_df.at[detail_index, 'a_victory_rate_by_trio'],
                        'b_victory_rate_by_trio':detail_df.at[detail_index, 'b_victory_rate_by_trio'],
                        'no_victory_rate':detail_df.at[detail_index, 'no_victory_rate'],
                        'a_victory_rate_by_duet':detail_df.at[detail_index, 'a_victory_rate_by_duet'],
                        'b_victory_rate_by_duet':detail_df.at[detail_index, 'b_victory_rate_by_duet'],
                        'unfair_point':detail_df.at[detail_index, 'unfair_point']}


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
                            summary_csv_file_path,
                            columns=[
                                'turn_system_name',
                                'failure_rate',
                                'p',
                                'span',
                                't_step',
                                'h_step',
                                'a_victory_rate_by_trio',
                                'b_victory_rate_by_trio',
                                'no_victory_rate',
                                'a_victory_rate_by_duet',
                                'b_victory_rate_by_duet',
                                'unfair_point'],
                            index=False)
                    print(f"[{datetime.datetime.now()}] please look `{summary_csv_file_path}`")


                except KeyError as e:
                    message = f"[{datetime.datetime.now()}] ファイルが壊れているかも？ {detail_csv_file_path=} {summary_csv_file_path=} {e=}"
                    print(message)
                    # スタックトレース表示
                    print(traceback.format_exc())

                    log_file_path = VictoryRateSummaryFilePaths.as_log()
                    with open(log_file_path, 'a', encoding='utf-8') as f:
                        f.write(f"{message}\n")    # ファイルへ出力

                    # １分休む
                    seconds = 60
                    print(f"[{datetime.datetime.now()}] retry after {seconds} seconds")
                    time.sleep(seconds)


                except PermissionError as e:
                    message = f"[{datetime.datetime.now()}] ファイルが他で開かれているのかも？ {detail_csv_file_path=} {summary_csv_file_path=} {e=}"
                    print(message)
                    # スタックトレース表示
                    print(traceback.format_exc())

                    log_file_path = VictoryRateSummaryFilePaths.as_log()
                    with open(log_file_path, 'a', encoding='utf-8') as f:
                        f.write(f"{message}\n")    # ファイルへ出力

                    # １分休む
                    seconds = 60
                    print(f"[{datetime.datetime.now()}] retry after {seconds} seconds")
                    time.sleep(seconds)


                except Exception as e:
                    message = f"[{datetime.datetime.now()}] 予期せぬ例外 {detail_csv_file_path=} {summary_csv_file_path=} {e=}"
                    print(message)
                    # スタックトレース表示
                    print(traceback.format_exc())

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
