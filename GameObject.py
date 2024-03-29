class GameObject:
    def __init__(self):
        self.parent = None
        self.position = (0,0)
        pass
    
    def get(self,attribute_name):
        if attribute_name in self.__dict__.keys():
            return self.__dict__[attribute_name]
        return self.parent.get(attribute_name)