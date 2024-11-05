import re
from library import Converter, Specification, SeriesRule


###########
# MARK: VRD
###########
class BasenameOfVictoryRateDetailFile():
    """優勝率詳細ファイルのベース名"""


    # ファイル名をパース
    _pattern = re.compile(r'VRD_(alter|froze)_f([\d.]+)_p([\d.]+)\.csv')


    @classmethod
    def to_spec(clazz, basename):
        result = clazz._pattern.match(basename)

        if result:
            turn_system_id = Converter.turn_system_code_to_id(code=result.group(1))
            # １００分率になってるので、0～1 に戻します
            failure_rate = float(result.group(2)) / 100
            p = float(result.group(3)) / 100

            # ［仕様］
            spec = Specification(
                    turn_system_id=turn_system_id,
                    failure_rate=failure_rate,
                    p=p)
            
            return spec
        
        
        return None


############
# MARK: GTWB
############
class BasenameOfGameTreeWorkbookFile():
    """樹形図データのワークブック・ファイルのベース名"""


    # ワークブック・ファイル名をパース
    _pattern = re.compile(r'GTWB_(alter|froze)_f([\d.]+)_p([\d.]+)_s(\d+)_t(\d+)_h(\d+)\.xlsx')


    @classmethod
    def to_series_rule(clazz, basename):
        result = clazz._pattern.match(basename)

        if result:
            turn_system_id = Converter.turn_system_code_to_id(code=result.group(1))
            # １００分率になってるので、0～1 に戻します
            failure_rate = float(result.group(2)) / 100
            p = float(result.group(3)) / 100
            span = int(result.group(4))
            t_step = int(result.group(5))
            h_step = int(result.group(6))

            # ［仕様］
            spec = Specification(
                    turn_system_id=turn_system_id,
                    failure_rate=failure_rate,
                    p=p)

            # ［シリーズ・ルール］
            series_rule = SeriesRule.make_series_rule_base(
                    spec=spec,
                    span=span,
                    t_step=t_step,
                    h_step=h_step)
            
            return series_rule
        
        
        return None


##########
# MARK: GT
##########
class BasenameOfGameTreeFile():
    """樹形図データ・ファイルのベース名"""


    # ファイル名をパース
    _pattern = re.compile(r'GT_(alter|froze)_f([\d.]+)_p([\d.]+)_s(\d+)_t(\d+)_h(\d+)\.csv')


    @classmethod
    def to_series_rule(clazz, basename):
        result = clazz._pattern.match(basename)

        if result:
            turn_system_id = Converter.turn_system_code_to_id(code=result.group(1))
            # １００分率になってるので、0～1 に戻します
            failure_rate = float(result.group(2)) / 100
            p = float(result.group(3)) / 100
            span = int(result.group(4))
            t_step = int(result.group(5))
            h_step = int(result.group(6))

            # ［仕様］
            spec = Specification(
                    turn_system_id=turn_system_id,
                    failure_rate=failure_rate,
                    p=p)

            # ［シリーズ・ルール］
            series_rule = SeriesRule.make_series_rule_base(
                    spec=spec,
                    span=span,
                    t_step=t_step,
                    h_step=h_step)
            
            return series_rule
        
        
        return None


###########
# MARK: TPR
###########
class BasenameOfTheoreticalProbabilityRates():
    """ファイルのベース名"""


    # ファイル名をパース
    _pattern = re.compile(r'TPR_(alter|froze)_f([\d.]+)_p([\d.]+)\.csv')


    @classmethod
    def to_spec(clazz, basename):
        result = clazz._pattern.match(basename)

        if result:
            turn_system_id = Converter.turn_system_code_to_id(code=result.group(1))
            # １００分率になってるので、0～1 に戻します
            failure_rate = float(result.group(2)) / 100
            p = float(result.group(3)) / 100

            # ［仕様］
            spec = Specification(
                    turn_system_id=turn_system_id,
                    failure_rate=failure_rate,
                    p=p)
            
            return spec
        
        
        return None
