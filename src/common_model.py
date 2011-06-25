#!/bin/env python
# -*- coding: utf-8 -*-
## common_model ##

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
        \if russian
        \brief Подключается к базе с данными модели
        \param connect_string В каждок конкретной реализации имеет разный вид.
        \else
        \brief connects to existing database and do not do anything
        \param connect_string
        \endif
        """
        raise NotImplementedError()

    def connected(self, ):
        """
        \if russian
        \brief Проверяет подключена ли модель к базе
        \retval True Подключена
        \retval False Не подключена
        \else
        return true if connected
        \endif
        """
        raise NotImplementedError()


    def disconnect(self, ):
        """disconnect from database
        """
        raise NotImplementedError()


    def dbinit(self, ):
        """
        \if russian
        \brief Создает пустую базу данных.

        Создает таблицы, триггеры, представления. Выполняется при создании новой базы
        \else
        itialize new empty database
        \endif
        """
        raise NotImplementedError()

    def dbtemp(self, ):
        """
        \if russian
        \brief Создает временные объекты в базе.

        Тоже что и dbinit но создает временные таблицы и прочие объекты.
        Выполняется каждый раз при при подключении к базе с данными. В некоторых реализациях может просто ничего не делать.
        Использование временных таблиц, триггеров и представлений удобно тем, что не придется менять формат базы, если
        появится необходимость менять эти объекты.
        \else
        initializes temporary objects in database
        \endif
        """
        raise NotImplementedError()
    

    def set_update_callback(self, update_callback):
        """
        \if russian
        \brief Устанавливает обратный вызов на обновление данных в базе
        \param update_callback эта функция будет вызываться без параметров каждый раз при обновлении данных в базе.
        \else
        Setter for property update_callback
        \param update_callback
        \endif
        """
        assert(hasattr(update_callback, "__call__"))
        self._update_callback = update_callback

    def get_update_callback(self):
        """Getter for property update_callback
        
        """
        
        return self._update_callback

    def call_update_callback(self, ):
        """
        \if russian
        \brief Вызывает обратный вызов на обновление базы

        Этот метод должен вызываться наследником класса для вызова коллбэка, когда данные в базе обновляются
        \else
        this must be executed when data has changed
        \endif
        """
        if self._update_callback != None:
            self._update_callback()




