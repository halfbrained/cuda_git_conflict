import os
from cudatext import *

re_pattern = r'^<<<<<<< .*\n(.*\n)*?^=======\n(.*\n)*?^>>>>>>> .*'

BM_TAG = app_proc(PROC_GET_UNIQUE_TAG, '')


class Command:

    def __init__(self):
        self.ed = None
        self.carets = None


    def solve_nearest(self):
        self.ed = Editor(ed.get_prop(PROP_HANDLE_SELF))
        self.carets = self.ed.get_carets()

        try:
            conflict, sep_line = self._find_conflict()
            if conflict  and  sep_line is not None:
                self._set_conflict_bookmarks(conflict, sep_line)

                self.set_carets(self.carets) # restore carets

                # scroll to conflict
                if not self._is_line_on_screen(conflict[1])  or  not self._is_line_on_screen(conflict[3]):
                    self.ed.set_prop(PROP_LINE_TOP, conflict[1])

                res = self._choose_commit(conflict, sep_line)
                if res is not None:
                    if res < 2:
                        # line indexes are inclusive
                        if res == 0:
                            choice_range = (conflict[1]+1, sep_line-1)
                        else:
                            choice_range = (sep_line+1, conflict[3]-1)
                        # del text after and before choice-text
                        self.ed.replace_lines(choice_range[1]+1, conflict[3],       [])
                        self.ed.replace_lines(conflict[1],       choice_range[0]-1, [])
                    else: # keep both
                        for y in (conflict[3], sep_line, conflict[1]):
                            self.ed.replace_lines(y, y, [])
            else:
                msg_status('No conflicts found')

        finally:
            self.ed.bookmark(BOOKMARK_DELETE_BY_TAG, nline=0, tag=BM_TAG)
            self.ed = None
            self.carets = None


    def _choose_commit(self, conflict, sep_line):
        l_change0 = (conflict[1]+1+1, sep_line)
        l_change1 = (sep_line+1+1,    conflict[3])

        dlg_items = []
        for caption,l_ch in zip(('Current change', 'Incoming change'), (l_change0, l_change1)):
            if l_ch:
                if l_ch[0] != l_ch[1]:
                    _lines_str = 'lines {}-{}'.format(*l_ch)
                else:
                    _lines_str = 'line '+str(l_ch[0])
            dlg_items.append(caption +'\t'+ _lines_str)

        dlg_items.append('Both')
        assert len(dlg_items) == 3

        res = dlg_menu(DMENU_LIST, dlg_items, caption='Git Conflict Solver')
        return res


    def _set_conflict_bookmarks(self, conflict, sep_line):
        start_line, end_line = conflict[1], conflict[3]
        for i in (start_line, sep_line, end_line):
            self.ed.bookmark(BOOKMARK_SET, i, tag=BM_TAG)


    def _find_conflict(self):
        """ returns conflict position tuple: (start_x, start_y, end_x, end_y)
        """
        # move caret to top of visible area - search start position
        y0, y1 = self.ed.get_prop(PROP_LINE_TOP),  self.ed.get_prop(PROP_LINE_BOTTOM)
        self.ed.set_caret(0, y0)

        # line of interest - if caret is on screen
        target_line = y0
        if self.carets  and  len(self.carets) == 1:
            caret = self.carets[0]
            if caret[3] == -1  and  y0 <= caret[1] <= y1:
                target_line = caret[1]

        _search_cfg = 'rfa' # r:regex, f:caret, a:wrap
        conflict = None
        for i in range(16): # avoiding while-loop just in case
            res = self.ed.action(EDACTION_FIND_ONE, re_pattern, _search_cfg)
            if res is None:
                break

            # if caret in this conflict - return _it_
            if res[1] <= target_line <= res[3]:
                conflict = res
                break

            # if conflict ends before target line - might have closer conflict - search further
            # this is first conflict after target line - stop search
            if res[3] >= target_line  or  res[1] < y0: # (or search wrapped)
                # if first,  or new is on-screen - return new
                if conflict is None  or  (res[1] <= y1 and res[1] > y0):
                    conflict = res
                break   # otherwise return previous

            conflict = res
            self.ed.set_caret(0, res[3])
        #end for

        sep_line = None
        if conflict:
            _sep_line_inds = (i for i in range(conflict[1], conflict[3]+1)
                                                if self.ed.get_text_line(i) == '=======')
            sep_line = next(_sep_line_inds, None)

        return conflict, sep_line


    def set_carets(self, carets):
        for i,c in enumerate(carets):
            id_ = CARET_SET_ONE if i == 0 else CARET_ADD
            self.ed.set_caret(*c, id=id_, options=CARET_OPTION_NO_SCROLL)

    def _is_line_on_screen(self, nline):
        y0, y1 = self.ed.get_prop(PROP_LINE_TOP),  self.ed.get_prop(PROP_LINE_BOTTOM)
        return y0 <= nline <= y1
