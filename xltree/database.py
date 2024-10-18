import re
import datetime
import pandas as pd

from xltree.library import INDENT


############
# MARK: Node
############
class TreeNode():
    """ノード（節）
    ノードの形に合わせて改造してください"""

    def __init__(self, edge_text, text):
        """初期化
        
        Parameters
        ----------
        edge_text : str
            辺のテキスト
        text : str
            節のテキスト
        """
        self._edge_text = edge_text
        self._text = text


    @property
    def edge_text(self):
        return self._edge_text


    @property
    def text(self):
        return self._text


    def stringify_dump(self, indent):
        succ_indent = indent + INDENT
        return f"""\
{indent}TreeNode
{indent}--------
{succ_indent}{self._edge_text=}
{succ_indent}{self._text=}
"""


##############
# MARK: Record
##############
class TreeRecord():


    def __init__(self, no, node_list):
        """初期化
        
        Parameters
        ----------
        no : int
            1から始まる連番。数詞は件
        node_list : list<TreeNode>
            ノードのリスト。
            第０層は根
        """
        self._no = no
        self._node_list = node_list


    @staticmethod
    def new_empty(specified_length_of_nodes):
        return TreeRecord(
                no=None,
                node_list=[None] * specified_length_of_nodes)


    @property
    def no(self):
        return self._no


    @property
    def len_node_list(self):
        return len(self._node_list)


    def node_at(self, depth_th):
        """
        Parameters
        ----------
        round_th : int
            th は forth や fifth の th。
            例：根なら０を指定してください。
            例：第１層なら 1 を指定してください
        """

        # NOTE -1 を指定すると最後尾の要素になるが、固定長配列の最後尾の要素が、思っているような最後尾の要素とは限らない。うまくいかない
        if depth_th < 0:
            raise ValueError(f'depth_th に負数を設定しないでください。意図した動作はしません {depth_th=}')

        return self._node_list[depth_th]


    def update(self, no=None, node_list=None):
        """no inplace
        何も更新しなければシャロー・コピーを返します"""

        def new_or_default(new, default):
            if new is None:
                return default
            return new

        return TreeRecord(
                no=new_or_default(no, self._no),
                node_list=new_or_default(node_list, self._node_list))


    def stringify_dump(self, indent):
        succ_indent = indent + INDENT

        blocks = []
        for node in self._node_list:
            blocks.append(node.stringify_dump(succ_indent))

        return f"""\
{indent}TreeRecord
{indent}----------
{succ_indent}{self._no=}
{'\n'.join(blocks)}
"""


    def get_th_of_leaf_node(self):
        """葉要素の層番号を取得。
        th は forth や fifth の th。
        葉要素は、次の層がない要素"""

        for depth_th in range(0, len(self._node_list)):
            nd = self._node_list[depth_th]
            if nd is None or nd.text is None:
                return depth_th

        return len(self._node_list)


