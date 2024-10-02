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

from library import HEAD, TAIL, ALICE, FROZEN_TURN, ALTERNATING_TURN, Converter, Specification, SeriesRule
from library.file_paths import get_score_board_data_csv_file_path, get_score_board_data_best_csv_file_path
from library.score_board import search_all_score_boards
from library.database import df_score_board_data_to_csv


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


    best_turn_system_str = None
    best_failure_rate = None
    best_p = None
    best_span = None
    best_t_step = None
    best_h_step = None
    best_a_win_rate = None
    best_b_win_rate = None
    best_no_win_match_rate = None

    # a_win_rate と b_win_rate の誤差
    best_win_rate_error = 100.1
    best_no_win_match_rate = 100.1


    # ファイルが存在したなら、読込
    if os.path.isfile(best_csv_file_path):
        df_b = pd.read_csv(best_csv_file_path, encoding="utf8")

        # （書き込むファイルの）該当レコードのキー
        key_b = (df_b['turn_system']==turn_system_str) & (df_b['failure_rate']==spec.failure_rate) & (df_b['p']==spec.p)

        # データが既存なら、取得
        if key_b.any():
            best_turn_system_str = df_b.loc[key_b, ['turn_system']].iat[0,0]
            best_failure_rate = df_b.loc[key_b, ['failure_rate']].iat[0,0]
            best_p = df_b.loc[key_b, ['p']].iat[0,0]
            best_span = df_b.loc[key_b, ['span']].iat[0,0]
            best_t_step = df_b.loc[key_b, ['t_step']].iat[0,0]
            best_h_step = df_b.loc[key_b, ['h_step']].iat[0,0]
            best_a_win_rate = df_b.loc[key_b, ['a_win_rate']].iat[0,0]
            best_b_win_rate = df_b.loc[key_b, ['b_win_rate']].iat[0,0]
            best_no_win_match_rate = df_b.loc[key_b, ['no_win_match_rate']].iat[0,0]

            best_win_rate_error = best_b_win_rate - best_a_win_rate


    # ファイルが存在しなかったなら、空データフレーム作成
    else:
        df_b = pd.DataFrame.from_dict({
                'turn_system': [],
                'failure_rate': [],
                'p': [],
                'span': [],
                't_step': [],
                'h_step': [],
                'a_win_rate': [],
                'b_win_rate': [],
                'no_win_match_rate': []})


    for           turn_system_str,       failure_rate,         p,         span,         t_step,         h_step,         a_win_rate,         b_win_rate,         no_win_match_rate in\
        zip(df_d['turn_system']  , df_d['failure_rate'], df_d['p'], df_d['span'], df_d['t_step'], df_d['h_step'], df_d['a_win_rate'], df_d['b_win_rate'], df_d['no_win_match_rate']):

        error = b_win_rate - a_win_rate

        if abs(error) < abs(best_win_rate_error):
            is_update = True
        elif error == best_win_rate_error and no_win_match_rate < best_no_win_match_rate:
            is_update = True
        else:
            is_update = False


        if is_update:
            best_win_rate_error = error
            best_no_win_match_rate = no_win_match_rate

            best_turn_system_str = turn_system_str
            best_failure_rate = failure_rate
            best_p = p
            best_span = span
            best_t_step = t_step
            best_h_step = h_step
            best_a_win_rate = a_win_rate
            best_b_win_rate = b_win_rate


    if best_turn_system_str is not None:
        # データフレーム更新
        # 新規レコード追加
        index = len(df_b.index)
        df_b.loc[index, ['turn_system']] = best_turn_system_str
        df_b.loc[index, ['failure_rate']] = best_failure_rate
        df_b.loc[index, ['p']] = best_p
        df_b.loc[index, ['span']] = best_span
        df_b.loc[index, ['t_step']] = best_t_step
        df_b.loc[index, ['h_step']] = best_h_step
        df_b.loc[index, ['a_win_rate']] = best_a_win_rate
        df_b.loc[index, ['b_win_rate']] = best_b_win_rate
        df_b.loc[index, ['no_win_match_rate']] = best_no_win_match_rate

        print(f"[{datetime.datetime.now()}][turn_system={best_turn_system_str}  failure_rate={best_failure_rate}  p={best_p}] write a csv to `{best_csv_file_path}` file ...")
        df_b.to_csv(best_csv_file_path,
                columns=['turn_system', 'failure_rate', 'p', 'span', 't_step', 'h_step', 'a_win_rate', 'b_win_rate', 'no_win_match_rate'],
                index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた


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
