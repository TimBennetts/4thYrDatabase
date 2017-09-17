import readData
import ExploreData

import matplotlib.pyplot as plt
import math
import pandas as pd
import numpy as np
import time
from createDatabase import OZPurchaseOrder, SalesData, TandWPurchaseOrder, hardToFind, \
    ordersExport, theActivePurchaseOrder, createDB, stockReports, freightInvoices
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import datetime
import scipy.stats as st
import random
import csv

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


def getSalesDF(skuRef,dbSession):
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

    #### use warehouse data ####

    return leadTime


def calcDemand(skuRef, timeRange, method):
    salesDF = getSalesDF(skuRef,dbSession)
    leadTime = 15 # L in days
    serviceLvl = 0.95 # service level (alpha):
    zScore = st.norm.ppf(serviceLvl)

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
    saleOQcurPercent = float(len(sumSalesDF['Date'])) / (sumSalesDF['Date'].max() - sumSalesDF['Date'].min()).days
    reorderPoint = int(math.ceil(meanDemand * leadTime))  # R, round up to nearest int

    if method == 1:
        methodDisc = "Deterministic demand"
        demand = [meanDemand] * timeRange
        #Std dev = 0 so safety stock = 0 so reorder point =  normal
        safetyStockLvl = 0
    elif method == 2:
        methodDisc = "poisson distribution"
        # find random poisson values
        demand = np.random.poisson(meanDemand, timeRange)
        # find safety stock
        safetyStockLvl = zScore*np.std(demand)*np.sqrt(leadTime)

    elif method == 3:
        methodDisc = "poisson distribution with uniform occurrence"
        demand = [0] * timeRange

        # model the demand by finding if a sale occurs on a particular day then model poisson on that
        for t in range(timeRange):  # vectorize this
            if np.random.uniform(0, 1) < saleOQcurPercent:
                demand[t] = float(np.random.poisson(meanSales, 1))

        meanDemand = float(sum(demand)) / len(demand)

        #### adding in confidence intervals/safety stock ####
        safetyStockLvl = zScore * np.std(demand) * np.sqrt(leadTime)

    elif method == 4:
        methodDisc = "normal distribution with uniform occurrence"
        demand = [0] * timeRange

        # model the demand by finding if a sale occurs on a particular day then model poisson on that
        for t in range(timeRange):  # vectorize this
            if np.random.uniform(0, 1) < saleOQcurPercent:
                demand[t] = int(np.random.normal(meanSales, stdDevSales, 1))

        meanDemand = int(sum(demand)) / len(demand)

        #### adding in confidence intervals/safety stock ####
        safetyStockLvl = zScore * np.std(demand) * np.sqrt(leadTime)

    else:
        print "Method not chosen"
        return

    reorderPoint = math.ceil(reorderPoint + safetyStockLvl)

    return demand, meanDemand, methodDisc, reorderPoint

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
#     saleOQcurPercent = float(len(sumSalesDF['Date'])) / (sumSalesDF['Date'].max() - sumSalesDF['Date'].min()).days
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


def EOQModel(skuRef, distMethod, dbSession):
    # initial variables - time in days
    prodCost = 5.36+1+0.2 #P production + transport cost + incoming warehouse rate, from email from Don
    initialQ = findCurrentQ(skuRef)
    if initialQ == None:
        return
    # fixedCost = 133 #K, cost per order, Don't know where this comes from?!
    fixedCost = 213.17 #K, comes from average order processing from warehouse
    holdCost = 0.001#h, per bottle per day
    leadTime = 15 #L in days
    timeRange = 2*365 # in days, arbitary

    #Find demand
    demand, meanDemand, methodDisc, reorderPoint = calcDemand(skuRef, timeRange, distMethod)
    if demand[0] == None: #D, number of items sold per day, the quantity currently in stock
        return

    Qstar = math.ceil(math.sqrt(2*meanDemand*fixedCost/holdCost)) #optimal order quantity Q*

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

    plotString = ("Missed sales: " + str(missedSales) + "," + " reorder quantity: " + str(reorderPoint))
    print plotString

    plt.plot(range(timeRange),quantity)
    plt.title("EOQ model of " + skuRef)
    plt.xlabel("Time in days")
    plt.ylabel("Stock level")
    plt.xticks(range(0,timeRange,90))
    # plt.text(timeRange/8, initialQ, plotString)


    return quantity, timeRange

