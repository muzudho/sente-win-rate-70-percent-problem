# エコ・システム


#################
# MARK: Candidate
#################
class Candidate():
    """［シリーズ・ルール候補］"""


    def __init__(self, p_error, trial_series, h_step, t_step, span, shortest_coins, upper_limit_coins):

        if not isinstance(trial_series, int):
            raise ValueError(f"［試行シリーズ数］は int 型である必要があります {trial_series=}")

        if not isinstance(h_step, int):
            raise ValueError(f"［表番で勝ったときの勝ち点］は int 型である必要があります {h_step=}")

        if not isinstance(t_step, int):
            raise ValueError(f"［裏番で勝ったときの勝ち点］は int 型である必要があります {t_step=}")

        if not isinstance(span, int):
            raise ValueError(f"［目標の点数］は int 型である必要があります {span=}")

        if not isinstance(shortest_coins, int):
            raise ValueError(f"［最短対局数］は int 型である必要があります {shortest_coins=}")

        if not isinstance(upper_limit_coins, int):
            raise ValueError(f"［上限対局数］は int 型である必要があります {upper_limit_coins=}")

        self._p_error = p_error
        self._trial_series = trial_series
        self._h_step = h_step
        self._t_step = t_step
        self._span = span
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins


    @property
    def p_error(self):
        return self._p_error


    @property
    def trial_series(self):
        return self._trial_series


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
    def shortest_coins(self):
        return self._shortest_coins


    @property
    def upper_limit_coins(self):
        return self._upper_limit_coins


    def as_str(self):
        # NOTE 可読性があり、かつ、パースのしやすい書式にする
        return f'[{self._p_error:.6f} {self._h_step}表 {self._t_step}裏 {self._span}目 {self._shortest_coins}～{self._upper_limit_coins}局 {self._trial_series}試]'


    _re_pattern_of_candidate = None

    @classmethod
    def parse_candidate(clazz, candidate):

        if clazz._re_pattern_of_candidate is None:
            clazz._re_pattern_of_candidate = re.compile(r'([0-9.-]+) (\d+)表 (\d+)裏 (\d+)目 (\d+)～(\d+)局 (\d+)試')

        result = _re_pattern_of_candidate.match(candidate)
        if result:
            return Candidate(
                    p_error=float(result.group(1)),
                    trial_series=float(result.group(7)),
                    h_step=int(result.group(2)),
                    t_step=int(result.group(3)),
                    span=int(result.group(4)),
                    shortest_coins=int(result.group(5)),
                    upper_limit_coins=int(result.group(6)))

        raise ValueError(f"パースできません {candidate=}")


