#
# 分析
# python create_a_csv_to_data_score_board.py
#
#   １シリーズのコインの出目について、全パターン網羅した表を作成します
#

import traceback
import os
import time
import datetime
import pandas as pd

from library import HEAD, TAIL, ALICE, FROZEN_TURN, ALTERNATING_TURN, TERMINATED, YIELD, CONTINUE, OUT_OF_UPPER_SPAN, UPPER_LIMIT_FAILURE_RATE, Converter, Specification, SeriesRule, is_almost_even
from library.file_paths import get_score_board_data_csv_file_path
from library.score_board import search_all_score_boards
from library.database import ScoreBoardDataTable


# CSV保存用タイマー
start_time_for_save = None
number_of_dirty = 0         # ファイルを新規作成したときに 1、レコードを１件追加したときも 1 増える
number_of_skip = 0          # 既存データをスキップした数

# FIXME この数も、オーバーヘッドが減るように自動調整したい。
#
#   NOTE failure_rate が増えて upper_limit_coins が増えれば、かかる時間も増えていくし。 failure_rate は 70% までにするか？
#
# CSV保存間隔（秒）、またはタイムシェアリング間隔
INTERVAL_SECONDS_FOR_SAVE_CSV = 3   # 2



def automatic_in_loop(df, spec, span, t_step, h_step, depth):
    """
    Returns
    -------
    calculation_status : int
        計算状況
    depth : int
        探索の深さ
    """

    # CSV保存用タイマー
    global start_time_for_save, number_of_dirty, number_of_skip

    turn_system_str = Converter.turn_system_to_code(spec.turn_system)

    # 指定間隔（秒）でループを抜ける
    end_time_for_save = time.time()
    if INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - start_time_for_save:
        start_time_for_save = end_time_for_save

        # 計算未停止だが、譲る（タイムシェアリング）
        return YIELD


    # FIXME 便宜的に［試行シリーズ数］は 1 固定
    trials_series = 1

    # ［シリーズ・ルール］
    specified_series_rule = SeriesRule.make_series_rule_base(
            spec=spec,
            trials_series=trials_series,
            h_step=h_step,
            t_step=t_step,
            span=span)


    if depth < specified_series_rule.upper_limit_coins:
        # 計算未停止だが、譲る（タイムシェアリング）
        return YIELD


    # 該当レコードのキー
    key = (df['turn_system']==turn_system_str) & (df['failure_rate']==spec.failure_rate) & (df['p']==spec.p) & (df['span']==specified_series_rule.step_table.span) & (df['t_step']==specified_series_rule.step_table.get_step_by(face_of_coin=TAIL)) & (df['h_step']==specified_series_rule.step_table.get_step_by(face_of_coin=HEAD))

    # データが既存なら
    if key.any():

        # イーブンが見つかっているなら、探索打ち切り
        if is_almost_even(df.loc[key, ['a_win_rate']].iat[0, 0]):
            print(f"[{datetime.datetime.now()}][failure_rate={spec.failure_rate:.2f}  p={p:.2f}  turn_system={turn_system_str:11}] even!   {span=:2}  {t_step=:2}  {h_step=:2}  shortest_coins={specified_series_rule.shortest_coins}  upper_limit_coins={specified_series_rule.upper_limit_coins}")
            return TERMINATED


        # スキップ
        number_of_skip += 1
        return CONTINUE


    def on_score_board_created(score_board):
        pass

    # 確率を求める
    three_rates, all_patterns_p = search_all_score_boards(
            series_rule=specified_series_rule,
            on_score_board_created=on_score_board_created)

    # データフレーム更新
    # 新規レコード追加
    ScoreBoardDataTable.append_new_record(
            df=df,
            turn_system_str=turn_system_str,
            failure_rate=failure_rate,
            p=p,
            span=span,
            t_step=t_step,
            h_step=h_step,
            shortest_coins=specified_series_rule.shortest_coins,
            upper_limit_coins=specified_series_rule.upper_limit_coins,
            three_rates=three_rates)

    number_of_dirty += 1

    # イーブンが見つかっているなら、探索打ち切り
    if three_rates.is_even:
        print(f"[{datetime.datetime.now()}][failure_rate={spec.failure_rate:.2f}  p={p:.2f}  turn_system={turn_system_str:11}] even!   {span=:2}  {t_step=:2}  {h_step=:2}  shortest_coins={specified_series_rule.shortest_coins}  upper_limit_coins={specified_series_rule.upper_limit_coins}")
        return TERMINATED


    return CONTINUE


