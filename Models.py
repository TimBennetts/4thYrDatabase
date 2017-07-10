import readData

import matplotlib.pyplot as plt
import math
import pandas as pd
import numpy as np
from createDatabase import OZPurchaseOrder, SalesData, TandWPurchaseOrder, hardToFind, \
    ordersExport, theActivePurchaseOrder, createDB, stockReports, freightInvoices
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
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


def getSalesDF(skuRef):
    # pre-allocate arrays
    salesQ = []
    salesDate = []
    salesSku = []

    # OZPurchaseOrder
    if skuRef == "all":
        for row in dbSession.query(OZPurchaseOrder):
            salesQ.append(row.quantity)
            salesDate.append(row.orderDate)
            salesSku.append(row.skuNum)
    else:
        for row in dbSession.query(OZPurchaseOrder):
            if skuRef in row.skuNum:
                salesQ.append(row.quantity)
                salesDate.append(row.orderDate)
                salesSku.append(row.skuNum)

    # SalesData
    if skuRef == "all":
        for row in dbSession.query(SalesData):
            salesQ.append(row.quantity)
            salesDate.append(row.orderDate)
            salesSku.append(row.skuNum)
    else:
        for row in dbSession.query(SalesData):
            if skuRef in row.skuNum:
                salesQ.append(row.quantity)
                salesDate.append(row.orderDate)
                salesSku.append(row.skuNum)

    # TandWPurchaseOrder
    if skuRef == "all":
        for row in dbSession.query(TandWPurchaseOrder):
            salesQ.append(row.quantity)
            salesDate.append(row.orderDate)
            salesSku.append(row.skuNum)
    else:
        for row in dbSession.query(TandWPurchaseOrder):
            if skuRef in row.skuNum:
                salesQ.append(row.quantity)
                salesDate.append(row.orderDate)
                salesSku.append(row.skuNum)

    # hardToFind
    if skuRef == "all":
        for row in dbSession.query(hardToFind):
            salesQ.append(row.quantity)
            salesDate.append(row.orderDate)
            salesSku.append(row.skuNum)
    else:
        for row in dbSession.query(hardToFind):
            if skuRef in row.skuNum:
                salesQ.append(row.quantity)
                salesDate.append(row.orderDate)
                salesSku.append(row.skuNum)

    # ordersExport
    if skuRef == "all":
        for row in dbSession.query(ordersExport):
            salesQ.append(row.quantity)
            salesDate.append(row.orderDate)
            salesSku.append(row.skuNum)
    else:
        for row in dbSession.query(ordersExport):
            if skuRef in row.skuNum:
                salesQ.append(row.quantity)
                salesDate.append(row.orderDate)
                salesSku.append(row.skuNum)

    # theActivePurchaseOrder
    if skuRef == "all":
        for row in dbSession.query(theActivePurchaseOrder):
            salesQ.append(row.quantity)
            salesDate.append(row.orderDate)
            salesSku.append(row.skuNum)
    else:
        for row in dbSession.query(theActivePurchaseOrder):
            if skuRef in row.skuNum:
                salesQ.append(row.quantity)
                salesDate.append(row.orderDate)
                salesSku.append(row.skuNum)

    # add to dataframe
    salesDF = pd.DataFrame({"salesQ": salesQ,
                            "Date": salesDate,
                            "skuNum": salesSku})

    #remove outliers and no date values
    salesDF = salesDF[salesDF['Date'] > datetime.datetime(2014,1,1,0,0,0).date()]

    return salesDF


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
    for row in dbSession.query(freightInvoices).order_by(freightInvoices.orderDate):
        date.append(row.orderDate)
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



def calcDemand(skuRef, timeRange, method):
    salesDF = getSalesDF(skuRef)

    #check sku
    if salesDF.empty:
        print "skuRef not found"
        return

    totalQ = salesDF["salesQ"].sum()
    timeDiff = (salesDF["Date"].max() - salesDF["Date"].min()).days
    meanDemand = float(totalQ)/timeDiff

    sumSales = []
    for i in salesDF['Date'].unique():
        sumSales.append(float(salesDF.salesQ[salesDF['Date'] == i].sum()))

    sumSalesDF = pd.DataFrame({"SumSales": sumSales,
                               "Date": salesDF['Date'].unique()})

    sumSalesDF.sort_values(by="Date", inplace=True)
    # Find average sale level on a given day and the standard deviation of that
    meanSales = sumSalesDF['SumSales'].mean()
    stdDevSales = sumSalesDF['SumSales'].std()
    # Find often a sale on a day occurs
    saleOccurPercent = float(len(sumSalesDF['Date'])) / (sumSalesDF['Date'].max() - sumSalesDF['Date'].min()).days

    if method == 1:
        methodDisc = "Deterministic demand"
        demand = [meanDemand] * timeRange
    elif method == 2:
        methodDisc = "poisson distribution"
        # find random poisson values
        demand = np.random.poisson(meanDemand, timeRange)
    elif method == 3:
        methodDisc = "poisson distribution with uniform occurrence"
        demand = [0] * timeRange

        # model the demand by finding if a sale occurs on a particular day then model poisson on that
        for t in range(timeRange):  # vectorize this
            if np.random.uniform(0, 1) < saleOccurPercent:
                demand[t] = float(np.random.poisson(meanSales, 1))

        meanDemand = float(sum(demand)) / len(demand)
    elif method == 4:
        methodDisc = "normal distribution with uniform occurrence"
        demand = [0] * timeRange

        # model the demand by finding if a sale occurs on a particular day then model poisson on that
        for t in range(timeRange):  # vectorize this
            if np.random.uniform(0, 1) < saleOccurPercent:
                demand[t] = int(np.random.normal(meanSales, stdDevSales, 1))

        meanDemand = int(sum(demand)) / len(demand)
    else:
        print "Method not chosen"
        return

    return demand, meanDemand, methodDisc

