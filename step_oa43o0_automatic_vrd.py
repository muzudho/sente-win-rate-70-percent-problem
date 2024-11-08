#
# python step_oa43o0_automatic_vrd.py
#

import traceback
import os
import math
import time
import datetime
import random
import openpyxl as xl
import pandas as pd
from library import TAIL, HEAD, SeriesRule, get_list_of_basename
from library.file_basename import BasenameOfGameTreeWorkbookFile
from library.file_paths import GameTreeWorkbookFilePaths, VictoryRateDetailFilePaths


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        while True:

            # １秒休む
            time.sleep(1)

            # ファイル名一覧取得
            basename_list = get_list_of_basename(dir_path=GameTreeWorkbookFilePaths.get_temp_directory_path())

            # シャッフル
            random.shuffle(basename_list)


            for basename in basename_list:
                print(f"[{datetime.datetime.now()}] step_oa43o0_automatic_vrd {basename=}")

                # １秒休む
                time.sleep(1)

                # ファイル名から［シリーズ・ルール］を取得する
                series_rule = BasenameOfGameTreeWorkbookFile.to_series_rule(basename=basename)

                if series_rule is None:
                    continue


                try:

                    # ファイルを開く
                    # -------------
                    #
                    #   GTWB ワークブック（.xlsx）
                    #
                    workbook_file_path = f'./{GameTreeWorkbookFilePaths.get_temp_directory_path()}/{basename}'
                    wb = xl.load_workbook(filename=workbook_file_path)

                    # GTWB ワークブック（.xlsx）ファイルの Summary シートの B2 セル（先手勝率）を見る
                    summary_ws = wb['Summary']
                    a_victory_rate_by_trio = float(summary_ws["B2"].value)      # Ａさん（シリーズを先手で始めた方）が優勝した率
                    b_victory_rate_by_trio = float(summary_ws["B3"].value)      # Ｂさん（シリーズを後手で始めた方）が優勝した率
                    no_victory_rate = float(summary_ws["B4"].value)     # 優勝が決まらなかった率

                    # victory_rate_detail (VRD) ファイル名を作成する。ファイル名には turn system, failure rate, p が含まれる
                    csv_file_path = VictoryRateDetailFilePaths.as_csv(spec=series_rule.spec)
                    print(f"[{datetime.datetime.now()}] step_oa43o0_automatic_vrd {csv_file_path=}")
                    
                    # ファイルを開く
                    # -------------
                    #
                    #   CSV ファイル。既存時
                    #
                    if os.path.isfile(csv_file_path):
                        df = pd.read_csv(
                                csv_file_path,
                                encoding="utf-8")
                    
                        # t_time が無ければ追加
                        if 't_time' not in df.columns.values:
                            df['t_time'] = (df['span'] / df['t_step']).map(math.ceil)

                        # h_time が無ければ追加
                        if 'h_time' not in df.columns.values:
                            df['h_time'] = (df['span'] / df['h_step']).map(math.ceil)

                        # shortest_coins が無ければ追加
                        if 'shortest_coins' not in df.columns.values:
                            df['shortest_coins'] = df[['span', 't_step', 'h_step']].apply(lambda X:SeriesRule.let_shortest_coins(h_step=X['h_step'], t_step=X['t_step'], span=X['span'], turn_system_id=series_rule.spec.turn_system_id), axis=1)

                        # upper_limit_coins が無ければ追加
                        if 'upper_limit_coins' not in df.columns.values:
                            df['upper_limit_coins'] = df[['t_time', 'h_time']].apply(lambda X:SeriesRule.let_upper_limit_coins_without_failure_rate(spec=series_rule.spec, h_time=X['h_time'], t_time=X['t_time']), axis=1)

                    # ファイルの新規作成
                    # -----------------
                    #
                    #   CSV ファイル。非存在時
                    #
                    else:
                        df = pd.DataFrame(columns=[
                            'span',
                            't_step',
                            'h_step',
                            'a_victory_rate_by_trio',
                            'b_victory_rate_by_trio',
                            'no_victory_rate',
                            'a_victory_rate_by_duet',
                            'b_victory_rate_by_duet',
                            'unfair_point',
                            't_time',
                            'h_time',
                            'shortest_coins',
                            'upper_limit_coins'])


                    # 型設定
                    dtypes = {
                        'span':'int64',
                        't_step':'int64',
                        'h_step':'int64',
                        'a_victory_rate_by_trio':'float64',
                        'b_victory_rate_by_trio':'float64',
                        'no_victory_rate':'float64',
                        'a_victory_rate_by_duet':'float64',
                        'b_victory_rate_by_duet':'float64',
                        'unfair_point':'float64',
                        't_time':'int64',
                        'h_time':'int64',
                        'shortest_coins':'int64',
                        'upper_limit_coins':'int64'}
                    df.astype(dtypes)


                    # 行の追加
                    # --------
                    #
                    #   victory_rate_detail (VRD) ファイルに span, t_step, h_step 毎の先手勝率を記録する
                    #
                    span = series_rule.step_table.span
                    t_step = series_rule.step_table.get_step_by(face_of_coin=TAIL)
                    h_step = series_rule.step_table.get_step_by(face_of_coin=HEAD)
                    t_time = SeriesRule.StepTable.let_t_time(span=span, t_step=t_step)
                    h_time = SeriesRule.StepTable.let_h_time(span=span, h_step=h_step)
                    a_victory_rate_by_duet = a_victory_rate_by_trio/(1 - no_victory_rate)
                    b_victory_rate_by_duet = b_victory_rate_by_trio/(1 - no_victory_rate)
                    df.loc[len(df) + 1] = {
                        'span':span,
                        't_step':t_step,
                        'h_step':h_step,
                        'a_victory_rate_by_trio':a_victory_rate_by_trio,
                        'b_victory_rate_by_trio':b_victory_rate_by_trio,
                        'no_victory_rate':no_victory_rate,
                        'a_victory_rate_by_duet':a_victory_rate_by_duet,
                        'b_victory_rate_by_duet':b_victory_rate_by_duet,
                        'unfair_point':(a_victory_rate_by_duet - 0.5) ** 2 + (b_victory_rate_by_duet - 0.5) ** 2,
                        't_time':t_time,
                        'h_time':h_time,
                        'shortest_coins':SeriesRule.let_shortest_coins(h_step=h_step, t_step=t_step, span=span, turn_system_id=series_rule.spec.turn_system_id),
                        'upper_limit_coins':SeriesRule.let_upper_limit_coins_without_failure_rate(spec=series_rule.spec, h_time=h_time, t_time=t_time)}

                    # ソート
                    # ------
                    #
                    #   ＡさんとＢさんの勝率が 0.5 から離れていない順に並んでほしい。［勝負なし］は少ないほど好ましい。span も短いほど好ましい。
                    #
                    df.sort_values(['unfair_point', 'no_victory_rate', 'span', 't_step', 'h_step'], inplace=True)
                    
                    # FIXME 重複データが無いようにする ----> 効いてない？
                    df.drop_duplicates(inplace=True)

                    # ファイル保存
                    df.to_csv(csv_file_path, index=False)
                    print(f"[{datetime.datetime.now()}] please look `{csv_file_path}`")


                except KeyError as e:
                    message = f"[{datetime.datetime.now()}] ファイルが壊れているかも？ {workbook_file_path=} {csv_file_path=} {e=}"
                    print(message)
                    # スタックトレース表示
                    print(traceback.format_exc())

                    log_file_path = VictoryRateDetailFilePaths.as_log(spec=series_rule.spec)
                    with open(log_file_path, 'a', encoding='utf-8') as f:
                        f.write(f"{message}\n")    # ファイルへ出力

                    # １分休む
                    seconds = 60
                    print(f"[{datetime.datetime.now()}] retry after {seconds} seconds")
                    time.sleep(seconds)


                except Exception as e:
                    message = f"[{datetime.datetime.now()}] 予期せぬ例外 {workbook_file_path=} {csv_file_path=} {e=}"
                    print(message)
                    # スタックトレース表示
                    print(traceback.format_exc())

                    log_file_path = VictoryRateDetailFilePaths.as_log(spec=series_rule.spec)
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
