import pandas as pd
import datetime


class Bitfinex_data_handling:

    def __init__(self):
        self.data_dir = "./Data/Bitfinex/"
        self.file_format = ".csv.gz"

    def load(self, symbol, resolution=None):
        data_raw = pd.read_table(self.data_dir+symbol+self.file_format,
                             compression='gzip',
                             sep=',',
                             names=['timestamp', 'price', 'volume'])

        data_raw['timestamp'] = \
            data_raw['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp( x ))  # [datetime.datetime.fromtimestamp( k ) for k in df['timestamp'] ]

        data_raw = data_raw.set_index('timestamp')

        if resolution is not None:
            data           = data_raw['price'].resample(resolution).ohlc()
            data['volume'] = data_raw['volume'].resample(resolution).sum()

        return data


