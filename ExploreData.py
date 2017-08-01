import os

from readData import *
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from createDatabase import OZPurchaseOrder, SalesData, TandWPurchaseOrder, hardToFind, \
    ordersExport, theActivePurchaseOrder, createDB, stockReports, freightInvoices
import matplotlib.pyplot as plt
import pandas as pd
from numpy import array
import numpy as np


def linreg(X, Y):

    # return a,b in solution to y = ax + b such that root mean square distance
    # between trend line and original points is minimized

    N = len(X)
    Sx = Sy = Sxx = Syy = Sxy = 0.0
    for x, y in zip(X, Y):
        Sx = Sx + x
        Sy = Sy + y
        Sxx = Sxx + x*x
        Syy = Syy + y*y
        Sxy = Sxy + x*y
    det = Sxx * N - Sx * Sx
    return (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det


def readCosts():
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

    #exploring correlations
    sortedDF = costDF.sort_values(by='TotalCost')
    # plt.plot(sortedDF['TotalCost'], sortedDF['NumShipped'])
    # plt.plot(sortedDF['TotalCost'], sortedDF['Volume']*1000)
    # plt.plot(sortedDF['TotalCost'], sortedDF['Weight'])
    # plt.show()

    #make a correlation matrix
    corrMatrix = costDF.corr()
    # print corrMatrix['TotalCost'].sort_values(ascending=False)
    # gives weight 0.85, volume 0.83 and numShipped 0.02
    # See if the two are correlated at all
    costDF['Added'] = costDF['Volume']+costDF['Weight']
    costDF['Multiplied'] = costDF['Volume'] * costDF['Weight']
    corrMatrix = costDF.corr()
    # print corrMatrix['TotalCost'].sort_values(ascending=False)
    # added 0.85 and multiplied 0.77
    # plotting
    sortedDF = costDF.sort_values(by='TotalCost')
    # plt.plot(sortedDF['TotalCost'], sortedDF['Added'])
    # plt.plot(sortedDF['TotalCost'], sortedDF['Multiplied'])
    # plt.legend(["Number shipped", "Volume", "Weight", "Added", "Multiplied"])


    # Checking using volume * 1000 (cm^3)
    costDF['VolumeCm'] = costDF['Volume']*1000
    costDF['AddedCm'] = costDF['VolumeCm'] + costDF['Weight']
    costDF['MultipliedCm'] = costDF['VolumeCm'] * costDF['Weight']
    sortedDF = costDF.sort_values(by='TotalCost')

    corrMatrix = costDF.corr()
    # print corrMatrix['TotalCost'].sort_values(ascending=False)


    # plt.plot(sortedDF['TotalCost'], sortedDF['AddedCm'])
    # plt.plot(sortedDF['TotalCost'], sortedDF['MultipliedCm']) # way too big
    # plt.show()

    #finding trend line
    addedA, addedB = linreg(sortedDF['TotalCost'], sortedDF['Added'])
    weightA, weightB = linreg(sortedDF['TotalCost'], sortedDF['Weight'])
    volA, volB = linreg(sortedDF['TotalCost'], sortedDF['Volume']*1000)

    print addedA,addedB, "vs", weightA, weightB, "vs", volA, volB

    # Making plots for added
    x = array(range(0, int(sortedDF['TotalCost'].max()), 100))
    y = addedA*x + addedB
    plt.plot(x,y)
    plt.plot(sortedDF['TotalCost'],sortedDF['Added'])

    # Making plots for weight
    x = array(range(0, int(sortedDF['TotalCost'].max()), 100))
    y = weightA * x + weightB
    plt.plot(x, y)
    plt.plot(sortedDF['TotalCost'], sortedDF['Weight'])

    # Making plots for volume
    x = array(range(0, int(sortedDF['TotalCost'].max()), 100))
    y = volA * x + volB
    plt.plot(x, y)
    plt.plot(sortedDF['TotalCost'], sortedDF['Volume']*1000)
    plt.show()



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

    return conn

def readSales(skuRef, orderType):
    # pre-allocate arrays
    salesQ = []
    salesDate = []
    salesSku = []


    if orderType == 1 or orderType == 2: #Order types: 1 = all, 2 = B2B, 3 = B2C
        #OZPurchaseOrder
        if skuRef == "all":
            for row in dbSession.query(OZPurchaseOrder):
                salesQ.append(row.quantity)
                salesDate.append(row.orderDate)
                salesSku.append(row.skuNum)
        else:
            for row in dbSession.query(OZPurchaseOrder):
                if skuRef.lower() in row.skuNum.lower():
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
                if skuRef.lower() in row.skuNum.lower():
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
                if skuRef.lower() in row.skuNum.lower():
                    salesQ.append(row.quantity)
                    salesDate.append(row.orderDate)
                    salesSku.append(row.skuNum)
    if orderType ==1 or orderType == 3:
        # hardToFind
        if skuRef == "all":
            for row in dbSession.query(hardToFind):
                salesQ.append(row.quantity)
                salesDate.append(row.orderDate)
                salesSku.append(row.skuNum)
        else:
            for row in dbSession.query(hardToFind):
                if skuRef.lower() in row.skuNum.lower():
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
                if skuRef.lower() in row.skuNum.lower():
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
                if skuRef.lower() in row.skuNum.lower():
                    salesQ.append(row.quantity)
                    salesDate.append(row.orderDate)
                    salesSku.append(row.skuNum)


    #add to dataframe
    salesDF = pd.DataFrame({"salesQ": salesQ,
                           "Date": salesDate,
                           "skuNum": salesSku})

    #remove non dated values
    salesDF = salesDF[salesDF['Date'] > datetime.datetime(2014,1,1,0,0,0).date()]

    return salesDF

def sumSales(salesDF, skuRef):

    #add all numbers at the same date together
    sumSales = []
    for i in salesDF['Date'].unique():
        sumSales.append(float(salesDF.salesQ[salesDF['Date']==i].sum()))

    sumSalesDF = pd.DataFrame({"SumSales": sumSales,
                               "Date": salesDF['Date'].unique()})

    sumSalesDF.sort_values(by="Date", inplace=True)

    # plt.plot(sumSalesDF['Date'], sumSalesDF['SumSales'])
    # plt.show()


    plt.hist(sumSalesDF['SumSales'], bins=100)
    plt.title("Histogram of sales for " + skuRef)
    plt.xlabel("Sales range")
    plt.ylabel("Number of appearances")
    # plt.show()

    meanSales = sumSalesDF['SumSales'].mean()
    print meanSales
    # Appears to be poisson distributed
    # pArray = np.random.poisson(meanSales, 1000)
    # plt.hist(pArray)
    # plt.show()


    #Find the % a sale occurs on a day
    saleOccurPercent = float(len(sumSalesDF['Date']))/(sumSalesDF['Date'].max()-sumSalesDF['Date'].min()).days
    print saleOccurPercent

    return salesDF


def readStock(skuRef):
    # stockdf = [instance for instance in dbSession.query(stockReports)]

    #pre-allocate arrays
    stockQty = []
    stockDate = []
    stockSku = []
    uniqueSku = []
    count = 0
    for sku in dbSession.query(stockReports.skuNum).distinct():
        uniqueSku.append(sku.skuNum)


    # #Multiple graphs
    # for sku in uniqueSku:
    #     stockFreeStock = []
    #     stockDate = []
    #     for row in dbSession.query(stockReports).order_by(stockReports.date.desc()):
    #         if row.skuNum == sku:
    #             stockFreeStock.append(row.freeStock)
    #             stockDate.append(row.date)
    #             if len(stockDate) == 16:
    #                 #plot
    #                 plt.plot(stockDate, stockFreeStock)
    #
    # plt.xlabel("Dates")
    # plt.ylabel("Stock level")
    # plt.title("Stock level for long term items")
    # plt.show()

  # Single graph
    for row in dbSession.query(stockReports).order_by(stockReports.orderDate.desc()):
        if skuRef.lower() in row.skuNum.lower():
            stockQty.append(row.freeStock)
            stockDate.append(row.orderDate)
            stockSku.append(row.skuNum)

    stockDF = pd.DataFrame({"StockQty": stockQty,
                            "Date": stockDate,
                            "skuNum": stockSku})

    plt.plot(stockDate, stockQty)
    plt.xlabel("Dates")
    plt.ylabel("Stock level")
    plt.title("Stock level for FTR items")
    plt.show()

    # return stockDF

def timeSinceOrder(salesDF):
    # need to create time since order array and amount ordered array for both B2C and B2B orders

    # add all numbers at the same date together
    sumSales = []
    for i in salesDF['Date'].unique():
        sumSales.append(float(salesDF.salesQ[salesDF['Date'] == i].sum()))

    sumSalesDF = pd.DataFrame({"SumSales": sumSales,
                               "Date": salesDF['Date'].unique()})

    sumSalesDF.sort_values(by="Date", inplace=True)

    timeOrderDiff = [0] #add a 0 to start to make even size w quantity list

    for i in sumSalesDF['Date']:
        if i == sumSalesDF['Date'].min():
            lastOrderDate = i
        else:
            timeOrderDiff.append((i-lastOrderDate).days)
            lastOrderDate = i


    #Plot the freq of time diff
    plt.hist(timeOrderDiff, bins = 20)
    plt.xlabel("Difference in time")
    plt.ylabel("Frequency")
    plt.title("Histogram of time between orders")
    # plt.show()


    # Plot the freq of amount
    plt.hist(sumSalesDF['SumSales'], bins = 20)
    plt.xlabel("Sales amount")
    plt.ylabel("Frequency")
    plt.title("Histogram of sales amount")
    # plt.show()


    # Plot time diff vs amount
    plt.scatter(timeOrderDiff, sumSalesDF['SumSales'])
    plt.xlabel("Time difference")
    plt.ylabel("Quantity ordered")
    plt.title("Distribution of sale times")
    # plt.show()



    csvFile = pd.DataFrame({"SalesQty": sumSalesDF["SumSales"],
                            "TimeBetweenOrders": timeOrderDiff,
                            "Date": sumSalesDF["Date"]})
    # csvFile.to_csv('AllSales.csv', sep=',')
    # sumSalesDF.to_csv('SummedSalesData.csv', sep=',')

    return csvFile


if __name__ == '__main__':
    loadSession()
    connection = dbEngine.connect()
    # readStock(skuRef='FTR')
    # readCosts()
    salesDF = readSales("ftr",1)
    sumSales(salesDF, "ftr")
    B2CsalesDF = readSales("FTR",3)
    B2BsalesDF = readSales("FTR",2)
    B2CCsv = timeSinceOrder(B2CsalesDF)
    B2BCsv = timeSinceOrder(B2BsalesDF)

    B2CCsv.to_csv('B2CData.csv', sep=',')
    B2BCsv.to_csv('B2BData.csv', sep=',')
    B2CsalesDF.to_csv("B2CRawData.csv", sep=',')
    B2BsalesDF.to_csv("B2BRawData.csv", sep=',')