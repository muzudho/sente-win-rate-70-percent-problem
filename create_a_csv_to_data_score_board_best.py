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

from library import FROZEN_TURN, ALTERNATING_TURN, Converter, Specification
from library.file_paths import get_score_board_data_csv_file_path, get_score_board_data_best_csv_file_path
from library.database import ScoreBoardDataBestRecord, ScoreBoardDataBestTable


def automatic(spec):
    """
    Returns
    -------
    is_terminated : bool
        計算停止
    """

    turn_system_str = Converter.turn_system_to_code(spec.turn_system)


    # CSVファイルパス（読み込むファイル）
    data_csv_file_path = get_score_board_data_csv_file_path(
            p=spec.p,
            failure_rate=spec.failure_rate,
            turn_system=spec.turn_system)

    # 読み込むファイルが存在しなければ無視
    if not os.path.isfile(data_csv_file_path):
        return True

    # ファイルが存在したなら、読込
    df_d = pd.read_csv(data_csv_file_path, encoding="utf8")


    # CSVファイルパス（書き込むファイル）
    best_csv_file_path = get_score_board_data_best_csv_file_path()


    best_record = ScoreBoardDataBestRecord(
            turn_system_str=None,
            failure_rate=None,
            p=None,
            span=None,
            t_step=None,
            h_step=None,
            a_win_rate=None,
            b_win_rate=None,
            no_win_match_rate=100.1)

    # a_win_rate と b_win_rate の誤差
    best_win_rate_error = 100.1


    # ファイルが存在したなら、読込
    if os.path.isfile(best_csv_file_path):
        df_b = pd.read_csv(best_csv_file_path, encoding="utf8")

        # （書き込むファイルの）該当レコードのキー
        key_b = (df_b['turn_system']==turn_system_str) & (df_b['failure_rate']==spec.failure_rate) & (df_b['p']==spec.p)

        # データが既存なら、取得
        if key_b.any():
            best_record = ScoreBoardDataBestTable.get_record_by_key(df=df_b, key=key_b)

            best_win_rate_error = best_record.b_win_rate - best_record.a_win_rate


    # ファイルが存在しなかったなら、空データフレーム作成
    else:
        df_b = ScoreBoardDataBestTable.new_data_frame()


    for           turn_system_str,       failure_rate,         p,         span,         t_step,         h_step,         a_win_rate,         b_win_rate,         no_win_match_rate in\
        zip(df_d['turn_system']  , df_d['failure_rate'], df_d['p'], df_d['span'], df_d['t_step'], df_d['h_step'], df_d['a_win_rate'], df_d['b_win_rate'], df_d['no_win_match_rate']):

        error = b_win_rate - a_win_rate

        if abs(error) < abs(best_win_rate_error):
            is_update = True
        elif error == best_win_rate_error and no_win_match_rate < best_record.no_win_match_rate:
            is_update = True
        else:
            is_update = False


        if is_update:
            best_win_rate_error = error
            best_record = ScoreBoardDataBestRecord(
                    turn_system_str=turn_system_str,
                    failure_rate=failure_rate,
                    p=p,
                    span=span,
                    t_step=t_step,
                    h_step=h_step,
                    a_win_rate=a_win_rate,
                    b_win_rate=b_win_rate,
                    no_win_match_rate=no_win_match_rate)


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