###############################
# MARK: LargeSeriesTrialSummary
###############################
class LargeSeriesTrialSummary():
    """［大量のシリーズを試行した結果］"""


    def __init__(self, specified_trial_series, list_of_trial_results_for_one_series):
        """初期化
        
        Parameters
        ----------
        specified_trial_series : int
            ［シリーズ試行回数］
        list_of_trial_results_for_one_series : list
            ［シリーズ］の結果のリスト
        """

        self._specified_trial_series = specified_trial_series
        self._list_of_trial_results_for_one_series = list_of_trial_results_for_one_series
        self._series_shortest_coins = None
        self._series_longest_coins = None
        self._successful_series = None
        self._failed_series = None

        # （Fully wins）［達成勝ち］数。二次元配列[challenged][PLAYERS]
        self._ful_wins = [
            # 未使用
            None,
            # ［引き分けが起こらなかったシリーズ］
            [
                None,   # 未使用
                None,   # 未使用
                None,   # 未使用
                None,   # Ａさんの［達成勝ち］数
                None],  # Ｂさんの［達成勝ち］数
            # ［引き分けが起こったシリーズ］
            [
                None,   # 未使用
                None,   # 未使用
                None,   # 未使用
                None,   # Ａさんの［達成勝ち］数
                None],  # Ｂさんの［達成勝ち］数
        ]

        # （Points wins）［勝ち点判定勝ち］の件数。二次元配列[challenged][PLAYERS]
        self._pts_wins = [
            # 未使用
            None,
            # ［引き分けが起こらなかったシリーズ］
            [
                None,   # 未使用
                None,   # 未使用
                None,   # 未使用
                None,   # Ａさんの［達成勝ち］数
                None],  # Ｂさんの［達成勝ち］数
            # ［引き分けが起こったシリーズ］
            [
                None,   # 未使用
                None,   # 未使用
                None,   # 未使用
                None,   # Ａさんの［達成勝ち］数
                None],  # Ｂさんの［達成勝ち］数
        ]

        # ［勝者がなかった回数］。ＡさんとＢさんについて。初期値は None
        self._no_wins = None


    @property
    def specified_trial_series(self):
        """シリーズ試行回数"""
        return self._specified_trial_series


    # 共通
    # ----

    @property
    def total(self):
        """シリーズ数"""

        # 検証
        # ----

        # 全部＝［表でも裏でもないものは出なかったシリーズの数］＋［表でも裏でもないものが出たシリーズの数］
        succ = self.successful_series
        fail = self.failed_series
        total_2 = succ + fail

        s_wins_a = self.wins(challenged=SUCCESSFUL, winner=ALICE)
        s_wins_b = self.wins(challenged=SUCCESSFUL, winner=BOB)
        f_wins_a = self.wins(challenged=FAILED, winner=ALICE)
        f_wins_b = self.wins(challenged=FAILED, winner=BOB)

        s_ful_wins_a = self.ful_wins(challenged=SUCCESSFUL, winner=ALICE)
        s_pts_wins_a = self.pts_wins(challenged=SUCCESSFUL, winner=ALICE)
        s_ful_wins_b = self.ful_wins(challenged=SUCCESSFUL, winner=BOB)
        s_pts_wins_b = self.pts_wins(challenged=SUCCESSFUL, winner=BOB)
        f_ful_wins_a = self.ful_wins(challenged=FAILED, winner=ALICE)
        f_pts_wins_a = self.pts_wins(challenged=FAILED, winner=ALICE)
        f_ful_wins_b = self.ful_wins(challenged=FAILED, winner=BOB)
        f_pts_wins_b = self.pts_wins(challenged=FAILED, winner=BOB)

        if s_wins_a != (s_ful_wins_a + s_pts_wins_a):
            raise ValueError(f"合計が合いません {s_wins_a=} != ({s_ful_wins_a=} + {s_pts_wins_a=})")

        if s_wins_b != (s_ful_wins_b + s_pts_wins_b):
            raise ValueError(f"合計が合いません {s_wins_b=} != ({s_ful_wins_b=} + {s_pts_wins_b=})")

        if f_wins_a != (f_ful_wins_a + f_pts_wins_a):
            raise ValueError(f"合計が合いません {f_wins_a=} != ({f_ful_wins_a=} + {f_pts_wins_a=})")

        if f_wins_b != (f_ful_wins_b + f_pts_wins_b):
            raise ValueError(f"合計が合いません {f_wins_b=} != ({f_ful_wins_b=} + {f_pts_wins_b=})")


        # 全部  ＝  ［表でも裏でもないものは出なかったシリーズでＡさんが勝った数］＋
        #           ［表でも裏でもないものは出なかったシリーズでＢさんが勝った数］＋
        #           NOTE これはない？ ［表でも裏でもないものは出なかったシリーズで、かつ勝ち負け付かずのシリーズの数］＋
        #           ［表でも裏でもないものが出たシリーズでＡさんが勝った数］＋
        #           ［表でも裏でもないものが出たシリーズでＢさんが勝った数］＋
        #           ［勝ち負け付かずのシリーズ数］
        #
        # FIXME 合計が合いません。
        #   total_1=21638  total_2=20000
        #   s_wins_a=0(s_ful_wins_a=0 + s_pts_wins_a=0) +
        #   s_wins_b=0(s_ful_wins_b=0 + s_pts_wins_b=0) +
        #   f_wins_a= 9155(f_ful_wins_a=9141 + f_pts_wins_a=14) +
        #   f_wins_b=10793(f_ful_wins_b=10775 + f_pts_wins_b=18) +
        #   self.no_wins=52
        #   succ=13269  fail=6731
        total_1 = s_wins_a + s_wins_b + f_wins_a + f_wins_b + self.no_wins

        if total_1 != total_2:
            raise ValueError(f"""合計が合いません。 {total_1=}  {total_2=}\
   {s_wins_a=}({s_ful_wins_a=} + {s_pts_wins_a=})\
 + {s_wins_b=}({s_ful_wins_b=} + {s_pts_wins_b=})\
 + {f_wins_a=}({f_ful_wins_a=} + {f_pts_wins_a=})\
 + {f_wins_b=}({f_ful_wins_b=} + {f_pts_wins_b=})\
 + {self.no_wins=}\
 {succ=}  {fail=}""")

        return total_1


    @property
    def series_shortest_coins(self):
        """［シリーズ最短対局数］"""
        if self._series_shortest_coins is None:
            self._series_shortest_coins = 2_147_483_647
            for s in self._list_of_trial_results_for_one_series:
                if s.number_of_coins < self._series_shortest_coins:
                    self._series_shortest_coins = s.number_of_coins

        return self._series_shortest_coins


    @property
    def series_longest_coins(self):
        """［シリーズ最長対局数］"""
        if self._series_longest_coins is None:
            self._series_longest_coins = 0
            for s in self._list_of_trial_results_for_one_series:
                if self._series_longest_coins < s.number_of_coins:
                    self._series_longest_coins = s.number_of_coins

        return self._series_longest_coins


    @property
    def successful_series(self):
        """［表も裏も出なかった対局を含まないシリーズ数］"""
        if self._successful_series is None:
            self._successful_series = 0
            for s in self._list_of_trial_results_for_one_series:
                if s.failed_coins < 1:
                    self._successful_series += 1

        return self._successful_series


    @property
    def failed_series(self):
        """［表も裏も出なかった対局を含むシリーズ数］"""
        if self._failed_series is None:
            self._failed_series = 0
            for s in self._list_of_trial_results_for_one_series:
                if 0 < s.failed_coins:
                    self._failed_series += 1

        return self._failed_series


    def ful_wins(self, challenged, winner):
        """elementary_event が［目標の点数］を集めて勝った回数

        TODO 勝利数は、［引き分けが起こったシリーズか、起こってないシリーズか］［目標の点数に達したか、点数差での判定勝ちか］も分けてカウントしたい
        """
        if self._ful_wins[challenged][winner] is None:
            self._ful_wins[challenged][winner] = 0
            for s in self._list_of_trial_results_for_one_series:

                if challenged == SUCCESSFUL:
                    if 0 < s.failed_coins:
                        # ［引き分けが起こらなかったシリーズ］ではない
                        continue
                
                elif challenged == FAILED:
                    if s.failed_coins < 1:
                        # ［引き分けが起こったシリーズ］ではない
                        continue
                
                else:
                    raise ValueError(f"{challenged=}")

                if not s.point_calculation.is_fully_won(winner):
                    # ［目標の点数］を満たしてない
                    continue

                self._ful_wins[challenged][winner] += 1

        return self._ful_wins[challenged][winner]


    def pts_wins(self, challenged, winner):
        """winner が［勝ち点差判定］で loser に勝った回数

        TODO 勝利数は、［引き分けが起こったシリーズか、起こってないシリーズか］［目標の点数に達したか、点数差での判定勝ちか］も分けてカウントしたい
        """
        loser = Converter.opponent(winner)
        if self._pts_wins[challenged][winner] is None:
            self._pts_wins[challenged][winner] = 0
            for s in self._list_of_trial_results_for_one_series:

                if challenged == SUCCESSFUL:
                    if 0 < s.failed_coins:
                        # ［引き分けが起こらなかったシリーズ］ではない
                        continue
                
                elif challenged == FAILED:
                    if s.failed_coins < 1:
                        # ［引き分けが起こったシリーズ］ではない
                        continue
                
                else:
                    raise ValueError(f"{challenged=}")

                if not s.is_pts_won(winner=winner):
                    # ［点差による勝ち］ではないい
                    continue

                self._pts_wins[challenged][winner] += 1


        return self._pts_wins[challenged][winner]


    @property
    def number_of_no_win_match_series(self):
        """［勝敗付かず］で終わったシリーズ数"""

        # ［Ａさんが勝った回数］と［Ｂさんが勝った回数］を数えるメソッドの働きの確認をしている
        #
        #   シリーズ数　－　［Ａさんが勝った回数］　－　［Ｂさんが勝った回数］
        #
        s_wins_a = self.wins(challenged=SUCCESSFUL, winner=ALICE)
        s_wins_b = self.wins(challenged=SUCCESSFUL, winner=BOB)
        f_wins_a = self.wins(challenged=FAILED, winner=ALICE)
        f_wins_b = self.wins(challenged=FAILED, winner=BOB)

        return self.total - (s_wins_a + s_wins_b + f_wins_a + f_wins_b)


    def won_rate(self, success_rate, winner):
        """試行した結果、 winner が loser に勝った率

        ［コインの表か裏が出た確率］ × ［winner が loser に勝った回数］ / ［シリーズ数］

        Parameters
        ----------
        success_rate : float
            ［コインの表か裏が出た確率］
        winner : int
            ［Ａさん］か［Ｂさん］

        """
        return success_rate * self.wins(winner=winner) / self.total


    def won_rate_error(self, success_rate, winner):
        """試行した結果、 winner が loser に勝った率と0.5との誤差］

        ［試行した結果、 winner が loser に勝った率］ - 0.5

        Parameters
        ----------
        success_rate : float
            ［コインの表か裏が出た確率］
        winner : int
            ［コインの表］か［コインの裏］か［Ａさん］か［Ｂさん］
        """
        return self.won_rate(success_rate=success_rate, winner=winner) - 0.5


    def trial_no_win_match_series_rate(self):
        """試行した結果、［勝敗付かず］で終わったシリーズの割合"""
        return self.number_of_no_win_match_series / self.total


    def wins(self, challenged, winner):
        """winner が loser に勝った数"""
        return self.ful_wins(challenged=challenged, winner=winner) + self.pts_wins(challenged=challenged, winner=winner)


    @property
    def no_wins(self):
        """勝者がなかった回数"""
        if self._no_wins is None:
            self._no_wins = 0
            for s in self._list_of_trial_results_for_one_series:
                if s.is_no_win_match():
                    self._no_wins += 1

        return self._no_wins


