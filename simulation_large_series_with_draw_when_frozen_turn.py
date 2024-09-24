#
# シミュレーション
# python simulation_large_series_with_draw_when_frozen_turn.py
#
#   引分けルールを考えるのに使っている
#

import traceback
import random
import math

import pandas as pd

from library import EMPTY, HEAD, TAIL, WHEN_FROZEN_TURN, Specification, round_letro, PointsConfiguration, PseudoSeriesResult, judge_series_when_frozen_turn, play_tie_break, LargeSeriesTrialSummary
from database import get_df_muzudho_recommends_points_when_frozen_turn
from views import stringify_simulation_log


LOG_FILE_PATH = 'output/simulation_large_series_when_frozen_turn.log'

# 引き分けになる確率
#FAILURE_RATE = 0.1
FAILURE_RATE = 0.9


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

    for series_num in range(0, number_of_series):

        # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
        pseudo_series_result = PseudoSeriesResult.playout_pseudo(
                p=spec.p,
                failure_rate=FAILURE_RATE,
                longest_times=longest_times)

        # ［先後固定制］で、シリーズを勝った方の手番を返す。引き分けを１局と数える
        series_result = judge_series_when_frozen_turn(
                pseudo_series_result=pseudo_series_result,
                pts_conf=pts_conf)
        
        series_result_list.append(series_result)

        # 引き分けを１局と数えると、シリーズの中で点数が足らず、決着が付かず、シリーズ全体としての引き分けが増えるので、対応が必要です
        #
        # # # NOTE ルールとして、引き分けを廃止することはできるか？ ----> 両者の実力が等しく、先手後手の有利も等しいとき、真の結果は引き分けがふさわしい。引き分けを消すことはできない
        # # #
        # # # NOTE その場合、先手勝利でいいのでは？ ----> 引き分け率１０％のとき、先手にしろ後手にしろ、そっちの勝率が５％上がってしまった。［目標の点数］を２倍にしてもだいたい同じ
        # # # NOTE 点数が引き分けということは、［最長対局数］を全部引き分けだったということです。引き分けが先手勝ちとか、後手勝ちと決めてしまうと、対局数が１のとき、影響がもろに出てしまう
        # # # NOTE 点数が引き分けのとき、最後に勝った方の勝ちとすればどうなる？ ----> 先手の方が勝つ機会が多いのでは？
        # # # NOTE 引き分けは［両者得点］にしたらどうか？ ----> step を足すのは裏番に有利すぎる。１点を足すのは数学的に意味がない。
        # # # NOTE 引き分けは［両者得点］にし、かつ、引き分けが奇数回なら後手勝ち、偶数回なら先手勝ちにしたらどうか？ ----> 対局数が１のときの影響がでかい
        # # # NOTE 引き分けは、［表勝ち１つの点数］が小さい表番の方に大きく響く？
        # # # NOTE 引き分けは減らせるが、ゼロにはできない、という感じ
        # NOTE タイブレークは、［将棋の引分け率］が上がってきたとき調整が困難。当然、引き分け率が上がるほど裏有利になる


    # シミュレーションの結果
    large_series_trial_summary = LargeSeriesTrialSummary(
            series_result_list=series_result_list)

    text = stringify_simulation_log(
            # ［表が出る確率］（指定値）
            p=spec.p,
            # ［引き分ける確率］
            failure_rate=FAILURE_RATE,
            # ［先後運用制度］
            turn_system=WHEN_FROZEN_TURN,
            # ［かくきんシステムのｐの構成］
            pts_conf=pts_conf,
            # シミュレーションの結果
            large_series_trial_summary=large_series_trial_summary,
            # タイトル
            title=title)


    print(text) # 表示

    # ログ出力
    with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


    # 表示とログ出力を終えた後でテスト
    #
    #   FIXME ［引き分けを１局として数えるケース］では、対局数の計算がまだ実装できていません
    #
    print("［引き分けを１局として数えるケース］では、対局数の計算がまだ実装できていません")


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

            #
            #   NOTE ［目標の点数］を整数倍すると、最小公倍数が何回も出てきて、引き分けになる回数も整数倍になるから、引き分けが増えるデメリットがある
            #

            # 仕様
            spec = Specification(
                    p=p,
                    failure_rate=FAILURE_RATE,
                    turn_system=WHEN_FROZEN_TURN)

            # ［かくきんシステムのｐの構成］           
            print("確率調整中")  # FIXME
            pts_conf = PointsConfiguration(
                    failure_rate=FAILURE_RATE,
                    b_step=b_step,
                    w_step=w_step,
                    span=span)

            simulate_stats(
                    spec=spec,
                    number_of_series=number_of_series,
                    pts_conf=pts_conf,
                    title='むずでょセレクション',
                    turn_system=turn_system)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
