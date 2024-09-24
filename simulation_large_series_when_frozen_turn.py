#
# シミュレーション
# python simulation_large_series_when_frozen_turn.py
#
#   ［先後固定制］
#   表が出る確率（p）が偏ったコインを、指定回数投げる
#

import traceback

from library import WHEN_FROZEN_TURN, Specification, PointsConfiguration, judge_series, LargeSeriesTrialSummary, PseudoSeriesResult
from file_paths import get_simulation_large_series_file
from database import get_df_muzudho_recommends_points
from views import stringify_simulation_log


# 引き分けになる確率
#FAILURE_RATE = 0.0
FAILURE_RATE = 0.1

# 対局数
#NUMBER_OF_SERIES = 2_000_000 # 十分多いケース
NUMBER_OF_SERIES = 20_000
#NUMBER_OF_SERIES = 10 # 少なすぎるケース


def simulate_stats(spec, number_of_series, pts_conf, title, turn_system):
    """大量のシリーズをシミュレートします
    
    Parameters
    ----------
    spec : Specification
        ［仕様］
    """

    series_result_list = []

    # ［最長対局数］は計算で求められます
    longest_times = pts_conf.number_longest_time(turn_system=turn_system)

    for round in range(0, number_of_series):

        # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
        pseudo_series_result = PseudoSeriesResult.playout_pseudo(
                p=spec.p,
                failure_rate=FAILURE_RATE,
                longest_times=longest_times)

        # シリーズの結果を返す
        series_result = judge_series(
                pseudo_series_result=pseudo_series_result,
                pts_conf=pts_conf,
                turn_system=turn_system)
        
        series_result_list.append(series_result)


    # シミュレーションの結果
    large_series_trial_summary = LargeSeriesTrialSummary(
            series_result_list=series_result_list)

    text = stringify_simulation_log(
            # ［表が出る確率］（指定値）
            p=spec.p,
            # ［表も裏も出ない率］
            failure_rate=FAILURE_RATE,
            # ［先後運用制度］
            turn_system=turn_system,
            # ［かくきんシステムのｐの構成］
            pts_conf=pts_conf,
            # シミュレーションの結果
            large_series_trial_summary=large_series_trial_summary,
            # タイトル
            title=title)

    print(text) # 表示

    # ログ出力
    with open(get_simulation_large_series_file(
            p=p,
            failure_rate=FAILURE_RATE,
            turn_system=WHEN_FROZEN_TURN), 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


    # 表示とログ出力を終えた後でテスト
    if large_series_trial_summary.shortest_time_th < pts_conf.number_shortest_time(turn_system=turn_system):
        raise ValueError(f"{spec.p=} ［先後固定制］の最短対局数の実際値 {large_series_trial_summary.shortest_time_th} が理論値 {pts_conf.number_shortest_time(turn_system=turn_system)} を下回った")

    if pts_conf.number_longest_time(turn_system=turn_system) < large_series_trial_summary.longest_time_th:
        raise ValueError(f"{spec.p=} ［先後固定制］の最長対局数の実際値 {large_series_trial_summary.longest_time_th} が理論値 {pts_conf.number_longest_time(turn_system=turn_system)} を上回った")


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df_mr = get_df_muzudho_recommends_points(turn_system=WHEN_FROZEN_TURN)

        for            p,          b_step,          w_step,          span,          presentable,          comment,          process in\
            zip(df_mr['p'], df_mr['b_step'], df_mr['w_step'], df_mr['span'], df_mr['presentable'], df_mr['comment'], df_mr['process']):

            # 仕様
            spec = Specification(
                    p=p,
                    failure_rate=FAILURE_RATE,
                    turn_system=WHEN_FROZEN_TURN)

            # ［かくきんシステムのｐの構成］。任意に指定します
            specified_points_configuration = PointsConfiguration(
                    failure_rate=FAILURE_RATE,
                    b_step=b_step,
                    w_step=w_step,
                    span=span)

            simulate_stats(
                    spec=spec,
                    number_of_series=NUMBER_OF_SERIES,
                    pts_conf=specified_points_configuration,
                    title='（先後固定制）    むずでょセレクション',
                    turn_system=spec.turn_system)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