def calculate_probability(p, H, T):
    """［表側を持っているプレイヤー］が勝つ確率を返します

    TODO オーバーフロー例外に対応したプログラミングをすること

    NOTE ＡさんとＢさんは、表、裏を入れ替えて持つことがあるので、［表側を持っているプレイヤー］が必ずＡさんとは限らない

    ［表側を持っているプレイヤー］が勝つ条件：　表が H 回出る前に裏が T 回出ないこと
    試行回数の考え方：　ゲームは最小で H 回、最大で N = H + T - 1 回のコイン投げで終了します
    確率の計算：　総試行回数 N 回で、表が H 回以上出る確率を計算します

    # パラメータの設定例
    p = 0.7  # 表が出る確率
    H = 7    # ［表側を持っているプレイヤー］が必要な表の回数
    T = 3    # ［裏側を持っているプレイヤー］が必要な裏の回数

    # 計算の実行例
    probability, err = calculate_probability(p, H, T)
    if err is not None:
        pass # エラー時対応

    print(f"［表側を持っているプレイヤー］が勝つ確率: {probability * 100:.2f}%")

    Parameters
    ----------
    p : float
        表が出る確率
    H : int
        ［表側を持っているプレイヤー］が必要な、表の先取回数
    T : int
        ［裏側を持っているプレイヤー］が必要な、裏の先取回数
    
    Returns
    -------
    probability : float
        ［表側を持っているプレイヤー］が勝つ確率
    err : str
        エラーが有ればメッセージを、無ければナンを返す
    """

    from math import comb

    try:

        err = None

        # 裏が出る確率
        q = 1 - p

        # 試行回数
        N = H + T - 1

        # Ａさんが勝つ確率を初期化
        probability = 0.0

        # 表が H 回から N 回出る確率を計算
        for n in range(H, N + 1):
            # 📖 ［累計二項分布］を調べること
            combinations = comb(N, n)   # 組み合わせの数

            # この累乗で、浮動小数点数が大きすぎてオーバーフロー例外を投げることがある
            prob = combinations * (p ** n) * (q ** (N - n))

            probability += prob

        return probability, err
    
    except OverflowError as ex:
        err = f"{ex}"
        return UPPER_OUT_OF_P, err


