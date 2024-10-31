#
# python demo_japanese.py
#
#   日本語での展示デモ
#

import traceback
import random
import math
import datetime
import time
import pandas as pd


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # メッセージスピード
        mspd = 2

        while True:

            print()
            print(f"わらべ島の先住民たちは、")
            time.sleep(mspd / 3)
            print(f"コインを投げて表と裏のどちらが出るかを")
            time.sleep(mspd / 3)
            print(f"当てる遊び（コイントス）を続けていた。")
            time.sleep(mspd)

            print()
            print(f"そして　わらべ島に")
            time.sleep(mspd / 3)
            print(f"きふわらべ王国が建国されると、")
            time.sleep(mspd)

            print()
            print(f"島から出土する金属の材質が悪くなり、")
            time.sleep(mspd / 3)
            print(f"当表と裏の出る確率が異なるコインしか")
            time.sleep(mspd / 3)
            print(f"造ることができなくなった。")
            time.sleep(mspd)

            print()
            print(f"熱心な国民は、")
            time.sleep(mspd / 3)
            print(f"表の出る確率を小数点第３位までの精度で測ることができたが、")
            time.sleep(mspd)

            print()
            print(f"このような材質の悪いコイン")
            time.sleep(mspd / 3)
            print(f"（先住民からはイカサマコインと呼ばれた）で")
            time.sleep(mspd / 3)
            print(f"コイントスすることは諦めていた。")
            time.sleep(mspd)

            print()
            print(f"そこで、きふわらべ王国の数学大臣は")
            time.sleep(mspd / 3)
            print(f"イカサマコインを使っても、")
            time.sleep(mspd)

            print()
            print(f"もし、無限回対決したならば、")
            time.sleep(mspd)

            print()
            print(f"まるで表と裏が均等に出たかのような")
            time.sleep(mspd / 3)
            print(f"結果に近づくことが期待できるという、")
            time.sleep(mspd)

            print()
            print(f"コイントスの方法を次のように示した。")
            time.sleep(mspd)


            print()
            print(f"国民の１人は言った。")
            time.sleep(mspd)

            print()
            print(f"「無限回も対決できないしなあ」")
            time.sleep(mspd)


            print()
            print(f"数学大臣は話しを続けた。")
            time.sleep(mspd)

            # 0.01 単位で 0 ～ 1 を想定
            p = 0.7
            q = 1 - p
            h_step = 1
            t_step = 2
            span = 4
            a_pts = 0   # 勝ち点の合計
            b_pts = 0
            number_of_trial = 0     # 試行回数
            number_of_a_victory = 0
            number_of_b_victory = 0

            while True:

                print()
                print(f"「ここに表が {p * 10:.1f} 割出るイカサマコインがある。")
                time.sleep(mspd)

                print()
                print(f"　表が出たら勝ち点が {h_step} 、")
                time.sleep(mspd / 3)
                print(f"　裏が出たら勝ち点が {t_step} とし、")
                time.sleep(mspd)

                print()
                print(f"　どちらかが先に {span} 点を取るまで")
                time.sleep(mspd / 3)
                print(f"　コイントスを続け、")
                time.sleep(mspd)

                print()
                print(f"　先に {span} 点取った方を優勝とする」")
                time.sleep(mspd)


                print()
                print(f"きふわらべ国王は、 {p * 10:.1f} 割出るという表が優勝する方に張った。")
                time.sleep(mspd)

                print()
                print(f"数学大臣は、 {q * 10:.1f} 割出るという裏が優勝する方に張った。")
                time.sleep(mspd)

                print()
                print(f"きふわらべ国王「おい、そこらへんのコクミン。")
                time.sleep(mspd / 3)
                print(f"　コインを投げろだぜ」")
                time.sleep(mspd)

                round_th = 1

                print()
                print(f"国民「自分で投げればいいのに……")
                time.sleep(mspd / 3)
                print(f"　じゃあ {round_th} 投目」")
                time.sleep(mspd)

                # 0.0 <= X < 1.0
                outcome = random.random()

                while True:

                    if outcome < p:
                        print()
                        print(f"　表が出た」")
                        time.sleep(mspd)
                        face_of_coin = 'head'
                        a_pts += h_step

                        print()
                        print(f"きふわらべ国王「わたしが勝ち点 {h_step} をもらって、")
                        time.sleep(mspd / 3)
                        print(f"　合計 {a_pts} 点だぜ。")
                        time.sleep(mspd)

                        if span <= a_pts:
                            print()
                            print(f"　{span} 点取ったから、")
                            time.sleep(mspd / 3)
                            print(f"　わたしの優勝だな」")
                            time.sleep(mspd)

                            number_of_a_victory += 1
                            break

                        else:
                            print()
                            print(f"　{span} 点まで")
                            time.sleep(mspd / 3)
                            print(f"　まだ {span - a_pts} 点足りないから、")
                            time.sleep(mspd / 3)
                            print(f"　続行だな」")
                            time.sleep(mspd)

                    else:
                        print()
                        print(f"　裏が出た」")
                        time.sleep(mspd)
                        face_of_coin = 'tail'
                        b_pts += t_step

                        print()
                        print(f"数学大臣「わたしが勝ち点 {t_step} をもらって、")
                        time.sleep(mspd / 3)
                        print(f"　合計 {b_pts} 点だぜ」")
                        time.sleep(mspd)

                        if span <= b_pts:
                            print()
                            print(f"　{span} 点取ったから、")
                            time.sleep(mspd / 3)
                            print(f"　わたしの優勝だな」")
                            time.sleep(mspd)

                            number_of_b_victory += 1
                            break

                        else:
                            print()
                            print(f"　{span} 点まで")
                            time.sleep(mspd / 3)
                            print(f"　まだ {span - b_pts} 点足りないから、")
                            time.sleep(mspd / 3)
                            print(f"　続行だな」")
                            time.sleep(mspd)


                    round_th += 1

                    print()
                    print(f"国民「じゃあ {round_th} 投目」")
                    time.sleep(mspd)

                    # 0.0 <= X < 1.0
                    outcome = random.random()


                number_of_trial += 1

                print()
                print(f"きふわらべ国王「これでわたしは {number_of_a_victory} 回優勝」")
                time.sleep(mspd)

                print()
                print(f"数学大臣「これでわたしは {number_of_b_victory} 回優勝」")
                time.sleep(mspd)

                print()
                print(f"国民「 {number_of_trial} 回やったぐらいじゃ、")
                time.sleep(mspd / 3)
                print(f"　本当に五分五分になってるのか、")
                time.sleep(mspd / 3)
                print(f"　よく分からないなあ」")
                time.sleep(mspd)


                if number_of_trial < 21:
                    break


                print()
                print(f"きふわらべ国王「もう１回やってみようぜ？」")
                time.sleep(mspd * 3)


            if number_of_trial * 47 / 100 <= number_of_a_victory and number_of_a_victory < number_of_trial * 53 / 100:
                print()
                print(f"きふわらべ国王「だいたい　五分五分ということでいいんじゃないか？」")
                time.sleep(mspd)
            
            else:
                print()
                print(f"きふわらべ国王「まー、偏ってるかなあ」")
                time.sleep(mspd)


            time.sleep(10)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
