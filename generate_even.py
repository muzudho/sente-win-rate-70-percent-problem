#
# 生成
# python generate_even.py
#
#   引き分けは考慮していない。
#   先手が勝つのに必要な先取本数と、後手が勝つのに必要な先取本数を探索する。
#

import traceback
import random
import math
import pandas as pd

from library import BLACK, WHITE, coin, n_bout_without_turn, n_round_without_turn, round_letro


LOG_FILE_PATH = 'output/generate_even_without_turn.log'
CSV_FILE_PATH = './data/generate_even_without_turn.csv'

# 先手勝率は 0.5 に近づけたい。その差の絶対値をエラーと呼んでいる。
# LIMIT で示す値よりエラーが下回れば、もう十分なので、探索を打ち切る。打ち切らないと延々と探索してしまう
#
#   NOTE とりあえず、0.1, 0.05, 0.04, 0.03, 0.02, 0.015, 0.01 のように少しずつ値を減らしていくこと。（いきなり小さくしても、処理時間がかかるから、適度に探索を切り上げて保存したい）
#   NOTE 例えば LIMIT = 0.03 にすると、黒番勝率 0.53 のときに 0.5 へ近づけるため 0.03 縮める必要があるから、運悪く 1:1 のときに外すと、そのあと見つけるのに時間がかかるようだ
#
LIMIT = 0.1
# 勝率は最低で 0.0、最大で 1.0 なので、0.5 との誤差は 0.5 が最大
OUT_OF_ERROR = 0.51


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:

        df = pd.read_csv(CSV_FILE_PATH, encoding="utf8")
        print(df)

        for p, best_new_p, best_new_p_error, best_max_bout_count, best_round_count, best_w_point, process in zip(df['p'], df['new_p'], df['new_p_error'], df['max_bout_count'], df['round_count'], df['w_point'], df['process']):
            #print(f"{p=}  {best_new_p_error=}  {best_max_bout_count=}  {best_round_count=}  {best_w_point=}  {process=}  {type(process)=}")

            # 黒の必要先取数は計算で求めます
            best_b_point = best_max_bout_count-(best_w_point-1)

            is_automatic = best_new_p_error >= LIMIT or best_max_bout_count == 0 or best_round_count < 2_000_000 or best_w_point == 0

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
                            black_win_rate=p,
                            max_bout_count=max_bout_count,
                            b_point=b_point,
                            w_point=w_point,
                            round_count=best_round_count)
                        
                        #print(f"{black_win_count=}  {best_round_count=}  {black_win_count / best_round_count=}")
                        new_p = black_win_count / best_round_count
                        new_p_error = abs(new_p - 0.5)

                        if new_p_error < best_new_p_error:
                            best_new_p = new_p
                            best_new_p_error = new_p_error
                            best_max_bout_count = max_bout_count
                            best_b_point = b_point
                            best_w_point = w_point
                        
                            # 進捗バー（更新時）
                            text = f'[{best_new_p_error:6.4f} {best_max_bout_count:2}本 {best_max_bout_count-best_w_point+1:2}黒 {best_w_point:2}白]'
                            print(text, end='', flush=True) # すぐ表示

                            # process 列を更新
                            #
                            #   途中の計算式。半角空白区切り
                            #
                            if math.isnan(process):
                                df.loc[df['p']==p, ['process']] = text
                            else:
                                df.loc[df['p']==p, ['process']] = f"{process} {text}"

                            # 十分な答えが出たので探索を打ち切ります
                            if best_new_p_error < LIMIT:
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



            # 自動計算未完了
            if is_automatic and best_new_p_error == OUT_OF_ERROR:
                print(f"先手勝率：{p*100:2} ％  （自動計算未完了）")

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

                print(f"先手勝率：{p*100:2.0f} ％ --調整後--> {best_new_p * 100:>7.04f} ％（± {best_new_p_error * 100:>7.04f}）  {best_max_bout_count:2}本勝負×{best_round_count:6}回  先手{best_b_point:2}本先取/後手{best_w_point:2}本先取制  つまり、先手一本の価値{b_unit:2.0f}  後手一本の価値{w_unit:2.0f}  ゴール{b_win_value_goal:3.0f}", end='')
                # 自動計算満了
                if is_automatic:
                    print(f"  （自動計算満了）")
                # 手動設定
                else:
                    print(f"  （手動設定）")

                # データフレーム更新
                # -----------------

                # ［調整後の表が出る確率］列を更新
                df.loc[df['p']==p, ['new_p']] = best_new_p

                # ［調整後の表が出る確率の５割との誤差］列を更新
                df.loc[df['p']==p, ['new_p_error']] = best_new_p_error

                # ［最大ｎ本勝負］列を更新
                df.loc[df['p']==p, ['max_bout_count']] = best_max_bout_count

                #best_b_point は max_bout_count と w_point から求まる

                # ［白が勝つのに必要な先取本数］列を更新
                df.loc[df['p']==p, ['w_point']] = best_w_point

            
            # CSV保存
            #
            #   NOTE なんか列が追加されるので、index=False を付けた
            #
            df.to_csv(CSV_FILE_PATH, index=False)

    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
