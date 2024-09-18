#
# 生成 手番を交互にするパターン
# NOTE まだできてない
# python generate_even_with_turn.py
#
#   引き分けは考慮していない。
#
#   * Ａさんが勝つために必要な先手先取本数
#   * Ａさんが勝つために必要な後手先取本数
#   * Ａさんが勝つために必要な先手と後手の先取合算本数 TODO 先手先取本数と、後手先取本数に、共通の軸での価値を付けれるか？
#   * Ｂさんが勝つために必要な先手先取本数
#   * Ｂさんが勝つために必要な後手先取本数
#   * Ｂさんが勝つために必要な先手と後手の先取合算本数
#

import traceback
import random
import math

from library import BLACK, WHITE, coin, n_bout_without_turn, n_round_without_turn, round_letro


SUMMARY_FILE_PATH = 'output/generate_even.log'

# 先手勝率は 0.5 に近づけたい。その差の絶対値をエラーと呼んでいる。
# LIMIT で示す値よりエラーが下回れば、もう十分なので、探索を打ち切る。打ち切らないと延々と探索してしまう
#
#   NOTE とりあえず、0.1, 0.05, 0.04, 0.03, 0.02, 0.015, 0.01 のように少しずつ値を減らしていくこと。（いきなり小さくしても、処理時間がかかるから、適度に探索を切り上げて保存したい）
#   NOTE 例えば LIMIT = 0.03 にすると、黒番勝率 0.53 のときに 0.5 へ近づけるため 0.03 縮める必要があるから、運悪く 1:1 のときに外すと、そのあと見つけるのに時間がかかるようだ
#
LIMIT = 0.1
# 勝率は最低で 0.0、最大で 1.0 なので、0.5 との誤差は 0.5 が最大
OUT_OF_ERROR = 0.51

