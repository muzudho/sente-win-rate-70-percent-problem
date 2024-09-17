#
# scipy ライブラリーの使い方の練習
#
# python -m pip install scipy
# python let_scipy.py
#
# 📖 [How do I properly write scipy.stats.binom.cdf() details](https://datascience.stackexchange.com/questions/51436/how-do-i-properly-write-scipy-stats-binom-cdf-details)
#

import scipy


INPUT_DATA = [
    #  k,  n,   p
    [  5, 10, 0.5],
    [  5, 10, 0.7],
    [  5, 10, 1.0],
    [  0, 10, 1.0],
    [ 10, 10, 1.0],
    [  9, 10, 0.9],
]


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        for datum in INPUT_DATA:
            # 表はこの数字以下が出る回数
            k = datum[0]

            # コイントス試行回数
            n = datum[1]

            # コインの表が出る偏り
            p = datum[2]

            # 確率
            y = scipy.stats.binom.cdf(k,n,p)

            print(f"{k=:2}  {n=}  {p=}  {y=:6.4f}")

    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
