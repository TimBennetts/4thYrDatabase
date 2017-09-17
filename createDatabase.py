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
import datetime
import numpy as np

class theActivePurchaseOrder(Base):
    __tablename__ = 'theActivePurchaseOrders'

    orderNum = Column(String, primary_key=True)
    description = Column(String)
    skuNum = Column(String)
    quantity = Column(Integer) #or total quantity
    costPrice = Column(Float) #exclude gst
    totalCost = Column(Float) #exclude gst
    orderDate = Column(Date)
    
    def __str__(self):
      theStr = "Order: " + str(self.orderNum)
      theStr += ", SKU: " + str(self.skuNum)
      theStr += ", Date: " + str(self.date)
      theStr += "\nAmount: " + str(self.quantity)
      theStr += " @ $" + str(self.costPrice)
      theStr += " = $" + str(self.totalCost)
      return theStr

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
    orderDate = Column(Date)
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
    quantity = Column(Integer)
    costPrice = Column(Float)
    totalCost = Column(Float)
    skuNum = Column(String)
    orderDate = Column(Date)

class SalesData(Base):
    __tablename__ = 'SalesData'

    saleID = Column(String, primary_key=True)
    orderDate = Column(Date)
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
    skuNum = Column(String)
    quantity = Column(Integer)
    costPrice = Column(Float)
    lineItemDiscount = Column(Float)
    orderDiscount = Column(Float)
    priceAfterDisc = Column(Float)
    Taxes = Column(Float)
    finalPrice = Column(Float)

class hardToFind(Base):
    __tablename__ = 'hardToFind'

    orderNum = Column(Integer, primary_key=True)
    orderID = Column(Integer)
    customerName = Column(String)
    companyName = Column(String)
    shippingAddress = Column(String)
    shippingSuburb = Column(String)
    shippingState = Column(String)
    shippingPostcode = Column(Integer)
    shippingCountry = Column(String)
    orderDate = Column(Date)
    orderStatus = Column(String)
    shipDate = Column(Date)
    productName = Column(String)
    productVariation = Column(String)
    personalisation = Column(String)
    quantity = Column(Integer)
    skuNum = Column(String)
    seller = Column(String)
    costPrice = Column(Float)
    subTotal = Column(Float)
    shipping = Column(String)
    shippingMethod = Column(String)

class ordersExport(Base):
    __tablename__ = 'ordersExport'

    orderNum = Column(String, primary_key=True)
    nameID = Column(String)
    email = Column(String)
    paymentStatus = Column(String)
    timePaid = Column(String)
    fulfillmentStatus = Column(String)
    fulfillmentTime = Column(String)
    acceptMarketing = Column(String)
    currency = Column(String)
    priceSubtotal = Column(String)
    priceShipping = Column(String)
    priceTaxes = Column(String)
    priceTotal = Column(String)
    discountCode = Column(String)
    discountAmount = Column(String)
    shippingMethod = Column(String)
    orderDate = Column(Date)
    quantity = Column(Integer)
    lineitemName = Column(String)
    lineitemPrice = Column(Float)
    lineitemComparePrice = Column(String)  # what is this?
    skuNum = Column(String)
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
    timeCancelled = Column(String)
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
    tax1Value = Column(String)

class stockReports(Base):
    __tablename__ = 'StockReports'
    itemNum = Column(String, primary_key=True)
    skuNum = Column(String)
    description = Column(String)
    receipts = Column(Integer)
    picks = Column(Integer)
    frozenStock = Column(Integer)
    freeStock = Column(Integer)
    orderDate = Column(Date)

class warehouseInvoices(Base):
    __tablename__ = 'warehouseInvoiceInfo'
    orderNum = Column(Integer, primary_key=True)
    Quantity = Column(Integer)
    Description = Column(String)
    Unit = Column(Float)
    Total = Column(Float)
    Date = Column(Date)

class freightInvoices(Base):
    __tablename__ = 'freightInvoiceInfo'
    orderNum = Column(String, primary_key=True)
    orderDate = Column(Date)
    weight = Column(Float)
    volume = Column(Float)
    chargeable = Column(Float)
    numShipped = Column(Integer)
    ETD = Column(Date) # Estimated time departed
    ETA = Column(Date) # Estimated time of arrival
    totalCost = Column(Float)


