# Dead code

```
        # 引き分けを１局と数えると、シリーズの中で点数が足らず、決着が付かず、シリーズ全体としての引き分けが増えるので、対応が必要です
        #
        # # # NOTE ルールとして、引き分けを廃止することはできるか？ ----> 両者の実力が等しく、先手後手の有利も等しいとき、真の結果は引き分けがふさわしい。引き分けを消すことはできない
        # # #
        # # # NOTE その場合、先手勝利でいいのでは？ ----> 引き分け率１０％のとき、先手にしろ後手にしろ、そっちの勝率が５％上がってしまった。［目標の点数］を２倍にしてもだいたい同じ
        # # # NOTE 点数が引き分けということは、［上限対局数］を全部引き分けだったということです。引き分けが先手勝ちとか、後手勝ちと決めてしまうと、対局数が１のとき、影響がもろに出てしまう
        # # # NOTE 点数が引き分けのとき、最後に勝った方の勝ちとすればどうなる？ ----> 先手の方が勝つ機会が多いのでは？
        # # # NOTE 引き分けは［両者得点］にしたらどうか？ ----> step を足すのは裏番に有利すぎる。１点を足すのは数学的に意味がない。
        # # # NOTE 引き分けは［両者得点］にし、かつ、引き分けが奇数回なら後手勝ち、偶数回なら先手勝ちにしたらどうか？ ----> 対局数が１のときの影響がでかい
        # # # NOTE 引き分けは、［表勝ち１つの点数］が小さい表番の方に大きく響く？
        # # # NOTE 引き分けは減らせるが、ゼロにはできない、という感じ
        # NOTE タイブレークは、［将棋の引分け率］が上がってきたとき調整が困難。当然、引き分け率が上がるほど裏有利になる


#
#   NOTE 手番を交代する場合、［最大ｎ本勝負］は、（Ａさんの［表だけでの反復実施数］－１）＋（Ａさんの［裏だけでの反復実施数］－１）＋（Ｂさんの［表だけでの反復実施数］－１）＋（Ｂさんの［裏だけでの反復実施数］－１）＋１ になる
#


        #   交互に手番を替えるか、変えないかに関わらず、先手と後手の重要さは p で決まっている。
        #
        #   ［表勝ちだけでの対局数］も、
        #   ［裏勝ちだけでの対局数］数も、 p で決まっている。
        #
        #   ひとまず、リーチしている状況を考えてみよう。
        #
        #   'Ｘ' を、Ａさん（またはＢさん）の［表勝ちだけでの対局数］、
        #   'ｘ' を、Ａさん（またはＢさん）の［裏勝ちだけでの対局数］とする。
        #
        #   リーチしている状況は下の式のようになる。
        #
        #       ２（Ｘ－１）＋２（ｘー１）
        #
        #   ここに、点数の最小単位である　ｘ　を足して、
        #
        #       ２（Ｘ－１）＋２（ｘー１）＋ｘ
        #
        #   としたものが、［上限対局数］だ。
        #
        #
        #   仮に、Ｘ＝１、ｘ＝１　を式に入れてみる。
        #
        #       ２（１－１）＋２（１ー１）＋１　＝　１
        #
        #   対局数は１と分かる。
        #
        #
        #   ・　Ｘ＝１、ｘ＝１ ----> 上限対局数　１
        #   ・　Ｘ＝２、ｘ＝１ ----> 上限対局数　３
        #   ・　Ｘ＝３、ｘ＝１ ----> 上限対局数　５
        #   ・　Ｘ＝３、ｘ＝２ ----> 上限対局数　７
        #   ・　Ｘ＝４、ｘ＝１ ----> 上限対局数　７
        #   ・　Ｘ＝４、ｘ＝２ ----> 上限対局数　９
        #   ・　Ｘ＝４、ｘ＝３ ----> 上限対局数１１
        #
        #   上限対局数は奇数になるようだ。
        #
        #
        #   'Ａ' を、Ａさんの先手一本、'ａ' を、Ａさんの後手一本、
        #   'Ｂ' を、Ｂさんの先手一本、'ｂ' を、Ｂさんの後手一本とする。
        #
        #
        #   Ｘ＝１、ｘ＝１　上限対局数が１のケースの全パターンを見てみよう
        #
        #   (1) Ａ （先） ----> Ａさんの勝ち
        #   (2) ｂ （後） ----> Ｂさんの勝ち
        #
        #   これだと、Ｂさんは後手しか持てなくて厳しそうだ。 p=0.5 ぐらいの、五分五分ということか？
        #
        #
        #   Ｘ＝２、ｘ＝１　上限対局数が３のケースの全パターンを見てみよう
        #
        #                                           通分 先手は 1 点、後手は 2 点
        #                                           ----------------------------
        #   (1) ＡＢＡ（先先先） ----> Ａさんの勝ち     Ａさん 2 点、Ｂさん 1 点
        #   (2) ＡＢｂ（先先後） ----> Ｂさんの勝ち     Ａさん 1 点、Ｂさん 3 点
        #   (3) Ａａ　（先後　） ----> Ａさんの勝ち     Ａさん 3 点
        #   (4) ｂ　　（後　　） ----> Ｂさんの勝ち     Ｂさん 2 点
        #
        #   Ａさんは先手２回で勝てるのに対し、Ｂさんは後手を含めないと勝てない。
        #
        #   NOTE なんか先手のＡさんが有利なような気がするが、コイン投げ試行をしてみると、印象とはべつに成績としてバランスはとれているようだ？
        #
        #   思考：
        #       以下、偶数対局毎に手番を交代するとしたときの、Ｘ＝２、ｘ＝１　３本勝負のケースの全パターン
        #       
        #       (1) ＡＢＢ（先先先） ----> Ｂさんの勝ち
        #       (2) ＡＢａ（先先後） ----> Ａさんの勝ち
        #       (3) Ａａ　（先後　） ----> Ａさんの勝ち
        #       (4) ｂ　　（後　　） ----> Ｂさんの勝ち
        #       
        #       Ｂさんは先手２回で勝てるのに対し、Ａさんは後手を含めないと勝てない。
        #   
        #   
        #   期待勝利機会という考え方。先手一本も後手一本も 0.5。
        #   後手が２回回ってくるのも、２局１セットで考えれば普通。
        #   先手が先にＡさんに回ってきて、そこで２局１セットでないのが不満感？
        #   第３局で終わりにせず、第４局の消化試合までやるべき？ そしたら引き分けが生まれるのでは？ 引き分けにする権利？
        #
        #   NOTE ［先後固定制］と［先後交互制］で、引き分けにならないかどうかは、変わるだろうか？
        #
        #   FIXME 合ってるか、あとで確認
        #


#   * Ａさんが勝つために必要な［表勝ちだけでの対局数］
#   * Ａさんが勝つために必要な［裏勝ちだけでの対局数］
#   * Ａさんが勝つために必要な［表裏の回数の合算］
#   * Ｂさんが勝つために必要な［表勝ちだけでの対局数］
#   * Ｂさんが勝つために必要な［裏勝ちだけでの対局数］
#   * Ｂさんが勝つために必要な［表裏の回数の合算］
```


