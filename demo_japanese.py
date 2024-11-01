#
# python demo_japanese.py
#
#   日本語での展示デモ
#

import traceback
import random
import datetime
import time

from library import ALICE, BOB, FROZEN_TURN, ALTERNATING_TURN, Converter, Specification
from library.file_paths import JapaneseDemoFilePaths


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


class DemoPlan():
    """デモ企画"""


    def __init__(self, turn_system_id, p, failure_rate, h_step, t_step, span):

        # ［仕様］
        self._spec = Specification(
                turn_system_id=turn_system_id,
                failure_rate=failure_rate,
                p=p)

        self._h_step = h_step
        self._t_step = t_step
        self._span = span



    @property
    def spec(self):
        return self._spec


    @property
    def h_step(self):
        return self._h_step


    @property
    def t_step(self):
        return self._t_step


    @property
    def span(self):
        return self._span


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # メッセージスピード
        #mspd = 2
        mspd = 0.02


        for demo_th in range(1, 100_000_001):

            # 200 回に 1 回、ゲームデータをリセットする
            if demo_th % 200 == 1:
                # デモ企画
                demo_plan = DemoPlan(
                        turn_system_id=FROZEN_TURN,
                        p=0.7,              # 0.01 単位で 0 ～ 1 を想定
                        failure_rate=0.0,
                        h_step=1,
                        t_step=2,
                        span=2)

                number_of_trial = 0     # 試行回数。 p=0.7,s=2,t=2,h=1 のとき、 400 times ぐらいでほぼ収束
                number_of_a_victory = 0
                number_of_b_victory = 0

                trial_history = TrialHistory()  # 試行履歴


            # プロローグ
            print()
            print(f"わらべ島の先住民たちは、")
            time.sleep(mspd / 3)
            print(f"コインを投げて表とｳﾗのどちらが出るかを")
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
            print(f"表とｳﾗの出る確率が異なるコインしか")
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
            print(f"まるで表とｳﾗがだいたい均等に出たかのように")
            time.sleep(mspd / 3)
            print(f"帳尻を合わせることが期待できるという、")
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


            print()
            print(f"「ここに表が {demo_plan.spec.p * 10:.1f} 割出るイカサマコインがある。")
            time.sleep(mspd)

            print()
            print(f"　表が出たら勝ち点が {demo_plan.h_step} 、")
            time.sleep(mspd / 3)
            print(f"　ｳﾗが出たら勝ち点が {demo_plan.t_step} とし、")
            time.sleep(mspd)

            print()
            print(f"　どちらかが先に {demo_plan.span} 点を取るまで")
            time.sleep(mspd / 3)
            print(f"　コイントスを続け、")
            time.sleep(mspd)

            print()
            print(f"　先に {demo_plan.span} 点取った方を優勝とする」")
            time.sleep(mspd)


            print()
            print(f"きふわらべ国王は、 {demo_plan.spec.p * 10:.1f} 割出るという表が優勝する方に張った。")
            time.sleep(mspd)

            print()
            print(f"数学大臣は、 {(1 - demo_plan.spec.p) * 10:.1f} 割出るというｳﾗが優勝する方に張った。")
            time.sleep(mspd)


            # 新シリーズ開始
            while True:

                # リセット
                a_pts = 0   # 勝ち点の合計
                b_pts = 0
                round_th = 1
                list_str_of_face_of_coin = ""

                print()
                print(f"きふわらべ国王「おい、そこらへんのコクミン。")
                time.sleep(mspd / 3)
                print(f"　コインを投げろだぜ」")
                time.sleep(mspd)


                print()
                print(f"国民「自分で投げればいいのに……")
                time.sleep(mspd / 3)
                print(f"　じゃあ {round_th} 投目」")
                time.sleep(mspd)

                # 0.0 <= X < 1.0
                outcome = random.random()

                # シリーズ中
                while True:

                    if outcome < demo_plan.spec.p:
                        face_of_coin = '表'

                        print()
                        print(f"　{face_of_coin}が出た」")
                        time.sleep(mspd)
                        a_pts += demo_plan.h_step
                        list_str_of_face_of_coin += face_of_coin

                        print()
                        print(f"きふわらべ国王「わたしが勝ち点 {demo_plan.h_step} をもらって、")
                        time.sleep(mspd / 3)
                        print(f"　合計 {a_pts} 点だぜ。")
                        time.sleep(mspd)

                        if demo_plan.span <= a_pts:
                            print()
                            print(f"　{demo_plan.span} 点取ったから、")
                            time.sleep(mspd / 3)
                            print(f"　わたしの優勝だな」")
                            time.sleep(mspd)

                            trial_history.append_victory(player=ALICE)
                            number_of_a_victory += 1
                            break

                        else:
                            print()
                            print(f"　{demo_plan.span} 点まで")
                            time.sleep(mspd / 3)
                            print(f"　まだ {demo_plan.span - a_pts} 点足りないから、")
                            time.sleep(mspd / 3)
                            print(f"　続行だな」")
                            time.sleep(mspd)

                    else:
                        face_of_coin = 'ｳﾗ'    # 表と裏の字が似すぎているので、変えてみる

                        print()
                        print(f"　{face_of_coin}が出た」")
                        time.sleep(mspd)
                        b_pts += demo_plan.t_step
                        list_str_of_face_of_coin += face_of_coin

                        print()
                        print(f"数学大臣「わたしが勝ち点 {demo_plan.t_step} をもらって、")
                        time.sleep(mspd / 3)
                        print(f"　合計 {b_pts} 点だぜ」")
                        time.sleep(mspd)

                        if demo_plan.span <= b_pts:
                            print()
                            print(f"　{demo_plan.span} 点取ったから、")
                            time.sleep(mspd / 3)
                            print(f"　わたしの優勝だな」")
                            time.sleep(mspd)

                            trial_history.append_victory(player=BOB)
                            number_of_b_victory += 1
                            break

                        else:
                            print()
                            print(f"　{demo_plan.span} 点まで")
                            time.sleep(mspd / 3)
                            print(f"　まだ {demo_plan.span - b_pts} 点足りないから、")
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

                # FIXME DEBUG
                sma_times = 20
                sma_percent = trial_history.get_a_victory_rate_using_simple_moving_average(times=sma_times) * 100
                print()
                print(f"※ 直近 {sma_times} シリーズ当たりの国王の優勝率の移動平均 {sma_percent:.1f} ％")
                time.sleep(mspd)

                print()
                print(f"国民「 {number_of_trial} 回やったぐらいじゃ、")
                time.sleep(mspd / 3)
                print(f"　本当に五分五分になってるのか、")
                time.sleep(mspd / 3)
                print(f"　よく分からないなあ」")
                time.sleep(mspd)


                if number_of_trial * 47 / 100 <= number_of_a_victory and number_of_a_victory < number_of_trial * 53 / 100:
                    print()
                    print(f"きふわらべ国王「だいたい　五分五分ということでいいんじゃないか？」")
                    time.sleep(mspd)
                
                else:
                    print()
                    print(f"きふわらべ国王「まー、偏ってるかなあ」")
                    time.sleep(mspd)


                # ログに残す
                # ---------

                log_file_path = JapaneseDemoFilePaths.as_log(spec=demo_plan.spec, span=demo_plan.span, t_step=demo_plan.t_step, h_step=demo_plan.h_step)
                with open(file=log_file_path, mode='a', encoding='utf-8') as f:
                    f.write(f"[{datetime.datetime.now()}] ts={Converter.turn_system_id_to_name(demo_plan.spec.turn_system_id)} fr={demo_plan.spec.failure_rate} p={demo_plan.spec.p} s={demo_plan.span} t={demo_plan.t_step} h={demo_plan.h_step}    {number_of_trial} シリーズ目。  {face_of_coin} の優勝。　表：きふわらべ国王 {number_of_a_victory} 回優勝。　ｳﾗ：数学大臣 {number_of_b_victory} 回優勝。　国王の勝率 {number_of_a_victory / number_of_trial * 100:.1f} ％  出目：{list_str_of_face_of_coin}        直近 {sma_times} シリーズ当たりの国王の優勝率の移動平均 {sma_percent:.1f} ％\n")


                print()
                print(f"きふわらべ国王「もう１回やってみようぜ？」")
                print()
                print()
                time.sleep(mspd * 3)


                # 何回かに一度、プロローグに戻る
                if number_of_trial % 5 == 0:
                    break


            # 無限ループ中


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
