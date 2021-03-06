#!/bin/env python
# -*- coding: utf-8 -*-
import gtk
from hide_control import value_returner_control

class combo_control(value_returner_control):
    """
    \~russian
    \brief Контрол для комбо боксов

    Используется для простого управления разными типами комбобоксов.
    В основном боксов со строкой редактирования и простыми раскрывающимися
    списками
    \todo Класс ComboBoxEntry считается устаревшим и не рекомендуется к использованию
    \~english
    controls combobox and comboedit with one interface
    you can easly update rows in combobox with update_widget
    """
    def __init__(self, combobox, checkbutton = None):
        """
        \~russian
        \param combobox виджет, наследник \c ComboBox
        \param checkbutton опциональный аргумент. Если указан, то метод \c get_value будет возвращать
        значение только если этот виджет нажат. Если не указан или равен None \c get_value всегда будет
        возвращать значение комбобокса
        """
        self.combobox = combobox
        self.checkbutton = checkbutton
        if not isinstance(self.combobox, gtk.ComboBoxEntry):
            if self.combobox.get_has_entry():
                self.combobox.set_entry_text_column(0)
            else:
                cell = gtk.CellRendererText()
                self.combobox.pack_start(cell)
                self.combobox.add_attribute(cell, 'text', 0)
                

    def update_widget(self, rows):
        """
        \~russian
        \brief Обновляет список возможных значений в выпадающем списке

        \param rows список строк. Старый список возможных значений теряется
        """
        m = gtk.ListStore(str)
        for row in rows:
            m.append((row,))
        self.combobox.set_model(m)
        if isinstance(self.combobox, gtk.ComboBoxEntry):
            self.combobox.set_text_column(0)

    def get_value(self):
        """
        \~russian
        \brief Возвращает значение в комбобоксе.

        Если комбобокс с редактируемым полем, то возвращает значение этого поля
        В противном случае вернет выбранный элемент или \c None если не выбран ни один элемент списка
        \retval None элемент не выбран
        \retval not-None выбранный элемент
        """
        if isinstance(self.combobox, gtk.ComboBoxEntry):
            return self.return_value(self.combobox.child.get_text())
        # elif isinstance(self.combobox, gtk.ComboBoxText):
        #     return self.return_value(self.combobox.get_active_text())
        elif isinstance(self.combobox, gtk.ComboBox):
            if self.combobox.get_has_entry():
                return self.return_value(self.combobox.get_child().get_text())
            else:
                cit = self.combobox.get_active_iter()
                if cit != None:
                    return self.return_value(self.combobox.get_model().get_value(cit, 0))
                else:
                    return None

    def set_value(self, data):
        """
        \~russian
        \brief Устанавливает значение комбобокса
        \param data значение или None чтобы снять активное значение

        Если комбобокс с редактируемым полем устанавливает значение этого поля в \c data
        в противном случае находит в списке значение указанное в \c data и выбирает это значение.
        Если в списке нет значения \c data то сначала добавляет его в список а потом выбирает
        """
        if isinstance(self.combobox, gtk.ComboBoxEntry):
            self.combobox.child.set_text((data == None and "" or data))
        elif isinstance(self.combobox, gtk.ComboBox):
            m = self.combobox.get_model()
            if m == None:
                m = gtk.ListStore(str)
                self.combobox.set_model(m)
            if data == None:
                self.combobox.set_active(-1)
                return
            it = m.get_iter_first()
            while it != None:
                if m.get_value(it, 0).decode("utf-8") == data.decode("utf-8"):
                    self.combobox.set_active_iter(it)
                    return
                else:
                    it = m.iter_next(it)
            new = m.append((data,))
            self.combobox.set_active_iter(new)
                
            

if __name__ == "__main__":
    w = gtk.Dialog()
    p = w.get_content_area()
    c = gtk.ComboBox()
    p.pack_start(c)
    con = combo_control(c)
    con.update_widget(["ajaja", "fjfjfj", "rurur"])
    cc = gtk.ComboBoxEntry()
    p.pack_start(cc)
    ccon = combo_control(cc)
    ccon.update_widget(["cococoar", "ejejr", "eijwiej"])
    ccc = gtk.combo_box_new_with_entry()
    p.pack_start(ccc)
    cccon = combo_control(ccc)
    cccon.update_widget(["some", "else", "and_other"])
    def pushed(bt):
        con.set_value("new_value")
        cccon.set_value("again")
    bt = gtk.Button("push")
    p.pack_start(bt)
    bt.connect("clicked", pushed)
    w.show_all()
    w.run()
    
