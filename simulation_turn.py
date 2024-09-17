#
# TODO シミュレーション 手番を交互にするパターン
# NOTE まだできてない
# python simulation_turn.py
#
#   Ａさん（Alice）とＢさん（Bob）の勝率を五分五分にする。Ａさんの先手から始める。
#   引き分けは考慮していない。
#

import traceback
import random
import math

from library import BLACK, WHITE, coin, n_bout, n_round, round_letro


SUMMARY_FILE_PATH = 'output/simulation_turn.log'


# 0.50 ～ 0.99 まで試算
INPUT_DATA = [
    # Ａさん（Alice）の勝率（alice_win_rate_in_best）も取る
    #
    # black_win_rate, best_black_win_error, best_max_bout_count, best_round_count, best_white_require, alice_win_rate_in_best
    # -----------------------------------------------------------------------------------------------------------------------
    # ここに設定されている場合、アルゴリズムを使った自動計算を省きます
    [0.50, 0.0000, 0, 0, 0, 0],  # 
    [0.51, 0.0000, 0, 0, 0, 0],  # 
    [0.52, 0.0000, 0, 0, 0, 0],  # 
    [0.53, 0.0000, 0, 0, 0, 0],  # 
    [0.54, 0.0000, 0, 0, 0, 0],  # 
    [0.55, 0.0000, 0, 0, 0, 0],  # 
    [0.56, 0.0000, 0, 0, 0, 0],  # 
    [0.57, 0.0000, 0, 0, 0, 0],  # 
    [0.58, 0.0000, 0, 0, 0, 0],  # 
    [0.59, 0.0000, 0, 0, 0, 0],  # 
    [0.60, 0.0000, 0, 0, 0, 0],  # 
    [0.61, 0.0000, 0, 0, 0, 0],  # 
    [0.62, 0.0000, 0, 0, 0, 0],  # 
    [0.63, 0.0000, 0, 0, 0, 0],  # 
    [0.64, 0.0000, 0, 0, 0, 0],  # 
    [0.65, 0.0000, 0, 0, 0, 0],  # 
    [0.66, 0.0000, 0, 0, 0, 0],  # 
    [0.67, 0.0000, 0, 0, 0, 0],  # 
    [0.68, 0.0000, 0, 0, 0, 0],  # 
    [0.69, 0.0000, 0, 0, 0, 0],  # 
    [0.70, 0.0000, 0, 0, 0, 0],  # 
    [0.71, 0.0000, 0, 0, 0, 0],  # 
    [0.72, 0.0000, 0, 0, 0, 0],  # 
    [0.73, 0.0000, 0, 0, 0, 0],  # 
    [0.74, 0.0000, 0, 0, 0, 0],  # 
    [0.75, 0.0000, 0, 0, 0, 0],  # 
    [0.76, 0.0000, 0, 0, 0, 0],  # 
    [0.77, 0.0000, 0, 0, 0, 0],  # 
    [0.78, 0.0000, 0, 0, 0, 0],  # 
    [0.79, 0.0000, 0, 0, 0, 0],  # 
    [0.80, 0.0000, 0, 0, 0, 0],  # 
    [0.81, 0.0000, 0, 0, 0, 0],  # 
    [0.82, 0.0000, 0, 0, 0, 0],  # 
    [0.83, 0.0000, 0, 0, 0, 0],  # 
    [0.84, 0.0000, 0, 0, 0, 0],  # 
    [0.85, 0.0000, 0, 0, 0, 0],  # 
    [0.86, 0.0000, 0, 0, 0, 0],  # 
    [0.87, 0.0000, 0, 0, 0, 0],  # 
    [0.88, 0.0000, 0, 0, 0, 0],  # 
    [0.89, 0.0000, 0, 0, 0, 0],  # 
    [0.90, 0.0000, 0, 0, 0, 0],  # 
    [0.91, 0.0000, 0, 0, 0, 0],  # 
    [0.92, 0.0000, 0, 0, 0, 0],  # 
    [0.93, 0.0000, 0, 0, 0, 0],  # 
    [0.94, 0.0000, 0, 0, 0, 0],  # 
    [0.95, 0.0000, 0, 0, 0, 0],  # 
    [0.96, 0.0000, 0, 0, 0, 0],  # 
    [0.97, 0.0000, 0, 0, 0, 0],  # 
    [0.98, 0.0000, 0, 0, 0, 0],  # 
    [0.99, 0.0000, 0, 0, 0, 0],  # 
]


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:

        # 誤差は LIMIT に接近するほどベスト。勝率は最低で 0.0、最大で 1.0 なので、0.5 との誤差は 0.5 が最大
        # LIMIT 未満からさらに 0 に近づいていくので、そうなる前に打ち切る
        LIMIT = 0.02    # 例えば LIMIT = 0.03 にすると、黒番勝率 0.53 のときに 0.5 へ近づけるため 0.03 縮める必要があるから、運悪く 1:1 のときに外すと、そのあと見つけるのに時間がかかるようだ
        OUT_OF_ERROR = 0.51

        for rule in INPUT_DATA:
            black_win_rate=rule[0]
            best_black_win_error=rule[1]
            best_max_bout_count=rule[2]
            best_round_count=rule[3]
            best_white_require=rule[4]
            alice_win_rate_in_best=rule[5]     # アリスの勝率

            is_automatic = best_black_win_error >= LIMIT or best_max_bout_count == 0 or best_round_count < 2_000_000 or best_white_require == 0

            # 全部再計算。あとで消す
            is_automatic = True

            # 途中の計算式
            calculation_list = []

            # 比が同じになるｎ本勝負と白のｍ勝先取のペアはスキップしたい
            ration_set = set()

            # アルゴリズムで求めるケース
            if is_automatic:
                # リセット
                best_black_win_count = 0
                best_max_bout_count = 0
                best_white_require = 0
                alice_win_rate_in_best = 0    # アリスの勝率
                round_count = 2_000 # 2_000_000

                best_black_win_error = OUT_OF_ERROR

                is_cutoff = False

                # 最低ｎ本勝負（先手のＡさんが全勝するケース）
                for bout_count_in_all_win_alice in range(1, 101):

                    # １本勝負のときだけ、白はｎ本－１ではない
                    if bout_count_in_all_win_alice == 1:
                        end_white_require = 2
                    else:
                        end_white_require = bout_count_in_all_win_alice

                    # 最大ｎ本勝負（後手のＢさんが必要勝ー１するケース）
                    max_bout_count = bout_count_in_all_win_alice + end_white_require - 2

                    for white_require in range(1, end_white_require):

                        # 同じ比はスキップ。１００００倍（１００×１００程度を想定）して小数点以下四捨五入
                        ration = round_letro(white_require / bout_count_in_all_win_alice * 10000)

                        if ration in ration_set:
                            continue

                        ration_set.add(ration)


                        black_win_count = n_round(
                            black_win_rate=black_win_rate,
                            bout_count=bout_count_in_all_win_alice,
                            white_require=white_require,
                            round_count=round_count)

                        # 奇数本のときはアリスが黒番、偶数本のときはアリスが白番
                        if bout_count_in_all_win_alice % 2 == 1:
                            alice_win_count = black_win_count
                        else:
                            alice_win_count = 0
                        

                        black_win_error = abs(black_win_count / round_count - 0.5)
                        alice_win_rate = alice_win_count / round_count


                        if black_win_error < best_black_win_error:
                            best_black_win_error = black_win_error
                            best_max_bout_count = max_bout_count
                            best_black_win_count = black_win_count
                            best_white_require = white_require
                            alice_win_rate_in_best = alice_win_rate
                        
                            # 進捗バー（更新時）
                            text = f'[{best_black_win_error:6.4f} {best_max_bout_count:2}本 {best_min_bout_count:2}黒 {best_white_require:2}白 {alice_win_rate_in_best:6.4f}ア]'
                            calculation_list.append(text)
                            print(text, end='')

                            # 十分な答えが出たので探索を打ち切ります
                            if black_win_error < LIMIT:
                                is_cutoff = True

                                # 進捗バー
                                print('x', end='')

                                break

                    if is_cutoff:
                        break

                    # 進捗バー
                    print('.', end='')
                print() # 改行

            # 結果が設定されていれば、そのまま表示
            else:
                pass


            with open(SUMMARY_FILE_PATH, 'a', encoding='utf8') as f:
                # 自動計算
                if is_automatic:
                    # 未完了
                    if best_black_win_error == OUT_OF_ERROR:
                        text = f"先手勝率：{black_win_rate:4.02f}  {''.join(calculation_list)}  （自動計算未完了）\n"

                    # 満了
                    else:           
                        text = f"先手勝率：{black_win_rate:4.02f}  {best_max_bout_count:2}本勝負×{round_count:6}回  先手{best_min_bout_count:2}本先取/後手{best_white_require:2}本先取制  調整先手勝率：{best_black_win_count * 100 / round_count:>7.04f} ％  Ａさん勝率 {alice_win_rate_in_best:>7.04f} ％  {''.join(calculation_list)}  （自動計算満了）\n"
                
                # 手動設定
                else:
                    text = f"先手勝率：{black_win_rate:4.02f}  {best_max_bout_count:2}本勝負×{best_round_count:6}回  先手{best_min_bout_count:2}本先取/後手{best_white_require:2}本先取制  調整先手勝率：{(best_black_win_error + 0.5) * 100:7.04f} ％  Ａさん勝率 {alice_win_rate_in_best:>7.04f} ％  （手動設定）\n"

                f.write(text)
                print(text, end='')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