#
#
# def poissonDemand(skuRef, timeRange):
#     salesDF = getSalesDF(skuRef)
#
#     #check sku
#     if salesDF.empty:
#         print "skuRef not found"
#         return
#
#     totalQ = salesDF["salesQ"].sum()
#     timeDiff = (salesDF["Date"].max() - salesDF["Date"].min()).days
#     meanDemand = float(totalQ)/timeDiff
#
#
#
#     return demand, meanDemand
#
#
#
# def poissonAndOccursDemand(skuRef, timeRange):
#     # Using poisson distribution due the look of the sales data
#     salesDF = getSalesDF(skuRef)
#
#     #check sku
#     if salesDF.empty:
#         print "skuRef not found"
#         return
#
#     # add all numbers at the same date together
#
#
#
#     return demand, meanDemand
#
#
#
# def normalAndOccursDemand(skuRef, timeRange):
#     # Using normal distribution with and occurrence probability
#     salesDF = getSalesDF(skuRef)
#
#     #check sku
#     if salesDF.empty:
#         print "skuRef not found"
#         return
#
#     # add all numbers at the same date together
#     sumSales = []
#     for i in salesDF['Date'].unique():
#         sumSales.append(float(salesDF.salesQ[salesDF['Date'] == i].sum()))
#
#     sumSalesDF = pd.DataFrame({"SumSales": sumSales,
#                                "Date": salesDF['Date'].unique()})
#
#     sumSalesDF.sort_values(by="Date", inplace=True)
#     # Find average sale level on a given day
#     meanSales = sumSalesDF['SumSales'].mean()
#
#     print stdDevSales
#
#     # Find often a sale on a day occurs
#     saleOccurPercent = float(len(sumSalesDF['Date'])) / (sumSalesDF['Date'].max() - sumSalesDF['Date'].min()).days
#
#
#
#     return demand, meanDemand



def findCurrentQ(skuRef):
    stockQ = []
    stockDate = []

    if skuRef == "all":
        for row in dbSession.query(stockReports).order_by(stockReports.orderDate):
            stockQ.append(row.freeStock)
            stockDate.append(row.orderDate)
    else:
        for row in dbSession.query(stockReports).order_by(stockReports.orderDate):
            if skuRef in row.skuNum:
                stockQ.append(row.freeStock)
                stockDate.append(row.orderDate)
    stockDF = pd.DataFrame({"stockQ": stockQ,
                            "Date": stockDate})

    initialQ = float(stockDF.stockQ[stockDF['Date']==stockDF['Date'].max()].sum())

    return initialQ


def EOCModel(skuRef, distMethod):
    # initial variables - time in days
    prodCost = 4.25+1 #P production + transport costin USD, from email from Don
    initialQ = findCurrentQ(skuRef)
    if initialQ == None:
        return
    fixedCost = 133 #K, cost per order, Don't know where this comes from?!
    holdCost = 0.001#h, per bottle per day
    leadTime = 15 #L in days
    timeRange = 2*365 # in days, arbitary

    #Find demand
    demand, meanDemand, methodDisc = calcDemand(skuRef, timeRange, distMethod)
    if demand[0] == None: #D, number of items sold per day, the quantity currently in stock
        return

    Qstar = math.ceil(math.sqrt(2*meanDemand*fixedCost/holdCost)) #optimal order quantity Q*
    reorderPoint = int(math.ceil(meanDemand*leadTime)) #R, round up to nearest int
    #allocate/initialise
    quantity = [0] * timeRange
    reordered = False
    quantity[0] = initialQ
    arrivalTime = 0
    missedSales = 0

    for t in range(1,timeRange):
        quantity[t] += quantity[t-1]-demand[t] #quantity[t] should be 0 unless a reorder has been made
        if (quantity[t] < reorderPoint) & (reordered == False):
            if t + leadTime < timeRange:
                arrivalTime = t + leadTime
                quantity[arrivalTime] = Qstar
                reordered = True
        elif arrivalTime == t:
            reordered = False
        if quantity[t] < 0:
            missedSales += -quantity[t]
            quantity[t] = 0


    totalCost = (fixedCost*meanDemand/Qstar) + (prodCost*meanDemand) + (0.5*Qstar*holdCost)

    plotString = ("Missed sales: " + str(missedSales) + "," + " Total cost: " + str(totalCost))
    print plotString

    plt.plot(range(timeRange),quantity)
    plt.title("EOC model of " + skuRef + " using " + methodDisc)
    plt.xlabel("Time in days")
    plt.ylabel("Stock level")
    plt.xticks(range(0,timeRange,90))
    plt.text(timeRange/8, initialQ, plotString)
    plt.show()


if __name__ == '__main__':
    loadSession()
    # skuRef = "FTRWOODGRAI"
    skuRef = "FTR"
    # skuRef = "all"
    distMethod = 4 #1 = deterministic, 2 = poisson, 3 = occurrence + poisson, 4 = occurrence + normal
    EOCModel(skuRef, distMethod)
    # leadTime = Costs()