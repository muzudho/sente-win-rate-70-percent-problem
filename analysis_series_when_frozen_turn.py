#
# 分析
# python analysis_series_when_frozen_turn.py
#
#   ［先後固定制］
#   表が出る確率（p）が偏ったコインを、指定回数投げる
#

import traceback
import random
import math

import pandas as pd

from library import HEAD, TAIL, ALICE, PointsConfiguration, PseudoSeriesResult, judge_series_when_frozen_turn, LargeSeriesTrialSummary, make_all_pseudo_series_results_when_frozen_turn
from database import get_df_muzudho_single_points_when_frozen_turn
from views import stringify_series_log, stringify_analysis_series_when_frozen_turn


LOG_FILE_PATH = 'output/analysis_series_when_frozen_turn.log'

# 引き分けになる確率
FAILURE_RATE = 0.0     # 引分けなし
#FAILURE_RATE = 10.0     # １０％。コンピュータ将棋など


def analysis_series(series_result, p, pts_conf, title):
    """シリーズ１つを分析します
    
    Parameters
    ----------
    pts_conf : PointsConfiguration
        ［勝ち点ルール］の構成
    """

    text = stringify_series_log(
            # ［表が出る確率］（指定値）
            p=p,
            failure_rate=FAILURE_RATE,
            # ［かくきんシステムのｐの構成］
            pts_conf=pts_conf,
            # シリーズの結果
            series_result=series_result,
            # タイトル
            title=title)


    print(text) # 表示

    # ログ出力
    with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df_mr_ft = get_df_muzudho_single_points_when_frozen_turn()

        for               p,             b_step,             w_step,             span,             presentable,             comment,             process in\
            zip(df_mr_ft['p'], df_mr_ft['b_step'], df_mr_ft['w_step'], df_mr_ft['span'], df_mr_ft['presentable'], df_mr_ft['comment'], df_mr_ft['process']):

            # ［かくきんシステムのｐの構成］。任意に指定します
            specified_points_configuration = PointsConfiguration(
                    failure_rate=FAILURE_RATE,
                    b_step=b_step,
                    w_step=w_step,
                    span=span)


            series_result_list = []

            # FIXME 動作テスト
            stats_result_data = make_all_pseudo_series_results_when_frozen_turn(
                    can_draw=False,
                    pts_conf=specified_points_configuration)
            for successful_color_list in stats_result_data:
                #print(f"動作テスト {successful_color_list=}")

                pseudo_series_result = PseudoSeriesResult(
                        p=None,                 # FIXME 未設定
                        failure_rate=FAILURE_RATE,
                        longest_times=specified_points_configuration.number_longest_time_when_frozen_turn,
                        successful_color_list=successful_color_list)

                #
                # 到達できない棋譜は除去しておきたい
                #

                old_number_of_times = len(successful_color_list)

                # ［先後固定制］で、シリーズを勝った方の手番を返す
                series_result = judge_series_when_frozen_turn(
                        pseudo_series_result=pseudo_series_result,
                        pts_conf=specified_points_configuration)

                if series_result.number_of_all_times < old_number_of_times:
                    # 棋譜の長さが短くなったということは、到達できない記録が混ざっていたということです。
                    #print(f"到達できない棋譜を除去 {series_result.number_of_all_times=}  {old_number_of_times=}")
                    pass

                elif old_number_of_times < specified_points_configuration.number_shortest_time_when_frozen_turn:
                    # 棋譜の長さが足りていないということは、最後までプレイしていない
                    #print(f"最後までプレイしていない棋譜を除去 {old_number_of_times=}  {specified_points_configuration.number_shortest_time_when_frozen_turn=}")
                    pass

                #
                # 引分け不可のときに、［最短対局数］までプレイして［目標の点数］へ足りていない棋譜が混ざっているなら、除去したい
                #
                elif FAILURE_RATE == 0.0 and series_result.is_no_won(HEAD, TAIL):
                    #print(f"引分け不可のときに、［最短対局数］までプレイして［目標の点数］へ足りていない棋譜が混ざっているなら、除去 {FAILURE_RATE=}")
                    pass

                else:
                    series_result_list.append(series_result)

            # 表示
            print(stringify_analysis_series_when_frozen_turn(
                    p=p,
                    failure_rate=FAILURE_RATE,
                    series_result_list=series_result_list))

            for series_result in series_result_list:
                analysis_series(
                        series_result=series_result,
                        p=p,
                        pts_conf=specified_points_configuration,
                        title='（先後固定制）    むずでょセレクション')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
