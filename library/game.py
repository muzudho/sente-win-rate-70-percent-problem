from . import Specification


class GamePlan():
    """ゲーム企画"""


    def __init__(self, turn_system_id, p, failure_rate, h_step, t_step, span, a_victory_rate, b_victory_rate, no_victory_rate):
        """初期化

        Parameters
        ----------
        p : float
            0.01 単位で 0 ～ 1 を想定
        """

        # ［仕様］
        self._spec = Specification(
                turn_system_id=turn_system_id,
                failure_rate=failure_rate,
                p=p)

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