def createDemand(lengthDays, seedNum):
    random.seed(seedNum)
    # Initialise
    B2CNextSaleDay = round(np.random.lognormal(0.1994, 0.4327), 0)
    B2BNextSaleDay = round(35.9183 * np.random.weibull(1.2590), 0)
    B2CSimSales = []
    B2BSimSales = []
    totSimSales = []
    B2CCumulatSales = 0
    B2BCumulatSales = 0
    cumulatSales = 0

    for time in range(lengthDays+1):
        # Generate B2C orders first
        # Sales = 1
        # TimeBtwn = lognormal(mean=0.1994, std=0.4327)
        # SalesCount = lognormal(mean=0.9519, std=0.7615)

        if B2CNextSaleDay == time:
            # Generate next next order time
            B2CNextSaleDay = round(np.random.lognormal(0.1994, 0.4327), 0)+time

            # Assuption that we can not get a 0 from the random output
            if B2CNextSaleDay == time:
                B2CNextSaleDay = time + 1

            # Generate number of sales for today
            B2CSalesCount = round(np.random.lognormal(0.9519, 0.7615), 0)

            # Assumption that we can not get a 0 from the random output
            # if B2CSalesCount == 0:
            #     B2CSalesCount = 1

            # Calculate number sales that day
            # Assumption that all sales are for only 1 bottle
            B2CCumulatSales += B2CSalesCount
            cumulatSales += B2CSalesCount

        # Generate B2B orders
        # Generate time between orders
        if B2BNextSaleDay == time:  # Sale occurs
            # Generate next next order time
            B2BNextSaleDay = round(35.9183 * np.random.weibull(1.2590), 0) + time
            # print B2BNextSaleDay

            # Assuption that we can not get a 0 from the random output
            if B2BNextSaleDay == time:
                B2BNextSaleDay = time + 1

            # Generate number of sales for today
            B2BSalesCount = int(round(41.685 * np.random.weibull(4.535), 0))

            # Assumption that we can not get a 0 from the random output
            # if B2BSalesCount == 0:
            #     B2BSalesCount = 1

            # For each sale generate number ordered
            B2BSaleAmount = sum(np.round(np.random.lognormal(2.0454, 1.0287, B2BSalesCount), 0))
            B2BCumulatSales += B2BSaleAmount
            cumulatSales += B2BSaleAmount

        # Record total sales


        # create 3 arrays for total sales - appending the current cumulative totals
        B2CSimSales.append(B2CCumulatSales)
        B2BSimSales.append(B2BCumulatSales)
        totSimSales.append(cumulatSales)

    # plt.plot(range(lengthDays + 1), totSimSales, 'c')
    # plt.plot(range(lengthDays + 1), B2CSimSales, 'm')
    # plt.plot(range(lengthDays + 1), B2BSimSales, 'y')
    # plt.legend(["Total sales", "B2C sales", "B2B sales", "Total simulated sales", "B2C simulated sales", "B2B simulated sales"])
    # plt.ylabel("cumulative sales volume")
    # plt.xlabel("Time in days")
    # plt.title("Sales volume over time")
    # plt.xlim([0, lengthDays + 25])
    # plt.show()
    return B2CSimSales, B2BSimSales, totSimSales

