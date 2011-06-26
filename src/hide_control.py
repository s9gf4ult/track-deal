#!/bin/env python
# -*- coding: utf-8 -*-
import gtk

class hide_control:
    """
    \if russian
    \brief Контрол, управляет видимостью виджетов

    В зависимости от чекбуттона показывает или скрывает группу виджетов, либо делает виджеты неактивными
    \endif
    """
    def __init__(self, checkbutton, hide_widgets, hide = False, reverse = False):
        """
        \if russian
        \param checkbutton Gtk виджет с методом get_active и сигналом "toggled"
        \param hide_widgets список с виджетами которые будут отображаться или скрываться в зависимости от состояния
        виджета \c checkbutton
        \param hide Если \c True то виджеты из списка \c hide_widgets будут скрываться, в противном случае
        будет переключаться свойство \c "sensitive" и виджет будет становится "серым" или неактивным для пользователя
        \param reverse если \c True то виджеты будут скрываться когда метод get_active() виджета \c checkbutton наоборот возвращает \c True
        \todo Экземпляры класса ничего не делают когда их собирает GC. Нужно отработать удаление обекта и снять обработчик
        события "toggled" с виджета \c checkbutton
        \endif
        """
        
        self.checkbutton = checkbutton
        self.hide_widgets = hide_widgets
        self.hide = hide
        self.reverse = reverse
        self.checkbutton.connect("toggled", self.toggled)
        for w in self.hide_widgets:
            w.connect("show", self.toggled)
        self.toggled(None)

    def hide_all(self):
        for w in self.hide_widgets:
            w.hide()

    def show_all(self):
        for w in self.hide_widgets:
            w.show()

    def set_sensitive_all(self, sens):
        for w in self.hide_widgets:
            w.set_sensitive(sens)

    def toggled(self, something):
        p = self.checkbutton.get_active()
        if self.reverse:
            p = not p
        if p:
            if self.hide:
                self.show_all()
            else:
                self.set_sensitive_all(True)
        else:
            if self.hide:
                self.hide_all()
            else:
                self.set_sensitive_all(False)

class all_checked_control:
    """
    \if russian
    \brief Управляет наследниками TobbleButton

    Используется для создания зависимых галочек или кнопок, когда выбранная родительская галочка
    не имеет смысла если все дочерние галочки сняты. Этот контрол снимает родительскую галочк
    когда все дочерние галочки сняты
    \todo Экземпляры долджны снимать обработку сигнала "toggled" с виджетов \c child_checkbuttons перед GC.
    \endif
    """
    def __init__(self, parent_checkbutton, child_checkbuttons):
        """
        \if russian
        \param parent_checkbutton виджет наследник ToggleButton
        \param child_checkbuttons список наследников ToggleButton

        Когда все виджеты из списка \c child_checkbuttons будут сняты (\c get_active() вернет \c False) то \c parent_checkbutton также будет снята.
        \endif
        """
        self.parent_checkbutton = parent_checkbutton
        self.child_checkbuttons = child_checkbuttons
        for w in self.child_checkbuttons:
            w.connect("toggled", self.toggled)
        self.toggled(None)

    def toggled(self, something):
        for w in self.child_checkbuttons:
            if w.get_active():
                return
        self.parent_checkbutton.set_active(False)
        
class value_returner_control:
    """
    \if russian
    \brief Контрол возвращающий значение
    \endif
    """
    
    def return_value(self, value):
        """
        \if russian
        \param value значение для возврата
        \retval None Если у экземпляра есть атрибут \c checkbutton и у этого атрибута метод \c get_active не вернет \c True
        \retval value в том случае если у экземпляра нет атрибута \c checkbutton или метод \c get_active этого свойства вернул \c True
        \endif
        """
        if self.checkbutton:
            if self.checkbutton.get_active():
                return value
        else:
            return value
        return None


if __name__ == "__main__":
    w = gtk.Dialog(buttons = (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    p = w.get_content_area()
    c = gtk.CheckButton("eijeifj")
    b = gtk.Button("eifjefij")
    p.pack_start(c, False)
    p.pack_start(b)
    hide_control(c, [b])
    cc = gtk.ToggleButton("yayaya")
    bb = gtk.Label("super yagoo")
    bbb = gtk.Label("another super")
    p.pack_start(cc)
    p.pack_start(bb, False)
    p.pack_start(bbb, False)
    hide_control(cc, [bb, bbb], hide = True)
    pc = gtk.CheckButton("Dady")
    all_checked_control(pc, [c, cc])
    p.pack_start(pc, False)
    w.show_all()
    w.run()
