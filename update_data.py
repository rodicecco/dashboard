import datamgmt

fred_series = [
                'PCE',                              #Personal Consumption Expenditures
                'DFXARC1M027SBEA',                  #Food PCE
                'DNRGRC1M027SBEA',                  #Energy PCE
                'DSPI',                             #Disposable Income
                'B069RC1',                          #Personal Interest  
                'DSPIC96',                          #Real Disposable Income
                'USREC',                            #Recession
                'GDP',                              #Gross Domestic Product 
                'DGS10',                            #10-Year UST Yield
                'DGS2',                             #2-Year UST Yield
                'FEDFUNDS',                         #Federal Funds Rate 
                'CPIAUCSL',                         #Consumer Price Index
                'LNS12005977',                      #Part-time for non-economic reasons
                'LNS12032194',                      #Part-time for economic reasons
                'CE16OV'                            #Employemnet level (household survey)
            ]


def update_sequence():
    datamgmt.fred.Observations(fred_series).update_sequence()
    datamgmt.fred.SeriesMeta(fred_series).update_sequence()
    datamgmt.fred.SeriesRelease(fred_series).update_sequence()
    datamgmt.ism.ISM().update_sequence()
    datamgmt.ism.ISMSeriesMeta().update_sequence()

    return True

if __name__ == '__main__':
    update_sequence()