from library import FROZEN_TURN, ALTERNATING_TURN


def make_file_subname(trial_series=None, turn_system_id=None, failure_rate=None, p=None, span=None, t_step=None, h_step=None):
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
    span : int
        ［目標の点数］
    t_step : int
        ［裏番で勝ったときの勝ち点］
    h_step : int
        ［表番で勝ったときの勝ち点］
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


############
# MARK: KDWB
############

class KakukinDataWorkbookFilePaths():
    """［かくきんデータ］関連のファイルパス一覧"""
    @staticmethod
    def as_excel(trial_series, turn_system_id):
        subname = make_file_subname(trial_series=trial_series, turn_system_id=turn_system_id)
        return f'reports/kakukin/auto_generated_kakukin_data{subname}.xlsx'


    @staticmethod
    def as_log():
        return 'logs/kakukin_data_workbook.log'


###########
# MARK: KDS
###########

class KakukinDataSheetFilePaths():
    """［かくきんデータ・シート］関連ファイルパス一覧"""


    @staticmethod
    def as_sheet_csv(trial_series, turn_system_id, failure_rate):
        """大量のシリーズをシミュレーションしたログを保存するファイルへのパスを取得します
        Excel で表示するためのデータファイル
        """
        subname = make_file_subname(trial_series=trial_series, turn_system_id=turn_system_id, failure_rate=failure_rate)
        return f'temp/kakukin_data_sheet/KDS{subname}.csv'    


    @staticmethod
    def as_log(trial_series=None, turn_system_id=None, failure_rate=None):
        subname = make_file_subname(trial_series=trial_series, turn_system_id=turn_system_id, failure_rate=failure_rate)
        return f'logs/kakukin_data_sheet/KDS{subname}.log'


###########
# MARK: TPB
###########

class TheoreticalProbabilityBestFilePaths():
    """理論的確率ベスト・データのファイルパス一覧"""
    @staticmethod
    def as_csv():
        # データ・フォルダーの方に置く
        return f'data/thoretical_probability_best.csv'


    @staticmethod
    def as_log():
        return f'logs/thoretical_probability_best.log'


###########
# MARK: TPR
###########

class TheoreticalProbabilityRatesFilePaths():
    """理論的確率の率データのファイルパス一覧"""


    @staticmethod
    def get_temp_directory_path():
        # './' は付けない
        return 'temp/theoretical_probability_rates'


    @staticmethod
    def get_logs_directory_path():
        # './' は付けない
        return 'logs/theoretical_probability_rates'


    @staticmethod
    def as_csv(spec):
        subname = make_file_subname(turn_system_id=spec.turn_system_id, failure_rate=spec.failure_rate, p=spec.p)
        return f'{TheoreticalProbabilityRatesFilePaths.get_temp_directory_path()}/TPR{subname}.csv'


    @staticmethod
    def as_log(spec):
        subname = make_file_subname(turn_system_id=spec.turn_system_id, failure_rate=spec.failure_rate, p=spec.p)
        return f'{TheoreticalProbabilityRatesFilePaths.get_logs_directory_path()}/TPR{subname}.csv'


##########
# MARK: TP
##########

class TheoreticalProbabilityFilePaths():
    """理論的確率データのファイルパス一覧"""


    @staticmethod
    def get_temp_directory_path():
        # './' は付けない
        return 'temp/theoretical_probability'


    @staticmethod
    def get_logs_directory_path():
        # './' は付けない
        return 'logs/theoretical_probability'


    @staticmethod
    def as_csv(turn_system_id, failure_rate, p):
        subname = make_file_subname(turn_system_id=turn_system_id, failure_rate=failure_rate, p=p)
        return f'{TheoreticalProbabilityFilePaths.get_temp_directory_path()}/TP{subname}.csv'


    @staticmethod
    def as_log(turn_system_id, failure_rate, p):
        subname = make_file_subname(turn_system_id=turn_system_id, failure_rate=failure_rate, p=p)
        return f'{TheoreticalProbabilityFilePaths.get_logs_directory_path()}/TP{subname}.csv'


################
# MARK: StepO1o0
################

class StepO1o0AutomaticFilePaths():
    """自動スクリプト１号のファイルパス一覧"""
    @staticmethod
    def as_log():
        return 'logs/step_o1o0_automatic.log'


############
# MARK: EPDT
############

