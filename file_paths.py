from library import WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN


def turn_system_to_file_name(turn_system):
    if turn_system == WHEN_FROZEN_TURN:
        return '_when_frozen_turn'
    
    if turn_system == WHEN_ALTERNATING_TURN:
        return '_when_alternating_turn'
    
    raise ValueError(f"{turn_system=}")


def get_simulation_large_series_log_file_path(p, failure_rate, turn_system):
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

    ts = turn_system_to_file_name(turn_system=turn_system)

    return f'output/simulation_large_series_p{p}_f{failure_rate}{ts}.log'


def get_even_log_file_path(turn_system):
    """勝ち点を探索したログ・ファイルへのパス"""
    ts = turn_system_to_file_name(turn_system=turn_system)
    return f'output/generate_even{ts}.log'


def get_even_csv_file_path(turn_system):
    """勝ち点を探索した記録ファイルへのパス"""
    ts = turn_system_to_file_name(turn_system=turn_system)
    return f'./data/generate_even{ts}.csv'
