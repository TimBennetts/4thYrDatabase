import os

from readData import *
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from createDatabase import OZPurchaseOrder, SalesData, TandWPurchaseOrder, hardToFind, \
    ordersExport, theActivePurchaseOrder, createDB, stockReports, freightInvoices, warehouseInvoices
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
    purchRef = []


    if orderType == 1 or orderType == 2: #Order types: 1 = all, 2 = B2B, 3 = B2C
        #OZPurchaseOrder
        if skuRef == "all":
            for row in dbSession.query(OZPurchaseOrder):
                salesQ.append(row.quantity)
                salesDate.append(row.orderDate)
                salesSku.append(row.skuNum)
                purchRef.append("Oz")
        else:
            for row in dbSession.query(OZPurchaseOrder):
                if skuRef.lower() in row.skuNum.lower():
                    salesQ.append(row.quantity)
                    salesDate.append(row.orderDate)
                    salesSku.append(row.skuNum)
                    purchRef.append("Oz")

        # TandWPurchaseOrder
        if skuRef == "all":
            for row in dbSession.query(TandWPurchaseOrder):
                salesQ.append(row.quantity)
                salesDate.append(row.orderDate)
                salesSku.append(row.skuNum)
                purchRef.append("TnW")
        else:
            for row in dbSession.query(TandWPurchaseOrder):
                if skuRef.lower() in row.skuNum.lower():
                    salesQ.append(row.quantity)
                    salesDate.append(row.orderDate)
                    salesSku.append(row.skuNum)
                    purchRef.append("TnW")

        # theActivePurchaseOrder
        if skuRef == "all":
            for row in dbSession.query(theActivePurchaseOrder):
                salesQ.append(row.quantity)
                salesDate.append(row.orderDate)
                salesSku.append(row.skuNum)
                purchRef.append("Active")
        else:
            for row in dbSession.query(theActivePurchaseOrder):
                if skuRef.lower() in row.skuNum.lower():
                    salesQ.append(row.quantity)
                    salesDate.append(row.orderDate)
                    salesSku.append(row.skuNum)
                    purchRef.append("Active")

    if orderType ==1 or orderType == 3:
        # hardToFind
        if skuRef == "all":
            for row in dbSession.query(hardToFind):
                salesQ.append(row.quantity)
                salesDate.append(row.orderDate)
                salesSku.append(row.skuNum)
                purchRef.append("B2C")
        else:
            for row in dbSession.query(hardToFind):
                if skuRef.lower() in row.skuNum.lower():
                    salesQ.append(row.quantity)
                    salesDate.append(row.orderDate)
                    salesSku.append(row.skuNum)
                    purchRef.append("B2C")

        # ordersExport
        if skuRef == "all":
            for row in dbSession.query(ordersExport):
                salesQ.append(row.quantity)
                salesDate.append(row.orderDate)
                salesSku.append(row.skuNum)
                purchRef.append("B2C")
        else:
            for row in dbSession.query(ordersExport):
                if skuRef.lower() in row.skuNum.lower():
                    salesQ.append(row.quantity)
                    salesDate.append(row.orderDate)
                    salesSku.append(row.skuNum)
                    purchRef.append("B2C")

        # SalesData
        if skuRef == "all":
            for row in dbSession.query(SalesData):
                salesQ.append(row.quantity)
                salesDate.append(row.orderDate)
                salesSku.append(row.skuNum)
                purchRef.append("B2C")
        else:
            for row in dbSession.query(SalesData):
                if skuRef.lower() in row.skuNum.lower():
                    salesQ.append(row.quantity)
                    salesDate.append(row.orderDate)
                    salesSku.append(row.skuNum)
                    purchRef.append("B2C")


    #add to dataframe
    salesDF = pd.DataFrame({"salesQ": salesQ,
                           "Date": salesDate,
                           "skuNum": salesSku,
                            "purchRef": purchRef})

    # print len(salesDF.Date)
    #remove non dated values
    salesDF = salesDF[salesDF['Date'] > datetime.datetime(2014,1,1,0,0,0).date()]

    return salesDF

def plotSales(salesDF, skuRef):
    # This function plots the sales for a product and plots it over time
    salesDF.sort_values(by="Date", inplace=True)
    plt.plot(salesDF['Date'], salesDF['salesQ'])
    plt.xlabel("Dates")
    plt.ylabel("Sales level")
    plt.title("Sales level for " + str(skuRef) + " items")
    # plt.title("Sales level for Wood Grain Future bottles")
    plt.show()

    plt.hist(salesDF['salesQ'], bins=25)
    plt.title("Histogram of sales for " + skuRef)
    plt.xlabel("Sales range")
    plt.ylabel("Number of appearances")
    plt.show()