def getMeanData(salesDF):
    # Time
    timeDiff = (max(salesDF['Date']) - min(salesDF['Date'])).days
    # order mean - number of orders per sale day
    orderMean = float(len(salesDF['Date']))/len(salesDF['Date'].unique()) # Number of orders/time period
    salesDF.sort_values(by = 'Date', inplace = True)

    # Time mean
    timeBtwn = []
    for i in range(len(salesDF['Date'].unique())-1):
        timeBtwn.append((salesDF.Date.unique()[i+1]-salesDF.Date.unique()[i]).days)
    timeMean = np.mean(timeBtwn)

    # Sales mean
    salesMean = np.mean(salesDF['salesQ'])

    return orderMean, timeMean, salesMean

def createDemand2(inclOrder, inclTime, inclSales, timeRange, B2CsalesDF, B2BsalesDF, seedNum):
    # Initialise
    np.random.seed(seedNum)
    quantitySold = [0]*timeRange
    # Used for non-distribution demand
    B2CorderMean, B2CtimeMean, B2CsalesMean = getMeanData(B2CsalesDF)
    B2BorderMean, B2BtimeMean, B2BsalesMean = getMeanData(B2BsalesDF)

    # Find days
    B2CsaleDays = []
    B2BsaleDays = []
    B2CsumDays = 0
    B2BsumDays = 0

    # Find B2C sale days
    while B2CsumDays < timeRange:
        if inclTime:
            nextSale = int(round(np.random.lognormal(0.1994, 0.4327), 0))
        else:
            nextSale = int(round(B2CorderMean,0))
        B2CsumDays += nextSale
        B2CsaleDays.append(B2CsumDays)

    # Find B2B sale days
    while B2BsumDays < timeRange:
        if inclTime:
            nextSale = int(round(35.9183 * np.random.weibull(1.2590), 0))
        else:
            nextSale = int(round(B2BtimeMean,0))

        B2BsumDays += nextSale
        B2BsaleDays.append(B2BsumDays)

    # Make sure that the last date is within time range
    if B2BsaleDays[len(B2BsaleDays)-1] > timeRange:
        B2BsaleDays = B2BsaleDays[:-1]

    if B2CsaleDays[len(B2CsaleDays) - 1] > timeRange:
        B2CsaleDays = B2CsaleDays[:-1]

    # Find orders and amount of sales on a sale day
    # B2C orders
    B2CsumSales = [0]*len(B2CsaleDays)
    B2BsumSales = [0] * len(B2BsaleDays)
    totalSales = []
    for i in range(timeRange):
        salesList = []
        numOrders = 0
        if i in B2CsaleDays:
            if inclOrder:
                numOrders = int(round(np.random.lognormal(0.9519, 0.7615), 0))
            else:
                numOrders = int(round(B2CorderMean, 0))
            # Find number of sales in each order
            # for B2C all sales are 1 unit
            for j in range(numOrders):
                salesList.append(1)

        # B2B orders
        numOrders = 0
        if i in B2BsaleDays:
            if inclOrder:
                numOrders = int(round(41.685 * np.random.weibull(4.535), 0))
            else:
                numOrders = int(round(B2BorderMean,0))

            for j in range(numOrders):
                if inclSales:
                    salesList.append(int(round(np.random.lognormal(2.0454, 1.0287),0)))
                else:
                    salesList.append(round(B2BsalesMean))

        quantitySold[i-1] = salesList
        totalSales.append(sum(salesList))
    return quantitySold, totalSales

