from library import WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN


################
# File sub-name
################

def make_file_subname(failure_rate=None, turn_system=None, generation_algorythm=None):
    """ファイル名の部分を作成

    Parameters
    ----------
    failure_rate : float

    turn_system : int

    generation_algorythm : int

    """
    subname = []


    if failure_rate is None:
        pass

    else:
        subname.append('f_{failure_rate}')


    if turn_system is None:
        pass

    elif turn_system == WHEN_FROZEN_TURN:
        subname.append('ts_frozen')
    
    elif turn_system == WHEN_ALTERNATING_TURN:
        subname.append('ts_alternating')

    else:
        raise ValueError(f"{turn_system=}")


    if generation_algorythm is None:
        pass

    elif generation_algorythm == THEORETICAL:
        subname.append('ga_theoretical')
    
    elif generation_algorythm == BRUTE_FORCE:
        subname.append('ga_bruteforce')

    else:
        raise ValueError(f"{generation_algorythm=}")


    return '_'.join(subname)


##################
# Analysis series
##################

def get_analysis_series_log_file_path(turn_system):
    subname = make_file_subname(turn_system=turn_system)
    return f'output/analysis_series_{subname}.log'


##########################
# Simulation large series
##########################

def get_simulation_large_series_log_file_path(failure_rate, turn_system):
    """大量のシリーズをシミュレーションしたログを保存するファイルへのパスを取得します

    Parameters
    ----------
    failure_rate : float
        ［コインを投げて表も裏も出ない確率］
    turn_system : float
        ［先後の選び方の制度］
    """
    subname = make_file_subname(failure_rate=failure_rate, turn_system=turn_system)
    return f'output/simulation_large_series_{subname}.log'


#############
# Even table
#############

def get_even_table_log_file_path(turn_system):
    """勝ち点を探索したログ・ファイルへのパス"""
    subname = make_file_subname(turn_system=turn_system)
    return f'output/even_table_{subname}.log'


def get_even_table_csv_file_path(turn_system):
    """勝ち点を探索した記録ファイルへのパス"""
    subname = make_file_subname(turn_system=turn_system)
    return f'./data/even_table_{subname}.csv'


############################
# Muzudho recommends points
############################

def get_muzudho_recommends_points_csv_file_path(turn_system):
    """勝ち点ルールのむずでょセレクション"""
    subname = make_file_subname(turn_system=turn_system)
    return f'./data/muzudho_recommends_points_{subname}.csv'


def get_muzudho_single_points_csv_file_path(turn_system):
    """勝ち点ルールのむずでょ１点セレクション"""
    subname = make_file_subname(turn_system=turn_system)
    return f'./data/muzudho_single_points_{subname}.csv'