```
    # ファイルが存在せず、空データフレームが新規作成されたら
    if is_new:

        # ループカウンター
        span = 1        # ［目標の点数］
        t_step = 1      # ［後手で勝ったときの勝ち点］
        h_step = 1      # ［先手で勝ったときの勝ち点］

        print(f"[{datetime.datetime.now()}][{depth=}  turn_system={turn_system_name:11}  p={spec.p:.2f}  failure_rate={spec.failure_rate:.2f}] NEW_FILE")

        # １件も処理してないが、ファイルを保存したいのでフラグを立てる
        number_of_dirty += 1

    # ファイルが存在して、読み込まれたなら
    else:
        # ループカウンター
        if len(df) < 1:
            span = 1        # ［目標の点数］
            t_step = 1      # ［後手で勝ったときの勝ち点］
            h_step = 1      # ［先手で勝ったときの勝ち点］

        else:
            # 途中まで処理が終わってるんだったら、途中から再開したいが。ループの途中から始められるか？

            # TODO 最後に処理された span は？
            span = int(df['span'].max())

            # TODO 最後に処理された span のうち、最後に処理された t_step は？
            t_step = int(df.loc[df['span']==span, 't_step'].max())

            # TODO 最後に処理された span, t_step のうち、最後に処理された h_step は？
            h_step = int(df.loc[(df['span']==span) & (df['t_step']==t_step), 'h_step'].max())

            print(f"[{datetime.datetime.now()}][{depth=}  turn_system={turn_system_name:11}  p={p:.2f}  failure_rate={spec.failure_rate:.2f}] RESTART_ {span=:2}  {t_step=:2}  {h_step=:2}")
```

