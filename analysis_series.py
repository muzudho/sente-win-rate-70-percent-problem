#
# 分析
# python analysis_series.py
#
#   ［先後固定制］
#   表が出る確率（p）が偏ったコインを、指定回数投げる
#

import traceback
import random
import math

import pandas as pd

from library import HEAD, TAIL, ALICE, FACE_OF_COIN, WHEN_FROZEN_TURN, Specification, PointsConfiguration, PseudoSeriesResult, judge_series, LargeSeriesTrialSummary, make_all_pseudo_series_results
from file_paths import get_analysis_series_log_file_path
from database import get_df_muzudho_single_points
from views import stringify_series_log, stringify_analysis_series


# 引き分けになる確率
FAILURE_RATE = 0.0     # 引分けなし
#FAILURE_RATE = 10.0     # １０％。コンピュータ将棋など


def analysis_series(series_result, spec, pts_conf, title, turn_system):
    """シリーズ１つを分析します
    
    Parameters
    ----------
    spec : Specification
        ［仕様］
    pts_conf : PointsConfiguration
        ［勝ち点ルール］の構成
    """

    text = stringify_series_log(
            # ［表が出る確率］（指定値）
            p=spec.p,
            failure_rate=FAILURE_RATE,
            # ［かくきんシステムのｐの構成］
            pts_conf=pts_conf,
            # シリーズの結果
            series_result=series_result,
            # タイトル
            title=title,
            turn_system=turn_system)


    print(text) # 表示

    # ログ出力
    with open(get_analysis_series_log_file_path(turn_system=turn_system), 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        print(f"""\
(1) Frozen turn
(2) Alternating turn
Which one(1-2)? """)

        choice = input()

        if choice == '1':
            turn_system = WHEN_FROZEN_TURN

        elif choice == '2':
            turn_system = WHEN_ALTERNATING_TURN

        else:
            raise ValueError(f"{choice=}")


        df_mr = get_df_muzudho_single_points(turn_system=turn_system)

        for            p,          p_step,          q_step,          span,          presentable,          comment,          process in\
            zip(df_mr['p'], df_mr['p_step'], df_mr['q_step'], df_mr['span'], df_mr['presentable'], df_mr['comment'], df_mr['process']):

            # 仕様
            spec = Specification(
                    p=p,
                    failure_rate=FAILURE_RATE,
                    turn_system=turn_system)

            # ［かくきんシステムのｐの構成］。任意に指定します
            specified_pts_conf = PointsConfiguration(
                    failure_rate=FAILURE_RATE,
                    turn_system=turn_system,
                    p_step=p_step,
                    q_step=q_step,
                    span=span)


            series_result_list = []

            # FIXME 動作テスト
            stats_result_data = make_all_pseudo_series_results(
                    can_failure=False,
                    pts_conf=specified_pts_conf)
            
            for face_of_coin_list in stats_result_data:
                #print(f"動作テスト {face_of_coin_list=}")

                pseudo_series_result = PseudoSeriesResult(
                        p=None,                 # FIXME 未設定
                        failure_rate=FAILURE_RATE,
                        longest_times=specified_pts_conf.number_longest_time(),
                        face_of_coin_list=face_of_coin_list)

                #
                # 到達できない棋譜は除去しておきたい
                #

                old_number_of_times = len(face_of_coin_list)

                # ［先後固定制］で、シリーズを勝った方の手番を返す
                series_result = judge_series(
                        pseudo_series_result=pseudo_series_result,
                        pts_conf=specified_pts_conf,
                        turn_system=turn_system)

                if series_result.number_of_times < old_number_of_times:
                    # 棋譜の長さが短くなったということは、到達できない記録が混ざっていたということです。
                    #print(f"到達できない棋譜を除去 {series_result.number_of_times=}  {old_number_of_times=}")
                    pass

                elif old_number_of_times < specified_pts_conf.number_shortest_time():
                    # 棋譜の長さが足りていないということは、最後までプレイしていない
                    #print(f"最後までプレイしていない棋譜を除去 {old_number_of_times=}  {specified_pts_conf.number_shortest_time()=}")
                    pass

                #
                # 引分け不可のときに、［最短対局数］までプレイして［目標の点数］へ足りていない棋譜が混ざっているなら、除去したい
                #
                elif FAILURE_RATE == 0.0 and series_result.is_no_won(opponent_pair=FACE_OF_COIN):
                    #print(f"引分け不可のときに、［最短対局数］までプレイして［目標の点数］へ足りていない棋譜が混ざっているなら、除去 {FAILURE_RATE=}")
                    pass

                else:
                    series_result_list.append(series_result)

            # 表示
            print(stringify_analysis_series(
                    p=p,
                    failure_rate=FAILURE_RATE,
                    series_result_list=series_result_list,
                    turn_system=turn_system))

            for series_result in series_result_list:
                analysis_series(
                        series_result=series_result,
                        spec=spec,
                        pts_conf=specified_pts_conf,
                        title='（先後固定制）    むずでょセレクション',
                        turn_system=turn_system)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
