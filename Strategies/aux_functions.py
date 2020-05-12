
def sharpe_ratio(pnl):
    """
    Measures the 300D annuallised sharpe of a PnL profile.
    """
    import pandas as pd
    import numpy as np

    # If no trades, return -inf
    if pnl.std() == 0 and pnl.mean() == 0:  return -np.inf

   # pnl = pnl.resample('1H').sum()
    N  = pd.Timedelta('300D') / (pnl.index[1] - pnl.index[0])

    return np.sqrt(N) * pnl.mean() / pnl.std()
    
    
def minwidth_BBANDS(p, ma_ts, sigma, mid_width):
    """
    Custom technical indicator: 
        Bollinger bands, with a user-defined minimum width.
    """
    from talib import BBANDS
    import numpy as np

    # Obtain indicators
    (t_b, m_o, b_b) = BBANDS(p.values, timeperiod=ma_ts, nbdevup=sigma, nbdevdn=sigma)

    # Impose a minimum width on the bollinger bands - can't use nan values as clips
    t_m = np.isfinite(t_b * m_o)  # top band mask: neither top band nor moving av can be nan
    b_m = np.isfinite(b_b * m_o)  # bot band mask: neither bot band nor moving av can be nan

    # Clip bands
    t_b[t_m] = np.clip(t_b[t_m], m_o[t_m] + mid_width, np.inf)
    b_b[b_m] = np.clip(b_b[b_m], -np.inf, m_o[b_m] - mid_width)

    return t_b, m_o, b_b
    
    
def brute_force_with_HoF(bars, strategy, parameters_dict, const_args, score_key, n_hof=10):
    """
    Runs strategies over a search space, and returns the hall of 
    fame (that is, the best strategies.
    
    The search space is defined by the user. Given a dict of 
    iterables, we create all possible combinations (see ParameterGrid 
    of sklearn for details).
    
    The argument 'strategy' should take as input a Dataframe of OHLC(V)
    data, and the arguements created in ParameterGrid, and return a 
    StrategyProfile instance.
    
    The score_key argument allows the user to define how to assess a 
    strategy. The score is a strategy is given by:
        score_key(StrategyProfile)
    The hall of fame will include the n_hof top strategies, based on
    this score.

    """
    from sklearn.model_selection import ParameterGrid
    from collections import Iterable
    import numpy as np
    
    # Ensure the user provided a dictionary of iterables
    assert(all([isinstance(parameters_dict[k], Iterable) for k in parameters_dict]))
        
    # Create search space
    search_space = ParameterGrid(parameters_dict)
    if len(search_space) >= 1000: 
        print('We are testing a large number of strategies: '+str(len(search_space)))
    
    # Brute force search: run all strats in the parameter space
    # TODO: Use multiprocessing to paralise the search
    strats = [ strategy(p=bars, **args, **const_args) for args in search_space ]

    # Find the Hall of Fame        
    scores   = np.array( [ score_key(strat) for strat in strats ] )
    HoF_ids  = scores.argsort()[-n_hof:][::-1].astype(int) 
    HoF      = np.array(strats)[HoF_ids]
    HoF_args = np.array(search_space)[HoF_ids]

    return HoF, HoF_args
    