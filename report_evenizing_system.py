#
# レポート作成
# python report_evenizing_system.py
#
#   ［黒勝ち１つの点数］、［白勝ち１つの点数］、［目標の点数］をテキストにまとめる。
#

import traceback
import datetime
import random
import math
import pandas as pd

from library import round_letro, calculate_probability, PointsConfiguration
from views import stringify_when_report_evenizing_system_ft, stringify_when_report_evenizing_system_at


# とりあえず、ログファイルとして出力する。あとで手動で拡張子を .txt に変えるなどしてください
REPORT_FILE_PATH = 'reports/report_evenizing_system.log'

#CSV_FILE_PATH_P = "./data/p.csv"
#CSV_FILE_PATH_EVEN = './data/report_evenizing_system.csv'
CSV_FILE_PATH_SP_FT = './data/specified_points_when_frozen_turn.csv'
CSV_FILE_PATH_SP_AT = './data/specified_points_when_alternating_turn.csv'
CSV_FILE_PATH_FT = './data/generate_even_when_frozen_turn.csv'
CSV_FILE_PATH_AT = './data/generate_even_when_alternating_turn.csv'


OUT_OF_ERROR = 0.51

# 先手勝率が 5割 +-0.03未満なら良い
LIMIT_ERROR = 0.03


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        #df_p = pd.read_csv(CSV_FILE_PATH_P, encoding="utf8")
        df_sp_at = pd.read_csv(CSV_FILE_PATH_SP_AT, encoding="utf8")
        df_sp_ft = pd.read_csv(CSV_FILE_PATH_SP_FT, encoding="utf8")
        df_at = pd.read_csv(CSV_FILE_PATH_AT, encoding="utf8")
        df_ft = pd.read_csv(CSV_FILE_PATH_FT, encoding="utf8")
        #df_even = pd.read_csv(CSV_FILE_PATH_EVEN, encoding="utf8")

        # ［先後交互制］
        for            p,          best_p,          best_p_error,          best_round_count,          best_b_step,          best_w_step,          best_span,          latest_p,          latest_p_error,          latest_round_count,          latest_b_step,          latest_w_step,          latest_span,          process in\
            zip(df_at['p'], df_at['best_p'], df_at['best_p_error'], df_at['best_round_count'], df_at['best_b_step'], df_at['best_w_step'], df_at['best_span'], df_at['latest_p'], df_at['latest_p_error'], df_at['latest_round_count'], df_at['latest_b_step'], df_at['latest_w_step'], df_at['latest_span'], df_at['process']):
            with open(REPORT_FILE_PATH, 'a', encoding='utf8') as f:

                # ［勝ち点ルール］の構成。任意に指定します
                points_configuration = PointsConfiguration(
                        b_step=df_sp_at.loc[df_sp_at['p']==p, ['b_step']].iat[0,0],
                        w_step=df_sp_at.loc[df_sp_at['p']==p, ['w_step']].iat[0,0],
                        span=df_sp_at.loc[df_sp_at['p']==p, ['span']].iat[0,0])

                # 文言の作成
                text = stringify_when_report_evenizing_system_at(
                        p=p,
                        best_p=best_p,
                        best_p_error=best_p_error,
                        best_round_count=best_round_count,
                        specified_points_configuration=points_configuration,    # TODO 任意のポイントを指定したい
                        process=process)
                print(text) # 表示
                f.write(f"{text}\n")    # ログファイルへ出力

        # ［先後固定制］
        for            p,          best_p,          best_p_error,          best_round_count,          best_b_step,          best_w_step,          best_span,          latest_p,          latest_p_error,          latest_round_count,          latest_b_step,          latest_w_step,          latest_span,          process in\
            zip(df_ft['p'], df_ft['best_p'], df_ft['best_p_error'], df_ft['best_round_count'], df_ft['best_b_step'], df_ft['best_w_step'], df_ft['best_span'], df_ft['latest_p'], df_ft['latest_p_error'], df_ft['latest_round_count'], df_ft['latest_b_step'], df_ft['latest_w_step'], df_ft['latest_span'], df_ft['process']):
            with open(REPORT_FILE_PATH, 'a', encoding='utf8') as f:

                # ［勝ち点ルール］の構成。任意に指定します
                points_configuration = PointsConfiguration(
                        b_step=df_sp_ft.loc[df_sp_ft['p']==p, ['b_step']].iat[0,0],
                        w_step=df_sp_ft.loc[df_sp_ft['p']==p, ['w_step']].iat[0,0],
                        span=df_sp_ft.loc[df_sp_ft['p']==p, ['span']].iat[0,0])

                # 文言の作成
                text = stringify_when_report_evenizing_system_ft(
                        p=p,
                        best_p=best_p,
                        best_p_error=best_p_error,
                        best_round_count=best_round_count,
                        specified_points_configuration=points_configuration,    # TODO 任意のポイントを指定したい
                        process=process)
                print(text) # 表示
                f.write(f"{text}\n")    # ログファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