def eoqModel2(skuRef, inclOrder, inclTime, inclSales, inclSafety, B2CsalesDF, B2BsalesDF, seedNum, timeRange, serviceLvl, reorderPoint, Qstar, inclInputs):
    # initial variables - time in days
    prodCost = 5.36 + 1 + 0.2  # P production + transport cost + incoming warehouse rate, from email from Don
    initialQ = findCurrentQ(skuRef)
    if initialQ == None:
        print str(initialQ) + " None?"
        return
    # fixedCost = 133  # K, cost per order, Don't know where this comes from?!
    fixedCost = 213.17  # K, comes from average order processing from warehouse - Need fixed rate on freighting...
    holdCost = 0.001  # h, per bottle per day
    leadTime = 15  # L in days

    # Find demand
    demand, totalSales = createDemand2(inclOrder, inclTime, inclSales, timeRange, B2CsalesDF, B2BsalesDF, seedNum)
    meanDemand = sum(totalSales)/timeRange

    # Find re-order quantity
    if not inclInputs:
        Qstar = math.ceil(math.sqrt(2 * meanDemand * fixedCost / holdCost)) # optimal order quantity Q*

    # Find reorder quantity
    if not inclInputs: #only do this if reorder Q has not already been set
        if inclSafety:
            zScore = st.norm.ppf(serviceLvl)
            reorderPoint = math.ceil(meanDemand*leadTime) + round(zScore * np.std(totalSales) * np.sqrt(leadTime),0)
        else:
            reorderPoint = math.ceil(meanDemand*leadTime)

    # allocate/initialise
    quantity = [0] * timeRange
    reordered = False
    quantity[0] = initialQ
    arrivalTime = 0
    missedSales = 0
    missedTime = 0
    biggestMissedSale = 0
    smallestMissedSale = 99999

    for t in range(1, timeRange):
        # print t, type(quantity[t]), type(quantity[t-1]), type(sum(demand[t]))
        quantity[t] += quantity[t - 1] - sum(demand[t]) # quantity[t] should be 0 unless a reorder has been made
        if (quantity[t] < reorderPoint) & (reordered == False):
            if t + leadTime < timeRange:
                arrivalTime = t + leadTime
                quantity[arrivalTime] = Qstar
                reordered = True
        elif arrivalTime == t:
            reordered = False
        if quantity[t] < 0:
            quantity[t] + sum(demand[t]) # Re-add the unfulfillable demand
            stockLeft = quantity[t]
            for sales in sorted(demand[t], reverse=True):
                if sales < stockLeft:
                    quantity[t] - sales
                    stockLeft - sales
                else:
                    missedSales += sales
                    # Record biggest and smallest missed sales
                    if sales > biggestMissedSale:
                        biggestMissedSale = sales
                    if sales < smallestMissedSale:
                        smallestMissedSale = sales
            missedTime += 1


    # Find costs
    totProdCost = sum(totalSales)*prodCost
    totHoldCost = sum(quantity)*holdCost
    totCost = totProdCost + totHoldCost
    dailyCost = totCost/timeRange
    yearCost = dailyCost*365

    plotString = ("Missed sales: " + str(missedSales) + ", reorder quantity: " + str(reorderPoint)
                  + ", days without stock:" + str(missedTime) + ", annual cost: " + str(yearCost))
    # print plotString

    # plt.plot(range(timeRange), quantity)
    # plt.title("EOQ model of " + skuRef)
    # plt.xlabel("Time in days")
    # plt.ylabel("Stock level")
    # plt.xticks(range(0, timeRange, 90))
    # plt.axhline(y=reorderPoint , color='r', linestyle='-')
    # plt.text(10, initialQ, plotString)
    # plt.show()

    return quantity, missedSales, missedTime, reorderPoint, Qstar, yearCost, biggestMissedSale, smallestMissedSale

