from library import FROZEN_TURN, ALTERNATING_TURN


def make_file_subname(trial_series=None, turn_system_id=None, failure_rate=None, p=None, h_step=None, t_step=None, span=None):
    """ファイル名の部分を作成

    Parameters
    ----------
    trial_series : int
        ［試行シリーズ数］
    turn_system_id : int
        ［先後の決め方］
    failure_rate : float
        ［表も裏も出ない確率］
    p : float
        ［表が出る確率］
    h_step : int
        ［表番で勝ったときの勝ち点］
    t_step : int
        ［裏番で勝ったときの勝ち点］
    span : int
        ［目標の点数］
    """
    subname = []


    # ［試行シリーズ数］
    #
    #   NOTE 試行回数が異なれば、試行回数が少ないデータが混じってしまうと、全く内容が正しくなくなるという考え方で、重要度を１番上にする
    #
    if trial_series is None:
        pass

    else:
        # try は number of trials series の略
        subname.append(f'try{trial_series}')


    # ［手番の決め方］
    if turn_system_id is None:
        pass

    elif turn_system_id == FROZEN_TURN:
        # NOTE ファイル名は長くならないようにしたい。パースのしやすさは保ちつつ、読みやすさは捨てる
        # frozen turn の略
        subname.append('froze')
    
    elif turn_system_id == ALTERNATING_TURN:
        # NOTE ファイル名は長くならないようにしたい。パースのしやすさは保ちつつ、読みやすさは捨てる
        # alternating turn の略
        subname.append('alter')

    else:
        raise ValueError(f"{turn_system_id=}")


    # ［表も裏も出ない確率（％）］
    if failure_rate is None:
        pass

    else:
        subname.append(f'f{failure_rate*100:.1f}')


    # ［表が出る確率（％）］
    if p is None:
        pass

    else:
        subname.append(f'p{p*100:.1f}')

    # NOTE ［表番で勝ったときの勝ち点］≦［裏番で勝ったときの勝ち点］≦［目標の点数］
    #
    # ［目標の点数］
    if span is None:
        pass

    else:
        subname.append(f's{span}')


    # ［裏番で勝ったときの勝ち点］
    if t_step is None:
        pass

    else:
        subname.append(f't{t_step}')


    # ［表番で勝ったときの勝ち点］
    if h_step is None:
        pass

    else:
        subname.append(f'h{h_step}')


    # サブ・ファイル名の連結
    subname = '_'.join(subname)

    if len(subname) < 1:
        return ''
    
    return f'_{subname}'


###########
# MARK: KDF
###########

class KakukinDataFilePaths():
    """［かくきんデータ］関連のファイルパス一覧"""
    @staticmethod
    def as_excel(turn_system_id, trial_series):
        subname = make_file_subname(turn_system_id=turn_system_id, trial_series=trial_series)
        return f'reports/auto_generated_kakukin_data{subname}.xlsx'


    @staticmethod
    def as_sheet_csv(failure_rate, turn_system_id, trial_series=None):
        """大量のシリーズをシミュレーションしたログを保存するファイルへのパスを取得します
        Excel で表示するためのデータファイル
        """
        subname = make_file_subname(failure_rate=failure_rate, turn_system_id=turn_system_id, trial_series=trial_series)
        # ファイル名は長くなりすぎないようにする
        return f'temp/kakukin_data_sheet/KDS{subname}.csv'    


###########
# MARK: TPB
###########

class TheoreticalProbabilityBestFilePaths():
    """理論的確率ベスト・データのファイルパス一覧"""
    @staticmethod
    def as_csv():
        # データ・フォルダーの方に置く
        return f'data/thoretical_probability_best.csv'


##########
# MARK: TP
##########

class TheoreticalProbabilityFilePaths():
    """理論的確率データのファイルパス一覧"""
    @staticmethod
    def as_csv(p, failure_rate, turn_system_id):
        subname = make_file_subname(p=p, failure_rate=failure_rate, turn_system_id=turn_system_id)
        # 大量に生成されるので、GitHubに上げたくないので logs の方に入れる
        return f'temp/theoretical_probability/TP{subname}.csv'


################
# MARK: StepO1o0
################

class StepO1o0AutomaticFilePaths():
    """自動スクリプト１号のファイルパス一覧"""
    @staticmethod
    def as_log():
        return 'logs/step_o1o0_automatic.log'


############
# MARK: TPTR
############

class TheoreticalProbabilityTrialResultsFilePaths():
    """理論的確率の試行結果データのファイルパス一覧"""
    @staticmethod
    def as_csv(p, failure_rate, turn_system_id):
        subname = make_file_subname(p=p, failure_rate=failure_rate, turn_system_id=turn_system_id)
        # 大量に生成されるので、GitHubに上げたくないので logs の方に入れる
        return f'temp/theoretical_probability_trial_results/TPTR{subname}.csv'


############
# MARK: EPDT
############

class EmpiricalProbabilityDuringTrialsFilePaths():
    """試行中の経験的確率データのファイルパス一覧"""
    @staticmethod
    def as_csv(failure_rate=None, turn_system_id=None, trial_series=None):
        """勝ち点を探索した記録ファイルへのパス
        
        Parameters
        ----------
        failure_rate : float
            ［将棋の引分け率］
        turn_system_id : int
            ［先後の決め方］
        trial_series : int
            ［試行シリーズ数］
        """
        subname = make_file_subname(failure_rate=failure_rate, turn_system_id=turn_system_id, trial_series=trial_series)

        # NOTE ファイル名が長いと、Excel のシート名にそのまま貼り付けられなくて不便なので短くする
        return f'./temp/empirical_probability_during_trials/EPDT{subname}.csv'


##########
# MARK: SB
##########

class ScoreBoardFilePaths():
    """スコアボードのファイルパス一覧"""
    @staticmethod
    def as_csv(p, failure_rate, turn_system_id, h_step, t_step, span):
        subname = make_file_subname(p=p, failure_rate=failure_rate, turn_system_id=turn_system_id, h_step=h_step, t_step=t_step, span=span)
        return f'output/score_board_view{subname}.csv'


###########
# MARK: SLS
###########

class SimulationLargeSeriesFilePaths():
    """大量のシリーズのシミュレーションのファイルパス一覧"""
    @staticmethod
    def as_log(failure_rate, turn_system_id):
        """大量のシリーズをシミュレーションしたログを保存するファイルへのパスを取得します

        Parameters
        ----------
        failure_rate : float
            ［コインを投げて表も裏も出ない確率］
        turn_system_id : float
            ［先後の選び方の制度］
        """
        subname = make_file_subname(failure_rate=failure_rate, turn_system_id=turn_system_id)
        return f'logs/simulation_large_series{subname}.log'
