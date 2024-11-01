#
# python o5o0_play_mixed_coin_toss.py
#
#   均等なのも不均等なのも混ぜられたコイントス
#

import traceback
import random
import datetime
import time

from library import HEAD, TAIL, FROZEN_TURN, Converter, Specification
from library_for_game import GamePlan, SeriesStatus, Paragraphs, choice_game_plan
from library_for_game.data import fair_list_of_game_plan, unfair_list_of_game_plan


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # メッセージスピード
        msg_spd = 2
        #msg_spd = 0.02

        # プロローグ
        print()
        print(f"きふわらべ国王は言った。")
        time.sleep(msg_spd)

        stock = 3

        print()
        print(f"「コクミンの間でコイントスが流行っている。")
        time.sleep(msg_spd / 3)
        print(f"　{stock} 回プレイできるチケットが余ってるから、")
        time.sleep(msg_spd / 3)
        print(f"　お前にやろう。")
        time.sleep(msg_spd / 3)
        print(f"　コイントスしてこいだぜ、ヒマだろ」")
        time.sleep(msg_spd)

        print()
        print(f"こうして、コクミンの間で流行っているコイントスの投げ場に向かった。")
        time.sleep(msg_spd)


        while True:

            stock -= 1

            print()
            print(f"チケットを 1 枚支払った。")
            time.sleep(msg_spd / 3)
            print(f"残りのチケットは {stock} 枚です。")
            time.sleep(msg_spd)

            # ゲーム企画
            mixed_list_of_game_plan = []
            mixed_list_of_game_plan.extend(fair_list_of_game_plan)
            mixed_list_of_game_plan.extend(unfair_list_of_game_plan)
            game_plan = choice_game_plan(mixed_list_of_game_plan)

            # 例：　先住民が持っているコインは、～確率うんぬん～ フェア？コインだ
            Paragraphs.coins_that_people_had(msg_spd=msg_spd, game_plan=game_plan)

            # 例：　ここでコインを投げて、～うんぬん～　点先取した方が優勝とする
            Paragraphs.explain_series_rule(msg_spd=msg_spd, game_plan=game_plan)

            # 例：　「表とｳﾗ、どっちが出る方に張る？」「じゃあ　ｳﾗで」
            your_choice = Paragraphs.do_you_choice_head_or_tail(msg_spd=msg_spd, game_plan=game_plan)

            # リセット
            series_status = SeriesStatus()

            for round_th in range(1, 100_000_001):

                if your_choice == HEAD:
                    your_pts = series_status.a_pts
                    your_step = game_plan.h_step
                    opponent_pts = series_status.b_pts
                    opponent_step = game_plan.t_step

                elif your_choice == TAIL:
                    your_pts = series_status.b_pts
                    your_step = game_plan.t_step
                    opponent_pts = series_status.a_pts
                    opponent_step = game_plan.h_step
                
                else:
                    raise ValueError(f"{your_choice=}")


                print()
                print(f"アナウンサー「王国兵の勝ち点は {your_pts} 点")
                time.sleep(msg_spd / 6)
                print(f"　　コクミンの勝ち点は {opponent_pts} 点")
                time.sleep(msg_spd / 6)
                print(f"　　優勝に必要な点は {game_plan.span} 点です！」")
                time.sleep(msg_spd)

                print()
                print(f"　「王国兵は {Converter.face_of_coin_to_str(your_choice)} に、")
                time.sleep(msg_spd / 6)
                print(f"　　コクミンは {Converter.face_of_coin_to_str(Converter.opponent(your_choice))} に張っています！」")
                time.sleep(msg_spd)

                print()
                print(f"　「{Converter.face_of_coin_to_str(your_choice)}が出ると、王国兵に {your_step} 点が、")
                time.sleep(msg_spd / 6)
                print(f"　{Converter.face_of_coin_to_str(Converter.opponent(your_choice))}が出ると、コクミンに {opponent_step} 点が入ります！」")
                time.sleep(msg_spd)

                print()
                print(f"　「しかし、表が出る確率は {game_plan.spec.p * 100:.1f} です！")
                time.sleep(msg_spd / 6)
                print(f"　　さあ、どっちが出るか！？」")
                time.sleep(msg_spd)


                print()
                print(f"国民「 {round_th} 投目」")
                time.sleep(msg_spd)

                # 例：　ピンッ　バシッ　「表が出た」
                face_of_coin = Paragraphs.toss_a_coin(msg_spd=msg_spd, game_plan=game_plan)

                # 例：　「やったぜ！　当たった！」　～うんぬん～　「優勝だな」
                victory_occurred = Paragraphs.open_face_of_coin(msg_spd=msg_spd, game_plan=game_plan, series_status=series_status, your_choice=your_choice, face_of_coin=face_of_coin)

                # どちらかが優勝したらループを抜ける
                if victory_occurred:
                    break


            # 優勝 or 敗退後
            # -------------

            # 数学大臣「ちなみに、先手が勝つ確率は　～うんぬん～　だったんだぜ」
            Paragraphs.spoilers_from_the_minister_of_mathematics(msg_spd=msg_spd, game_plan=game_plan)


            # プレイヤーの優勝
            # FIXME この式は FROZEN_TURN 用
            if (your_choice == HEAD and game_plan.span <= series_status.a_pts) or (your_choice == TAIL and game_plan.span <= series_status.b_pts):
                print()
                print(f"コイントスするチケットを 1 枚もらった。")

                stock += 1

            # 相手の優勝
            else:
                pass
            

            if stock < 1:
                print()
                print(f"こうして、コイントスは終わった。")
                time.sleep(msg_spd)
                break


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
