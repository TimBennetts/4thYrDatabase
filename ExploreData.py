import os

from readData import *
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from createDatabase import theActivePurchaseOrder, createDB, stockReports, freightInvoices
import matplotlib.pyplot as plt
import pandas as pd
from numpy import array

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

def readSales():
    data = Table('SalesData', metadata, autoload=True, autoload_with=dbEngine)
    print(repr(data))
    print data

def readStock():
    # stockdf = [instance for instance in dbSession.query(stockReports)]

    #pre-allocate arrays
    stockFreeStock = []
    stockDate = []
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
    for row in dbSession.query(stockReports).order_by(stockReports.date.desc()):
        if row.skuNum == 'FTRWOODGRAI':
            stockFreeStock.append(row.freeStock)
            stockDate.append(row.date)

    plt.plot(stockDate, stockFreeStock, '.-')
    plt.xlabel("Dates")
    plt.ylabel("Stock level")
    plt.title("Stock level for FTR-WOODGRAIN")
    plt.show()


if __name__ == '__main__':
    loadSession()
    connection = dbEngine.connect()
    # readStock()
    readCosts()