```
    while span < OUT_OF_UPPER_SPAN + 1:

        calculation_status = automatic_in_loop(
                df=df,
                spec=spec,
                span=span,
                t_step=t_step,
                h_step=h_step,
                depth=depth)

        if calculation_status in [TERMINATED, YIELD]:
            return df, calculation_status, span

        # カウントアップ
        h_step += 1
        if t_step < h_step:
            h_step = 1
            t_step += 1
            if span < t_step:
                t_step = 1
                span += 1
```


```
                        # # 理論値の場合
                        # elif self._generation_algorythm == THEORETICAL:

                        #     # オーバーフロー例外に対応したプログラミングをすること
                        #     latest_p, err = calculate_probability(
                        #             p=spec.p,
                        #             H=latest_series_rule.step_table.get_time_by(challenged=SUCCESSFUL, face_of_coin=HEAD),
                        #             T=latest_series_rule.step_table.get_time_by(challenged=SUCCESSFUL, face_of_coin=TAIL))
                            
                        #     # FIXME とりあえず、エラーが起こっている場合は、あり得ない値をセットして計算を完了させておく
                        #     if err is not None:
                        #         latest_p_error = 0      # 何度計算しても失敗するだろうから、計算完了するようにしておく
                        #     else:
                        #         latest_p_error = latest_p - 0.5
```


```
#             # 該当レコードのキー
#             #
#             #   <class 'pandas.core.series.Series'>
#             #   各行について True, False の論理値を付けたシリーズ
#             #
#             list_of_enable_each_row = (tp_table._df['span']==span) & (tp_table._df['t_step']==t_step) & (tp_table._df['h_step']==h_step)
# #                         print(f"""\
# # {type(list_of_enable_each_row)=}
# # {list_of_enable_each_row=}""")


            # # 該当データが１つも無いなら、新規追加
            # #
            # #   TODO データが飛び番とか無ければ、必ずデータは無いはずだが。一応確認しておく？
            # #
            # is_new = not list_of_enable_each_row.any()
            # if is_new:
            #if len(result_set_df_by_index) < 1:
```


```
            ep_df = self._epdt_table.df
            list_of_enable_each_row = (ep_df['p'] == p)
            if not list_of_enable_each_row.any():
```


```
    @classmethod
    def sub_insert_record(clazz, base_df, welcome_record):
        # 新規レコードが入ったデータフレームを新規作成します
        new_df = pd.DataFrame.from_dict({
            'p': [welcome_record.p],
            'best_p': [welcome_record.best_p],
            'best_p_error': [welcome_record.best_p_error],
            'best_span': [welcome_record.best_span],
            'best_t_step': [welcome_record.best_t_step],
            'best_h_step': [welcome_record.best_h_step],
            'latest_p': [welcome_record.latest_p],
            'latest_p_error': [welcome_record.latest_p_error],
            'latest_span': [welcome_record.latest_span],
            'latest_t_step': [welcome_record.latest_t_step],
            'latest_h_step': [welcome_record.latest_h_step],
            'candidate_history_text': [welcome_record.candidate_history_text]})
        clazz.setup_data_frame(new_df)

        # ２つのテーブルを連結します
        merged_df = pd.concat(
                [base_df, new_df],
                ignore_index=False)  # 真： インデックスを振り直します

        # FIXME 再設定はいるか？
        clazz.setup_data_frame(merged_df, shall_set_index=False)

        return merged_df
```


```
    def get_result_set_by_index(self, span, t_step, h_step):
        """0～複数件のレコードを含むデータフレームを返します"""

        # 絞り込み。 DataFrame型が返ってくる
        result_set_df = self._df.query('span==@span & t_step==@t_step & h_step==@h_step')

        if 1 < len(result_set_df):
            raise ValueError(f"データが重複しているのはおかしいです {len(result_set_df)=}  {span=}  {t_step=}  {h_step=}")

        return result_set_df
```


```
            # # 空振りが多いとき、探索を打ち切ります
            # if self._passage_upper_limit < self._passage_count:
            #     self._is_cutoff = True
            #     self._number_of_passaged += 1

            #     # # 進捗バー
            #     # print('cutoff (procrastinate)', flush=True)
            #     return True     # break

            # print() # 改行
```