def automatic(spec, depth):
    """
    Parameters
    ----------
    depth : int
        探索の深さ

    Returns
    -------
    df : DataFrame
        データフレーム
    calculation_status : int
        計算状況
    span : int
        計算終了時の span
    """

    global start_time_for_save, number_of_dirty, number_of_skip

    turn_system_str = Converter.turn_system_to_code(spec.turn_system)

    df, is_new = ScoreBoardDataTable.read_df(spec=spec, new_if_it_no_exists=True)


    # ファイルが存在せず、空データフレームが新規作成されたら
    if is_new:

        # ループカウンター
        span = 1        # ［目標の点数］
        t_step = 1      # ［後手で勝ったときの勝ち点］
        h_step = 1      # ［先手で勝ったときの勝ち点］

        print(f"[{datetime.datetime.now()}][failure_rate={spec.failure_rate:.2f}  p={spec.p:.2f}  turn_system={turn_system_str:11}] new file  {depth=}")

        # １件も処理してないが、ファイルを保存したいのでフラグを立てる
        number_of_dirty += 1

    # ファイルが存在して、読み込まれたなら
    else:
        # ループカウンター
        if len(df) < 1:
            span = 1        # ［目標の点数］
            t_step = 1      # ［後手で勝ったときの勝ち点］
            h_step = 1      # ［先手で勝ったときの勝ち点］

        else:
            # 途中まで処理が終わってるんだったら、途中から再開したいが。ループの途中から始められるか？

            # TODO 最後に処理された span は？
            span = int(df['span'].max())

            # TODO 最後に処理された span のうち、最後に処理された t_step は？
            t_step = int(df.loc[df['span']==span, 't_step'].max())

            # TODO 最後に処理された span, t_step のうち、最後に処理された h_step は？
            h_step = int(df.loc[(df['span']==span) & (df['t_step']==t_step), 'h_step'].max())

            print(f"[{datetime.datetime.now()}][failure_rate={spec.failure_rate:.2f}  p={p:.2f}  turn_system={turn_system_str:11}] restart {span=:2}  {t_step=:2}  {h_step=:2}  {depth=}")


    while span < OUT_OF_UPPER_SPAN + 1:

        calculation_status = automatic_in_loop(
                df=df,
                spec=spec,
                span=span,
                t_step=t_step,
                h_step=h_step,
                depth=depth)

        if calculation_status in [TERMINATED, YIELD]:
            return df, calculation_status, span

        # カウントアップ
        h_step += 1
        if t_step < h_step:
            h_step = 1
            t_step += 1
            if span < t_step:
                t_step = 1
                span += 1


    # 探索範囲内に見つからなかった。計算途中
    return df, CONTINUE, span


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # upper_limit_coins がツリー構造の深さに関わってくるので、これを反復深化探索にしたい
        depth = 0

        # 計算停止していない数（ループに入るために最初の１回はダミー値）
        # 時間を譲ったか、計算続行中の数
        number_of_not_terminated = 1

        while number_of_not_terminated != 0:

            depth += 1
            print(f"search {depth=} ...")

            # リセット
            number_of_not_terminated = 0

            # ［将棋の引分け率］
            for failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5): # 5％刻み。 100%は除く。0除算が発生するので
                failure_rate = failure_rate_percent / 100

                # ［将棋の先手勝率］
                for p_percent in range(50, 96):
                    p = p_percent / 100

                    # ［先後の決め方］
                    for turn_system in [ALTERNATING_TURN, FROZEN_TURN]:

                        # リセット
                        number_of_dirty = 0
                        number_of_skip = 0

                        # CSV保存用タイマー
                        start_time_for_save = time.time()


                        # 仕様
                        spec = Specification(
                                p=p,
                                failure_rate=failure_rate,
                                turn_system=turn_system)

                        df, calculation_status, span = automatic(
                                spec=spec,
                                depth=depth)


                        # 変更があれば保存
                        if 0 < number_of_dirty:
                            # CSVファイルへ書き出し
                            csv_file_path_to_wrote = ScoreBoardDataTable.to_csv(df, spec)

                            turn_system_str = Converter.turn_system_to_code(spec.turn_system)
                            print(f"[{datetime.datetime.now()}][failure_rate={spec.failure_rate:.2f}  p={p:.2f}  turn_system={turn_system_str:11}]  dirty={number_of_dirty}  skip={number_of_skip}  {calculation_status=}  write file to `{csv_file_path_to_wrote}` ...")


                        if calculation_status != TERMINATED:
                            number_of_not_terminated += 1


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
