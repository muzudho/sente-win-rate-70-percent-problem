import time
from library import Specification


class GamePlan():
    """ゲーム企画"""


    def __init__(self, spec, h_step, t_step, span, a_victory_rate, b_victory_rate, no_victory_rate):
        """初期化

        Parameters
        ----------
        p : float
            0.01 単位で 0 ～ 1 を想定
        """

        # ［仕様］
        self._spec = spec

        self._h_step = h_step
        self._t_step = t_step
        self._span = span
        self._a_victory_rate = a_victory_rate
        self._b_victory_rate = b_victory_rate
        self._no_victory_rate = no_victory_rate


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


    @property
    def a_victory_rate(self):
        return self._a_victory_rate


    @property
    def b_victory_rate(self):
        return self._b_victory_rate


    @property
    def no_victory_rate(self):
        return self._no_victory_rate


class Paragraphs():
    """各段落"""


    @staticmethod
    def coins_that_people_had(msg_spd, game_plan):
        """国民が持ってたコイン"""

        print()
        print(f"国民が持っているコインは、")
        time.sleep(msg_spd)

        print()
        print(f"投げて表が出る確率 {game_plan.spec.p * 100:.1f} ％")
        time.sleep(msg_spd / 3)
        print(f"投げてｳﾗが出る確率 {(1 - game_plan.spec.p) * 100:.1f} ％")
        time.sleep(msg_spd / 3)
        print(f"投げて表もｳﾗも出ない確率 {game_plan.spec.failure_rate * 100:.1f} ％")
        time.sleep(msg_spd / 3)
        print(f"の、")
        time.sleep(msg_spd)

        if game_plan.spec.p == 0.5:
            print()
            print(f"フェアコインだ。")
            time.sleep(msg_spd)

        else:
            print()
            print(f"アンフェアコインだ。")
            time.sleep(msg_spd)
