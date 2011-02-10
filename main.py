#!/bin/env python
# -*- coding: utf-8 -*-

from xml.dom.minidom import parse
import gtk

class main_ui():
    def __init__(self):
        a = gtk.Builder()
        a.add_from_file("main_ui.glade")
        self.window = a.get_object("main_window")
        self.axce1 = a.get_object("get_axcel")
        self.segfault = a.get_object("get_seg")
        self.choose_file = a.get_object("choose_file")
        self.buffer = a.get_object("buffer")
        self.window.connect("destroy", gtk.main_quit)
        self.choose_file.connect("file-set", self.file_set)

    def show_error(self, text):
        dial = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_OK, flags=gtk.DIALOG_MODAL, parent = self.window)
        dial.props.text = text
        dial.run()
        dial.destroy()

    def file_set(self, widget):
        try:
            self.coats = xml_parser(widget.get_filename())
        except:
            self.show_error(u'Это походу не xml')
            return

        try:
            self.coats.check_file()
        except Exception as e:
            self.show_error(e.__str__())
            return

            
    def show(self):
        self.window.show_all()

class xml_parser():
    def __init__(self, filename):
        self.xml = parse(filename)

    def check_file(self):
        if not (self.xml.childNodes.length == 1 and self.xml.childNodes[0].nodeName == "report"):
            raise Exception(u'Нет тега report')
        self.report = self.xml.childNodes[0]
        for name in ["common_deal", "briefcase_position", "account_totally_line"]:
            if self.report.getElementsByTagName(name).length != 1:
                raise Exception("there is no {0} in report or more that one found".format(name))
        self.common_deal = self.report.getElementsByTagName("common_deal")[0]
        



if __name__ == "__main__":
    obj = main_ui()
    obj.show()
    gtk.main()
