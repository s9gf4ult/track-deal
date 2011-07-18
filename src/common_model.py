#!/bin/env python
# -*- coding: utf-8 -*-
## common_model ##

from sources import common_source

class common_model(object):
    """abstract model class
    """
    _update_callback = None
    
    def __init__(self, ):
        """not implemented model constructor
        """
        
        raise NotImplementedError()

    def connect(self, connect_string):
        """
        \~russian
        \brief Подключается к базе с данными модели
        \param connect_string В каждок конкретной реализации имеет разный вид.
        \~english
        \brief connects to existing database and do not do anything
        \param connect_string
        """
        raise NotImplementedError()

    def connected(self, ):
        """
        \~russian
        \brief Проверяет подключена ли модель к базе
        \retval True Подключена
        \retval False Не подключена
        \~english
        return true if connected
        """
        raise NotImplementedError()


    def disconnect(self, ):
        """disconnect from database
        """
        raise NotImplementedError()


    def dbinit(self, ):
        """
        \~russian
        \brief Создает пустую базу данных.

        Создает таблицы, триггеры, представления. Выполняется при создании новой базы
        \~english
        itialize new empty database
        """
        raise NotImplementedError()

    def dbtemp(self, ):
        """
        \~russian
        \brief Создает временные объекты в базе.

        Тоже что и dbinit но создает временные таблицы и прочие объекты.
        Выполняется каждый раз при при подключении к базе с данными. В некоторых реализациях может просто ничего не делать.
        Использование временных таблиц, триггеров и представлений удобно тем, что не придется менять формат базы, если
        появится необходимость менять эти объекты.
        \~english
        initializes temporary objects in database
        """
        raise NotImplementedError()
    

    def set_update_callback(self, update_callback):
        """
        \~russian
        \brief Устанавливает обратный вызов на обновление данных в базе
        \param update_callback эта функция будет вызываться без параметров каждый раз при обновлении данных в базе.
        \~english
        Setter for property update_callback
        \param update_callback
        """
        assert(hasattr(update_callback, "__call__"))
        self._update_callback = update_callback

    def get_update_callback(self):
        """Getter for property update_callback
        
        """
        
        return self._update_callback

    def call_update_callback(self, ):
        """
        \~russian
        \brief Вызывает обратный вызов на обновление базы

        Этот метод должен вызываться наследником класса для вызова коллбэка, когда данные в базе обновляются
        \~english
        this must be executed when data has changed
        """
        if self._update_callback != None:
            self._update_callback()

    def load_from_source(self, source):
        """\brief load deals from souce
        \param source \ref sources.common_source instance
        """
        assert(isinstance(source, common_source))
        
        