class EmpiricalProbabilityDuringTrialsFilePaths():
    """試行中の経験的確率データのファイルパス一覧"""


    @staticmethod
    def as_csv(trial_series=None, turn_system_id=None, failure_rate=None):
        """勝ち点を探索した記録ファイルへのパス
        
        Parameters
        ----------
        trial_series : int
            ［試行シリーズ数］
        turn_system_id : int
            ［先後の決め方］
        failure_rate : float
            ［将棋の引分け率］
        """
        subname = make_file_subname(trial_series=trial_series, turn_system_id=turn_system_id, failure_rate=failure_rate)
        return f'./temp/empirical_probability_during_trials/EPDT{subname}.csv'


    @staticmethod
    def as_log(trial_series=None, turn_system_id=None, failure_rate=None):
        """ログ・ファイルへのパス
        
        Parameters
        ----------
        trial_series : int
            ［試行シリーズ数］
        turn_system_id : int
            ［先後の決め方］
        failure_rate : float
            ［将棋の引分け率］
        """
        subname = make_file_subname(trial_series=trial_series, turn_system_id=turn_system_id, failure_rate=failure_rate)
        return f'./logs/empirical_probability_during_trials/EPDT{subname}.csv'


##########
# MARK: SB
##########

class ScoreBoardFilePaths():
    """スコアボードのファイルパス一覧"""
    @staticmethod
    def as_csv(turn_system_id, failure_rate, p, span, t_step, h_step):
        subname = make_file_subname(turn_system_id=turn_system_id, failure_rate=failure_rate, p=p, span=span, t_step=t_step, h_step=h_step)
        return f'output/score_board_view{subname}.csv'


###########
# MARK: SLS
###########

class SimulationLargeSeriesFilePaths():
    """大量のシリーズのシミュレーションのファイルパス一覧"""
    @staticmethod
    def as_log(turn_system_id, failure_rate):
        """大量のシリーズをシミュレーションしたログを保存するファイルへのパスを取得します

        Parameters
        ----------
        turn_system_id : float
            ［先後の選び方の制度］
        failure_rate : float
            ［コインを投げて表も裏も出ない確率］
        """
        subname = make_file_subname(turn_system_id=turn_system_id, failure_rate=failure_rate)
        return f'logs/simulate_large_series{subname}.log'


##########
# MARK: JD
##########

class JapaneseDemoFilePaths():
    """日本語版展示デモファイルへのパス"""


    @staticmethod
    def get_temp_directory_path():
        # './' は付けない
        return 'temp/demo_japanese'


    @staticmethod
    def get_logs_directory_path():
        # './' は付けない
        return 'logs/demo_japanese'


    @staticmethod
    def as_csv(spec, span, t_step, h_step):
        subname = make_file_subname(turn_system_id=spec.turn_system_id, failure_rate=spec.failure_rate, p=spec.p, span=span, t_step=t_step, h_step=h_step)
        return f'{JapaneseDemoFilePaths.get_temp_directory_path()}/VRS{subname}.csv'


    @staticmethod
    def as_log(spec, span, t_step, h_step):
        subname = make_file_subname(turn_system_id=spec.turn_system_id, failure_rate=spec.failure_rate, p=spec.p, span=span, t_step=t_step, h_step=h_step)
        return f'{JapaneseDemoFilePaths.get_logs_directory_path()}/JD{subname}.log'


###########
# MARK: VRS
###########

class VictoryRateSummaryFilePaths():
    """優勝率集計ファイルへのパス"""


    @staticmethod
    def get_temp_directory_path():
        # './' は付けない
        return 'temp/victory_rate_summary'


    @staticmethod
    def get_reports_directory_path():
        # './' は付けない
        return 'reports'


    @staticmethod
    def get_logs_directory_path():
        # './' は付けない
        return 'logs/victory_rate_summary'


    @staticmethod
    def as_csv():
        return f'{VictoryRateSummaryFilePaths.get_temp_directory_path()}/VRS.csv'


    @staticmethod
    def as_workbook_on_reports():
        return f'{VictoryRateSummaryFilePaths.get_reports_directory_path()}/victory_rate_summary.xlsx'


    @staticmethod
    def as_log():
        return f'{VictoryRateSummaryFilePaths.get_logs_directory_path()}/VRS.log'


###########
# MARK: VRD
###########

