import sqlalchemy
import os
import csv
import sqlite3
# from Classes import TandWPurchaseOrder
# import Classes; reload(Classes)

from readData import *
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


#Change these
dbname = "PurchaseOrders"

metadata = MetaData()
Base = declarative_base()
filePath = "CAM MIKE DATA\B2B"
filePath2 = "CAM MIKE DATA\Stock Reports"
purchDirectory = os.path.abspath(os.path.join(filePath))
stockDirectory = os.path.abspath(os.path.join(filePath2))
print purchDirectory

class theActivePurchaseOrder(Base):
    __tablename__ = 'theActivePurchaseOrders'

    date = Column(String)
    description = Column(String)
    skuNum = Column(String, primary_key=True)
    eanBarcode = Column(String)
    quantity = Column(Integer) #or total quantity
    costPrice = Column(Float) #exclude gst
    totalCost = Column(Float) #exclude gst
    gst = Column(Float)

class TandWPurchaseOrder(Base):
    __tablename__ = 'TandWPurchaseOrder'

    orderNum = Column(String, primary_key=True)
    barcode = Column(String)
    skuNum = Column(String)
    shipID = Column(String)
    description = Column(String)
    quantity = Column(Integer)
    costPrice = Column(Float)
    totalCost = Column(Float)
    agreedDeliveryDate = Column(String)
    colour = Column(String)
    material = Column(String)
    itemDims = Column(String)
    CoO = Column(String) #what even is this?
    itemWeightEa = Column(String)
    shipWidth = Column(String)
    shipDepth = Column(String)
    shipHeight = Column(String)
    itemCubic = Column(String)
    totalCubic = Column(String)
    deadweight = Column(String)

class OZPurchaseOrder(Base):
    __tablename__ = 'OZPurchaseOrder'

    orderNum = Column(String, primary_key=True)
    itemName = Column(String)
    skuNum = Column(String)
    size = Column(String)
    quantity = Column(Integer)
    costPrice = Column(Float)
    totalCost = Column(Float)
    boxNum = Column(String)
    shipped = Column(String)

class SalesData(Base):
    __tablename__ = 'SalesData'

    saleID = Column(String, primary_key=True)
    date = Column(String)
    orderName = Column(String)
    transactionType = Column(String)
    saleType = Column(String)
    salesChannel = Column(String)
    POSLocation = Column(String)
    billingCountry = Column(String)
    billingRegion = Column(String)
    billingCity = Column(String)
    shippingCountry = Column(String)
    shippingRegion = Column(String)
    shippingCity = Column(String)
    productType = Column(String)
    productVendor = Column(String)
    productTitle = Column(String)
    productVariantTitle = Column(String)
    productVariantTitleSku = Column(String)
    quantity = Column(Integer)
    costPrice = Column(Float)
    lineItemDiscount = Column(Float)
    orderDiscount = Column(Float)
    priceAfterDisc = Column(Float)
    Taxes = Column(Float)
    finalPrice = Column(Float)

class hardToFind(Base):
    __tablename__ = 'hardToFind'

    orderID = Column(Integer, primary_key=True)
    customerName = Column(String)
    shippingAddress = Column(String)
    shippingSuburb = Column(String)
    shippingState = Column(String)
    shippingPostcode = Column(Integer)
    shippingCountry = Column(String)
    orderDate = Column(String)
    orderStatus = Column(String)
    shipDate = Column(String)

class ordersExport(Base):
    __tablename__ = 'ordersExport'

    nameID = Column(String, primary_key=True)
    email = Column(String)
    paymentStatus = Column(String)
    timePaid = Column(DateTime)
    fulfillmentStatus = Column(String)
    fulfillmentTime = Column(DateTime)
    acceptMarketing = Column(String)
    currency = Column(String)
    priceSubtotal = Column(Float)
    priceShipping = Column(Float)
    priceTaxes = Column(Float)
    priceTotal = Column(Float)
    discountCode = Column(String)
    discountAmount = Column(Float)
    shippingMethod = Column(String)
    timeEntryCreated = Column(DateTime)
    lineitemQty = Column(Integer)
    lineitemName = Column(String)
    lineitemPrice = Column(Float)
    lineitemComparePrice = Column(Float)  # what is this?
    lineitemSku = Column(String)
    lineitemReqShipping = Column(Boolean)
    lineitemTaxable = Column(Boolean)
    lineitemFulfillmentStatus = Column(String)
    billingName = Column(String)
    billingStreet = Column(String)
    billingAddress1 = Column(String)
    billingAddress2 = Column(String)
    billingCompany = Column(String)
    billingCity = Column(String)
    billingZip = Column(String)
    billingProvince = Column(String)
    billingCountry = Column(String)
    billingPhone = Column(String)
    shippingName = Column(String)
    shippingStreet = Column(String)
    shippingAddress1 = Column(String)
    shippingAddress2 = Column(String)
    shippingCompany = Column(String)
    shippingCity = Column(String)
    shippingZip = Column(String)
    shippingProvince = Column(String)
    shippingCountry = Column(String)
    shippingPhone = Column(String)
    notes = Column(String)
    noteAttributes = Column(String)
    timeCancelled = Column(DateTime)
    paymentMethod = Column(String)
    paymentRef = Column(String)
    refundAmount = Column(String)
    vendor = Column(String)
    ID = Column(Integer)
    tags = Column(String)
    riskLevel = Column(String)
    source = Column(String)
    lineitemDiscount = Column(Float)
    tax1Name = Column(String)
    tax1Value = Column(Float)
    tax2Name = Column(String)
    tax2Value = Column(Float)
    tax3Name = Column(String)
    tax3Value = Column(Float)
    tax4Name = Column(String)
    tax4Value = Column(Float)
    tax5Name = Column(String)
    tax5Value = Column(Float)

