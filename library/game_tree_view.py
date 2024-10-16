import datetime


class GameTreeView():


    @staticmethod
    def can_connect_to_parent(curr_gt_record, prev_gt_record, round_th):
        """前ラウンドのノードに接続できるか？"""

        prev_round_th = round_th - 1
        prev_round_no = prev_round_th - 1

        # 先頭行は、ラウンド０も含め、全部親ノードに接続できる
        if curr_gt_record.no == 1:
            return True

        # 先頭行以外の第１ラウンドは、親ノードに接続できない
        elif round_th == 1:
            return False

        try:
            # 前ラウンドは、前行とコインの出目またはレートが異なるか？
            #
            #   NOTE 表0.5、裏0.5 のときレートだけ見てると同じなので、コインの出目も見る
            #
            return curr_gt_record.node_at(prev_round_no).face != prev_gt_record.node_at(prev_round_no).face or curr_gt_record.node_at(prev_round_no).rate != prev_gt_record.node_at(prev_round_no).rate

        # AttributeError: 'NoneType' object has no attribute 'rate'
        except AttributeError as e:
            raise AttributeError(f"{round_th=}  {prev_round_no=}  {prev_gt_record.node_at(prev_round_no)=}  {curr_gt_record.node_at(prev_round_no)=}") from e

        # IndexError: round_th=9  prev_round_no=7  prev_gt_record.len_node_list=6  curr_gt_record.len_node_list=6
        except IndexError as e:
            raise IndexError(f"{round_th=}  {prev_round_no=}  {prev_gt_record.len_node_list=}  {curr_gt_record.len_node_list=}") from e


    @staticmethod
    def is_same_as_avobe(curr_gt_record, prev_gt_record, round_th):
        # 先頭行に兄は無い
        if curr_gt_record.no == 1:
            return False

        curr_round_no = round_th - 1
        # prev_round_th = round_th - 1
        # prev_round_no = prev_round_th - 1

        # 現業と前行は、現ラウンドについて、コインの出目もレートも等しい
        a = curr_gt_record.node_at(curr_round_no).face
        b = prev_gt_record.node_at(curr_round_no).face
        c = curr_gt_record.node_at(curr_round_no).rate
        d = prev_gt_record.node_at(curr_round_no).rate
        print(f"[{datetime.datetime.now()}] {round_th=}  {a=}  {b=}  {c=}  {d=}")
        return a == b and\
            c == d


    @staticmethod
    def is_elder_sibling(curr_gt_record, prev_gt_record, round_th):
        """兄か？"""

        # 先頭行に兄は無い
        if curr_gt_record.no == 1:
            return False

        prev_round_th = round_th - 1
        prev_round_no = prev_round_th - 1

        # 前ラウンドは、現業と前行で、コインの出目かつレートが等しいか？
        return curr_gt_record.node_at(prev_round_no).face == prev_gt_record.node_at(prev_round_no).face and curr_gt_record.node_at(prev_round_no).rate == prev_gt_record.node_at(prev_round_no).rate


    @staticmethod
    def is_younger_sibling(curr_gt_record, next_gt_record, round_th):
        """弟か？

        TODO 下方に弟ノードがあるかどうかは、数行読み進めないと分からない
        """

        # 次行が無ければ弟は無い
        if next_gt_record.no is None:
            return False

        prev_round_th = round_th - 1
        prev_round_no = prev_round_th - 1

        # 次ラウンドは、現業と前行で、コインの出目かつレートが等しいか？
        return curr_gt_record.node_at(prev_round_no).face == next_gt_record.node_at(prev_round_no).face and curr_gt_record.node_at(prev_round_no).rate == next_gt_record.node_at(prev_round_no).rate


    @staticmethod
    def get_kind_connect_to_child(prev_gt_record, curr_gt_record, next_gt_record, round_th):
        """
        子ノードへの接続は４種類の線がある
        
        (1) Horizontal
          .    under_border
        ...__  
          .    None
        
        (2) Down
          .    under_border
        ..+__  
          |    leftside_border
        
        (3) TLetter
          |    l_letter_border
        ..+__  
          |    leftside_border
        
        (4) Up
          |    l_letter_border
        ..+__  
          .    None
        """

        # 上は兄か？
        if GameTreeView.is_elder_sibling(curr_gt_record=curr_gt_record, prev_gt_record=prev_gt_record, round_th=round_th):

            # 下は弟か？
            if GameTreeView.is_younger_sibling(curr_gt_record=curr_gt_record, next_gt_record=next_gt_record, round_th=round_th):
                return 'TLetter'

            else:
                return 'Up'

        # 下は弟か？
        elif GameTreeView.is_younger_sibling(curr_gt_record=curr_gt_record, next_gt_record=next_gt_record, round_th=round_th):
            return 'Down'


        return 'Horizontal'
