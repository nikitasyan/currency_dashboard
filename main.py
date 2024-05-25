from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
from parse_currency import ParseCurrency
import sqlite3
import plotly.express as px
import pandas as pd


app = Dash(__name__)
con = sqlite3.connect("test.db")
cur = con.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS currency_rate (
    coin TEXT,
    date TEXT,
    value REAL
);
""")
con.close()


class Currency:
    def __init__(self, currency_code):
        self.currency_code = currency_code

    def is_exist_record(self, date):
        with (sqlite3.connect("test.db") as conn):
            query = f"""
                SELECT *
                FROM currency_rate
                WHERE coin = '{self.currency_code}'
                AND date = '{date}';
            """
            cursor = conn.cursor()
            cursor.execute(query)

        result = cursor.fetchone()
        conn.close()
        return result

    def update_record(self, date, value):
        with sqlite3.connect("test.db") as connect:
            cursor = connect.cursor()
            statement = (f"UPDATE currency_rate "
                         f"   SET value = {value} "
                         f" WHERE coin = '{self.currency_code}'"
                         f"   AND date = '{date}'")
            cursor.execute(statement)

    def create_record(self, date, value):
        with sqlite3.connect("test.db") as connect:
            cursor = connect.cursor()
            statement = (f"INSERT INTO currency_rate "
                         f"VALUES ('{self.currency_code}', '{date}', {value})")
            cursor.execute(statement)


app.layout = html.Div(
    children=[
        html.Div(
            className="div-controller",
            children=[
                html.H4("Введите данные для построения графика"),
                html.P("Выберите диапазон дат с 1 января 2020 по 1 января 2022"),
                html.Div(
                    className="div-for-change",
                    children=[
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed="2020-01-01",
                            max_date_allowed="2022-01-01",
                            start_date="2020-01-10",
                            end_date="2020-01-15"
                        ),
                        dcc.Dropdown(
                            id="currencies",
                            options=[
                                {"label": "Евро", "value": "EUR"},
                                {"label": "Доллар", "value": "USD"},
                                {"label": "Фунт", "value": "GBP"},
                                {"label": "Японская йена", "value": "JPY"},
                                {"label": "Турецкая лира", "value": "TRY"},
                                {"label": "Индийская рупия", "value": "INR"},
                                {"label": "Китайский юань", "value": "CNY"}
                            ],
                            multi=True,
                            value=[],
                        ),
                        dbc.Button(
                            "Считать данные",
                            id="submit-change",
                            n_clicks=0,
                            color="primary",
                            className="mr-1"
                        )
                    ]
                ),
                html.Div(
                    className="graph-display",
                    children=[
                        dcc.Graph(id="timeseries",
                                  config={"displayModeBar": False},
                                  animate=True)
                    ]
                )
            ]
        )
    ]
)


@app.callback(Output("timeseries", "figure"),
              Input("submit-change", "n_clicks"),
              State("date-range", "start_date"),
              State("date-range", "end_date"),
              State("currencies", "value"))
def update_graph(n_clicks, start_date: str, end_date: str, value: list[str]):
    start_y, start_m, start_d = start_date.strip().split("-")
    end_y, end_m, end_d = end_date.strip().split("-")
    for currency in value:
        parser = ParseCurrency(start_d, start_m, start_y, end_d, end_m, end_y)
        dates, currency_rates = parser.get_dates_and_courses(currency)
        current_currency = Currency(currency)
        for index in range(len(dates)):
            if current_currency.is_exist_record(dates[index]):
                current_currency.update_record(dates[index], currency_rates[index])
            else:
                current_currency.create_record(dates[index], currency_rates[index])

        start_date = start_date.replace("-", ".")
        end_date = end_date.replace("-", ".")
        with sqlite3.connect("test.db") as connect:
            coin = f"('{value[0]}')" if len(value) == 1 else tuple(value)
            query = f"""
                SELECT * 
                FROM currency_rate 
                WHERE date >= '{start_date}' 
                AND date <= '{end_date}'
                AND coin in {coin};
            """
            data_frame = pd.read_sql(query, connect)
            figure = px.line(data_frame, x="date", y="value", color="coin")
    return figure


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")
