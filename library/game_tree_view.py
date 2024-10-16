class GameTreeView():


    def can_connect_to_parent(prev_gt_record, curr_gt_record, round_th):
        """前ラウンドのノードに接続できるか？"""

        prev_round_th = round_th - 1
        prev_round_no = prev_round_th - 1

        # 先頭行は、ラウンド０も含め、全部親ノードに接続できる
        if curr_gt_record.no == 1:
            return True

        try:
            # 前ラウンドは、前行とコインの出目またはレートが異なるか？
            #
            #   NOTE 表0.5、裏0.5 のときレートだけ見てると同じなので、コインの出目も見る
            #
            return prev_gt_record.node_at(prev_round_no).face != curr_gt_record.node_at(prev_round_no).face or prev_gt_record.node_at(prev_round_no).rate != curr_gt_record.node_at(prev_round_no).rate

        # AttributeError: 'NoneType' object has no attribute 'rate'
        except AttributeError as e:
            raise AttributeError(f"{round_th=}  {prev_round_no=}  {prev_gt_record.node_at(prev_round_no)=}  {curr_gt_record.node_at(prev_round_no)=}") from e

        # IndexError: round_th=9  prev_round_no=7  prev_gt_record.len_node_list=6  curr_gt_record.len_node_list=6
        except IndexError as e:
            raise IndexError(f"{round_th=}  {prev_round_no=}  {prev_gt_record.len_node_list=}  {curr_gt_record.len_node_list=}") from e


    def is_elder_sibling(prev_gt_record, curr_gt_record, next_gt_record, round_th):
        """兄か？"""

        # 先頭行に兄は無い
        if curr_gt_record.no == 1:
            return False

        prev_round_th = round_th - 1
        prev_round_no = prev_round_th - 1

        # 全ラウンドのレートが同じか？
        pass


    def is_younger_sibling(prev_gt_record, curr_gt_record, next_gt_record, round_th):
        """弟か？"""
        prev_round_th = round_th - 1
        prev_round_no = prev_round_th - 1

        pass


    def get_type_connect_to_child(prev_gt_record, curr_gt_record, next_gt_record, round_th):
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
        
        (3) Vertical
          |    l_letter_border
        ..+__  
          |    leftside_border
        
        (4) Up
          |    l_letter_border
        ..+__  
          .    None
        """

        # 上は兄か？
        if is_elder_sibling(prev_gt_record=prev_gt_record, curr_gt_record=curr_gt_record, next_gt_record=next_gt_record, round_th=round_th):

            # 下は弟か？
            if is_younger_sibling(prev_gt_record=prev_gt_record, curr_gt_record=curr_gt_record, next_gt_record=next_gt_record, round_th=round_th):
                return 'Vertical'

            else:
                return 'Up'

        # 下は弟か？
        elif is_younger_sibling(prev_gt_record=prev_gt_record, curr_gt_record=curr_gt_record, next_gt_record=next_gt_record, round_th=round_th):
            return 'Down'


        return 'Horizontal'
