class Quote(object):

    def __init__(self, index, quote, author, date):
        self.index = index
        self.quote = quote
        self.author = author
        self.date = date

    def get_index(self):
        return self.index

    def get_quote(self):
        return self.quote

    def get_author(self):
        return self.author

    def get_date(self):
        return self.date
