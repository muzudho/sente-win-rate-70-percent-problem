#
# python o1o0_demo_japanese.py
#
#   日本語での展示デモ
#

import traceback
import random
import datetime
import time

from library import HEAD, TAIL, ALICE, BOB, FROZEN_TURN, ALTERNATING_TURN, Converter, Specification
from library.file_paths import JapaneseDemoFilePaths
from library_for_game import GamePlan, SeriesStatus, choice_game_plan
from library_for_game.data import fair_list_of_game_plan


DEMO_MONITOR_FILE_PATH = './logs/demo_japanese.log'


class TrialHistory():
    """試行履歴"""


    def __init__(self):
        self._history_of_victory = []


    def append_victory(self, player):
        self._history_of_victory.append(player)


    def get_a_victory_rate_using_simple_moving_average(self, times):
        if len(self._history_of_victory) < times:
            a_victory = 0
            #b_victory = 0
            for player in self._history_of_victory:
                if player == ALICE:
                    a_victory += 1
                elif player == BOB:
                    #b_victory += 1
                    pass
                else:
                    raise ValueError(f"{player=}")

            return a_victory / len(self._history_of_victory) #, b_victory / len(self._history_of_victory)

        a_victory = 0
        #b_victory = 0
        for t in range(0, times):
            player = self._history_of_victory[len(self._history_of_victory) - 1 - t]
            if player == ALICE:
                a_victory += 1
            elif player == BOB:
                #b_victory += 1
                pass
            else:
                raise ValueError(f"{player=}")

        return a_victory / times #, b_victory / times


