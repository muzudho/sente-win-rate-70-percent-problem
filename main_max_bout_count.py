# 何本勝負にするかを算出
# python main_max_bout_count.py

import traceback
import datetime
import math

from library import round_letro


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # 先手勝率
        expected_black_win_rate = 0.65
        expected_black_target = 9
        expected_white_target = 5
        expected_max_bout_count = 13    # この数字は、無理数の小数点以下何桁という精度を追求すれば、いくらでも増えていくのではないか？
        print(f"[{datetime.datetime.now()}] 入力データ： {expected_black_win_rate=}  {expected_white_target=}  {expected_max_bout_count=}")

        # （式）
        #
        #           先手が先取する必要のある本数　＋　後手が先取する必要のある本数　ー　１
        # １　＝　────────────────────────────────────────────────────────────────────
        #                                     最大本数
        #
        one = (expected_black_target + expected_white_target - 1) / expected_max_bout_count
        if 1 != one:
            raise ValueError(f"{one=}")

        # なんでこいつら似てんの？

        #ずれると似てない print(f"[{datetime.datetime.now()}] {0.51 - 0.48} ＝ 0.51 - 0.48")
        #ずれると似てない print(f"[{datetime.datetime.now()}] {0.51**2 - 0.48**2} ＝ (0.51^2) － (0.48^2)")
        print(f"[{datetime.datetime.now()}] なんでこいつら似てんの？")
        print(f"[{datetime.datetime.now()}] {0.51 - 0.49} ＝ 0.51 - 0.49")
        print(f"[{datetime.datetime.now()}] {0.51**2 - 0.49**2} ＝ (0.51^2) － (0.49^2)")
        print(f"[{datetime.datetime.now()}] なんでこいつら似てんの？")
        print(f"[{datetime.datetime.now()}] {0.65 - 0.35} ＝ 0.65 - 0.35")
        print(f"[{datetime.datetime.now()}] {0.65**2 - 0.35**2} ＝ (0.65^2) － (0.35^2)")
        #print(f"[{datetime.datetime.now()}] {0.35**2 - 0.65**2} ＝ (0.35^2) － (0.65^2)")
        #print(f"[{datetime.datetime.now()}] {0.65**3 - 0.35**3} ＝ (0.65^3) － (0.35^3)")
        print(f"[{datetime.datetime.now()}] なんでこいつら似てんの？")
        print(f"[{datetime.datetime.now()}] {0.7 - 0.3} ＝ 0.7 - 0.3")
        print(f"[{datetime.datetime.now()}] {0.7**2 - 0.3**2} ＝ (0.7^2) － (0.3^2)")

        print(f"[{datetime.datetime.now()}] なんでこいつら似てんの？")
        print(f"[{datetime.datetime.now()}] {0.79 - 0.21} ＝ 0.79 - 0.21")
        print(f"[{datetime.datetime.now()}] {0.79**2 - 0.21**2} ＝ (0.79^2) － (0.21^2)")

        # print(f"[{datetime.datetime.now()}] {1 / 0.65**2} ＝ 1 ／ (0.65^2)")
        # print(f"[{datetime.datetime.now()}] {1 / 0.35**2} ＝ 1 ／ (0.35^2)")

        # print(f"[{datetime.datetime.now()}] {0.65**2 + 0.35**2} ＝ (0.65^2) ＋ (0.35^2)")
        # print(f"[{datetime.datetime.now()}] {0.65**2 - 0.35**2} ＝ (0.65^2) － (0.35^2)")
        # print(f"[{datetime.datetime.now()}] {0.35**2 - 0.65**2} ＝ (0.35^2) － (0.65^2)")
        # print(f"[{datetime.datetime.now()}] {0.65**2 * 0.35**2} ＝ (0.65^2) × (0.35^2)")
        # print(f"[{datetime.datetime.now()}] {0.35**2 / 0.65**2} ＝ (0.35^2) ／ (0.65^2)")
        # print(f"[{datetime.datetime.now()}] {0.65**2 / 0.35**2} ＝ (0.65^2) ／ (0.35^2)")

        # print(f"[{datetime.datetime.now()}] {math.sqrt(0.65**2 + 0.35**2)} ＝ sqrt(0.65^2 + 0.35^2)")

        # print(f"[{datetime.datetime.now()}] {1 - 0.65} ＝ 1 － 0.65")
        # print(f"[{datetime.datetime.now()}] {1 / 0.65} ＝ 1 ／ 0.65")
        # print(f"[{datetime.datetime.now()}] {1 / (1 - 0.65)} ＝ １ ／ （1 － 0.65）")
        # print(f"[{datetime.datetime.now()}] {0.65 / (1 - 0.65)} ＝ 0.65 ／ （1 － 0.65）")
        # print(f"[{datetime.datetime.now()}] {(1 - 0.65) / 0.65} ＝ (1 － 0.65) ／ 0.65")
        # print(f"[{datetime.datetime.now()}] {(1 - 0.65) / (1 + 0.65)} ＝ (1 － 0.65) ／ (1 ＋ 0.65)")
        # print(f"[{datetime.datetime.now()}] {(1 + 0.65) / (1 - 0.65)} ＝ (1 ＋ 0.65) ／ (1 － 0.65)")
        # print(f"[{datetime.datetime.now()}] {0.65 * 0.65} ＝ 0.65 × 0.65")
        # print(f"[{datetime.datetime.now()}] {0.65 * 0.35} ＝ 0.65 × 0.35")
        # print(f"[{datetime.datetime.now()}] {0.35 * 0.35} ＝ 0.35 × 0.35")
        # print(f"[{datetime.datetime.now()}] {math.sqrt(0.65)} ＝ sqrt(0.65)")
        # print(f"[{datetime.datetime.now()}] {math.sqrt(0.35)} ＝ sqrt(0.35)")

        # expected_both_targets = expected_black_target + expected_white_target

        # print(f"[{datetime.datetime.now()}] {0.65 / expected_max_bout_count} ＝ 0.65 ／ {expected_max_bout_count=}")
        # print(f"[{datetime.datetime.now()}] {0.65 / expected_both_targets} ＝ 0.65 ／ {expected_both_targets=}")
        # print(f"[{datetime.datetime.now()}] {0.65 / expected_black_target} ＝ 0.65 ／ {expected_black_target=}")
        # print(f"[{datetime.datetime.now()}] {0.65 / expected_white_target} ＝ 0.65 ／ {expected_white_target=}")

        # print(f"[{datetime.datetime.now()}] {expected_max_bout_count * 0.65} ＝ {expected_max_bout_count=} ＊ 0.65")
        # print(f"[{datetime.datetime.now()}] {expected_both_targets * 0.65} ＝ {expected_both_targets=} ＊ 0.65")
        # print(f"[{datetime.datetime.now()}] {expected_black_target * 0.65} ＝ {expected_black_target=} ＊ 0.65")
        # print(f"[{datetime.datetime.now()}] {expected_white_target * 0.65} ＝ {expected_white_target=} ＊ 0.65")

        # print(f"[{datetime.datetime.now()}] {expected_max_bout_count / 0.65} ＝ {expected_max_bout_count=} ／ 0.65")
        # print(f"[{datetime.datetime.now()}] {expected_both_targets / 0.65} ＝ {expected_both_targets=} ／ 0.65")
        # print(f"[{datetime.datetime.now()}] {expected_black_target / 0.65} ＝ {expected_black_target=} ／ 0.65")
        # print(f"[{datetime.datetime.now()}] {expected_white_target / 0.65} ＝ {expected_white_target=} ／ 0.65")


        # # （仮説）何本勝負にするかは、以下の式で求まる ----> 合ってなかった
        # max_bout_count = round_letro(1/(1-expected_black_win_rate)-1)    # ※小数点以下四捨五入
        # print(f"[{datetime.datetime.now()}] {expected_black_win_rate=}  {max_bout_count=}")

        # # これが有力そう ----> ダメだった
        # print(f"[{datetime.datetime.now()}] {round_letro(math.sqrt(0.65)*10+1)} ＝ sqrt(0.65)*10+1 四捨五入")
        # print(f"[{datetime.datetime.now()}] {round_letro(math.sqrt(0.35)*10-1)} ＝ sqrt(0.35)*10-1 四捨五入")
        # print(f"[{datetime.datetime.now()}] {round_letro(math.sqrt(0.7)*10+1)} ＝ sqrt(0.7)*10+1 四捨五入")
        # print(f"[{datetime.datetime.now()}] {round_letro(math.sqrt(0.3)*10-1)} ＝ sqrt(0.3)*10-1 四捨五入")
        # print(f"[{datetime.datetime.now()}] {round_letro(math.sqrt(0.79)*10+1)} ＝ sqrt(0.79)*10+1 四捨五入")
        # print(f"[{datetime.datetime.now()}] {round_letro(math.sqrt(0.21)*10-1)} ＝ sqrt(0.21)*10-1 四捨五入")

        # print(f"[{datetime.datetime.now()}] {0.65 / expected_max_bout_count * 100} ＝ 0.65 ／ {expected_max_bout_count=} × 100")
        # print(f"[{datetime.datetime.now()}] {0.7 / expected_max_bout_count * 100} ＝ 0.7 ／ {expected_max_bout_count=} × 100")
        # print(f"[{datetime.datetime.now()}] {0.79 / expected_max_bout_count * 100} ＝ 0.79 ／ {expected_max_bout_count=} × 100")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
