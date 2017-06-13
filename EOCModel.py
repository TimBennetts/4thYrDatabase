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
    return demand


def EOCModel():
    # initial variables - time in days
    prodCost = 4.25 #P in USD, from email from Don
    orderQ = 1#Q
    demand = deterministicDemand(skuRef="FTRWOODGRAI")#D
    fixedCost = 1#K
    holdCost = 1#h
    leadTime = 15 #L in days
    timeRange = 4*365 #4 years


    Qstar = math.sqrt(2*demand*fixedCost/holdCost) #optimal order quantity Q*
    reorderPoint = demand*leadTime #R

    for i in range(timeRange):
        stuff = "happens here"



if __name__ == '__main__':
    loadSession()
    EOCModel()