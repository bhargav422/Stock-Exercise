from empyrial import empyrial, Engine


portfolio = Engine(    
                  start_date= "2022-01-01", #start date for the backtesting
                  portfolio= ["IRCTC.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS"], #assets in your portfolio 
                  weights = [0.2, 0.2, 0.2, 0.2], #equal weighting is set by default
                  benchmark = ["^NSEI"] #NIFTY50 is set by default
)

empyrial(portfolio)