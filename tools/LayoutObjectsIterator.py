class LayoutObjectsIterator:

    """Итератор для перебора объектов в Layout."""

    def __init__(self, layout, start=0):
        self.num_object = start
        self.layout = layout
        self.end = layout.count() - 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.end != self.num_object:
            num = self.num_object
            self.num_object += 1
            return self.layout.itemAt(num).widget()
        else:
            raise StopIteration
