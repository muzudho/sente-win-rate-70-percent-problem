#
# 生成
# python generate_muzudho_recommends_points_data.py
#
#   TODO むずでょが推奨する［かくきんシステムのｐの構成］一覧の各種 CSV を生成する。
#

import traceback
import datetime
import random
import math
import pandas as pd

from library import round_letro, calculate_probability, PointsConfiguration
from views import stringify_report_muzudho_recommends_points_ft, stringify_report_muzudho_recommends_points_at


# とりあえず、ログファイルとして出力する。あとで手動で拡張子を .txt に変えるなどしてください
REPORT_FILE_PATH = 'reports/report_muzudho_recommends_points.log'

CSV_FILE_PATH_AT = './data/generate_even_when_alternating_turn.csv'
CSV_FILE_PATH_FT = './data/generate_even_when_frozen_turn.csv'
CSV_FILE_PATH_MR_AT = './data/muzudho_recommends_points_when_alternating_turn.csv'
CSV_FILE_PATH_MR_FT = './data/muzudho_recommends_points_when_frozen_turn.csv'


OUT_OF_ERROR = 0.51

# 先手勝率が 5割 +-0.03未満なら良い
LIMIT_ERROR = 0.03


def generate_when_alternating_turn():
    """［先後交互制］"""

    df_at = pd.read_csv(CSV_FILE_PATH_AT, encoding="utf8")
    df_mr_at = pd.read_csv(CSV_FILE_PATH_MR_AT, encoding="utf8")

    for            p,          best_p,          best_p_error,          best_round_count,          best_b_step,          best_w_step,          best_span,          latest_p,          latest_p_error,          latest_round_count,          latest_b_step,          latest_w_step,          latest_span,          process in\
        zip(df_at['p'], df_at['best_p'], df_at['best_p_error'], df_at['best_round_count'], df_at['best_b_step'], df_at['best_w_step'], df_at['best_span'], df_at['latest_p'], df_at['latest_p_error'], df_at['latest_round_count'], df_at['latest_b_step'], df_at['latest_w_step'], df_at['latest_span'], df_at['process']):

        # # ［計算過程］
        # process_list = process[1:-1].split('] [')

        # #   NOTE ［計算過程］リストの後ろの方のデータの方が精度が高い
        # #   NOTE ［最長対局数］を気にする。長すぎるものは採用しづらい
        # # 指定した精度のもの。［先手勝ち１つの点数］、［後手勝ち１つの点数］、［目標の点数］を指定。
        # for process_element in process_list:
        #     p_error, black, white, span, shortest, longest = parse_process_element(process_element)

        #     if p_error is not None:
        #         return f"先手勝率 {seg_1:2.0f} ％ --調整後--> {p_error*100+50:7.4f} ％（{p_error*100:+8.4f}）   先手勝ち{black:>3}点、後手勝ち{white:>3}点、目標{span:>3}点    {shortest:>3}～{longest:>3}局（先後交互制）    試行{seg_2c}回"


        # ［コメント］列を更新
        df_mr_at.loc[df_mr_at['p']==p, ['comment']] = process

        # CSV保存
        df_mr_at.to_csv(CSV_FILE_PATH_MR_AT,
                # ［計算過程］列は長くなるので末尾に置きたい
                columns=['p', 'b_step', 'w_step', 'span', 'comment'],
                index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた


        # # ［かくきんシステムのｐの構成］。任意に指定します
        # points_configuration = PointsConfiguration(
        #         b_step=df_mr_at.loc[df_mr_at['p']==p, ['b_step']].iat[0,0],
        #         w_step=df_mr_at.loc[df_mr_at['p']==p, ['w_step']].iat[0,0],
        #         span=df_mr_at.loc[df_mr_at['p']==p, ['span']].iat[0,0])

        # # 文言の作成
        # text = stringify_report_muzudho_recommends_points_at(
        #         p=p,
        #         best_round_count=best_round_count,
        #         specified_points_configuration=points_configuration,    # TODO 任意のポイントを指定したい
        #         process=process)
        # print(text) # 表示

        # with open(REPORT_FILE_PATH, 'a', encoding='utf8') as f:
        #     f.write(f"{text}\n")    # ログファイルへ出力


def generate_when_frozen_turn():
    """［先後固定制］"""

    df_mr_ft = pd.read_csv(CSV_FILE_PATH_MR_FT, encoding="utf8")
    df_ft = pd.read_csv(CSV_FILE_PATH_FT, encoding="utf8")

    for            p,          best_p,          best_p_error,          best_round_count,          best_b_step,          best_w_step,          best_span,          latest_p,          latest_p_error,          latest_round_count,          latest_b_step,          latest_w_step,          latest_span,          process in\
        zip(df_ft['p'], df_ft['best_p'], df_ft['best_p_error'], df_ft['best_round_count'], df_ft['best_b_step'], df_ft['best_w_step'], df_ft['best_span'], df_ft['latest_p'], df_ft['latest_p_error'], df_ft['latest_round_count'], df_ft['latest_b_step'], df_ft['latest_w_step'], df_ft['latest_span'], df_ft['process']):

        # ［コメント］列を更新
        df_mr_ft.loc[df_mr_ft['p']==p, ['comment']] = process

        # CSV保存
        df_mr_ft.to_csv(CSV_FILE_PATH_MR_FT,
                # ［計算過程］列は長くなるので末尾に置きたい
                columns=['p', 'b_step', 'w_step', 'span', 'comment'],
                index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた

        # # ［かくきんシステムのｐの構成］。任意に指定します
        # points_configuration = PointsConfiguration(
        #         b_step=df_mr_ft.loc[df_mr_ft['p']==p, ['b_step']].iat[0,0],
        #         w_step=df_mr_ft.loc[df_mr_ft['p']==p, ['w_step']].iat[0,0],
        #         span=df_mr_ft.loc[df_mr_ft['p']==p, ['span']].iat[0,0])

        # # 文言の作成
        # text = stringify_report_muzudho_recommends_points_ft(
        #         p=p,
        #         best_round_count=best_round_count,
        #         specified_points_configuration=points_configuration,    # TODO 任意のポイントを指定したい
        #         process=process)
        # print(text) # 表示

        # with open(REPORT_FILE_PATH, 'a', encoding='utf8') as f:
        #     f.write(f"{text}\n")    # ログファイルへ出力


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［先後交互制］
        generate_when_alternating_turn()

        # ［先後固定制］
        generate_when_frozen_turn()


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
