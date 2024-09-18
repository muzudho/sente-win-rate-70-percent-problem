#
# 計算
# python let_calculate_probability.py
#
#   確率の試算
#

import traceback
import datetime
import random
import math

from library import calculate_probability


LOG_FILE_PATH = 'output/let_calculate_probability.log'
CSV_FILE_PATH = './data/let_calculate_probability.csv.csv'


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:

        df = pd.read_csv(CSV_FILE_PATH, encoding="utf8")
        print(df)

        # * `p` - 先手が勝つ確率
        # * `b_require` - 先手の必要な先取本数
        # * `w_require` - 後手の必要な先取本数
        # * `new_p` - 調整後の先手が勝つ確率
        # * `new_p_error` - 調整後の表が出る確率の 0.50 からの差の絶対値です。初期値は 0.51
        # * `comment` - この行データの説明
        # 
        for p, b_require, w_require, new_p, new_p_error, comment in zip(df['p'], df['b_require'], df['w_require'], df['new_p'], df['new_p_error'], df['comment']):

            balanced_black_win_rate = calculate_probability(
                p=p,
                H=b_require,
                T=w_require)

            # 誤差
            error = balanced_black_win_rate - 0.5


            with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
                # 文言作成
                # -------

                text = f"[{datetime.datetime.now()}]  先手勝率 {p:4.2f}  先取本数　先手：後手＝{b_require:>2}：{w_require:>2}  調整後の先手勝率 {balanced_black_win_rate:6.4f}  誤差{error:7.4f}"
                print(text) # 表示
                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