def try_series(spec, series_rule, specified_trial_series):
    """シリーズをシミュレーションします
    
    Returns
    -------
    large_series_trial_summary : LargeSeriesTrialSummary
        シミュレーション結果
    """
    list_of_trial_results_for_one_series = []

    # シミュレーション
    for round in range(0, specified_trial_series):

        # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
        path_of_face_of_coin = SequenceOfFaceOfCoin.make_sequence_of_playout(
                spec=spec,
                upper_limit_coins=series_rule.upper_limit_coins)

        # 検証
        if len(path_of_face_of_coin) < series_rule.shortest_coins:
            text = f"{spec.p=} 指定の対局シートの長さ {len(path_of_face_of_coin)} は、最短対局数の理論値 {series_rule.shortest_coins} を下回っています。このような対局シートを指定してはいけません"
            print(f"""{text}
{path_of_face_of_coin=}
{series_rule.upper_limit_coins=}
""")
            raise ValueError(text)


        # ［シリーズ］１つ分の試行結果を返す
        trial_results_for_one_series = judge_series(
                spec=spec,
                series_rule=series_rule,
                path_of_face_of_coin=path_of_face_of_coin)
        #print(f"{trial_results_for_one_series.stringify_dump()}")

        
#         if trial_results_for_one_series.number_of_coins < series_rule.shortest_coins:
#             text = f"{spec.p=} 最短対局数の実際値 {trial_results_for_one_series.number_of_coins} が理論値 {series_rule.shortest_coins} を下回った"
#             print(f"""{text}
# {path_of_face_of_coin=}
# {series_rule.upper_limit_coins=}
# {trial_results_for_one_series.stringify_dump('   ')}
# """)
#             raise ValueError(text)