```
############
# MARK: TPTR
############

class TheoreticalProbabilityTrialResultsRecord():
    """理論的確率の試行結果レコード"""


    def __init__(self, turn_system_name, failure_rate, p, span, t_step, h_step, shortest_coins, upper_limit_coins, trial_a_win_rate, trial_no_win_match_rate):
        self._turn_system_name = turn_system_name
        self._failure_rate = failure_rate
        self._p = p
        self._span = span
        self._t_step = t_step
        self._h_step = h_step
        self._shortest_coins = shortest_coins
        self._upper_limit_coins = upper_limit_coins
        self._trial_a_win_rate = trial_a_win_rate
        self._trial_no_win_match_rate = trial_no_win_match_rate


    @property
    def turn_system_name(self):
        return self._turn_system_name


    @property
    def failure_rate(self):
        return self._failure_rate


    @property
    def p(self):
        return self._p


    @property
    def span(self):
        return self._span


    @property
    def t_step(self):
        return self._t_step


    @property
    def h_step(self):
        return self._h_step


    @property
    def shortest_coins(self):
        return self._shortest_coins


    @property
    def upper_limit_coins(self):
        return self._upper_limit_coins


    @property
    def trial_a_win_rate(self):
        return self._trial_a_win_rate


    @property
    def trial_no_win_match_rate(self):
        return self._trial_no_win_match_rate


# TODO 用意してるけど使ってない
class TheoreticalProbabilityTrialResultsTable():
    """TODO 理論的確率の試行結果テーブル"""


    _dtype = {
        'turn_system_name':'object',     # string 型は無い？
        'failure_rate':'float64',
        'p':'float64',
        'span':'int64',
        't_step':'int64',
        'h_step':'int64',
        'shortest_coins':'int64',
        'upper_limit_coins':'int64',
        'trial_a_win_rate':'float64',
        'trial_no_win_match_rate':'float64'}


    def __init__(self, df):
        self._df = df


    @classmethod
    def new_empty_table(clazz):
        df = pd.DataFrame.from_dict({
                'turn_system_name': [],
                'failure_rate': [],
                'p': [],
                'span': [],
                't_step': [],
                'h_step': [],
                'shortest_coins': [],
                'upper_limit_coins': [],
                'trial_a_win_rate': [],
                'trial_no_win_match_rate': []})
        clazz.setup_data_frame(df=df)
        return TheoreticalProbabilityTrialResultsTable(df)


    @classmethod
    def read_csv(clazz, spec, new_if_it_no_exists=False):
        """ファイル読込

        Parameters
        ----------
        spec : Specification
            ［仕様］
        new_if_it_no_exists : bool
            ファイルが存在しなければ新規作成するか？
        
        Returns
        -------
        tptr_table : TheoreticalProbabilityTrialResultsTable
            テーブル、無ければナン
        is_new : bool
            新規作成されたか？
        """

        # CSVファイルパス
        csv_file_path = TheoreticalProbabilityTrialResultsFilePaths.as_csv(
                p=spec.p,
                failure_rate=spec.failure_rate,
                turn_system_id=spec.turn_system_id)


        # ファイルが存在しなかった場合
        is_new = not os.path.isfile(csv_file_path)
        if is_new:
            if new_if_it_no_exists:
                tptr_table = TheoreticalProbabilityTrialResultsTable.new_data_frame()
            else:
                tptr_table = None

        else:
            tptr_df = pd.read_csv(csv_file_path, encoding="utf8",
                    dtype=clazz._dtype)
            clazz.setup_data_frame(df=tptr_df)
            tptr_table = TheoreticalProbabilityTrialResultsTable(df=tptr_df)


        return tptr_table, is_new


    @property
    def df(self):
        return self._df


    @classmethod
    def setup_data_frame(clazz, df):
        """データフレームの設定"""

        # データ型の設定
        df.astype(clazz._dtype)

        # インデックスの設定
        df.set_index(
                ['p'],
                inplace=True)   # NOTE インデックスを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身を更新します


    @classmethod
    def sub_insert_record(clazz, base_df, welcome_record):

        # 新規レコードが入ったデータフレームを新規作成します
        new_df = pd.DataFrame.from_dict({
            'turn_system_name': [welcome_record.turn_system_name],
            'failure_rate': [welcome_record.failure_rate],
            'p': [welcome_record.p],
            'span': [welcome_record.span],
            't_step': [welcome_record.t_step],
            'h_step': [welcome_record.h_step],
            'shortest_coins': [welcome_record.shortest_coins],
            'upper_limit_coins': [welcome_record.upper_limit_coins],
            'trial_a_win_rate': [welcome_record.trial_a_win_rate],
            'trial_no_win_match_rate': [welcome_record.trial_no_win_match_rate]})
        clazz.setup_data_frame(new_df)

        # ２つのテーブルを連結します
        merged_df = pd.concat(
                [base_df, new_df],
                ignore_index=True)  # 真： インデックスを振り直します
        clazz.setup_data_frame(merged_df)

        # ソートの設定
        # NOTE ソートをしておかないと、インデックスのパフォーマンスが機能しない
        merged_df.sort_index(
                inplace=True)   # NOTE ソートを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身をソートします

        return merged_df


    def upsert_record(self, index, welcome_record):
        """該当レコードが無ければ新規作成、あれば更新

        Parameters
        ----------
        index : any
            インデックス。整数なら numpy.int64 だったり、複数インデックスなら tuple だったり、型は変わる。
            <class 'numpy.int64'> は int型ではないが、pandas では int型と同じように使えるようだ
        welcome_record : TheoreticalProbabilityBestRecord
            レコード

        Returns
        -------
        shall_record_change : bool
            レコードの新規追加、または更新があれば真。変更が無ければ偽
        """


        # データ変更判定
        # -------------
        is_new_index = index not in self._df['span']

        # インデックスが既存でないなら
        if is_new_index:
            shall_record_change = True
        
        else:
            # 更新の有無判定
            shall_record_change =\
                self._df['span'][index] != welcome_record.span or\
                self._df['t_step'][index] != welcome_record.t_step or\
                self._df['h_step'][index] != welcome_record.h_step or\
                self._df['shortest_coins'][index] != welcome_record.shortest_coins or\
                self._df['upper_limit_coins'][index] != welcome_record.upper_limit_coins or\
                self._df['trial_a_win_rate'][index] != welcome_record.trial_a_win_rate or\
                self._df['trial_no_win_match_rate'][index] != welcome_record.trial_no_win_match_rate


        # 行の挿入または更新
        if shall_record_change:
            self._df.loc[index] = {
                'turn_system_name': welcome_record.turn_system_name,
                'failure_rate': welcome_record.failure_rate,
                # インデックス 'p': welcome_record.p,
                'span': welcome_record.span,
                't_step': welcome_record.t_step,
                'h_step': welcome_record.h_step,
                'shortest_coins': welcome_record.shortest_coins,
                'upper_limit_coins': welcome_record.upper_limit_coins,
                'trial_a_win_rate': welcome_record.trial_a_win_rate,
                'trial_no_win_match_rate': welcome_record.trial_no_win_match_rate}

        if is_new_index:
            # NOTE ソートをしておかないと、インデックスのパフォーマンスが機能しない
            self._df.sort_index(
                    inplace=True)   # NOTE ソートを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身をソートします


        return shall_record_change


    def to_csv(self, spec):
        """ファイル書き出し
        
        Returns
        -------
        csv_file_path : str
            ファイルパス
        """

        # CSVファイルパス
        csv_file_path = TheoreticalProbabilityTrialResultsFilePaths.as_csv(
                p=spec.p,
                failure_rate=spec.failure_rate,
                turn_system_id=spec.turn_system_id)

        self._df.to_csv(csv_file_path,
                columns=['turn_system_name', 'failure_rate', 'p', 'span', 't_step', 'h_step', 'shortest_coins', 'upper_limit_coins', 'trial_a_win_rate', 'trial_no_win_match_rate'],
                index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた

        return csv_file_path


    def for_each(self, on_each):
        """
        Parameters
        ----------
        on_each : func
            record 引数を受け取る関数
        """

        df = self._df

        for         turn_system_name,         failure_rate  ,     p  ,     span  ,     t_step  ,     h_step  ,     shortest_coins  ,     upper_limit_coins  ,     trial_a_win_rate  ,     trial_no_win_match_rate in\
            zip(df['turn_system_name']  , df['failure_rate'], df['p'], df['span'], df['t_step'], df['h_step'], df['shortest_coins'], df['upper_limit_coins'], df['trial_a_win_rate'], df['trial_no_win_match_rate']):

            # レコード作成
            record = EmpiricalProbabilityDuringTrialsRecord(
                    turn_system_name=turn_system_name,
                    failure_rate=failure_rate,
                    p=p,
                    span=span,
                    t_step=t_step,
                    h_step=h_step,
                    shortest_coins=shortest_coins,
                    upper_limit_coins=upper_limit_coins,
                    trial_a_win_rate=trial_a_win_rate,
                    trial_no_win_match_rate=trial_no_win_match_rate)

            on_each(record)
```
