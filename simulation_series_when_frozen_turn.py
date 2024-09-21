#
# シミュレーション
# python simulation_series_when_frozen_turn.py
#
#   ［先後固定制］
#   引き分けは考慮していない。
#   表が出る確率（p）が偏ったコインを、指定回数投げる
#

import traceback
import random
import math

import pandas as pd

from library import BLACK, ALICE, PointsConfiguration, play_series_when_frozen_turn, SimulationResultWhenFrozenTurn
from database import get_df_muzudho_recommends_points_when_frozen_turn
from views import stringify_simulation_log


LOG_FILE_PATH = 'output/simulation_series_when_frozen_turn.log'


def simulate(p, number_of_series, points_configuration, title):
    """シミュレート"""

    series_result_ft_list = []

    for round in range(0, number_of_series):
        # ［先後固定制］で、勝った方の手番を返す
        series_result_ft = play_series_when_frozen_turn(
                p=p,
                points_configuration=points_configuration)
        
        series_result_ft_list.append(series_result_ft)


    # シミュレーションの結果
    simulation_result_ft = SimulationResultWhenFrozenTurn(
            series_result_ft_list=series_result_ft_list)

    text = stringify_simulation_log(
            # 出力先ファイルへのパス
            output_file_path=LOG_FILE_PATH,
            # ［表が出る確率］（指定値）
            p=p,
            draw_rate=0,
            # ［かくきんシステムのｐの構成］
            points_configuration=points_configuration,
            # シミュレーションの結果
            simulation_result_ft=simulation_result_ft,
            # タイトル
            title=title)


    print(text) # 表示

    # ログ出力
    with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


    # 表示とログ出力を終えた後でテスト
    if simulation_result_ft.shortest_time_th < points_configuration.count_shortest_time_when_frozen_turn():
        raise ValueError(f"{p=} ［先後固定制］の最短対局数の実際値 {simulation_result_ft.shortest_time_th} が理論値 {points_configuration.count_shortest_time_when_frozen_turn()} を下回った")

    if points_configuration.count_longest_time_when_frozen_turn() < simulation_result_ft.longest_time_th:
        raise ValueError(f"{p=} ［先後固定制］の最長対局数の実際値 {simulation_result_ft.longest_time_th} が理論値 {points_configuration.count_longest_time_when_frozen_turn()} を上回った")


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df_mr_ft = get_df_muzudho_recommends_points_when_frozen_turn()

        # 対局数
        number_of_series = 2_000_000 # 十分多いケース
        #number_of_series = 10 # 少なすぎるケース

        for               p,             b_step,             w_step,             span,             presentable,             comment,             process in\
            zip(df_mr_ft['p'], df_mr_ft['b_step'], df_mr_ft['w_step'], df_mr_ft['span'], df_mr_ft['presentable'], df_mr_ft['comment'], df_mr_ft['process']):

            # ［かくきんシステムのｐの構成］。任意に指定します
            specified_points_configuration = PointsConfiguration(
                    b_step=b_step,
                    w_step=w_step,
                    span=span)

            simulate(
                    p=p,
                    number_of_series=number_of_series,
                    points_configuration=specified_points_configuration,
                    title='（先後固定制）    むずでょセレクション')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
