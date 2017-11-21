from Publication import Publication


class Book(Publication):
    def __init__(self, title, publisher, status, created_by, category, type, synopsis, author, isbnno):
        Publication.__init__(self, title, publisher, status, created_by, category, type)
        self.__synopsis = synopsis
        self.__author = author
        self.__isbnno = isbnno

    #getters

    def get_synopsis(self):
        return self.__synopsis

    def get_author(self):
        return self.__author

    def get_isbnno(self):
        return self.__author

    #setters

    def set_synopsis(self, synopsis):
        self.__synopsis = synopsis

    def set_author(self, author):
        self.__author = author


    def set_isbnno(self, isbnno):
        self.__isbnno = isbnno