class VictoryRateDetailFilePaths():
    """優勝率詳細ファイルへのパス"""


    @staticmethod
    def get_temp_directory_path():
        # './' は付けない
        return 'temp/victory_rate_detail'


    @staticmethod
    def get_temp_xl_directory_path():
        # './' は付けない
        return 'temp/victory_rate_detail_xl'


    @staticmethod
    def get_logs_directory_path():
        # './' は付けない
        return 'logs/victory_rate_detail'


    @staticmethod
    def as_csv(spec):
        subname = make_file_subname(turn_system_id=spec.turn_system_id, failure_rate=spec.failure_rate, p=spec.p)
        return f'{VictoryRateDetailFilePaths.get_temp_directory_path()}/VRD{subname}.csv'


    @staticmethod
    def as_workbook_on_temp_xl(spec):
        subname = make_file_subname(turn_system_id=spec.turn_system_id, failure_rate=spec.failure_rate, p=spec.p)
        return f'{VictoryRateDetailFilePaths.get_temp_xl_directory_path()}/VRD{subname}.xlsx'


    @staticmethod
    def as_log(spec):
        subname = make_file_subname(turn_system_id=spec.turn_system_id, failure_rate=spec.failure_rate, p=spec.p)
        return f'{VictoryRateDetailFilePaths.get_logs_directory_path()}/VRD{subname}.log'


############
# MARK: GTWB
############

class GameTreeWorkbookFilePaths():
    """樹形図データのファイルパス一覧"""


    @staticmethod
    def get_temp_directory_path():
        # './' は付けない
        return 'temp/game_tree_wb'


    @staticmethod
    def get_logs_directory_path():
        # './' は付けない
        return 'logs/game_tree_wb'


    @staticmethod
    def as_workbook(spec, span, t_step, h_step):
        subname = make_file_subname(turn_system_id=spec.turn_system_id, failure_rate=spec.failure_rate, p=spec.p, span=span, t_step=t_step, h_step=h_step)
        return f'{GameTreeWorkbookFilePaths.get_temp_directory_path()}/GTWB{subname}.xlsx'


    @staticmethod
    def as_log(spec, span, t_step, h_step):
        subname = make_file_subname(turn_system_id=spec.turn_system_id, failure_rate=spec.failure_rate, p=spec.p, span=span, t_step=t_step, h_step=h_step)
        return f'{GameTreeWorkbookFilePaths.get_logs_directory_path()}/GTWB{subname}.log'


#################
# MARK: GTChecked
#################

class GameTreeCheckedFilePaths():
    """樹形図データのファイルパス一覧"""


    @staticmethod
    def get_temp_directory_path():
        # './' は付けない
        return "temp/game_tree_checked"


    @staticmethod
    def get_logs_directory_path():
        # './' は付けない
        return "logs/game_tree_checked"


    @staticmethod
    def as_csv(spec, span, t_step, h_step):
        subname = make_file_subname(turn_system_id=spec.turn_system_id, failure_rate=spec.failure_rate, p=spec.p, span=span, t_step=t_step, h_step=h_step)
        return f'{GameTreeCheckedFilePaths.get_temp_directory_path()}/GT{subname}.csv'


    @staticmethod
    def as_log(spec, span, t_step, h_step):
        subname = make_file_subname(turn_system_id=spec.turn_system_id, failure_rate=spec.failure_rate, p=spec.p, span=span, t_step=t_step, h_step=h_step)
        return f'{GameTreeCheckedFilePaths.get_logs_directory_path()}/GT{subname}.log'


##########
# MARK: GT
##########

class GameTreeFilePaths():
    """樹形図データのファイルパス一覧"""


    @staticmethod
    def get_temp_directory_path():
        # './' は付けない
        return "temp/game_tree"


    @staticmethod
    def get_logs_directory_path():
        # './' は付けない
        return "logs/game_tree"


    @staticmethod
    def as_csv(spec, span, t_step, h_step):
        subname = make_file_subname(turn_system_id=spec.turn_system_id, failure_rate=spec.failure_rate, p=spec.p, span=span, t_step=t_step, h_step=h_step)
        return f'{GameTreeFilePaths.get_temp_directory_path()}/GT{subname}.csv'


    @staticmethod
    def as_log(spec, span, t_step, h_step):
        subname = make_file_subname(turn_system_id=spec.turn_system_id, failure_rate=spec.failure_rate, p=spec.p, span=span, t_step=t_step, h_step=h_step)
        return f'{GameTreeFilePaths.get_logs_directory_path()}/GT{subname}.log'