class DemoResult():


    def __init__(self):
        self._number_of_trial = 0       # 試行回数。 p=0.7,s=2,t=2,h=1 のとき、 400 times ぐらいでほぼ収束
        self._number_of_a_victory = 0
        self._number_of_b_victory = 0


    @property
    def number_of_trial(self):
        return self._number_of_trial


    @property
    def number_of_a_victory(self):
        return self._number_of_a_victory


    @property
    def number_of_b_victory(self):
        return self._number_of_b_victory


    def alice_won(self):
        self._number_of_trial += 1
        self._number_of_a_victory += 1


    def bob_won(self):
        self._number_of_trial += 1
        self._number_of_b_victory += 1


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # メッセージスピード
        msg_spd = 2
        #msg_spd = 0.02


        for demo_th in range(1, 100_000_001):

            # 200 回に 1 回、ゲームデータをリセットする。小ループがあるので、シリーズ数は５倍ぐらい進む
            if demo_th % 100 == 1:
                # ゲーム企画
                game_plan = choice_game_plan(fair_list_of_game_plan)

                demo_result = DemoResult()

                trial_history = TrialHistory()  # 試行履歴


            # プロローグ
            print()
            print(f"わらべ島の先住民たちは、")
            time.sleep(msg_spd / 3)
            print(f"コインを投げて表とｳﾗのどちらが出るかを")
            time.sleep(msg_spd / 3)
            print(f"当てる遊び（コイントス）を続けていた。")
            time.sleep(msg_spd)

            print()
            print(f"そして　わらべ島に")
            time.sleep(msg_spd / 3)
            print(f"きふわらべ王国が建国されると、")
            time.sleep(msg_spd)

            print()
            print(f"島から出土する金属の材質が悪くなり、")
            time.sleep(msg_spd / 3)
            print(f"表とｳﾗの出る確率が異なるコインしか")
            time.sleep(msg_spd / 3)
            print(f"造ることができなくなった。")
            time.sleep(msg_spd)

            print()
            print(f"熱心な国民は、")
            time.sleep(msg_spd / 3)
            print(f"表の出る確率を小数点第３位までの精度で測ることができたが、")
            time.sleep(msg_spd)

            print()
            print(f"このような材質の悪いコイン")
            time.sleep(msg_spd / 3)
            print(f"（先住民からはイカサマコインと呼ばれた）で")
            time.sleep(msg_spd / 3)
            print(f"コイントスすることは諦めていた。")
            time.sleep(msg_spd)

            print()
            print(f"そこで、きふわらべ王国の数学大臣は")
            time.sleep(msg_spd / 3)
            print(f"イカサマコインを使っても、")
            time.sleep(msg_spd)

            print()
            print(f"もし、無限回対決したならば、")
            time.sleep(msg_spd)

            print()
            print(f"まるで表とｳﾗがだいたい均等に出たかのように")
            time.sleep(msg_spd / 3)
            print(f"帳尻を合わせることが期待できるという、")
            time.sleep(msg_spd)

            print()
            print(f"コイントスの方法を次のように示した。")
            time.sleep(msg_spd)


            print()
            print(f"国民の１人は言った。")
            time.sleep(msg_spd)

            print()
            print(f"「無限回も対決できないしなあ」")
            time.sleep(msg_spd)


            print()
            print(f"数学大臣は話しを続けた。")
            time.sleep(msg_spd)


            print()
            print(f"「ここに表が {game_plan.spec.p * 10:.1f} 割出るイカサマコインがある。")
            time.sleep(msg_spd)

            print()
            print(f"　表が出たら勝ち点が {game_plan.h_step} 、")
            time.sleep(msg_spd / 3)
            print(f"　ｳﾗが出たら勝ち点が {game_plan.t_step} とし、")
            time.sleep(msg_spd)

            print()
            print(f"　どちらかが先に {game_plan.span} 点を取るまで")
            time.sleep(msg_spd / 3)
            print(f"　コイントスを続け、")
            time.sleep(msg_spd)

            print()
            print(f"　先に {game_plan.span} 点取った方を優勝とする」")
            time.sleep(msg_spd)


            print()
            print(f"きふわらべ国王は、 {game_plan.spec.p * 10:.1f} 割出るという表が優勝する方に張った。")
            time.sleep(msg_spd)

            print()
            print(f"数学大臣は、 {(1 - game_plan.spec.p) * 10:.1f} 割出るというｳﾗが優勝する方に張った。")
            time.sleep(msg_spd)


            # 新シリーズ開始
            while True:

                # リセット
                series_status = SeriesStatus()

                print()
                print(f"きふわらべ国王「おい、そこらへんのコクミン。")
                time.sleep(msg_spd / 3)
                print(f"　コインを投げろだぜ」")
                time.sleep(msg_spd)


                print()
                print(f"国民「自分で投げればいいのに……」")
                time.sleep(msg_spd)


                # シリーズ中
                for round_th in range(1, 100_000_001):

                    print()
                    print(f"国民「じゃあ {round_th} 投目」")
                    time.sleep(msg_spd)

                    # 0.0 <= X < 1.0
                    outcome = random.random()

                    if outcome < game_plan.spec.p:
                        face_of_coin = HEAD

                        print()
                        print(f"　{Converter.face_of_coin_to_str(face_of_coin)}が出た」")
                        time.sleep(msg_spd)

                        series_status.alice_won(face_of_coin=face_of_coin, h_step=game_plan.h_step)

                        print()
                        print(f"きふわらべ国王「わたしが勝ち点 {game_plan.h_step} をもらって、")
                        time.sleep(msg_spd / 3)
                        print(f"　合計 {series_status.a_pts} 点だぜ。")
                        time.sleep(msg_spd)

                        if game_plan.span <= series_status.a_pts:
                            print()
                            print(f"　{game_plan.span} 点取ったから、")
                            time.sleep(msg_spd / 3)
                            print(f"　わたしの優勝だな」")
                            time.sleep(msg_spd)

                            trial_history.append_victory(player=ALICE)
                            demo_result.alice_won()
                            break

                        else:
                            print()
                            print(f"　{game_plan.span} 点まで")
                            time.sleep(msg_spd / 3)
                            print(f"　まだ {game_plan.span - series_status.a_pts} 点足りないから、")
                            time.sleep(msg_spd / 3)
                            print(f"　続行だな」")
                            time.sleep(msg_spd)

                    else:
                        face_of_coin = TAIL

                        print()
                        print(f"　{Converter.face_of_coin_to_str(face_of_coin)}が出た」")
                        time.sleep(msg_spd)
                        series_status.bob_won(face_of_coin=face_of_coin, t_step=game_plan.t_step)

                        print()
                        print(f"数学大臣「わたしが勝ち点 {game_plan.t_step} をもらって、")
                        time.sleep(msg_spd / 3)
                        print(f"　合計 {series_status.b_pts} 点だぜ」")
                        time.sleep(msg_spd)

                        if game_plan.span <= series_status.b_pts:
                            print()
                            print(f"　{game_plan.span} 点取ったから、")
                            time.sleep(msg_spd / 3)
                            print(f"　わたしの優勝だな」")
                            time.sleep(msg_spd)

                            trial_history.append_victory(player=BOB)
                            demo_result.bob_won()
                            break

                        else:
                            print()
                            print(f"　{game_plan.span} 点まで")
                            time.sleep(msg_spd / 3)
                            print(f"　まだ {game_plan.span - series_status.b_pts} 点足りないから、")
                            time.sleep(msg_spd / 3)
                            print(f"　続行だな」")
                            time.sleep(msg_spd)


                print()
                print(f"きふわらべ国王「これでわたしは {demo_result.number_of_a_victory} 回優勝」")
                time.sleep(msg_spd)

                print()
                print(f"数学大臣「これでわたしは {demo_result.number_of_b_victory} 回優勝」")
                time.sleep(msg_spd)

                # FIXME DEBUG
                sma_times = 20
                sma_percent = trial_history.get_a_victory_rate_using_simple_moving_average(times=sma_times) * 100
                print()
                print(f"※ 直近 {sma_times} シリーズ当たりの国王の優勝率の移動平均 {sma_percent:.1f} ％")
                time.sleep(msg_spd)

                print()
                print(f"国民「 {demo_result.number_of_trial} 回やったぐらいじゃ、")
                time.sleep(msg_spd / 3)
                print(f"　本当に五分五分になってるのか、")
                time.sleep(msg_spd / 3)
                print(f"　よく分からないなあ」")
                time.sleep(msg_spd)


                if demo_result.number_of_trial * 47 / 100 <= demo_result.number_of_a_victory and demo_result.number_of_a_victory < demo_result.number_of_trial * 53 / 100:
                    print()
                    print(f"きふわらべ国王「だいたい　五分五分ということでいいんじゃないか？」")
                    time.sleep(msg_spd)
                
                else:
                    print()
                    print(f"きふわらべ国王「まー、偏ってるかなあ」")
                    time.sleep(msg_spd)


                # ログに残す
                # ---------
                message = f"[{datetime.datetime.now()}] ts={Converter.turn_system_id_to_name(game_plan.spec.turn_system_id)} fr={game_plan.spec.failure_rate} p={game_plan.spec.p} s={game_plan.span} t={game_plan.t_step} h={game_plan.h_step}    {demo_result.number_of_trial} シリーズ目。  {Converter.face_of_coin_to_str(face_of_coin)} の優勝。　表：きふわらべ国王 {demo_result.number_of_a_victory} 回優勝。　ｳﾗ：数学大臣 {demo_result.number_of_b_victory} 回優勝。　国王の勝率 {demo_result.number_of_a_victory / demo_result.number_of_trial * 100:.1f} ％  出目：{series_status._list_str_of_face_of_coin}        直近 {sma_times} シリーズ当たりの国王の優勝率の移動平均 {sma_percent:.1f} ％\n"

                log_file_path = JapaneseDemoFilePaths.as_log(spec=game_plan.spec, span=game_plan.span, t_step=game_plan.t_step, h_step=game_plan.h_step)
                with open(file=log_file_path, mode='a', encoding='utf-8') as f:
                    f.write(message)

                # ２重ログ
                with open(file=DEMO_MONITOR_FILE_PATH, mode='a', encoding='utf-8') as f:
                    f.write(message)
                

                print()
                print(f"きふわらべ国王「もう１回やってみようぜ？」")
                print()
                print()
                time.sleep(msg_spd * 3)


                # 何回かに一度、プロローグに戻る
                if demo_result.number_of_trial % 5 == 0:
                    break


            # 無限ループ中


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
