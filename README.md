# backtesting_demo
Backtesting simple mean reversion strategies on BTCUSD

Anectodal discussions with experienced crypto traders have suggested that BTCUSD is so strongly driven by sentiment that it offers a good opportunity for mean revertion trading.
BTCUSD is an interesting case: relatively low volatility (imploying the presence of more inefficiencies), involving many inexperienced traders, driven purely by speculative value, and heavily manipulated by big players (pump n dumps are common, there is no regualtory body).

# Strategies
I explore basic MR strats in the the two notebooks found in 'Strategies'. I use 5min OHLC data from Kraken (a timescale over which we may observe the effects of fast sentimental reactions). I rely on technical indicators, and backtest over 34 months.
 - First, I consider a basic strategy relying only on Bollinger Bands. We tune the strategy and find that it performs inconsistently: making profit only a tiny fraction of the time. It is clear that we have to switch off MR trading when price is trending.
 - In the second notebook I enhance the previous method with a MACD indicator to determine trending. Calibrating the strat's parameters by maximizing sharpe results in pathological strategies (making only 2 or 3 hugely succesful trades). I overcome this by changing the objective functions (see Assessing strategies below).
 
The results of the second strategy are promising, but still need to be improved to achieve consistent performance. 
Next steps would be a create a more accurate trending indicator, using additional technicals and idealy also sentiment data.

### Slippage and transaction costs
BTCUSD is very illiquid, and we can expect ot bite the order book easily. Thus, my implementation allows to easily add a 'transaction cost' in USD.
The data does not say whether transactions were buyer of seller initiated.
Thus, with 0 transaction costs hyperparamter tuning may suggest pathological strats (e.g. high freq MR trading where you buy at sell price and sell at buy price).

The strategies considered so far have 1-5 trades per day, and should be realively insensitive to transaction costs.

# Implementation & methodology details
Data from various exchange are in the 'Data' folder. Here I only use kraken data, and I gitignore all data files. The files can be found on Bitcoincharts.
 
### Parameter fitting
The parameters of strategies are optimised via brute force over a sparse grid. A function in Strategies implements the search, and returns the Hall Of Fame over the search space. 
Inspecting the Hall of Fame allows us to undertand whether the located optimum is robust to parameter variations - helping us avoid 'overfitting' the strategy.

### Implementing strategies
The user needs to implement a simple function that takes the OHLC data in a pandas dataframe ('open', 'high', 'low', 'close', plus optionally 'volume'), and determines the positions (in a pd.Series).
I use talib to calculate technicals, and a for loop (accelerated by numba jit compilation) to iterate over time.

Once the pd.Series of positions has been determined it is used to instantiate the StrategyProfile class. This class takes care of extracting the PNL and all perfomance metrics.
Encaptulating all stragegy-agnostic performance assessment in a class minimizes operational risks (e.g. hard to fall into the look ahead bias trap).

### Assessing strategies
I use PyFolio's tear sheet functionality to extract perfomance reports over daily PnL's.
PnL is defined as the pct change from the close prices, from bar to bar. 

To compare strategies I consider one or more of three metrics:
 - sharpe (this is naive, and allows for many pitfalls)
 - number of trades per day (we don't want to do HFT)
 - calculate the sharpe for each month, and take the minimum. This protect us of strategies that rely on 2-3 trades to drastically increase the PnL.