def createDB(dbname):
    global dbEngine
    global dbSession
    
    dbEngine = create_engine('sqlite:///' + dbname, echo=False)
    
    #create tables
    Base.metadata.create_all(dbEngine)
    Session = sessionmaker()
    Session.configure(bind=dbEngine)
    
    #create Session
    dbSession = Session()

    print "DB created"
    
    return dbSession


def readPurchaseOrder(purchDirectory):
    wsList = readFiles(purchDirectory)
    print purchDirectory
    wsRange = []
    headers = []
    for ws in wsList:
        list1, list2 = readWs(ws)  # list1 = wsRange, list2 = headers
        wsRange.append(list1)
        headers.append(list2)

    counter = 1
    for i in range(len(wsRange)):
        for j in range(len(wsRange[i])):
            if "OZSALE" in purchDirectory:
                OZPurchOrder = OZPurchaseOrder(
                    orderNum = counter,
                    itemName = wsRange[i][j][0].value,
                    skuNum = wsRange[i][j][4].value,
                    quantity = wsRange[i][j][1].value,
                    costPrice = wsRange[i][j][2].value,
                    totalCost = wsRange[i][j][3].value,
                    orderDate = dateTimeConv(wsRange[i][j][5].value)
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
                                                    orderDate = dateTimeConv(wsRange[i][j][8].value),
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
                                                            orderNum = counter,
                                                            description = wsRange[i][j][0].value,
                                                            skuNum = wsRange[i][j][1].value,
                                                            quantity = wsRange[i][j][2].value,  # or total quantity
                                                            costPrice = wsRange[i][j][3].value,  # exclude gst
                                                            totalCost = wsRange[i][j][4].value,  # exclude gst
                                                            orderDate = dateTimeConv(wsRange[i][j][5].value),

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
                                    orderDate = dateTimeConv(wsRange[i][j][6].value),
                )
            dbSession.add(stockReport)
            counter1 = counter1 + 1
    dbSession.commit()

