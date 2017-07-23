import readData
import Models
import ExploreData

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
import scipy.stats as st


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

def readStock(skuRef):
    #pre-allocate arrays
    stockQty = []
    stockDate = []
    stockSku = []

    for row in dbSession.query(stockReports).order_by(stockReports.date.desc()):
        if skuRef in row.skuNum:
            stockQty.append(row.freeStock)
            stockDate.append(row.date)
            stockSku.append(row.skuNum)

    stockDF = pd.DataFrame({"StockQty": stockQty,
                            "Date": stockDate,
                            "skuNum": stockSku})

    return stockDF


if __name__ == '__main__':
    loadSession()

    skuRef = "FTR"
    salesDF = Models.getSalesDF(skuRef, dbSession) #need to input dbSession because across scripts
    stockDF = readStock(skuRef)
    # quantity1, timeRange = Models.EOCModel(skuRef, 1)
    # quantity2, timeRange = Models.EOCModel(skuRef, 2)
    # quantity3, timeRange = Models.EOCModel(skuRef, 3)
    # quantity4, timeRange = Models.EOCModel(skuRef, 4)


