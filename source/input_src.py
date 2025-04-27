import yfinance as yf
import datetime
class InputLayout:
    def __init__(self, layout=None):
        self.layout = layout

    def get_layout(self):
        return self.layout

    def get_input(self, value):
        stock_name = yf.Ticker(value)
        return stock_name


if __name__ == "__main__":
    start = datetime.datetime(2020, 1, 1)
    end = datetime.datetime.now()
    get_stock = InputLayout()
    s_name = get_stock.get_input('Reliance')
    # print(s_name.__dict__)