def readSales(salesDirectory):
    print salesDirectory
    wsList = readFiles(salesDirectory)
    wsRange = []
    headers = []
    for ws in wsList:
        list1, list2 = readSaleWs(ws)  # list1 = wsRange, list2 = headers
        wsRange.append(list1)
        headers.append(list2)

    for i in range(len(wsRange)):
         counter2 = 0
         for j in range(len(wsRange[i])):
            if i == 0: #hard to find
                hardtofind = hardToFind(
                                        orderNum = counter2,
                                        orderID = wsRange[i][j][0].value,
                                        customerName = wsRange[i][j][1].value,
                                        companyName = wsRange[i][j][2].value,
                                        shippingAddress = wsRange[i][j][3].value,
                                        shippingSuburb = wsRange[i][j][4].value,
                                        shippingState = wsRange[i][j][5].value,
                                        shippingPostcode = wsRange[i][j][6].value,
                                        shippingCountry = wsRange[i][j][7].value,
                                        orderDate = dateTimeConv(wsRange[i][j][8].value),
                                        orderStatus = wsRange[i][j][9].value,
                                        shipDate = dateTimeConv(wsRange[i][j][10].value),
                                        productName = wsRange[i][j][11].value,
                                        productVariation = wsRange[i][j][12].value,
                                        personalisation = wsRange[i][j][13].value,
                                        quantity = wsRange[i][j][14].value,
                                        skuNum = wsRange[i][j][15].value,
                                        seller = wsRange[i][j][16].value,
                                        costPrice = wsRange[i][j][17].value,
                                        subTotal = wsRange[i][j][18].value,
                                        shipping = wsRange[i][j][19].value,
                                        shippingMethod = wsRange[i][j][20].value,
                )
                dbSession.add(hardtofind)

            elif i == 1: #orders export
                ordersexport = ordersExport(
                                            orderNum = counter2,
                                            nameID = wsRange[i][j][0].value,
                                            email = wsRange[i][j][1].value,
                                            paymentStatus = wsRange[i][j][2].value,
                                            timePaid = wsRange[i][j][3].value,
                                            fulfillmentStatus = wsRange[i][j][4].value,
                                            fulfillmentTime = wsRange[i][j][5].value,
                                            acceptMarketing = wsRange[i][j][6].value,
                                            currency = wsRange[i][j][7].value,
                                            priceSubtotal = wsRange[i][j][8].value,
                                            priceShipping = wsRange[i][j][9].value,
                                            priceTaxes = wsRange[i][j][10].value,
                                            priceTotal = wsRange[i][j][11].value,
                                            discountCode = wsRange[i][j][12].value,
                                            discountAmount = wsRange[i][j][13].value,
                                            shippingMethod = wsRange[i][j][14].value,
                                            orderDate = dateTimeConv(wsRange[i][j][15].value),
                                            quantity = wsRange[i][j][16].value,
                                            lineitemName = wsRange[i][j][17].value,
                                            lineitemPrice = wsRange[i][j][18].value,
                                            lineitemComparePrice = wsRange[i][j][19].value,  # what is this?
                                            skuNum = wsRange[i][j][20].value,
                                            lineitemReqShipping = wsRange[i][j][21].value,
                                            lineitemTaxable = wsRange[i][j][22].value,
                                            lineitemFulfillmentStatus = wsRange[i][j][23].value,
                                            billingName = wsRange[i][j][24].value,
                                            billingStreet = wsRange[i][j][25].value,
                                            billingAddress1 = wsRange[i][j][26].value,
                                            billingAddress2 = wsRange[i][j][27].value,
                                            billingCompany = wsRange[i][j][28].value,
                                            billingCity = wsRange[i][j][29].value,
                                            billingZip = wsRange[i][j][30].value,
                                            billingProvince = wsRange[i][j][31].value,
                                            billingCountry = wsRange[i][j][32].value,
                                            billingPhone = wsRange[i][j][33].value,
                                            shippingName = wsRange[i][j][34].value,
                                            shippingStreet = wsRange[i][j][35].value,
                                            shippingAddress1 = wsRange[i][j][36].value,
                                            shippingAddress2 = wsRange[i][j][37].value,
                                            shippingCompany = wsRange[i][j][38].value,
                                            shippingCity = wsRange[i][j][39].value,
                                            shippingZip = wsRange[i][j][40].value,
                                            shippingProvince = wsRange[i][j][41].value,
                                            shippingCountry = wsRange[i][j][42].value,
                                            shippingPhone = wsRange[i][j][43].value,
                                            notes = wsRange[i][j][44].value,
                                            noteAttributes = wsRange[i][j][45].value,
                                            timeCancelled = wsRange[i][j][46].value,
                                            paymentMethod = wsRange[i][j][47].value,
                                            paymentRef = wsRange[i][j][48].value,
                                            refundAmount = wsRange[i][j][49].value,
                                            vendor = wsRange[i][j][50].value,
                                            ID = wsRange[i][j][51].value,
                                            tags = wsRange[i][j][52].value,
                                            riskLevel = wsRange[i][j][53].value,
                                            source = wsRange[i][j][54].value,
                                            lineitemDiscount = wsRange[i][j][55].value,
                                            tax1Name = wsRange[i][j][56].value,
                                            tax1Value = wsRange[i][j][57].value,
                )
                dbSession.add(ordersexport)

            elif i == 2: # sales
                salesdata = SalesData(
                                    saleID = wsRange[i][j][0].value,
                                    orderDate = dateTimeConv(wsRange[i][j][1].value),
                                    orderName = wsRange[i][j][2].value,
                                    transactionType = wsRange[i][j][3].value,
                                    saleType = wsRange[i][j][4].value,
                                    salesChannel = wsRange[i][j][5].value,
                                    POSLocation = wsRange[i][j][6].value,
                                    billingCountry = wsRange[i][j][7].value,
                                    billingRegion = wsRange[i][j][8].value,
                                    billingCity = wsRange[i][j][9].value,
                                    shippingCountry = wsRange[i][j][10].value,
                                    shippingRegion = wsRange[i][j][11].value,
                                    shippingCity = wsRange[i][j][12].value,
                                    productType = wsRange[i][j][13].value,
                                    productVendor = wsRange[i][j][14].value,
                                    productTitle = wsRange[i][j][15].value,
                                    productVariantTitle = wsRange[i][j][16].value,
                                    skuNum = wsRange[i][j][17].value,
                                    quantity = wsRange[i][j][18].value,
                                    costPrice = wsRange[i][j][19].value,
                                    lineItemDiscount = wsRange[i][j][20].value,
                                    orderDiscount = wsRange[i][j][21].value,
                                    priceAfterDisc = wsRange[i][j][22].value,
                                    Taxes = wsRange[i][j][23].value,
                                    finalPrice = wsRange[i][j][24].value,
                    )

                dbSession.add(salesdata)
            counter2 = counter2 + 1
    dbSession.commit()

