from library import WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN


def turn_system_to_file_name(turn_system):
    if turn_system == WHEN_FROZEN_TURN:
        return 'frozen'
    
    if turn_system == WHEN_ALTERNATING_TURN:
        return 'alternating'
    
    raise ValueError(f"{turn_system=}")


def get_analysis_series_log_file_path(turn_system):
    ts = turn_system_to_file_name(turn_system=turn_system)
    return f'output/analysis_series{ts}.log'


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


def get_even_table_log_file_path(turn_system):
    """勝ち点を探索したログ・ファイルへのパス"""
    ts = turn_system_to_file_name(turn_system=turn_system)
    return f'output/even_table{ts}.log'


def get_even_table_csv_file_path(turn_system):
    """勝ち点を探索した記録ファイルへのパス"""
    if turn_system is None:
        ts1 = ''
    else:
        ts1 = f'_{turn_system_to_file_name(turn_system=turn_system)}'

    return f'./data/even_table_ts{ts1}.csv'


def get_muzudho_recommends_points_csv_file_path(turn_system):
    """勝ち点ルールのむずでょセレクション"""
    if turn_system is None:
        ts = ''
    else:
        ts = f"_{turn_system_to_file_name(turn_system=turn_system)}"
    return f'./data/muzudho_recommends_points_ts{ts}.csv'


def get_muzudho_single_points_csv_file_path(turn_system):
    """勝ち点ルールのむずでょ１点セレクション"""
    ts = turn_system_to_file_name(turn_system=turn_system)
    return f'./data/muzudho_single_points_when_frozen_turn.csv'
