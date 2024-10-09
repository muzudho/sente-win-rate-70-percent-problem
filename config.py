# ［探索の深さ］の上限。この値を含まない
DEFAULT_MAX_DEPTH = 1001    # 実現不可能そうな値


# ［試行シリーズ回数］
DEFAULT_TRIAL_SERIES = 2000


# failure_rate が上がると upper_limit_coins も増えて、処理時間が増えるから、上限を決めておく。また、100% は 0除算が発生するので、それを取り除く意味もある
DEFAULT_UPPER_LIMIT_FAILURE_RATE = 0.7


# 0.95 より大きくなると、計算が指数関数的に膨大になっていくから、上限を決めておく
DEFAULT_UPPER_LIMIT_OF_P = 0.95


# ［目標の点数］の上限。この値を含まない
DEFAULT_UPPER_LIMIT_SPAN = 101       # 反復深化探索で到達するのが実現不可能そうな値
