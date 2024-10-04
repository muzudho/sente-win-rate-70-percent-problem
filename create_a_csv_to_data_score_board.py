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

from library import HEAD, TAIL, ALICE, FROZEN_TURN, ALTERNATING_TURN, TERMINATED, YIELD, CONTINUE, OUT_OF_P, OUT_OF_UPPER_SPAN, UPPER_LIMIT_FAILURE_RATE, EVEN, Converter, Specification, SeriesRule, is_almost_even
from library.file_paths import get_score_board_data_csv_file_path
from library.score_board import search_all_score_boards
from library.database import ScoreBoardDataTable


# CSV保存用タイマー
start_time_for_save = None
number_of_dirty = 0         # ファイルを新規作成したときに 1、レコードを１件追加したときも 1 増える

# CSV保存間隔（秒）、またはタイムシェアリング間隔
INTERVAL_SECONDS_FOR_SAVE_CSV = 5   # 2


def create_or_update_all_files(upper_limit_span):

    global number_of_dirty

    # ［将棋の引分け率］
    for failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5): # 5％刻み。 100%は除く。0除算が発生するので
        failure_rate = failure_rate_percent / 100
        print(f"[{datetime.datetime.now()}] in create_or_update_all_files {failure_rate=:.2f}")

        # ［将棋の先手勝率］
        for p_percent in range(50, 96):
            p = p_percent / 100
            #print(f"[{datetime.datetime.now()}] CREATE_FILE {p=:.2f}")

            # ［先後の決め方］
            for turn_system in [ALTERNATING_TURN, FROZEN_TURN]:
                turn_system_str = Converter.turn_system_to_code(turn_system)
                #print(f"[{datetime.datetime.now()}] CREATE_FILE {turn_system_str=}")

                # 仕様
                spec = Specification(
                        p=p,
                        failure_rate=failure_rate,
                        turn_system=turn_system)

                df, is_new = ScoreBoardDataTable.read_df(spec=spec, new_if_it_no_exists=True)


                # FIXME 便宜的に［試行シリーズ数］は 1 固定
                trials_series = 1


                # ファイルが存在せず、空データフレームが新規作成されたら
                if is_new:

                    # ループカウンター
                    span = 1        # ［目標の点数］
                    t_step = 1      # ［後手で勝ったときの勝ち点］
                    h_step = 1      # ［先手で勝ったときの勝ち点］

                    print(f"[{datetime.datetime.now()}][turn_system={turn_system_str:11}  p={spec.p:.2f}  failure_rate={spec.failure_rate:.2f}] NEW_FILE")

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

                        print(f"[{datetime.datetime.now()}][turn_system={turn_system_str:11}  p={p:.2f}  failure_rate={spec.failure_rate:.2f}] RESTART_ {span=:2}  {t_step=:2}  {h_step=:2}")


                while span < upper_limit_span + 1:

                    # 該当レコードのキー
                    key = (df['span']==span) & (df['t_step']==t_step) & (df['h_step']==h_step)

                    # データが既存でないなら
                    if not key.any():

                        # ［シリーズ・ルール］
                        specified_series_rule = SeriesRule.make_series_rule_base(
                                spec=spec,
                                trials_series=trials_series,
                                h_step=h_step,
                                t_step=t_step,
                                span=span)

                        # データフレーム更新
                        # 新規レコード追加
                        ScoreBoardDataTable.append_new_record(
                                df=df,
                                turn_system_str=turn_system_str,
                                failure_rate=spec.failure_rate,
                                p=spec.p,
                                span=span,
                                t_step=t_step,
                                h_step=h_step,
                                shortest_coins=specified_series_rule.shortest_coins,
                                upper_limit_coins=specified_series_rule.upper_limit_coins,
                                three_rates=None)    # NOTE three_rates を求める処理は重たいので、後回しにする
                        
                        number_of_dirty += 1


                    # カウントアップ
                    h_step += 1
                    if t_step < h_step:
                        h_step = 1
                        t_step += 1
                        if span < t_step:
                            t_step = 1
                            span += 1


                if 0 < number_of_dirty:
                    csv_file_path_to_wrote = ScoreBoardDataTable.to_csv(df=df, spec=spec)
                    print(f"[{datetime.datetime.now()}][turn_system={turn_system_str:11}  p={p:.2f}  failure_rate={spec.failure_rate:.2f}] SAVE_FILE  {number_of_dirty=}  write file to `{csv_file_path_to_wrote}` ...")
                    number_of_dirty = 0


