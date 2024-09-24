from library import WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN


def get_simulation_large_series_file(p, failure_rate, turn_system):
    """大量のシリーズをシミュレーションしたログを保存するファイルへのパスを取得します

    Parameters
    ----------
    p : float
        ［コインを投げて表が出る確率］
    failure_rate : float
        ［コインを投げて表も裏も出ない確率］
    turn_system : float
        ［先後の選び方の制度］
    """

    if turn_system == WHEN_FROZEN_TURN:
        ts = '_when_frozen_turn'
    elif turn_system == WHEN_ALTERNATING_TURN:
        ts = '_when_alternating_turn'
    else:
        raise ValueError(f"{turn_system=}")

    return f'output/simulation_large_series_p{p}_f{failure_rate}{ts}.log'