def plotSims(numSims, msdSalesCumul, msdTimeCumul, reorderSchd, QstarSchd):

    plt.plot(range(0, numSims), msdSalesCumul)
    plt.title("Missed sales")
    plt.xlabel("Simulation number")
    plt.ylabel("Number of sales missed")
    plotString1 = "Min = " + str(min(msdSalesCumul)) + ", " + "Max = " + str(
        max(msdSalesCumul)) + ", " + "Mean = " + str(np.mean(msdSalesCumul))
    plt.text(1, 0.75 * max(msdSalesCumul), plotString1)
    plt.show()

    plt.plot(range(0, numSims), msdTimeCumul)
    plt.title("Total days out of stock")
    plt.xlabel("Simulation number")
    plt.ylabel("Number of days with no stock")
    plotString1 = "Min = " + str(min(msdTimeCumul)) + ", " + "Max = " + str(
        max(msdTimeCumul)) + ", " + "Mean = " + str(np.mean(msdTimeCumul))
    plt.text(1, 0.75 * max(msdTimeCumul), plotString1)
    plt.show()

    plt.plot(range(0, numSims), reorderSchd)
    plt.title("Reorder amounts")
    plt.xlabel("Simulation number")
    plt.ylabel("Number of items before a reorder")
    plotString1 = "Min = " + str(min(reorderSchd)) + ", " + "Max = " + str(
        max(reorderSchd)) + ", " + "Mean = " + str(np.mean(reorderSchd))
    plt.text(1, 0.75 * max(reorderSchd), plotString1)
    plt.show()

    plt.plot(range(0, numSims), QstarSchd)
    plt.title("Amount of stock reordered")
    plt.xlabel("Simulation number")
    plt.ylabel("Number of items reordered")
    plotString1 = "Min = " + str(min(QstarSchd)) + ", " + "Max = " + str(
        max(QstarSchd)) + ", " + "Mean = " + str(np.mean(QstarSchd))
    plt.text(1, 0.75 * max(QstarSchd), plotString1)
    plt.show()

def sumStock(stockDF):
    # add all numbers at the same date together
    sumStock = []
    for i in stockDF['Date'].unique():
        sumStock.append(float(stockDF.StockQty[stockDF['Date'] == i].sum()))

    sumStockDF = pd.DataFrame({"SumStock": sumStock,
                               "Date": stockDF['Date'].unique()})

    sumStockDF.sort_values(by="Date", inplace=True)

    return sumStockDF

def stockVSsales():


# plot sims against stock lvls
    stockDF = ExploreData.readStock(skuRef)
# # sum unique dates
# # print stockDF
# sumStockDF = sumStock(stockDF)
# daysFromStart = []
# for i in sumStockDF.Date:
#     daysFromStart.append((i-min(sumStockDF.Date)).days)
#
# sumStockDF['dayCount'] = daysFromStart
# # Linear interpolating stock
# stockQrange = []
# for i in range(len(sumStockDF.dayCount[:-1])):
#     stockQrange.append(sumStockDF.iloc[i, sumStockDF.columns.get_loc('SumStock')])
#     diffDays = sumStockDF.iloc[i+1, sumStockDF.columns.get_loc('dayCount')] - sumStockDF.iloc[i, sumStockDF.columns.get_loc('dayCount')] - 1
#     diffSales = round((sumStockDF.iloc[i+1, sumStockDF.columns.get_loc('SumStock')] - sumStockDF.iloc[i, sumStockDF.columns.get_loc('SumStock')])/(diffDays-1), 0)
#
#     for j in range(diffDays):
#         stockQrange.append(diffSales*(j+1)+ sumStockDF.iloc[i, sumStockDF.columns.get_loc('SumStock')])
#
#
# # stockQrange.append(sumStockDF.SumStock[sumStockDF.Date==max(sumStockDF.Date)])
#
# plt.plot(range(timeRange), stockQrange)
# plt.show()

