#!/bin/env python
# -*- coding: utf-8 -*-
## common_view ##
from common_model import common_model

class common_view(object):
    """
    \if russian
    Общий класс для представления
    \else
    abstract class for view
    \endif
    """
    _model = None
    
    def __init__(self):
        """
        """
        
        raise NotImplementedError()

    def set_model(self, model):
        """
        \if russian
        \param model должна быть наследником класса \ref common_model
        \else
        \brief sets _model variable in view
        \param model
        \endif
        """
        assert(isinstance(model, common_model))
        self._model = model

    def get_model(self):
        """
        \if russian
        \return модель активная в данном представлении
        \endif
        """
        return self._model


    def run(self, ):
        """
        \if russian
        \brief Отображает окно программы.

        забирает управление у потока вызвавшего метод до тех пор пока окно не будет закрыто
        \else
        run the view
        \endif
        """
        raise NotImplementedError()
