import os

from readData import *
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from math import *
from createDatabase import theActivePurchaseOrder, createDB, stockReports
from matplotlib import *
import matplotlib.pyplot as plt
from numpy import *

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
        if row.skuNum == 'FTR-WOOD500':
            stockFreeStock.append(row.freeStock)
            stockDate.append(row.date)

    plt.plot(stockDate, stockFreeStock, '.-')
    plt.xlabel("Dates")
    plt.ylabel("Stock level")
    plt.title("Stock level for FTR-WOOD500")
    plt.show()

if __name__ == '__main__':
    loadSession()
    connection = dbEngine.connect()
    readStock()