def update_three_rates_for_all_files(upper_limit_upper_limit_coins):
    """次に、スリー・レーツを更新する
    
    Returns
    -------
    calculation_status : int
        計算状況
    """

    # CSV保存用タイマー
    global start_time_for_save, number_of_dirty

    def on_score_board_created(score_board):
        pass

    # ［将棋の引分け率］
    for failure_rate_percent in range(0, int(UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5): # 5％刻み。 100%は除く。0除算が発生するので
        failure_rate = failure_rate_percent / 100
        print(f"[{datetime.datetime.now()}] CREATE_FILE {failure_rate=:.2f}")

        # ［将棋の先手勝率］
        for p_percent in range(50, 96):
            p = p_percent / 100
            print(f"[{datetime.datetime.now()}] CREATE_FILE {p=:.2f}")

            # ［先後の決め方］
            for turn_system in [ALTERNATING_TURN, FROZEN_TURN]:

                # リセット
                number_of_dirty = 0
                start_time_for_save = time.time()       # CSV保存用タイマー

                turn_system_str = Converter.turn_system_to_code(turn_system)
                print(f"[{datetime.datetime.now()}] CREATE_FILE {turn_system_str=}")

                # 仕様
                spec = Specification(
                        p=p,
                        failure_rate=failure_rate,
                        turn_system=turn_system)

                df, is_new = ScoreBoardDataTable.read_df(spec=spec, new_if_it_no_exists=False)

                if df is None:
                    print(f"[{datetime.datetime.now()}][turn_system={turn_system_str:11}  p={p:.2f}  failure_rate={spec.failure_rate:.2f}] FILE_NOT_FOUND")
                    continue

                # イーブンが見つかっているなら、探索打ち切り
                if is_almost_even(df['a_win_rate_abs_error'].min()):
                    print(f"[{datetime.datetime.now()}][turn_system={turn_system_str:11}  p={p:.2f}  failure_rate={spec.failure_rate:.2f}] RE_EVEN_")
                    continue

                # 該当レコードのキー
                key = (df['a_win_rate']==OUT_OF_P) & (df['upper_limit_coins']<=upper_limit_upper_limit_coins)

                # データが既存なら
                if key.any():

                    # FIXME 便宜的に［試行シリーズ数］は 1 固定
                    trials_series = 1

                    for index, row in df[key].iterrows():

                        # 指定間隔（秒）でループを抜ける
                        end_time_for_save = time.time()
                        if INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - start_time_for_save:
                            # 計算未停止だが、譲る（タイムシェアリング）
                            return YIELD

                        h_step = row['h_step']
                        t_step = row['t_step']
                        span = row['span']

                        # ［シリーズ・ルール］
                        specified_series_rule = SeriesRule.make_series_rule_base(
                                spec=spec,
                                trials_series=trials_series,
                                h_step=h_step,
                                t_step=t_step,
                                span=span)

                        # 確率を求める
                        three_rates, all_patterns_p = search_all_score_boards(
                                series_rule=specified_series_rule,
                                on_score_board_created=on_score_board_created)

                        # データフレーム更新
                        # row['a_win_rate'] = three_rates.a_win_rate
                        # row['a_win_rate_abs_error'] = abs(three_rates.a_win_rate - EVEN)
                        # row['no_win_match_rate'] = three_rates.no_win_match_rate

                        df.loc[index,['a_win_rate']] = three_rates.a_win_rate
                        df.loc[index,['a_win_rate_abs_error']] = abs(three_rates.a_win_rate - EVEN)
                        df.loc[index,['no_win_match_rate']] = three_rates.no_win_match_rate

                        number_of_dirty += 1


                # 変更があれば保存
                if 0 < number_of_dirty:
                    # CSVファイルへ書き出し
                    csv_file_path_to_wrote = ScoreBoardDataTable.to_csv(df, spec)

                    print(f"[{datetime.datetime.now()}][{depth=}  turn_system={turn_system_str:11}  p={p:.2f}  failure_rate={spec.failure_rate:.2f}] SAVE____ dirty={number_of_dirty}  write file to `{csv_file_path_to_wrote}` ...")
                
                else:
                    print(f"[{datetime.datetime.now()}][{depth=}  turn_system={turn_system_str:11}  p={p:.2f}  failure_rate={spec.failure_rate:.2f}] UNCHANGE dirty={number_of_dirty}")


    return CONTINUE


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        number_of_dirty = 0

        # TODO 自動調整のいい方法が思い浮かばない
        #
        # まず、ファイルを全部作る
        create_or_update_all_files(
            upper_limit_span=15     # 数字が増えると処理が重くなる  3,  11, 15
            #upper_limit_span=OUT_OF_UPPER_SPAN + 1
            )

        # 次に、スリー・レーツを更新する
        # depth は upper_limit_coins に対応
        for depth in range(1, 15):      # range(1, 10)
            print(f"search {depth=} ...")

            calculation_status = update_three_rates_for_all_files(
                upper_limit_upper_limit_coins=depth)     # 数字が増えると処理が重くなる


        print("完了")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