def sumSales(salesDF, skuRef):

    #add all numbers at the same date together
    sumSales = []
    for date in salesDF['Date'].unique():
        sumSales.append(float(salesDF.salesQ[salesDF['Date']==date].sum()))

    sumSalesDF = pd.DataFrame({"salesQ": sumSales,
                               "Date": salesDF['Date'].unique()})

    sumSalesDF.sort_values(by="Date", inplace=True)

    # plt.plot(sumSalesDF['Date'], sumSalesDF['SumSales'])
    # plt.show()


    plt.hist(sumSalesDF['salesQ'], bins=25)
    plt.title("Histogram of sales for " + skuRef)
    plt.xlabel("Sales range")
    plt.ylabel("Number of appearances")
    # plt.show()

    meanSales = sumSalesDF['salesQ'].mean()
    # print meanSales
    # Appears to be poisson distributed
    # pArray = np.random.poisson(meanSales, 1000)
    # plt.hist(pArray)
    # plt.show()


    #Find the % a sale occurs on a day
    saleOccurPercent = float(len(sumSalesDF['Date']))/(sumSalesDF['Date'].max()-sumSalesDF['Date'].min()).days
    # print saleOccurPercent

    return sumSalesDF

def readStock(skuRef):
    # stockdf = [instance for instance in dbSession.query(stockReports)]

    #pre-allocate arrays
    stockQty = []
    stockDate = []
    stockSku = []
    uniqueSku = []
    sumStock = []
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

    for date in stockDF.Date.unique():
        sumStock.append(sum(stockDF.StockQty[stockDF.Date==date]))

    # plt.plot(stockDF.Date.unique(), sumStock)
    # plt.xlabel("Dates")
    # plt.ylabel("Stock level")
    # plt.title("Stock level for FTR items")
    # plt.show()

    return stockDF

def plotProcess(salesDF, skuRef):
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

    # Find order amounts
    orderAmt = []
    for date in salesDF.Date.unique():
        orderAmt.append(len(salesDF.salesQ[salesDF['Date'] == date]))

    #Plot the freq of time diff
    plt.hist(timeOrderDiff, bins = 20)
    plt.xlabel("Difference in time")
    plt.ylabel("Frequency")
    plt.xlim(0,18)
    plt.title("Histogram of time between orders")
    plt.show()


    # Plot the sales
    plt.hist(sumSalesDF['SumSales'], bins = 20)
    plt.xlabel("Sales amount")
    plt.ylabel("Frequency")
    plt.title("Histogram of sales amount")
    plt.show()


    # Plot the order amount
    plt.hist(orderAmt, bins=20)
    plt.xlabel("Number of orders")
    plt.ylabel("Frequency")
    plt.title("Distribution of order amounts")
    plt.show()



    csvFile = pd.DataFrame({"SalesQty": sumSalesDF["SumSales"],
                            "TimeBetweenOrders": timeOrderDiff,
                            "Date": sumSalesDF["Date"]})
    # csvFile.to_csv('AllSales.csv', sep=',')
    # sumSalesDF.to_csv('SummedSalesData.csv', sep=',')

    return csvFile

def plotTotSales(B2CsalesDF, B2BsalesDF, salesDF):
    # Find dates/days
    startDate = min(salesDF['Date'])
    # print startDate
    stopDate = max(salesDF['Date'])
    # print stopDate
    lengthDays = (stopDate-startDate).days
    print lengthDays # 1162
    # print type(lengthDays)

    # Pre-allocate array
    totSales = []
    B2CTotSales = []
    B2BTotSales = []
    cumulSales = 0
    cumulB2C = 0
    cumulB2B = 0

    # Loop through time
    for i in range(lengthDays+1):
        # print startDate + datetime.timedelta(i)
        # Sum total sales
        #cumulate sales
        cumulSales += salesDF.salesQ[salesDF['Date']==(startDate+datetime.timedelta(i))].sum()
        #Add to array
        totSales.append(cumulSales)
        # B2C cumulative sales
        cumulB2C += B2CsalesDF.salesQ[B2CsalesDF['Date']==(startDate+datetime.timedelta(i))].sum()
        B2CTotSales.append(cumulB2C)
        #B2B cumulative sales
        cumulB2B += B2BsalesDF.salesQ[B2BsalesDF['Date']==(startDate+datetime.timedelta(i))].sum()
        B2BTotSales.append(cumulB2B)

    plt.plot(range(lengthDays+1),totSales, 'r')
    plt.plot(range(lengthDays+1), B2CTotSales, 'b')
    plt.plot(range(lengthDays+1), B2BTotSales, 'g')
    plt.ylabel("cumulative sales volume")
    plt.xlabel("Time in days")
    plt.title("Sales volume over time")
    plt.xlim([0,lengthDays+25])
    # plt.show()

    return totSales, B2BTotSales, B2CTotSales, lengthDays

def splitSales(salesDF):
    ozDF = salesDF[salesDF.purchRef == "Oz"]
    twDF = salesDF[salesDF.purchRef == "TnW"]
    activeDF = salesDF[salesDF.purchRef == "Active"]
    B2CsalesDF = salesDF[salesDF.purchRef == "B2C"]

    return ozDF, twDF, activeDF, B2CsalesDF