##############
# MARK: Record
##############
class TreeTable():
    """樹形図データのテーブル"""


    # 列が可変長
    _dtype = {}

    @classmethod
    def create_dtype(clazz, specified_length_of_edges, specified_length_of_nodes):
        """dtypeの辞書を作成します

        Parameters
        ----------
        specified_length_of_edges : int
            エッジ数。空欄の根を含むとみなして数える
        specified_length_of_nodes : int
            ノード数。根を含む
        """

        # no はインデックスなので含めない
        clazz._dtype = {}

        # ノードだけ根を含む
        clazz._dtype['node0'] = 'object'    # string 型は無いので object 型にする

        for edge_th in range(1, specified_length_of_edges):
            clazz._dtype[f'edge{edge_th}'] = 'object'

        for node_th in range(1, specified_length_of_nodes):
            clazz._dtype[f'node{node_th}'] = 'object'

        return clazz._dtype


    @staticmethod
    def create_column_name_list(specified_length_of_nodes, include_index):
        column_name_list = []

        if include_index:
            column_name_list.append('no')

        # 根ノードは必ず追加
        column_name_list.append('node0')

        for node_th in range(1, specified_length_of_nodes):
            column_name_list.append(f'edge{node_th}')
            column_name_list.append(f'node{node_th}')

        return column_name_list


    def __init__(self, df, length_of_edges, length_of_nodes):
        self._df = df
        self._length_of_edges = length_of_edges
        self._length_of_nodes = length_of_nodes


    @classmethod
    def new_empty_table(clazz, specified_length_of_edges, specified_length_of_nodes):
        column_name_list = TreeTable.create_column_name_list(
                specified_length_of_nodes=specified_length_of_nodes,
                include_index=True) # 'no' は後でインデックスに変換

        df = pd.DataFrame(
                columns=column_name_list)
        
        clazz.setup_data_frame(df=df, specified_length_of_edges=specified_length_of_edges, specified_length_of_nodes=specified_length_of_nodes, shall_set_index=True)
        return TreeTable(df=df, length_of_edges=specified_length_of_edges, length_of_nodes=specified_length_of_nodes)


    @classmethod
    def find_list_size_of_column(clazz, df, prefix, start_number):
        """'prefix{n}'列を数える。nは0から始まる
        
        列名を左から見ていくと、 node0, node1, node2 といった形で 0から始まる昇順の連番が付いている "node数" 形式の列名が見つかるものとします

        Parameters
        ----------
        df : DataFrame
            データフレーム
        prefix : str
            列名の数字の前の部分。 'node' または 'edge'
        start_number : int
            開始番号。エッジなら 1、ノードなら 0
        """
        expected_node_th = start_number    # 次は 'node{0}' を期待する
        pattern = re.compile(prefix + r'(\d+)')
        for column_name in df.columns.values:
            result = pattern.match(column_name)
            if result:
                node_th = int(result.group(1))
                if expected_node_th == node_th:
                    expected_node_th += 1

        # テーブルにあるノード数
        #print(f"[{datetime.datetime.now()}] Table has {expected_node_th} nodes root node included")

        return expected_node_th     # end 番号に相当


    @classmethod
    def from_csv(clazz, file_path):
        """ファイル読込

        Parameters
        ----------
        file_path : str
            CSVファイルパス
        
        Returns
        -------
        table : TreeTable
            テーブル、またはナン
        file_read_result : FileReadResult
            ファイル読込結果
        """
        df = pd.read_csv(file_path, encoding="utf8", index_col=['no'])

        # エッジ数、ノード数を数えたい。エッジは 'edge1' から数えはじめるが、'edge0' があるものとみなして数える
        length_of_edges = TreeTable.find_list_size_of_column(df=df, prefix='edge', start_number=1)
        length_of_nodes = TreeTable.find_list_size_of_column(df=df, prefix='node', start_number=0)

        # テーブルに追加の設定
        clazz.setup_data_frame(df=df, specified_length_of_edges=length_of_edges, specified_length_of_nodes=length_of_nodes, shall_set_index=False)

        return TreeTable(df=df, length_of_edges=length_of_edges, length_of_nodes=length_of_nodes)


    @property
    def df(self):
        return self._df


    @property
    def length_of_edges(self):
        """CSV読取時に作成したエッジのリストのリストサイズ。edge[0]=None とする"""
        return self._length_of_edges


    @property
    def length_of_nodes(self):
        """CSV読取時に数えたノード数"""
        return self._length_of_nodes


    @classmethod
    def setup_data_frame(clazz, df, specified_length_of_edges, specified_length_of_nodes, shall_set_index):
        """データフレームの設定"""

        if shall_set_index:
            # インデックスの設定
            df.set_index('no',
                    inplace=True)   # NOTE インデックスを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身を更新します

        # データ型の設定
        dtype = clazz.create_dtype(specified_length_of_edges=specified_length_of_edges, specified_length_of_nodes=specified_length_of_nodes)
        #print(f"setup_data_frame {dtype=}")
        df.astype(dtype)


    def upsert_record(self, welcome_record):
        """該当レコードが無ければ新規作成、あれば更新

        Parameters
        ----------
        welcome_record : GameTreeRecord
            レコード

        Returns
        -------
        shall_record_change : bool
            レコードの新規追加、または更新があれば真。変更が無ければ偽
        """

        # インデックス
        # -----------
        # index : any
        #   インデックス。整数なら numpy.int64 だったり、複数インデックスなら tuple だったり、型は変わる。
        #   <class 'numpy.int64'> は int型ではないが、pandas では int型と同じように使えるようだ
        index = welcome_record.no

        # データ変更判定
        # -------------
        is_new_index = index not in self._df.index

        # インデックスが既存でないなら
        if is_new_index:
            shall_record_change = True

        else:
            # 更新の有無判定
            shall_record_change = True
            # no はインデックスなので含めない

            # 根は必ず含める
            if self._df['node0'][index] != welcome_record.node_at(0).text:
                shall_record_change = False
            
            for node_th in range(1, self._length_of_nodes):
                if self._df[f'node{node_th}'][index] != welcome_record.node_at(node_th).text:
                    shall_record_change = False
                    break


        # 行の挿入または更新
        if shall_record_change:

            # no はインデックスなので含めない
            dictionary = {}

            # 根は必ず含める
            dictionary['node0'] = welcome_record.node_at(0).text

            for node_th in range(1, self.length_of_nodes):
                dictionary[f'edge{node_th}'] = welcome_record.node_at(node_th).edge_text
                dictionary[f'node{node_th}'] = welcome_record.node_at(node_th).text

            self._df.loc[index] = dictionary


        if is_new_index:
            # NOTE ソートをしておかないと、インデックスのパフォーマンスが機能しない
            self._df.sort_index(
                    inplace=True)   # NOTE ソートを指定したデータフレームを戻り値として返すのではなく、このインスタンス自身をソートします


        return shall_record_change


    def to_csv(self, file_path):
        """ファイル書き出し
        
        Parameters
        ----------
        file_path : str
            CSVファイルパス
        """

        column_name_list = TreeTable.create_column_name_list(
                specified_length_of_nodes=self.length_of_nodes,
                include_index=False) # no はインデックスなので含めない

        self._df.to_csv(
                csv_file_path,
                columns=column_name_list)


    def for_each(self, on_each):
        """
        Parameters
        ----------
        on_each : func
            TreeRecord 引数を受け取る関数
        """

        df = self._df

        node_list = [None] * self._length_of_nodes
        edge_list = [None] * self._length_of_nodes

        for row_number in range(0, len(df)):
            # no はインデックス
            no = df.index[row_number]

            node_list = []

            # 根
            node_list.append(TreeNode(edge_text=None, text=df.at[no, f'node0']))

            # 中間～葉ノード
            for node_th in range(1, self._length_of_nodes):

                # エッジはオプション
                if node_th < self._length_of_edges:
                    edge_text = df.at[no, f'edge{node_th}']
                else:
                    edge_text = None

                node_list.append(TreeNode(edge_text=edge_text, text=df.at[no, f'node{node_th}']))


            # レコード作成
            record = TreeRecord(
                    no=no,
                    node_list=node_list)

            on_each(row_number, record)