if __name__ == '__main__':
    startRunTime = time.time()
    loadSession()
    connection = dbEngine.connect()
    # skuRef = "FTRWOODGRAI"
    skuRef = "FTR"
    # skuRef = "all"
    # distMethod = 1 #1 = deterministic, 2 = poisson, 3 = occurrence + poisson, 4 = occurrence + normal
    # quantity, timeRange = EOQModel(skuRef, distMethod, dbSession)
    # simulateDemand(skuRef)
    ExploreData.loadSession()
    salesDF = ExploreData.readSales("ftr",1)
    B2CsalesDF = ExploreData.readSales("FTR",3)
    B2BsalesDF = ExploreData.readSales("FTR",2)
    # ozDF, twDF, activeDF, B2CsalesDF =  ExploreData.splitSales(salesDF)

    timeRange = 365*2  # in days, amount of days of stock reports
    serviceLvl = 0.95  # service level (alpha):
    numSims = 100

    # distMethod = 2
    # for distMethod in range(2,4):
    #     print distMethod
    #     EOQModel(skuRef, distMethod, dbSession)

    inclOrder = True
    inclTime = True
    inclSales = True
    inclSafety = True
    inclInputs = True

    simList = []
    for reorderPoint in range(400,2000,50):
        for Qstar in range(1500,4000,50):
            print reorderPoint, Qstar
            # Create arrays
            quantity = [[0 for x in range(timeRange + 1)] for y in range(0, numSims)]
            msdSalesCumul = []
            msdTimeCumul = []
            reorderSchd = []
            QstarSchd = []
            yearCostCumul = []
            lrgstMsdSaleCumul = []
            smlstMsdSaleCumul = []
            for i in range(0,numSims):
                seedNum = i
                quantity[i], missedSales, missedTime, reorderPoint, Qstar, yearCost, lrgstMsdSale, smlstMsdSale = \
                    eoqModel2(skuRef, inclOrder, inclTime, inclSales, inclSafety, B2CsalesDF, B2BsalesDF, seedNum, timeRange, serviceLvl,reorderPoint, Qstar, inclInputs) #missedSales, missedTime, reorderPoint, Qstar

                msdSalesCumul.append(missedSales)
                msdTimeCumul.append(missedTime)
                reorderSchd.append(reorderPoint)
                QstarSchd.append(Qstar)
                yearCostCumul.append(yearCost)
                lrgstMsdSaleCumul.append(lrgstMsdSale)
                smlstMsdSaleCumul.append(smlstMsdSale)

            simDF = pd.DataFrame({
                                "simulationNumber": range(1,numSims+1),
                                "reorderPoint": [reorderPoint]*len(range(1,numSims+1)),
                                "Qstar": [Qstar]*len(range(1,numSims+1)),
                                "missedDays": msdTimeCumul,
                                "missedSales": msdSalesCumul,
                                "largestMissedSale": lrgstMsdSaleCumul,
                                "smallestMissedSale": smlstMsdSaleCumul,
                                "quantity": quantity,
                                "Cost": yearCostCumul
            })
            simList.append(simDF)

    storeDF = pd.concat(simList, axis=0, ignore_index=True)

    # Write output to csv
    fileDir = "SimulationResults.csv" #file name
    storeDF.to_csv(fileDir, index=False)


    print("--- %s seconds ---" % (time.time() - startRunTime))

    # Plot simulation results
    # plotSims(numSims, msdSalesCumul, msdTimeCumul, reorderSchd, QstarSchd)

    # #turn individual tables to csvs
    # ozDF.to_csv("ozDF.csv", sep=',', header=True)
    # twDF.to_csv("twDF.csv", sep=',', header=True)
    # activeDF.to_csv("activeDF.csv", sep=',', header=True)

    # totSales, B2BTotSales, B2CTotSales, lengthDays = ExploreData.plotTotSales(B2CsalesDF, B2BsalesDF, salesDF)
    #
    # B2CSimSales = [[0 for x in range(lengthDays+1)] for y in range(1,11)]
    # B2BSimSales = [[0 for x in range(lengthDays+1)] for y in range(1,11)]
    # totSimSales = [[0 for x in range(lengthDays+1)] for y in range(1,11)]
    #
    # for i in range(1,11):
    #     seedNum = i
    #     B2CSimSales[i-1], B2BSimSales[i-1], totSimSales[i-1] = createDemand(lengthDays, seedNum)
    #
    #     plt.plot(range(lengthDays + 1), totSimSales[i-1], 'c')
    #     plt.plot(range(lengthDays + 1), B2CSimSales[i-1], 'm')
    #     plt.plot(range(lengthDays + 1), B2BSimSales[i-1], 'y')
    #
    # plt.legend(["Total sales", "B2C sales", "B2B sales", "Total simulated sales", "B2C simulated sales", "B2B simulated sales"])
    # plt.ylabel("cumulative sales volume")
    # plt.xlabel("Time in days")
    # plt.title("Sales volume over time")
    # plt.xlim([0, lengthDays + 25])
    # plt.show()


