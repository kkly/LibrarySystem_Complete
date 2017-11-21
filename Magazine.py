from Publication import Publication


class Magazine(Publication):

    def __init__(self, title, publisher, status, created_by, category, type, frequency):
        Publication.__init__(self, title, publisher, status, created_by, category, type)
        self.__frequency = frequency

    def get_frequency(self):
        return self.__frequency

    def set_frequency(self, frequency):
        self.__frequency = frequency


