import ccxt
import time
import mydbutil
import logging
import datetime
from threading import Thread
from apscheduler.schedulers.blocking import BlockingScheduler

   
def logMe(msg):
    #logging.info(msg)
    print(msg)
    
def logMeError(msg):
    logging.info(msg)
    print(msg)
    
  
  
  

def jobDef(exc,pool):
 
   
   
    try:
            
        exchange = getattr(ccxt, exc)({
            # 'proxy':'https://cors-anywhere.herokuapp.com/',
        })
        
        logMeError('Store :'+exc+' started---------------------------------')
        logMe('Store :' +exc+ ' delay limit: '+str(exchange.rateLimit))


        # load all markets from the exchange
        markets = exchange.load_markets()
        tuples = list(ccxt.Exchange.keysort(markets).items())

    
    

        for (k, v) in tuples:
            try:
                pair = v['id'] 
                symbol = v['symbol'] #, v['base'], v['quote']))
                delay = int(exchange.rateLimit / 1000)+1  # delay in between requests
                ticker = exchange.fetch_ticker(symbol.upper())
                datetm = ticker['datetime']
                high =  str(ticker['high'])
                low =   str(ticker['low'])
                bid = str(ticker['bid'])
                ask = str(ticker['ask'])
                volume = str(ticker['quoteVolume'])
                
                symbolLeft = str(symbol).split('/')[0]
                symbolRight = str(symbol).split('/')[1]
                
                updateArbitrage(pool, exc, pair,symbol,datetm,high,low,bid,ask,volume,symbolLeft,symbolRight)
                logMe(exc +' added :' +symbol)
                time.sleep(delay)
            except BaseException as error:
                logMeError('---->> ERROR -->> Store :'+exc+' '+ v['id']+ 'An exception occurred: '+format(error))    
                
        logMe('Store :'+exc+' ended--------------------------------- sleeping ')  
        time.sleep(600)
        jobDef(exc, pool)
    except BaseException as error:
        logMeError('---->> Outer ERROR -->> Store :'+exc+' An exception occurred: '+format(error))               

      
       
def RefreshArbitrageCalc():
    try:
        
        connection = pool.get_conn()
        try:
            sql = "call Bat_CalculateArbitrage_Sp()"
            
            cursor = connection.cursor()
            cursor.execute(sql)
        except BaseException as error:
            logMeError('An exception occurred: '+format(error))   
            
        finally:
            pool.release(connection)
            
    except BaseException as error:
        logMeError('An exception occurred: '+format(error))   
            
    
def updateArbitrage(pool, store, pair, symbol, datetm, high, low,bid,ask,volume, symbolLeft,symbolRight):
    try:
        
        connection = pool.get_conn()
        try:
            sql = "call Upd_ArbitrageRaw_Sp(%s, %s, %s,%s, %s, %s,%s, %s, %s,%s,%s)"
            
            cursor = connection.cursor()
            cursor.execute(sql, (store, pair, symbol, datetm, high, low,bid,ask,volume,symbolLeft,symbolRight))
        except BaseException as error:
            logMeError('An exception occurred: '+format(error))   
            
        finally:
            pool.release(connection)
            
    except BaseException as error:
        logMeError('An exception occurred: '+format(error))   
            
    

if __name__ == '__main__':

    logging.basicConfig(handlers=[logging.FileHandler(filename="./ArbitrageLogs.log",encoding='utf-8', mode='a+')],
                        format="%(asctime)s %(name)s:%(levelname)s:%(message)s",datefmt="%F %A %T",level=logging.INFO)    # filename = 'credentials.txt'

    now = datetime.datetime.now()
    nowStr = now.strftime("%Y-%m-%d")+' 00:00:00'
    logMe("Arbitrage bot started "+now.strftime("%Y-%m-%d %H:%M:%S"))
    logMe("################## "+nowStr)
    logMe("#########################################")
 
    excLst = [
            'bequant',
            'bibox',
            'bigone',
            'binance',
            'binanceus',
            'bitbay',
            'bitcoincom',
            'bitfinex',
            'bitfinex2',
            'bitforex',
            'bitkk',
            'bitpanda',
            'bitso',
            'bittrex',
            'bitvavo',
            'bitz',
            'braziliex',
            'btcmarkets',
            'bw',
            'cdax',
            'cex',
            'coinbasepro',
            'coinex',
            'coinmate',
            'digifinex',
            'exmo',
            'gemini',
            'hitbtc',
            'huobijp',
            'huobipro',
            'idex',
            'independentreserve',
            'kraken',
            'kucoin',
            'kuna',
            'lbank',
            'liquid',
            'luno',
            'lykke',
            'ndax',
            'novadax',
            'oceanex',
            'okcoin',
            'phemex',
            'poloniex',
            'southxchange',
            'stex',
            'therock',
            'tidebit',
            'tidex',
            'wavesexchange',
            'whitebit',
            'zaif',
            'zb'
            ]
                                
    pool = mydbutil.getPool()
    pool.init()
    
    #Calculate summary every 5 minutes
    scheduler = BlockingScheduler()
    scheduler.add_job(RefreshArbitrageCalc, 'interval', minutes=5,start_date=nowStr)
    
    for exc in excLst:
        Thread(target=jobDef, args=(exc,pool)).start()
        time.sleep(10)