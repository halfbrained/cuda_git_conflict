import os
from cudatext import *

re_pattern = r'^<<<<<<< .*\n(.*\n)*?^=======\n(.*\n)*?^>>>>>>> .*'

BM_TAG = app_proc(PROC_GET_UNIQUE_TAG, '')


class Command:

    def __init__(self):
        self.ed = None


    def solve_nearest(self):
        self.ed = Editor(ed.get_prop(PROP_HANDLE_SELF))
        carets = self.ed.get_carets()

        try:
            conflict, sep_line = self._find_conflict()
            if conflict  and  sep_line is not None:
                self._set_conflict_bookmarks(conflict, sep_line)

                self.ed.set_prop(PROP_LINE_TOP, conflict[1])

                res = self._choose_commit(conflict, sep_line)
                if res is not None:
                    # line indexes are inclusive
                    choice_range = (conflict[1]+1, sep_line-1) if res == 0 else (sep_line+1, conflict[3]-1)
                    # del text after and before choice-text
                    self.ed.replace_lines(choice_range[1]+1, conflict[3],       [])
                    self.ed.replace_lines(conflict[1],       choice_range[0]-1, [])
            else:
                msg_status('No conflicts found')

        finally:
            self.ed.bookmark(BOOKMARK_DELETE_BY_TAG, nline=0, tag=BM_TAG)
            self.set_carets(carets)
            self.ed = None


    def _choose_commit(self, conflict, sep_line):
        l_change0 = (conflict[1]+1+1, sep_line)
        l_change1 = (sep_line+1+1,    conflict[3])

        dlg_items = []
        for caption,l_ch in zip(('Current change', 'Incoming change'), (l_change0, l_change1)):
            if l_ch[0] != l_ch[1]:
                _lines_str = 'lines {}-{}'.format(*l_ch)
            else:
                _lines_str = 'line '+str(l_ch[0])
            dlg_items.append(caption +'\t'+ _lines_str)

        res = dlg_menu(DMENU_LIST, dlg_items)
        return res


    def _set_conflict_bookmarks(self, conflict, sep_line):
        start_line, end_line = conflict[1], conflict[3]
        for i in (start_line, sep_line, end_line):
            self.ed.bookmark(BOOKMARK_SET, i, tag=BM_TAG)


    def _find_conflict(self):
        """ returns conflict position tuple: (start_x, start_y, end_x, end_y)
        """
        # move caret to top of visible area - search start position
        _top_line = self.ed.get_prop(PROP_LINE_TOP)
        self.ed.set_caret(0, _top_line)

        _search_cfg = 'rfa' # r:regex, f:caret, a:wrap
        res = self.ed.action(EDACTION_FIND_ONE, re_pattern, _search_cfg)

        sep_line = None
        if res:
            _sep_line_inds = (i for i in range(res[1], res[3]+1)  if self.ed.get_text_line(i) == '=======')
            sep_line = next(_sep_line_inds, None)

        return res, sep_line


    def set_carets(self, carets):
        for i,c in enumerate(carets):
            id_ = CARET_SET_ONE if i == 0 else CARET_ADD
            self.ed.set_caret(*c, id=id_, options=CARET_OPTION_NO_SCROLL)