#         if series_rule.upper_limit_coins < trial_results_for_one_series.number_of_coins:
#             text = f"{spec.p=} 上限対局数の実際値 {trial_results_for_one_series.number_of_coins} が理論値 {series_rule.upper_limit_coins} を上回った"
#             print(f"""{text}
# {path_of_face_of_coin=}
# {series_rule.shortest_coins=}
# {trial_results_for_one_series.stringify_dump('   ')}
# """)
#             raise ValueError(text)


        list_of_trial_results_for_one_series.append(trial_results_for_one_series)


    # ［大量のシリーズを試行した結果］
    large_series_trial_summary = LargeSeriesTrialSummary(
            specified_trial_series=specified_trial_series,
            list_of_trial_results_for_one_series=list_of_trial_results_for_one_series)

    return large_series_trial_summary


######################
# MARK: RenamingBackup
######################
class RenamingBackup():
    """ファイルのリネーム・バックアップ
    
    拡張子に .bak を追加する。これは WinMerge のバックアップと同じ拡張子
    """


    def __init__(self, file_path):
        self._file_path = file_path


    @property
    def backup_file_path(self):
        directory_path, file_base = os.path.split(self._file_path)
        return f'{directory_path}/{file_base}.bak'


    def rollback_if_file_crushed(self):
        """対象のファイルを読み込む前に呼び出してください"""

        if os.path.isfile(self.backup_file_path):
            seconds = random.randint(30, 15*60)
            print(f"バックアップ・ファイルが存在しています。対象のファイルは保存中か、保存に失敗している可能性があります。 {seconds} 秒待ってから復元を試みます backup=`{self.backup_file_path}`")
            time.sleep(seconds)

            self._rollback()


    def make_backup(self):
        """既存のバックアップ・ファイルがあれば削除し、既存のファイルのバックアップ・ファイルを作成する"""

        # バックアップ・ファイルが既存ということは、問題が発生しているのでは？
        if os.path.isfile(self.backup_file_path):
            raise ValueError(f"バックアップ・ファイルが既存のまま、バックアップ・ファイルを作成しようとしたので、対象ファイルが破損したまま作業を行った可能性があります。ファイルを確認してください file={self.backup_file_path}")

        # 対象のファイルが存在しなければ、バックアップは作成しません
        if not os.path.isfile(self._file_path):
            return

        new_path = shutil.copy2(
            self._file_path,
            self.backup_file_path)    # 第２引数にファイル名を指定すると、既存なら上書きになる


    def remove_backup(self):
        """バックアップ・ファイルを削除する"""

        # バックアップ・ファイルが存在しなければ、無視します
        if not os.path.isfile(self.backup_file_path):
            return

        s = self.backup_file_path
        # 安全用
        if not s.endswith(".bak"):
            raise ValueError(f"バックアップ・ファイル以外のものを削除しようとしました name={s}")
        os.remove(s)


    def _rollback(self):
        """既存のファイルを削除し、バックアップ・ファイルを正のファイルにリネームする"""
        print(f"[{datetime.datetime.now()}] copy `{self.backup_file_path}` to `{self._file_path}`")

        if not os.path.isfile(self.backup_file_path):
            raise ValueError(f'ロールバックしようとしましたが、指定されたバックアップファイルが見つかりません。保存中でバックアップファイルが削除されたタイミングかもしれません {self.backup_file_path=}')

        try:
            new_path = shutil.copy2(
                self.backup_file_path,
                self._file_path)    # 第２引数にファイル名を指定すると、既存なら上書きになる

        # FIXME FileNotFoundError: [WinError 2] 指定されたファイルが見つかりません。
        except FileNotFoundError as e:
            print(f"""\
{self.backup_file_path=}
{self._file_path=}
""")
            raise


@staticmethod
def get_list_of_basename(dir_path):
    """GT のファイル名一覧取得
    
    📖 [ファイル名のみの一覧を取得](https://note.nkmk.me/python-listdir-isfile-isdir/#_1)
    """
    basename_list = [
        f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))
    ]
    #print(basename_list)

    return basename_list
