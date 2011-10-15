#!/bin/env python
# -*- coding: utf-8 -*-


def iter_loaders():
    """\brief yelds (name, icon, dialog class)
    name is a string, icon is gtk.gdk.Pixbuf or None, dialog class is a class of dialog
    importing data to the model
    """
    import os.path
    import pkgutil
    import gtk.gdk
    dirpath = os.path.dirname(os.path.realpath(__file__))
    for (loader, name, is_pkg) in pkgutil.iter_modules([dirpath]):
        if is_pkg:
            ldr = loader.find_module(name)
            m = ldr.load_module(name)
            dn = os.path.dirname(m.__file__)
            iconpath = os.path.join(dn, 'icon.png')
            icon = None
            if os.path.isfile(iconpath):
                icon = gtk.gdk.pixbuf_new_from_file(iconpath)
            yield (name, icon, m.get_dialog_class())
                

                
