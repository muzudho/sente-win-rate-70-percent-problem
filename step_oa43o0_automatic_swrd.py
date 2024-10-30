# python step_oa43o0_automatic_swrd.py
#

import traceback
import os
import time
import datetime
import random
import openpyxl as xl
import pandas as pd
from library import TAIL, HEAD, get_list_of_basename
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

            # game_tree_wb フォルダーを見る
            basename_list = get_list_of_basename(dir_path=GameTreeWorkbookFilePaths.get_temp_directory_path())

            # シャッフル
            random.shuffle(basename_list)


            for basename in basename_list:
                print(f"[{datetime.datetime.now()}] step_oa43o0 {basename=}")

                # １秒休む
                time.sleep(1)

                # ファイル名から［シリーズ・ルール］を取得する
                series_rule = BasenameOfGameTreeWorkbookFile.to_series_rule(basename=basename)

                if series_rule is None:
                    continue


                try:

                    # GTWB ワークブック（.xlsx）ファイルを開く
                    workbook_file_path = f'./{GameTreeWorkbookFilePaths.get_temp_directory_path()}/{basename}'
                    wb = xl.load_workbook(filename=workbook_file_path)

                    # GTWB ワークブック（.xlsx）ファイルの Summary シートの B2 セル（先手勝率）を見る
                    summary_ws = wb['Summary']
                    a_victory_rate = float(summary_ws["B2"].value)      # Ａさん（シリーズを先手で始めた方）が優勝した率
                    b_victory_rate = float(summary_ws["B3"].value)      # Ｂさん（シリーズを後手で始めた方）が優勝した率
                    no_victory_rate = float(summary_ws["B4"].value)     # 優勝が決まらなかった率

                    # victory_rate_detail (VRD) ファイル名を作成する。ファイル名には turn system, failure rate, p が含まれる
                    csv_file_path = VictoryRateDetailFilePaths.as_csv(spec=series_rule.spec)
                    print(f"[{datetime.datetime.now()}] step_oa43o0 {csv_file_path=}")
                    
                    # ファイルが既存ならそれを読取る
                    if os.path.isfile(csv_file_path):
                        df = pd.read_csv(
                                csv_file_path,
                                encoding="utf-8")
                    
                    # ファイルが無ければ新規作成する
                    else:
                        df = pd.DataFrame(columns=['span', 't_step', 'h_step', 'a_victory_rate', 'b_victory_rate', 'no_victory_rate'])


                    # 型設定
                    dtypes = {
                        'span':'int64',
                        't_step':'int64',
                        'h_step':'int64',
                        'a_victory_rate':'float64',
                        'b_victory_rate':'float64',
                        'no_victory_rate':'float64'}
                    df.astype(dtypes)


                    # victory_rate_detail (VRD) ファイルに span, t_step, h_step 毎の先手勝率を記録する
                    # 行の追加
                    df.loc[len(df) + 1] = {
                        'span':series_rule.step_table.span,
                        't_step':series_rule.step_table.get_step_by(face_of_coin=TAIL),
                        'h_step':series_rule.step_table.get_step_by(face_of_coin=HEAD),
                        'a_victory_rate':a_victory_rate,
                        'b_victory_rate':b_victory_rate,
                        'no_victory_rate':no_victory_rate}

                    # Ａさんの優勝率順にソートする
                    df.sort_values(by=['a_victory_rate', 'no_victory_rate', 'span', 't_step', 'h_step'], inplace=True)
                    
                    # FIXME 重複データが無いようにする ----> 効いてない？
                    df.drop_duplicates(inplace=True)

                    # ファイル保存
                    df.to_csv(csv_file_path, index=False)
                    print(f"[{datetime.datetime.now()}] please look `{csv_file_path}`")

                except KeyError as e:
                    message = f"[{datetime.datetime.now()}] ファイルが壊れているかも？ {workbook_csv_file_name=} {csv_file_name=} {e=}"
                    print(message)

                    log_file_path = VictoryRateDetailFilePaths.as_log(spec=spec)
                    with open(log_file_path, 'a', encoding='utf-8') as f:
                        f.write(f"{message}\n")    # ファイルへ出力

                    # １分休む
                    time.sleep(60)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
