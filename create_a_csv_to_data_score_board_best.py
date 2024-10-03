#
# 分析
# python create_a_csv_to_data_score_board_best.py
#
#   ［仕様］［シリーズ・ルール］について、５分５分に近いものをピックアップします
#

import traceback
import os
import time
import datetime
import pandas as pd

from library import FROZEN_TURN, ALTERNATING_TURN, EVEN, ABS_OUT_OF_ERROR, Converter, Specification, ThreeRates
from library.file_paths import get_score_board_data_csv_file_path, get_score_board_data_best_csv_file_path
from library.database import ScoreBoardDataTable, ScoreBoardDataBestRecord, ScoreBoardDataBestTable


def automatic(spec):
    """
    Returns
    -------
    is_terminated : bool
        計算停止
    """

    turn_system_str = Converter.turn_system_to_code(spec.turn_system)

    df_d, is_new = ScoreBoardDataTable.read_df(spec=spec, new_if_it_no_exists=False)

    # 読み込むファイルが存在しなければ無視
    if is_new:
        return True


    # CSVファイルパス（書き込むファイル）
    best_csv_file_path = get_score_board_data_best_csv_file_path()


    best_record = ScoreBoardDataBestTable.create_none_record()

    # a_win_rate と EVEN の誤差
    best_win_rate_error = ABS_OUT_OF_ERROR


    # ファイルが存在しなかったなら、空データフレーム作成
    df_b, is_new = ScoreBoardDataBestTable.read_df(new_if_it_no_exists=True)

    # ファイルが存在したなら、読込
    if not is_new:
        # （書き込むファイルの）該当レコードのキー
        key_b = (df_b['turn_system']==turn_system_str) & (df_b['failure_rate']==spec.failure_rate) & (df_b['p']==spec.p)

        # データが既存なら、取得
        if key_b.any():
            best_record = ScoreBoardDataBestTable.get_record_by_key(df=df_b, key=key_b)

            best_win_rate_error = best_record.three_rates.a_win_rate - EVEN


    def on_each(record):

        error = record.a_win_rate - EVEN

        # 誤差が縮まれば更新
        if abs(error) < abs(best_win_rate_error):
            is_update = True
        
        # 誤差が同じでも、引き分け率が下がれば更新
        elif error == best_win_rate_error and (best_record.three_rates.no_win_match_rate is None or record.no_win_match_rate < best_record.three_rates.no_win_match_rate):
            is_update = True
        
        else:
            is_update = False


        if is_update:
            best_win_rate_error = error
            best_record = ScoreBoardDataBestRecord(
                    turn_system_str=record.turn_system_str,
                    failure_rate=record.failure_rate,
                    p=record.p,
                    span=record.span,
                    t_step=record.t_step,
                    h_step=record.h_step,
                    shortest_coins=record.shortest_coins,
                    upper_limit_coins=record.upper_limit_coins,
                    three_rates=ThreeRates(
                            a_win_rate=record.a_win_rate,
                            no_win_match_rate=record.no_win_match_rate))


    ScoreBoardDataBestTable.for_each(on_each=on_each)


    if best_record.turn_system_str is not None:
        # データフレーム更新
        # 新規レコード追加
        ScoreBoardDataBestTable.append_record(df=df_b, record=best_record)

        csv_file_path_to_wrote = ScoreBoardDataBestTable.to_csv(df=df_b)
        print(f"[{datetime.datetime.now()}][turn_system={best_record.turn_system_str}  failure_rate={best_record.failure_rate}  p={best_record.p}] write a csv to `{csv_file_path_to_wrote}` file ...")


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［先後の決め方］
        for turn_system in [ALTERNATING_TURN, FROZEN_TURN]:

            # ［将棋の引分け率］
            for failure_rate_percent in range(0, 100, 5): # 5％刻み。 100%は除く。0除算が発生するので
                failure_rate = failure_rate_percent / 100

                # ［将棋の先手勝率］
                for p_percent in range(50, 96):
                    p = p_percent / 100

                    # 仕様
                    spec = Specification(
                            p=p,
                            failure_rate=failure_rate,
                            turn_system=turn_system)

                    automatic(spec=spec)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
