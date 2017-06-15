import readData

import matplotlib.pyplot as plt
import math
import pandas as pd
import numpy as np
from createDatabase import theActivePurchaseOrder, createDB, stockReports, freightInvoices
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta


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


def Costs():
    # pre-allocate arrays
    date = []
    weight = []
    volume = []
    numShipped = []
    totalCost = []
    ETD = []
    ETA = []

    #getting all data that will be useful
    for row in dbSession.query(freightInvoices).order_by(freightInvoices.date):
        date.append(row.date)
        weight.append(row.weight)
        volume.append(row.volume)
        numShipped.append(row.numShipped)
        totalCost.append(row.totalCost)
        ETD.append(row.ETD)
        ETA.append(row.ETA)

    #putting data in a dataframe
    costDF = pd.DataFrame({
        "Date": date,
        "Weight": weight,
        "Volume": volume,
        "NumShipped": numShipped,
        "TotalCost": totalCost,
        "ETD": ETD,
        "ETA": ETA
    })

    #Finding lead time
    costDF['shippingTime'] = costDF['ETA'] - costDF['ETD']
    leadTime = costDF['shippingTime'].mean().days

    return leadTime

def createSalesDF(dbTableName, skuRef):
    # pre-allocate arrays
    salesQ = []
    salesDate = []
    salesSku = []

    if skuRef == "all":
        for row in dbSession.query(dbTableName).order_by(dbTableName.date):
            salesQ.append(row.freeStock)
            salesDate.append(row.date)
            salesSku.append(row.skuNum)
    else:
        for row in dbSession.query(stockReports).order_by(stockReports.date):
            if row.skuNum == skuRef:
                salesQ.append(row.freeStock)
                salesDate.append(row.date)
                salesSku.append(row.skuNum)

    #create pandas data frame
    salesDF = pd.DataFrame({"salesQ": salesQ,
                           "Date": salesDate,
                           "skuNum": salesSku})
    return salesDF

def deterministicDemand(skuRef):
    #need to use sales of these items

    #OZPurchaseOrder, SalesData, TandWPurchaseOrder, hardToFind, ordersExport, theActivePurchaseOrders

    #pre-allocate arrays
    salesQ = []
    salesDate = []
    salesSku = []
    #


    totalQ = stockDF["stockQ"].sum()
    timeDiff = (stockDF["Date"].max() - stockDF["Date"].min()).days
    demand = float(totalQ)/float(timeDiff)
    initialQ = stockDF["stockQ"].loc[stockDF["Date"]==stockDF["Date"].max()].sum()
    # print initialQ
    return demand, initialQ

def probabilisticDemand(skuRef):
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



def EOCModel(skuRef):
    # initial variables - time in days
    prodCost = 4.25+1 #P production + transport costin USD, from email from Don
    demand, initialQ = deterministicDemand(skuRef)#D, number of items sold per day, the quantity currently in stock
    fixedCost = 133 #K, cost per order, Don't know where this comes from?!
    holdCost = 0.001#h, per bottle per day
    leadTime = 15 #L in days
    timeRange = 2*365 # in days, arbitary amount



    Qstar = math.sqrt(2*demand*fixedCost/holdCost) #optimal order quantity Q*
    reorderPoint = math.ceil(demand*leadTime) #R, round up to nearest int
    #allocate/initialise
    quantity = [0] * timeRange
    reordered = false
    quantity[0] = initialQ
    arrivalTime = 0
    missedSales = 0

    for t in range(1,timeRange):
        quantity[t] += quantity[t-1]-demand #quantity[t] should be 0 unless a reorder has been made
        if quantity[t] < reorderPoint and reordered == false:
            if t + leadTime < timeRange:
                arrivalTime = t + leadTime
                quantity[arrivalTime] = Qstar
                reordered = true
        elif arrivalTime == t:
            reordered = false
        if quantity[t] < 0:
            missedSales += -quantity[t]
            quantity[t] = 0


    totalCost = (fixedCost*demand/Qstar) + (prodCost*demand) + (0.5*Qstar*holdCost)
    print totalCost

    plt.plot(range(timeRange),quantity)
    plt.title("EOC model of " + skuRef)
    plt.xlabel("Time in days")
    plt.ylabel("Stock level")
    plt.xticks(range(0,timeRange,90))
    plt.show()


if __name__ == '__main__':
    loadSession()
    # skuRef = "FTRWOODGRAI"
    skuRef = "all"
    # EOCModel(skuRef)
    leadTime = Costs()