# 先手勝率 0.50 ～ 0.99 まで試算
#
#   NOTE 手番を交代する場合、［最大ｎ本勝負］は、（Ａさんの先手取得本数－１）＋（Ａさんの後手取得本数－１）＋（Ｂさんの先手取得本数－１）＋（Ｂさんの後手取得本数－１）＋１ になる
#
#   
#
#
INPUT_DATA = [
    # 項目   p , best_alice_win_error, best_max_bout_count, best_round_count, best_w_point
    # 初期値 --,         OUT_OF_ERROR,                   1,                1,            1
    # ------------------------------------------------------------------------------------
    # これを初期値にして、続きからアルゴリズムを使った自動計算を行います
    [0.50, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.51, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.52, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.53, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.54, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.55, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.56, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.57, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.58, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.59, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.60, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.61, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.62, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.63, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.64, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.65, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.66, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.67, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.68, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.69, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.70, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.71, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.72, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.73, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.74, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.75, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.76, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.77, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.78, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.79, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.80, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.81, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.82, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.83, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.84, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.85, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.86, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.87, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.88, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.89, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.90, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.91, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.92, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.93, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.94, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.95, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.96, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.97, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.98, OUT_OF_ERROR, 1, 2_000_000, 1],  #
    [0.99, OUT_OF_ERROR, 1, 2_000_000, 1],  #
]


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:

        for rule in INPUT_DATA:
            # 初期値
            black_win_rate=rule[0]
            best_black_win_error=rule[1]
            best_max_bout_count=rule[2]
            best_round_count=rule[3]
            best_w_point=rule[4]

            # 黒の必要先取数は計算で求めます
            #
            #   FIXME 合ってるか、あとで確認
            #
            best_b_point = (best_max_bout_count-2*(best_w_point-1))/2

            is_automatic = best_black_win_error >= LIMIT or best_max_bout_count == 0 or best_round_count < 2_000_000 or best_w_point == 0

            # 途中の計算式
            calculation_list = []

            # アルゴリズムで求めるケース
            if is_automatic:

                is_cutoff = False

                # ［最大ｎ本勝負］
                for max_bout_count in range(best_max_bout_count, 101):

                    # １本勝負のときだけ、白はｎ本－１ではない
                    if max_bout_count == 1:
                        end_w_point = 2
                    else:
                        end_w_point = max_bout_count

                    for w_point in range(1, end_w_point):

                        # FIXME 黒の必要先取数は計算で求めます
                        b_point = max_bout_count-(w_point-1)

                        black_win_count = n_round_without_turn(
                            black_win_rate=black_win_rate,
                            max_bout_count=max_bout_count,
                            b_point=b_point,
                            w_point=w_point,
                            round_count=best_round_count)
                        
                        #print(f"{black_win_count=}  {best_round_count=}  {black_win_count / best_round_count=}")
                        black_win_error = abs(black_win_count / best_round_count - 0.5)

                        if black_win_error < best_black_win_error:
                            best_black_win_error = black_win_error
                            best_max_bout_count = max_bout_count
                            best_b_point = b_point
                            best_w_point = w_point
                        
                            # 進捗バー（更新時）
                            text = f'[{best_black_win_error:6.4f} {best_max_bout_count:2}本 {best_max_bout_count-best_w_point+1:2}黒 {best_w_point:2}白]'
                            print(text, end='', flush=True) # すぐ表示
                            calculation_list.append(text)

                            # 十分な答えが出たので探索を打ち切ります
                            if black_win_error < LIMIT:
                                is_cutoff = True

                                # 進捗バー
                                print('x', end='', flush=True)

                                break

                    if is_cutoff:
                        break

                    # 進捗バー（ｎ本目）
                    print('.', end='', flush=True)
                print() # 改行

            # 結果が設定されていれば、そのまま表示
            else:
                pass


            with open(SUMMARY_FILE_PATH, 'a', encoding='utf8') as f:

                # 自動計算未完了
                if is_automatic and best_black_win_error == OUT_OF_ERROR:
                    text = f"先手勝率：{black_win_rate:4.02f}"
                else:

                    # DO 通分したい。最小公倍数を求める
                    lcm = math.lcm(best_b_point, best_w_point)
                    # 先手一本の価値
                    b_unit = lcm / best_b_point
                    # 後手一本の価値
                    w_unit = lcm / best_w_point
                    # 先手勝ち、後手勝ちの共通ゴール
                    b_win_value_goal = best_w_point * w_unit
                    w_win_value_goal = best_b_point * b_unit
                    if b_win_value_goal != w_win_value_goal:
                        raise ValueError(f"{b_win_value_goal=}  {w_win_value_goal=}")

                    # 自動計算満了
                    if is_automatic:
                        text = f"先手勝率：{black_win_rate:4.02f}  {best_max_bout_count:2}本勝負×{best_round_count:6}回  先手{best_max_bout_count-best_w_point+1:2}本先取/後手{best_w_point:2}本先取制  調整先手勝率：{best_b_point * 100 / best_round_count:>7.04f} ％  つまり、先手一本の価値{b_unit:2.0f}  後手一本の価値{w_unit:2.0f}  ゴール{b_win_value_goal:3.0f}"
                
                    # 手動設定
                    else:
                        text = f"先手勝率：{black_win_rate:4.02f}  {best_max_bout_count:2}本勝負×{best_round_count:6}回  先手{best_max_bout_count-best_w_point+1:2}本先取/後手{best_w_point:2}本先取制  調整先手勝率：{(best_black_win_error + 0.5) * 100:7.04f} ％  つまり、先手一本の価値{b_unit:2.0f}  後手一本の価値{w_unit:2.0f}  ゴール{b_win_value_goal:3.0f}"


                # 計算過程を付けずに表示
                # --------------------

                # 自動計算未完了
                if is_automatic and best_black_win_error == OUT_OF_ERROR:
                    print(f"{text}  （自動計算未完了）")
                
                else:
                    # 自動計算満了
                    if is_automatic:
                        print(f"{text}  （自動計算満了）")
                    # 手動設定
                    else:
                        print(f"{text}  （手動設定）")


                # 計算過程と改行を付けてファイルへ出力
                # ---------------------------------

                # 自動計算
                if is_automatic:
                    # 計算過程
                    text += f"  {''.join(calculation_list)}"

                    # 未完了
                    if best_black_win_error == OUT_OF_ERROR:
                        text += "  （自動計算未完了）\n"
                    # 満了
                    else:
                        text += "  （自動計算満了）\n"

                # 手動設定
                else:
                    text += " （手動設定）\n"

                f.write(text)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
