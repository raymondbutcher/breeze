class API(object):

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __iter__(self):
        if False:
            yield False

    @property
    def name(self):
        raise NotImplementedError()

