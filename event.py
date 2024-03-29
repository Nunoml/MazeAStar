class Event:
    def __init__(self):
        # Eventos: Implementar uma lista onde quando é chamado corre todas as funções na lista?
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self
    
    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self
    
    def __call__(self, *args, **kwargs):
        for handler in self.__handlers:
            handler(*args, **kwargs)