class stockReports(Base):
    __tablename__ = 'StockReports'
    itemNum = Column(String, primary_key=True)
    skuNum = Column(String)
    description = Column(String)
    receipts = Column(Integer)
    picks = Column(Integer)
    frozenStock = Column(Integer)
    freeStock = Column(Integer)




def createDB(dbname):
    global dbEngine
    global dbSession

    dbEngine = create_engine('sqlite:///' + dbname, echo=False)
    #create Session
    Session = sessionmaker()
    Session.configure(bind=dbEngine)
    dbSession = Session()

    #create tables
    Base.metadata.create_all(dbEngine)
    print "db created"


def readPurchaseOrder(purchDirectory, session):
    wsList = readFiles(purchDirectory)
    print purchDirectory
    wsRange = []
    headers = []
    for ws in wsList:
        list1, list2 = readWs(ws)  # list1 = wsRange, list2 = headers
        wsRange.append(list1)
        headers.append(list2)

    if "OZSALE" in purchDirectory:
        wsRange = refineRange(wsRange, headers) #ToDo

    counter = 1
    for i in range(len(wsRange)):
        for j in range(len(wsRange[i])):
            if "OZSALE" in purchDirectory:
                OZPurchOrder = OZPurchaseOrder(
                    orderNum = counter,
                    itemName=Column(String),
                    skuNum = Column(String, primary_key=True),
                    quantity = Column(Integer),
                    costPrice = Column(Float),
                    totalCost = Column(Float),
                )
                dbSession.add(OZPurchOrder)

            elif "TEMPLE AND WEBSTER" in purchDirectory:
                TandWPurchOrder = TandWPurchaseOrder(
                                                    orderNum = counter,
                                                    barcode = wsRange[i][j][1].value,
                                                    skuNum = wsRange[i][j][2].value,
                                                    shipID = wsRange[i][j][3].value,
                                                    description = wsRange[i][j][4].value,
                                                    quantity = wsRange[i][j][5].value,
                                                    costPrice = wsRange[i][j][6].value,
                                                    totalCost = wsRange[i][j][7].value,
                                                    agreedDeliveryDate = wsRange[i][j][8].value,
                                                    colour = wsRange[i][j][9].value,
                                                    material = wsRange[i][j][10].value,
                                                    itemDims = wsRange[i][j][11].value,
                                                    CoO = wsRange[i][j][12].value,  # what even is this?
                                                    itemWeightEa = wsRange[i][j][13].value,
                                                    shipWidth = wsRange[i][j][14].value,
                                                    shipDepth = wsRange[i][j][15].value,
                                                    shipHeight = wsRange[i][j][16].value,
                                                    itemCubic = wsRange[i][j][17].value,
                                                    totalCubic = wsRange[i][j][18].value,
                                                    deadweight = wsRange[i][j][19].value,
                                                    )
                dbSession.add(TandWPurchOrder)
            elif "THE ACTIVE" in purchDirectory:
                theActivePurchOrder = theActivePurchaseOrder(
                   #ToDO
                )
                dbSession.add(theActivePurchOrder)
            counter = counter + 1
    dbSession.commit()

def readStockReports(stockDirectory):
    wsList = readFiles(stockDirectory)
    print stockDirectory
    wsRange =[]
    headers =[]
    for ws in wsList:
        list1, list2 = readStockWs(ws)  # list1 = wsRange, list2 = headers
        wsRange.append(list1)
        headers.append(list2)
    counter1 = 0
    for i in range(len(wsRange)):
        for j in range(len(wsRange[i])):
            stockReport = stockReports(
                itemNum = counter1,
                skuNum = wsRange[i][j][0].value,
                description = wsRange[i][j][1].value,
                receipts = wsRange[i][j][2].value,
                picks = wsRange[i][j][3].value,
                frozenStock = wsRange[i][j][4].value,
                freeStock = wsRange[i][j][5].value,
                )
            dbSession.add(stockReport)
            counter1 = counter1 + 1
    dbSession.commit()

createDB(dbname)
Base.metadata.create_all(dbEngine)
# for subDirs, dirs, files in os.walk(purchDirectory):
#     if subDirs != purchDirectory:
#         # print subDirs
#         readPurchaseOrder(subDirs, dbSession)
readStockReports(stockDirectory)


