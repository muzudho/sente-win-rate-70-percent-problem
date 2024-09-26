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

from library import WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN, make_generation_algorythm, round_letro, calculate_probability
from library.file_paths import get_muzudho_recommends_points_csv_file_path
from library.database import get_df_even, get_df_muzudho_recommends_points, df_mrp_to_csv, get_df_p, append_default_record_to_df_mrp
from library.views import parse_process_element


# とりあえず、ログファイルとして出力する。あとで手動で拡張子を .txt に変えるなどしてください
REPORT_FILE_PATH = 'reports/report_muzudho_recommends_points.log'

OUT_OF_ERROR = 0.51

# 先手勝率が 5割 +-0.03未満なら良い
LIMIT_ERROR = 0.03


def ready_records(df, specified_failure_rate, turn_system):
    """MRPテーブルについて、まず、行の存在チェック。無ければ追加"""
    is_append_new_record = False

    df_p = get_df_p()

    # ［コインを投げて表が出る確率］
    for p in df_p['p']:
        # 存在しなければデフォルトのレコード追加
        if not ((df['p'] == p) & (df['failure_rate'] == specified_failure_rate)).any():
            append_default_record_to_df_mrp(
                    df=df,
                    p=p,
                    failure_rate=specified_failure_rate)
            is_append_new_record = True

    if is_append_new_record:
        # CSV保存
        df_mrp_to_csv(df=df, turn_system=turn_system)


def generate_data(specified_failure_rate, turn_system, generation_algorythm):

    df_ev = get_df_even(turn_system=turn_system, generation_algorythm=generation_algorythm)
    df_mrp = get_df_muzudho_recommends_points(turn_system=turn_system)

    # まず、行の存在チェック。無ければ追加
    ready_records(df=df_mrp, specified_failure_rate=specified_failure_rate, turn_system=turn_system)


    for            p,          failure_rate,          best_p,          best_p_error,          best_number_of_series,          best_p_step,          best_q_step,          best_span,          latest_p,          latest_p_error,          latest_number_of_series,          latest_p_step,          latest_q_step,          latest_span,          process in\
        zip(df_ev['p'], df_ev['failure_rate'], df_ev['best_p'], df_ev['best_p_error'], df_ev['best_number_of_series'], df_ev['best_p_step'], df_ev['best_q_step'], df_ev['best_span'], df_ev['latest_p'], df_ev['latest_p_error'], df_ev['latest_number_of_series'], df_ev['latest_p_step'], df_ev['latest_q_step'], df_ev['latest_span'], df_ev['process']):

        # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
        best_p_step = round_letro(best_p_step)
        best_q_step = round_letro(best_q_step)
        best_span = round_letro(best_span)
        latest_p_step = round_letro(latest_p_step)
        latest_q_step = round_letro(latest_q_step)
        latest_span = round_letro(latest_span)


        # ［計算過程］一覧
        #
        #   NOTE ［計算過程］リストの後ろの方のデータの方が精度が高い
        #   NOTE ［最長対局数］を気にする。長すぎるものは採用しづらい
        #
        if isinstance(process, float):  # nan が入ってる？
            process_list = []
        else:
            process_list = process[1:-1].split('] [')


        #
        #   ［計算過程］が量が多くて調べものをしづらいので、量を減らします。
        #   NOTE ［最小対局数］と［最長対局数］が同じデータもいっぱいあります。その場合、リストの最初に出てきたもの以外は捨てます
        #
        process_element_dict = dict()


        for process_element in process_list:
            p_error, head, tail, span, shortest, longest = parse_process_element(process_element)

            if p_error is not None:
                key = (shortest, longest)
                value = (p_error, head, tail, span, shortest, longest)
                if key not in process_element_dict:
                    process_element_dict[key] = value


        comment_element_list = []
        for key, value in process_element_dict.items():
            p_error, head, tail, span, shortest, longest = value
            comment_element_list.append(f'[{p_error*100+50:.4f} ％（{p_error*100:+.4f}） {head}表 {tail}裏 {span}目 {shortest}～{longest}局]')


        # ［計算過程］列を更新
        df_mrp.loc[df_mrp['p']==p, ['process']] = ' '.join(comment_element_list)


        # CSV保存
        df_mrp_to_csv(df=df_mrp, turn_system=turn_system)


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
#         print(f"""\
# What is the probability of flipping a coin and getting heads?
# Example: 70% is 0.7
# ? """)
#         p = float(input())


        print(f"""\
What is the failure rate?
Example: 10% is 0.1
? """)
        specified_failure_rate = float(input())



        # ［先後固定制］
        generation_algorythm_ft = make_generation_algorythm(failure_rate=specified_failure_rate, turn_system=WHEN_FROZEN_TURN)
        generate_data(specified_failure_rate=specified_failure_rate, turn_system=WHEN_FROZEN_TURN, generation_algorythm=generation_algorythm_ft)

        # ［先後交互制］
        generation_algorythm_at = make_generation_algorythm(failure_rate=specified_failure_rate, turn_system=WHEN_ALTERNATING_TURN)
        generate_data(specified_failure_rate=specified_failure_rate, turn_system=WHEN_ALTERNATING_TURN, generation_algorythm=generation_algorythm_at)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