def plotSplitSales(ozDF, twDF, activeDF, B2CsalesDF):
    # Get an equal x axis
    startDate = min(min(ozDF['Date']), min(twDF['Date']), min(activeDF['Date']), min(B2CsalesDF['Date']))
    lastDate = max(max(ozDF['Date']), max(twDF['Date']), max(activeDF['Date']), max(B2CsalesDF['Date']))
    lengthDays = (lastDate-startDate).days

    # Pre-allocate arrays
    ozTot =[]
    twTot = []
    activeTot = []
    B2CTot = []
    ozCumul = 0
    twCumul = 0
    activeCumul = 0
    B2CCumul = 0

    # Create cumulative sales
    for i in range(lengthDays+1):
        ozCumul += ozDF.salesQ[ozDF['Date']==(startDate+datetime.timedelta(i))].sum()
        twCumul += twDF.salesQ[twDF['Date']==(startDate+datetime.timedelta(i))].sum()
        activeCumul += activeDF.salesQ[activeDF['Date']==(startDate+datetime.timedelta(i))].sum()
        B2CCumul += B2CsalesDF.salesQ[B2CsalesDF['Date']==(startDate+datetime.timedelta(i))].sum()
        ozTot.append(ozCumul)
        twTot.append(twCumul)
        activeTot.append(activeCumul)
        B2CTot.append(B2CCumul)

    plt.plot(range(lengthDays + 1), ozTot, 'r')
    plt.plot(range(lengthDays + 1), twTot, 'b')
    plt.plot(range(lengthDays + 1), activeTot, 'g')
    plt.plot(range(lengthDays + 1), B2CTot, 'c')
    plt.ylabel("cumulative sales volume")
    plt.xlabel("Time in days")
    plt.title("Sales volume over time")
    plt.xlim([0, lengthDays + 25])
    plt.legend(["Oz", "T&W", "Active", "B2C"])
    plt.show()

def exploreWarehouse():
    #Initialise
    Qty = []
    Desc = []
    Unit = []
    Total = []
    Date = []
    for row in dbSession.query(warehouseInvoices).order_by(warehouseInvoices.orderNum.asc()):
        Qty.append(row.Quantity)
        Desc.append(row.Description)
        Unit.append(row.Unit)
        Total.append(row.Total)
        Date.append(row.Date)
    warehouseDF = pd.DataFrame({
                                "Quantity": Qty,
                                "Description": Desc,
                                "Unit": Unit,
                                "Total": Total,
                                "Date": Date
    })

    # Sum unique descriptions
    sumTotals = []
    for i in warehouseDF.Description.str.lower().unique():
        # Sum all the totals
        sumTotals.append(sum(warehouseDF.Total[warehouseDF.Description.str.lower() == i]))

    descSumDF = pd.DataFrame({
                            "SumTotals": sumTotals,
                            "Description": warehouseDF.Description.str.lower().unique()
    })

    descSumDF.sort_values('SumTotals', inplace=True)

   # Sum dates
    sumTotals = []
    inclDates = []
    inclQty = []
    for i in warehouseDF.Date[warehouseDF.Description=="pick/pack rate (per item)"].unique():
        sumTotals.append(sum(warehouseDF.Total[warehouseDF.Date==i]))
        inclDates.append(i)
        inclQty.append(sum(warehouseDF.Quantity[(warehouseDF.Date==i) & (warehouseDF.Description=="pick/pack rate (per item)")]))

    dateSumDF = pd.DataFrame({
                            "Date": inclDates,
                            "SumTotalCost": sumTotals,
                            "Qty": inclQty
    })
    dateSumDF.sort_values('Qty', inplace=True)

    # print sum(dateSumDF.SumTotalCost)/sum(dateSumDF.Qty) # Average cost per item
    # print dateSumDF
    fixedX = warehouseDF.Date[warehouseDF.Description=="order processing (per order)"]
    fixedY = warehouseDF.Total[warehouseDF.Description=="order processing (per order)"]
    fixed = pd.DataFrame({
        "X": fixedX,
        "Y": fixedY
    })
    fixed.sort_values('X', inplace=True)
    # plt.plot(fixed.X, fixed.Y)
    # plt.xlabel("Dates")
    # plt.ylabel("Total cost of order processing")
    # plt.title("Cost of order processing over time")
    # plt.show()
    print sum(fixedY)/len(fixedY)# Average fixed cost


if __name__ == '__main__':
    loadSession()
    connection = dbEngine.connect()
    skuRef = "ftr"
    exploreWarehouse()
    # readStock(skuRef='ftr')
    # readCosts()
    # salesDF = readSales(skuRef,1)
    # plotSales(sumSalesDF, skuRef)
    # print sumSalesDF
    # B2CsalesDF = readSales("FTR",3)
    # B2BsalesDF = readSales("FTR",2)
    # B2CsumSalesDF = sumSales(B2CsalesDF, "ftr")
    # B2BsumSalesDF = sumSales(B2BsalesDF, "ftr")
    # plotProcess(B2CsalesDF, skuRef)
    # plotProcess(B2BsalesDF, skuRef)
    # plotTotSales(B2CsalesDF,B2BsalesDF,salesDF)
    # ozDF, twDF, activeDF, B2CsalesDF = splitSales(salesDF)
    # plotSplitSales(ozDF, twDF, activeDF, B2CsalesDF)