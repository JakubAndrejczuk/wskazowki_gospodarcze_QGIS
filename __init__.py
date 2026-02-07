# -*- coding: utf-8 -*-
from .plugin import WskazowkiGospodarczePlugin

def classFactory(iface):
    return WskazowkiGospodarczePlugin(iface)
