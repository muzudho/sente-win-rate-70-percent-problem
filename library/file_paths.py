from library import FROZEN_TURN, ALTERNATING_TURN, BRUTE_FORCE, THEORETICAL


################
# File sub-name
################

def make_file_subname(failure_rate=None, turn_system=None, generation_algorythm=None, trials_series=None):
    """ファイル名の部分を作成

    Parameters
    ----------
    failure_rate : float
        ［表も裏も出ない確率］
    turn_system : int
        ［先後の決め方］
    generation_algorythm : int
        ［データ生成アルゴリズム］
    trials_series : int
        ［試行シリーズ回数］
    """
    subname = []


    # ［手番の決め方］
    if turn_system is None:
        pass

    elif turn_system == FROZEN_TURN:
        # NOTE ファイル名は長くならないようにしたい。パースのしやすさは保ちつつ、読みやすさは捨てる
        # frozen turn の略
        subname.append('froze')
    
    elif turn_system == ALTERNATING_TURN:
        # NOTE ファイル名は長くならないようにしたい。パースのしやすさは保ちつつ、読みやすさは捨てる
        # alternating turn の略
        subname.append('alter')

    else:
        raise ValueError(f"{turn_system=}")


    # ［表も裏も出ない確率（％）］
    if failure_rate is None:
        pass

    else:
        subname.append(f'f{failure_rate*100}')


    if generation_algorythm is None:
        pass
    

    # ［生成アルゴリズム］
    elif generation_algorythm == BRUTE_FORCE:
        # NOTE ファイル名は長くならないようにしたい。パースのしやすさは保ちつつ、読みやすさは捨てる
        # brute-force の略
        subname.append('brute')

    elif generation_algorythm == THEORETICAL:
        # NOTE ファイル名は長くならないようにしたい。パースのしやすさは保ちつつ、読みやすさは捨てる
        # theoretical の略
        subname.append('theor')

    else:
        raise ValueError(f"{generation_algorythm=}")


    # ［試行シリーズ回数］
    if trials_series is None:
        pass

    else:
        # try は number of trials series の略
        subname.append(f'try{trials_series}')


    subname = '_'.join(subname)

    if len(subname) < 1:
        return ''
    
    return f'_{subname}'


##################
# Analysis series
##################

def get_analysis_series_log_file_path(turn_system):
    subname = make_file_subname(turn_system=turn_system)
    return f'output/analysis_series{subname}.log'


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
    return f'logs/simulation_large_series{subname}.log'


##########################
# show_table_of_large_event_series_rule.py (表示データの方)
##########################

def get_even_view_csv_file_path(spec):
    """大量のシリーズをシミュレーションしたログを保存するファイルへのパスを取得します
    Excel で表示するためのデータファイル

    Parameters
    ----------
    spec : Specification
        ［仕様］
    """
    subname = make_file_subname(failure_rate=spec.failure_rate, turn_system=spec.turn_system)
    # ファイル名は長くなりすぎないようにする
    return f'logs/even_view{subname}.csv'


#############
# Even table (元データの方)
#############

def get_even_data_csv_file_path(failure_rate=None, turn_system=None, generation_algorythm=None, trials_series=None):
    """勝ち点を探索した記録ファイルへのパス
    
    Parameters
    ----------
    failure_rate : float
        ［将棋の引分け率］
    turn_system : int
        ［先後の決め方］
    generation_algorythm : int
        ［データ生成アルゴリズム］
    trials_series : int
        ［試行シリーズ回数］
    """
    subname = make_file_subname(failure_rate=failure_rate, turn_system=turn_system, generation_algorythm=generation_algorythm, trials_series=trials_series)

    # NOTE ファイル名が長いと、Excel のシート名にそのまま貼り付けられなくて不便なので短くする
    return f'./data/even{subname}.csv'


############################
# Muzudho recommends points
############################

def get_selection_series_rule_csv_file_path(turn_system):
    """勝ち点ルールのむずでょセレクション"""
    subname = make_file_subname(turn_system=turn_system)
    return f'./data/selection_series_rule{subname}.csv'
