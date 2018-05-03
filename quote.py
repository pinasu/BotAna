class Quote(object):

    def __init__(self, quote, author, date):
        self.quote = quote
        self.author = author
        self.date = date

    def get_quote(self):
        return self.quote

    def get_author(self):
        return self.author

    def get_date(self):
        return self.date
