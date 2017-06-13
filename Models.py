import readData

import matplotlib.pyplot as plt
import math
import pandas as pd
import numpy as np
from createDatabase import theActivePurchaseOrder, createDB, stockReports
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import datetime


def loadSession():
    global dbEngine
    global dbSession
    global metadata
    global conn

    dbname = "BBBYO.db"
    dbEngine = create_engine('sqlite:///' + dbname, echo=False)
    Session = sessionmaker()
    Session.configure(bind=dbEngine)
    dbSession = Session()
    conn = dbEngine.connect()
    metadata = MetaData(dbEngine, reflect=True)

def deterministicDemand(skuRef):
    #pre-allocate arrays
    stockQ = []
    stockDate = []
    stockSku = []
    if skuRef == "all":
        for row in dbSession.query(stockReports).order_by(stockReports.date):
            stockQ.append(row.freeStock)
            stockDate.append(row.date)
            stockSku.append(row.skuNum)
    else:
        for row in dbSession.query(stockReports).order_by(stockReports.date):
            if row.skuNum == skuRef:
                stockQ.append(row.freeStock)
                stockDate.append(row.date)
                stockSku.append(row.skuNum)

    #create pandas data frame
    stockDF = pd.DataFrame({"stockQ": stockQ,
                           "Date": stockDate,
                           "skuNum": stockSku})

    totalQ = stockDF["stockQ"].sum(axis=0)
    timeDiff = (stockDF["Date"].max() - stockDF["Date"].min()).days
        # .datetime.days # recorded in days
    #convert timedelta to int (in days)
    demand = float(totalQ)/float(timeDiff)
    initialQ = stockDF["stockQ"].loc[stockDF["Date"]==stockDF["Date"].max()].iloc[0]
    return demand, initialQ


def EOCModel(skuRef):
    # initial variables - time in days
    prodCost = 4.25 #P in USD, from email from Don
    demand, initialQ = deterministicDemand(skuRef)#D, number of items sold per day, the quantity currently in stock
    fixedCost = float(133)/365#K
    holdCost = 0.001#h, per bottle per day
    leadTime = 15 #L in days
    timeRange = 4*365 #4 years, arbitary amount
    transportCost = 1 #C per item


    Qstar = math.sqrt(2*demand*fixedCost/holdCost) #optimal order quantity Q*
    reorderPoint = math.ceil(demand*leadTime) #R, round up to nearest int
    #allocate/initialise
    quantity = [0] * timeRange
    reordered = false
    quantity[0] = initialQ
    arrivalTime = 0

    for t in range(1,timeRange):
        quantity[t] += quantity[t-1]-demand #quantity[t] should be 0 unless a reorder has been made
        if quantity[t] < reorderPoint and reordered == false:
            if t + leadTime < timeRange:
                arrivalTime = t + leadTime
                quantity[arrivalTime] = Qstar
                reordered = true
        elif arrivalTime == t:
            reordered = false

    plt.plot(range(timeRange),quantity)
    plt.title("EOC model of " + skuRef)
    plt.xlabel("Time in days")
    plt.ylabel("Stock level")
    plt.show()

if __name__ == '__main__':
    loadSession()
    skuRef = "FTRWOODGRAI"
    EOCModel(skuRef)