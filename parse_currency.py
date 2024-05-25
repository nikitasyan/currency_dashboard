import requests
from bs4 import BeautifulSoup


currency_codes = {
    "EUR": 52170,
    "USD": 52148,
    "GBP": 52146,
    "JPY": 52246,
    "TRY": 52158,
    "INR": 52238,
    "CNY": 52207
}

coefficient = {
    "EUR": 1,
    "USD": 1,
    "GBP": 1,
    "JPY": 100,
    "TRY": 10,
    "INR": 10,
    "CNY": 1
}


class ParseCurrency:
    def __init__(self, start_day, start_month, start_year, end_day, end_month, end_year):
        self.start_day = start_day
        self.start_month = start_month
        self.start_year = start_year
        self.end_day = end_day
        self.end_month = end_month
        self.end_year = end_year

    @staticmethod
    def parse_dates(table):
        """
        Обработка тегов и получение дат в нужном формате (yyyy.mm.dd) за представленный диапазон
        """
        tags_dates = table.find_all("td", {"align": ""})
        dates = list(map(lambda x: x.text.split("."), tags_dates))
        dates = list(map(lambda x: ".".join(x[::-1]), dates))
        return dates

    @staticmethod
    def formatting_sequence(sequence):
        """
        Обрабатывает последовательность и убирает лишние нули,
        иногда встречающиеся на сайте, с которого забираются курсы валют.
        """
        while "0" in sequence:
            sequence.remove("0")
        return sequence

    def parse_currencies(self, table, currency_code):
        """
        Обработка тегов и получение курса валюты на каждый день
        """

        tags_currencies = table.find_all("td", {"align": "center", "class": ""})
        count_and_currency = list(map(lambda x: x.text, tags_currencies))
        count_and_currency = self.formatting_sequence(count_and_currency)

        currencies = (
            list(
                map(
                    lambda current_currency_rate:
                    float(current_currency_rate.replace(",", ".")) / coefficient[currency_code],
                    count_and_currency[1::2]
                )
            )
        )
        return currencies

    def get_dates_and_courses(self, currency_code):
        """
        Функция получает диапазон дат и код валюты.
        Возвращает два списка -- все даты из приведённого диапазона, по которым есть данные,
        а также второй список с курсами валют, соответствующих каждой дате.
        """
        url = f"""
https://www.finmarket.ru/currency/rates/\
?id=10148&pv=1&cur={currency_codes[currency_code]}\
&bd={self.start_day}&bm={self.start_month}&by={self.start_year}&ed={self.end_day}&em={self.end_month}&ey={self.end_year}
    """
        req = requests.get(url)
        src = req.text
        bs_html = BeautifulSoup(src, "html.parser")
        table = bs_html.find("tbody")

        dates = self.parse_dates(table)
        currencies = self.parse_currencies(table, currency_code)

        return dates, currencies