def readWarehousing(warehouseDF):

    for row in range(len(warehouseDF)):
        warehouseInvoiceInfo = warehouseInvoices(
                                                orderNum = row,
                                                Quantity = int(warehouseDF.Quantity[row].item()),
                                                Description = warehouseDF.Description[row],
                                                Unit = float(warehouseDF.Unit[row].item()),
                                                Total = float(warehouseDF.Total[row].item()),
                                                Date = warehouseDF.Date[row].to_pydatetime().date()
        )
        dbSession.add(warehouseInvoiceInfo)
    dbSession.commit()

def loadSession():
    global dbEngine
    global dbSession
    global m
    global conn

    dbname = "BBBYO.db"
    dbEngine = create_engine('sqlite:///' + dbname, echo=False)
    Session = sessionmaker()
    Session.configure(bind=dbEngine)
    dbSession = Session()
    conn = dbEngine.connect()
    m = MetaData(dbEngine, reflect=True)

def skuCompletion():
    # salesDF = readSales(skuRef = "all", orderType = 1)

    #load session
    # loadSession()

    # # Get db table names
    # dbTables = []
    # m.reflect(dbEngine)
    # for table in m.tables.values():
    #     dbTables.append(table.name)
    # Find the incomplete lists
    # incompSkus = []
    # for i in dbTables:
    #     count = 0
    #     skuCount = 0
    #     print i
    #     print type(i)
    #     print type(i.decode('utf-8'))
    #     for row in dbSession.query(i.decode('utf-8')):
    #         # Count entries
    #         count += 1
    #         # Count number of sku entries
    #         if row.skuNum != "":
    #             skuCount += 1
    #     if skuCount != count:
    #         incompSkus.append(i)

    for row in dbSession.query(hardToFind):
            if "fb" in row.productName.lower() or "future" in row.productName.lower():
                row.skuNum = "ftr"
                dbSession.commit()

    for row in dbSession.query(SalesData):
        if row.skuNum == "":
            if "fb" in row.productTitle.lower() or "future" in row.productTitle.lower():
                row.skuNum = "ftr"
                dbSession.commit()


    for row in dbSession.query(ordersExport):
        if row.skuNum == "":
            if "fb" in row.lineitemName.lower() or "future" in row.lineitemName.lower():
                row.skuNum = "ftr"
                dbSession.commit()




def initialise():
    createDB(dbname)

    print os.getcwd()

    # Adding the purchase order files into the database
    for subDirs, dirs, files in os.walk(purchDirectory):
        if subDirs != purchDirectory:
            # print subDirs
            readPurchaseOrder(subDirs)

    # Adding the stock reports to the database
    readStockReports(stockDirectory)

    # Adding the sales files to the database
    readSales(salesDirectory)
    # Adding the cost files to the database
    warehouseDF = readWarehouse(warehouseDir)
    readWarehousing(warehouseDF)

    # Add skus for incomplete lists
    # skuCompletion()

if __name__ == '__main__':
  # Change these
  dbname = "BBBYO.db"

  # metadata = MetaData()
  # Session = sessionmaker()
  # dbEngine = None
  # dbSession = None

  filePath = "CAM MIKE DATA\B2B"
  filePath2 = "CAM MIKE DATA\Stock Reports"
  filePath3 = "CAM MIKE DATA\B2C"
  filePath4 = "CAM MIKE DATA\Costings"
  filePath5 = "CAM MIKE DATA\Costings\Warehouse"

  purchDirectory = os.path.abspath(os.path.join(filePath))
  stockDirectory = os.path.abspath(os.path.join(filePath2))
  salesDirectory = os.path.abspath(os.path.join(filePath3))
  costDirectory = os.path.abspath(os.path.join(filePath4))
  warehouseDir = os.path.abspath(os.path.join(filePath5))

  # warehouseDF = readWarehouse(warehouseDir)
  # readWarehousing(warehouseDF)
  #
  initialise()