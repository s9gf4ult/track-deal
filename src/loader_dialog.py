#!/bin/env python
# -*- coding: utf-8 -*-
## loader_dialog ##

import gtk
import loaders

class loader_dialog(object):
    """\brief dialog class showing buttons calling the appropriate loaders
    """
    def __init__(self, parent):
        """\brief constructor
        """
        self.parent = parent
        self.window = gtk.Dialog(flags=gtk.DIALOG_MODAL)
        self.window.set_transient_for(self.parent.window.builder.get_object('main_window'))
        self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.buttons = []
        for (name, icon, dialog_class) in loaders.iter_loaders():
            bt = gtk.Button(name)
            if icon != None:
                image = gtk.Image()
                image.set_from_pixbuf(icon)
                bt.set_image(image)
            bt.connect('clicked', self.button_clicked, dialog_class)
            bt.get_settings().set_long_property("gtk-button-images", 1, 'loader_dialog:dialog_button')
            self.buttons.append(bt)

        p = self.window.get_content_area()
        for button in self.buttons:
            p.pack_start(button)

    def button_clicked(self, button, dialog_class):
        """\brief executed when dialog button is clicked
        \param button
        \param dialog_class - dialog class given from 
        """
        if dialog_class != None:
            dialog = dialog_class(self)
            ret = dialog.run()
            dialog.destroy()
            self.window.response(ret)

    def run(self, ):
        """\brief run dialog and show window
        """
        self.window.show_all()
        ret = self.window.run()
        self.window.hide()
        return ret
        
