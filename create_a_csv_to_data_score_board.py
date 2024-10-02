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

from library import HEAD, TAIL, ALICE, FROZEN_TURN, ALTERNATING_TURN, Converter, Specification, SeriesRule, is_almost_even
from library.file_paths import get_score_board_data_csv_file_path
from library.score_board import search_all_score_boards
from library.database import ScoreBoardDataTable


# CSV保存間隔（秒）、またはタイムシェアリング間隔
INTERVAL_SECONDS_FOR_SAVE_CSV = 2


def automatic(turn_system, failure_rate, p):
    """
    Returns
    -------
    is_terminated : bool
        計算停止
    """

    # 仕様
    spec = Specification(
            p=p,
            failure_rate=failure_rate,
            turn_system=turn_system)

    # CSVファイルパス
    csv_file_path = get_score_board_data_csv_file_path(
            p=spec.p,
            failure_rate=spec.failure_rate,
            turn_system=spec.turn_system)

    # ファイルが存在したなら、読込
    if os.path.isfile(csv_file_path):
        df = pd.read_csv(csv_file_path, encoding="utf8")

    # ファイルが存在しなかったなら、空データフレーム作成
    else:
        df = ScoreBoardDataTable.new_data_frame()

    def on_score_board_created(score_board):
        pass


    # CSV保存用タイマー
    start_time_for_save = time.time()
    number_of_dirty = 0
    number_of_skip = 0

    turn_system_str = Converter.turn_system_to_code(spec.turn_system)


    # ［目標の点数］
    for span in range(1, 100):

        # ［後手で勝ったときの勝ち点］
        # over_t_step = min(span + 1, 11)     # FIXME 時間がかかりすぎるので上限を作っておく
        # for t_step in range(1, over_t_step):
        for t_step in range(1, span + 1):

            # ［先手で勝ったときの勝ち点］
            for h_step in range(1, t_step + 1):

                # 指定間隔（秒）で保存
                end_time_for_save = time.time()
                if INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - start_time_for_save:
                    start_time_for_save = end_time_for_save
                    print(f"[{datetime.datetime.now()}][turn_system={turn_system_str}  failure_rate={spec.failure_rate}  p={p}] skip={number_of_skip}")
                    number_of_skip = 0

                    # 変更があれば保存
                    if 0 < number_of_dirty:
                        print(f"[{datetime.datetime.now()}][turn_system={turn_system_str}  failure_rate={spec.failure_rate}  p={p}] dirty={number_of_dirty} write file to `{csv_file_path}` ...")
                        number_of_dirty = 0

                        # CSVファイルへ書き出し
                        ScoreBoardDataTable.to_csv(df, spec)

                    # 計算未停止だが、譲る（タイムシェアリング）
                    return False


                # FIXME 便宜的に［試行シリーズ数］は 1 固定
                trials_series = 1

                # ［シリーズ・ルール］
                specified_series_rule = SeriesRule.make_series_rule_base(
                        spec=spec,
                        trials_series=trials_series,
                        h_step=h_step,
                        t_step=t_step,
                        span=span)

                # 該当レコードのキー
                key = (df['turn_system']==turn_system_str) & (df['failure_rate']==spec.failure_rate) & (df['p']==spec.p) & (df['span']==specified_series_rule.step_table.span) & (df['t_step']==specified_series_rule.step_table.get_step_by(face_of_coin=TAIL)) & (df['h_step']==specified_series_rule.step_table.get_step_by(face_of_coin=HEAD))

                # データが既存なら
                if key.any():

                    # イーブンが見つかっているなら、ファイルへ保存して探索打ち切り
                    if is_almost_even(df.loc[key, ['a_win_rate']].iat[0, 0]):
                        print(f"[{datetime.datetime.now()}][turn_system={turn_system_str}  failure_rate={spec.failure_rate}  p={p}] even! {span=}  {t_step=}  {h_step=}  shortest_coins={specified_series_rule.shortest_coins}  upper_limit_coins={specified_series_rule.upper_limit_coins}")

                        # CSVファイルへ書き出し
                        ScoreBoardDataTable.to_csv(df, spec)
                        return True

                    # スキップ
                    number_of_skip += 1
                    continue

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

                # イーブンが見つかっているなら、ファイルへ保存して探索打ち切り
                if three_rates.is_even:
                    print(f"[{datetime.datetime.now()}][turn_system={turn_system_str}  failure_rate={spec.failure_rate}  p={p}] even! {span=}  {t_step=}  {h_step=}  shortest_coins={specified_series_rule.shortest_coins}  upper_limit_coins={specified_series_rule.upper_limit_coins}")
                    # CSVファイルへ書き出し
                    ScoreBoardDataTable.to_csv(df, spec)
                    return True


    # 探索範囲内に見つからなかったが、計算停止扱いとする
    return True


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # 計算停止していない数（ループに入るために最初の１回はダミー値）
        number_of_not_terminated = 1

        while number_of_not_terminated != 0:
            # リセット
            number_of_not_terminated = 0

            # ［将棋の引分け率］
            for failure_rate_percent in range(0, 100, 5): # 5％刻み。 100%は除く。0除算が発生するので
                failure_rate = failure_rate_percent / 100

                # ［将棋の先手勝率］
                for p_percent in range(50, 96):
                    p = p_percent / 100

                    # ［先後の決め方］
                    for turn_system in [ALTERNATING_TURN, FROZEN_TURN]:

                        is_terminated = automatic(turn_system=turn_system, failure_rate=failure_rate, p=p)
                        if not is_terminated:
                            number_of_not_terminated += 1


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
