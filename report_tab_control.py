#!/bin/env python
# -*- coding: utf-8 -*-
import gtk

class report_tab_control:
    def __init__(self, database, builder, update_callback):
        def shorter(name, action, *method):
            self.builder.get_object(name).connect(action, *method)

        shorter("comma_separator", "value-changed", self.comma_separator_changed)
        shorter("comma_as_splitter", "toggled", self.comma_as_splitter_changed)
        shorter("radio_segfault", "toggled", self.radio_button_changed)
        shorter("radio_axce1", "toggled", self.radio_button_changed)
        self.textview = self.builder.get_object("report_text_view")
        self.stock_buttons = self.builder.get_object("stock_buttons")
        
    def comma_separator_changed(self, sb):
        self.update_textview()

    def comma_as_splitter_changed(self, cb):
        self.update_textview()

    def radio_button_changed(self, rb, call_me):
        if rb.get_active():
            self.update_textview()

    def update_textview(self):
        m = gtk.TextBuffer()
        if self.builder.get_object("radio_segfault").get_active():
            ticks = self.get_ticks()
            m.set_text(self._gen_seg(ticks))
            self.textview.set_buffer(m)
        elif self.builder.get_object("radio_axce1").get_active():
            ticks = self.get_ticks()
            m.set_text(self._gen_axcel(ticks))
            self.textview.set_buffer(m)

    def tb_clicked(self, tb):
        self.update_textview()

    def get_ticks(self):
        ret = []
        self.stock_buttons.foreach(lambda w: isinstance(w, gtk.ToggleButton) and w.get_active() and ret.append(w.get_label()))
        return ret

    def remake_buttons(self):
        if not self.database.connect:
            return
        
        for w in self.stock_buttons.get_children():
            self.stock_buttons.remove(w)
        
        for (name) in self.database.connection.execute("select distinct ticket from positions order by ticket"):
            tb = gtk.ToggleButton(name)
            tb.connect("toggled", self.tb_clicked)
            tb.set_active(True)
            self.stock_buttons.pack_start(tb, False)

        irev = gtk.Button(u'Реверс')
        irev.connect("clicked", self.irev_clicked)
        iunset = gtk.Button(u'Снять')
        iunset.connect("clicked", self.iunset_clicked)
        self.stock_buttons.pack_end(irev, False)
        self.stock_buttons.pack_end(iunset, False)
        self.builder.get_object("main_window").show_all()

    def update_widget(self):
        self.remake_buttons()
        self.update_textview()

    def irev_clicked(self, bt):
        self.stock_buttons.foreach(self._reverse)

    def iunset_clicked(self, bt):
        self.stock_buttons.foreach(self._unset)

    def _unset(self, cb):
        if isinstance(cb, gtk.ToggleButton):
            cb.set_active(False)
            
    def _reverse(self, cb):
        if isinstance(cb, gtk.ToggleButton):
            cb.set_active(not cb.get_active())


    def _gen_seg(self, ticks):
        ret = u''
        is_comma = self.builder.get_object("comma_as_splitter").get_active()
        after_comma = self.builder.get_object("comma_separator").get_value_as_int()
        for pos in self.database.connection.execute("select ticket, direction, count, open_coast, close_coast, broker_comm + stock_comm, open_datetime, close_datetime from positions order by close_datetime, open_datetime"):
            if not pos[0] in ticks:
                continue
            (open_datetime, close_datetime) = map(lambda a: u'{0:4}.{1:02}.{2:02}'.format(a.year, a.month, a.day), pos[-2:])
            ret += u'{0}\t{1}'.format(pos[0], -1 == pos[1] and 'L' or 'S')
            v = reduce(lambda a, b: u'{0}\t{1}'.format(a, b), map(lambda a: after_comma < 1 and u'{0}'.format(float(a).__trunc__()) or round(a, after_comma), pos[2:-2]))
            if is_comma:
                v = v.replace('.', ',')
            ret += u'\t{0}\t\t\t\t\t\t{1}\t{2}\n'.format(v, open_datetime, close_datetime)
        return ret

    def _gen_axcel(self, ticks):
        after_comma = self.builder.get_object("comma_separator").get_value_as_int()
        is_comma = self.builder.get_object("comma_as_splitter").get_active()
        ret = u''
        for pos in self.database.connection.execute("select open_datetime, close_datetime, ticket, direction, open_coast, close_coast, count, open_volume, close_volume, broker_comm + stock_comm from positions order by close_datetime, open_datetime"):
            if not pos[2] in ticks:
                continue
            vvv = map(lambda a: [u'{0:02}.{1:02}.{2:04}'.format(a.day, a.month, a.year), u'{0:02}:{1:02}:{2:02}'.format(a.hour, a.minute, a.second)], pos[:2])
            ret += reduce(lambda a, b: u'{0}\t{1}'.format(a, b), vvv[0] + vvv[1])
            ret += u'\t{0}\t{1}'.format(pos[2], -1 == pos[3] and 'L' or 'S')
            aa = reduce(lambda a, b: u'{0}\t{1}'.format(a, b), map(lambda a: after_comma < 1 and u'{0}'.format(float(a).__trunc__()) or round(a, after_comma), pos[4:-1]))
            aa += u'\t\t\t\t{0}'.format(after_comma < 1 and u'{0}'.format(float(pos[-1]).__trunc__()) or u'{0}'.format(round(pos[-1], after_comma)))
            if is_comma:
                aa = aa.replace('.', ',')
            ret += u'\t{0}\n'.format(aa)
            
        return ret

