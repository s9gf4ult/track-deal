#!/bin/env python
# -*- coding: utf-8 -*-
## common_view ##
from common_model import common_model

class common_view(object):
    """
    \~russian
    Общий класс для представления
    \~english
    abstract class for view
    """
    _model = None
    
    def __init__(self):
        """
        """
        
        raise NotImplementedError()

    def set_model(self, model):
        """
        \~russian
        \param model должна быть наследником класса \ref common_model
        \~english
        \brief sets _model variable in view
        \param model
        """
        assert(isinstance(model, common_model))
        self._model = model

    def get_model(self):
        """
        \~russian
        \return модель активная в данном представлении
        """
        return self._model


    def run(self, ):
        """
        \~russian
        \brief Отображает окно программы.

        забирает управление у потока вызвавшего метод до тех пор пока окно не будет закрыто
        \~english
        run the view
        """
        raise NotImplementedError()
