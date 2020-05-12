
from aux_functions import sharpe_ratio
import matplotlib.pyplot as plt
from pyfolio import create_simple_tear_sheet


class StrategyProfile:
    """
    This class is used to analyse and visualise the ouput of strategies.
    Given:
     - bars data (pandas.Dataframe with 'open' 'high' 'low' 'close'), 
     - positions (pandas.Series of 0, 1, -1)
    this class extracts perfomance statistics and plots for the PnL.
    
    Keeping the assement of strategies separate for the decision logic 
    is a design decision that reduces operational risks.
    """
    
    def __init__(self, pos, bars):
        self.pos = pos    # Position in time, 1 is long, -1, is short 0 is out
        self.bars = bars  # Price of the traded asset

    def get_pnl(self, tx_cost=0):
        
        # Get the PnL: 
        # e.g. profit from going long today is -> price[tomorrow]/price[today] - 1
        # Profit/loss is the relative change of price (pct_change)
        # Delay the positions by one, via .shift(1) 
        pnl = self.bars['close'].pct_change() * self.pos.shift(1)
        
        # Calculate transaction costs
        if tx_cost != 0: 
            action = self.pos.shift(1).diff().abs()
            pnl -= action/self.bars['close'] * tx_cost 
        return pnl
        
    def get_sharpe(self, tx_cost=0):
        pnl = self.get_pnl(tx_cost)
        return sharpe_ratio(pnl)  # Sharpe on the bar-by-bar PnL

    def simple_visualisation(self, tx_cost=0, timescale='1D', color='steelblue', label=None, ax=None):
        if label is None: label = str(self.get_sharpe(tx_cost))
        pnl = self.get_pnl(tx_cost)
        pnl.resample(timescale).sum().cumsum().plot(color=color, label=label, ax=ax)
        if ax is None:
            plt.ylabel('Cumulative PnL')
        
    def report(self):
        """
        TODO: currently this function only supports daily PnL data.
              I should adjust it to work with a user-defined timescale.
        """
        from pyfolio import create_simple_tear_sheet

        total_days = (self.bars.index[-1]-self.bars.index[0]).days
        n_of_trades = self.pos.diff().abs().sum()/2
        print('Mean value of trades per day = '+str(n_of_trades/total_days))
        
        create_simple_tear_sheet(
            returns = self.get_pnl().resample('1D').sum())

