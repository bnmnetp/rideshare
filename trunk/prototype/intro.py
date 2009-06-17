class Foo:
    x = 1
    y = 2

    def __init__(self):
        self.x = 1
        self.y = 2

    def to_dict(self):
        for i in self.__dict__.keys():
            print i

t = Foo()
t.to_dict()
