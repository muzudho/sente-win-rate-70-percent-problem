#
# python o3o0_play_equalized_unfair_coin_toss.py
#
#   イコーライズド・アンフェア・コイントス
#

import traceback
import random
import datetime
import time

from library import HEAD, TAIL, FROZEN_TURN, Specification
from library_for_game import GamePlan, Paragraphs


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # メッセージスピード
        #msg_spd = 2
        msg_spd = 0.02


        for demo_th in range(1, 2): # ループ無し

            # プロローグ
            print()
            print(f"きふわらべ王国の国民は言った。")
            time.sleep(msg_spd)

            print()
            print(f"「コイントスしようぜ？」")
            time.sleep(msg_spd)

            game_plan = GamePlan(
                    spec=Specification.by_three_rates(
                            turn_system_id=FROZEN_TURN,
                            failure_rate=0.0,
                            head_rate=0.7),
                    h_step=1,
                    t_step=2,
                    span=2,
                    a_victory_rate=0.49,
                    b_victory_rate=0.51,
                    no_victory_rate=0.0)

            # 先住民が持っているコインは、～確率うんぬん～ フェア？コインだ
            Paragraphs.coins_that_people_had(msg_spd=msg_spd, game_plan=game_plan)

            print()
            print(f"ここで")
            time.sleep(msg_spd / 3)
            print(f"コインを投げて、")
            time.sleep(msg_spd)


            print()
            print(f"表が出たら、表に張った方に勝ち点が {game_plan.h_step} 、")
            time.sleep(msg_spd / 3)
            print(f"ｳﾗが出たら、ｳﾗに張った方に勝ち点が {game_plan.t_step} 、")
            # time.sleep(msg_spd / 3)
            # print(f"表も裏も出なかったら 0 点、")
            time.sleep(msg_spd)

            print()
            print(f"先に勝ち点を {game_plan.span} 取った方を優勝とする。")
            time.sleep(msg_spd / 3)

            print()
            print(f"「表とｳﾗ、どっちが出る方に張る？」")
            time.sleep(msg_spd)

            while True:
                prompt = f"""\

表に張るなら h を、ｳﾗに張るなら t を入力してください
> """
                input_str = input(prompt)

                if input_str in ['h', 't']:
                    break

            if input_str == 'h':
                your_choice = HEAD

                print()
                print(f"「じゃあ　表で」")
                time.sleep(msg_spd)
            
            else:
                your_choice = TAIL

                print()
                print(f"「じゃあ　ｳﾗで」")
                time.sleep(msg_spd)

            # リセット
            a_pts = 0
            b_pts = 0

            for round_th in range(1, 100_000_001):

                print()
                print(f"国民「 {round_th} 投目」")
                time.sleep(msg_spd)

                print()
                print(f"ピンッ")
                time.sleep(msg_spd / 3)
                print(f"バシッ")
                time.sleep(msg_spd)


                # 0.0 <= X < 1.0
                outcome = random.random()


                if outcome < 0.5:
                    face_of_coin = HEAD
                    face_of_coin_str = '表'

                    print()
                    print(f"「{face_of_coin_str}が出た」")
                    time.sleep(msg_spd)

                else:
                    face_of_coin = TAIL
                    face_of_coin_str = 'ｳﾗ'    # 表と裏の字が似すぎているので、変えてみる

                    print()
                    print(f"　{face_of_coin_str}が出た」")
                    time.sleep(msg_spd)


                if your_choice == face_of_coin:
                    print()
                    print(f"「やったぜ！　当たった！」")
                    time.sleep(msg_spd)

                    if your_choice == HEAD:
                        a_pts += game_plan.h_step

                        print()
                        print(f"「わたしが勝ち点 {game_plan.h_step} をもらって、")
                        time.sleep(msg_spd / 3)
                        print(f"　合計 {a_pts} 点だぜ。")
                        time.sleep(msg_spd)

                        if game_plan.span <= a_pts:
                            print()
                            print(f"　{game_plan.span} 点取ったから、")
                            time.sleep(msg_spd / 3)
                            print(f"　わたしの優勝だな」")
                            time.sleep(msg_spd)
                            break

                        else:
                            print()
                            print(f"　{game_plan.span} 点まで")
                            time.sleep(msg_spd / 3)
                            print(f"　まだ {game_plan.span - a_pts} 点足りないから、")
                            time.sleep(msg_spd / 3)
                            print(f"　続行だな」")
                            time.sleep(msg_spd)


                    elif your_choice == TAIL:
                        b_pts += game_plan.t_step

                        print()
                        print(f"「わたしが勝ち点 {game_plan.t_step} をもらって、")
                        time.sleep(msg_spd / 3)
                        print(f"　合計 {b_pts} 点だぜ。")
                        time.sleep(msg_spd)

                        if game_plan.span <= b_pts:
                            print()
                            print(f"　{game_plan.span} 点取ったから、")
                            time.sleep(msg_spd / 3)
                            print(f"　わたしの優勝だな」")
                            time.sleep(msg_spd)
                            break

                        else:
                            print()
                            print(f"　{game_plan.span} 点まで")
                            time.sleep(msg_spd / 3)
                            print(f"　まだ {game_plan.span - b_pts} 点足りないから、")
                            time.sleep(msg_spd / 3)
                            print(f"　続行だな」")
                            time.sleep(msg_spd)


                    else:
                        raise ValueError(f"{your_choice=}")


                else:
                    print()
                    print(f"「ハズレかあ」")
                    time.sleep(msg_spd)


                    if your_choice == TAIL:
                        a_pts += game_plan.h_step

                        print()
                        print(f"「相手に勝ち点 {game_plan.h_step} が入って、")
                        time.sleep(msg_spd / 3)
                        print(f"　合計 {a_pts} 点だぜ。")
                        time.sleep(msg_spd)

                        if game_plan.span <= a_pts:
                            print()
                            print(f"　{game_plan.span} 点取られたから、")
                            time.sleep(msg_spd / 3)
                            print(f"　わたしの敗退だな」")
                            time.sleep(msg_spd)
                            break

                        else:
                            print()
                            print(f"　{game_plan.span} 点まで")
                            time.sleep(msg_spd / 3)
                            print(f"　まだ {game_plan.span - a_pts} 点足りないから、")
                            time.sleep(msg_spd / 3)
                            print(f"　続行だな」")
                            time.sleep(msg_spd)


                    elif your_choice == HEAD:
                        b_pts += game_plan.t_step

                        print()
                        print(f"「相手に勝ち点 {game_plan.t_step} が入って、")
                        time.sleep(msg_spd / 3)
                        print(f"　合計 {b_pts} 点だぜ。")
                        time.sleep(msg_spd)

                        if game_plan.span <= b_pts:
                            print()
                            print(f"　{game_plan.span} 点取られたから、")
                            time.sleep(msg_spd / 3)
                            print(f"　わたしの敗退だな」")
                            time.sleep(msg_spd)
                            break

                        else:
                            print()
                            print(f"　{game_plan.span} 点まで")
                            time.sleep(msg_spd / 3)
                            print(f"　まだ {game_plan.span - b_pts} 点足りないから、")
                            time.sleep(msg_spd / 3)
                            print(f"　続行だな」")
                            time.sleep(msg_spd)


                    else:
                        raise ValueError(f"{your_choice=}")


            # 優勝 or 敗退後
            # -------------

            print()
            print(f"こうして、コイントスは終わった。")
            time.sleep(msg_spd)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
