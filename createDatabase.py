import sqlalchemy
import os
import csv

from readData import *
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
Base = declarative_base()
filePath = "CAM MIKE DATA\B2B\THE ACTIVE PO"
purchDirectory = os.path.abspath(os.path.join(filePath))
print purchDirectory


def createDB(dbname):
    dbEngine = create_engine('sqlite:///' + dbname, echo=False)

    Session = sessionmaker(bind=dbEngine)
    dbSession = Session()
    Base.metadata.create_all(dbEngine)
    print "db created"
    return dbSession


dbSession = createDB('bbyoSales.db')

class purchaseOrder(Base):
    __tablename__ = 'purchaseOrders'

    description = Column(String)
    skuNum = Column(String, primary_key=True)
    eanBarcode = Column(String)
    quantity = Column(Integer)
    costPrice = Column(Float)
    totalCost = Column(Float)
    gst = Column(Float)

def readPurchaseOrder(purchDirectory, session):
    wsList = readFiles(purchDirectory)
    wsRange = []
    headers = []
    # print type(wsList) #List
    for i,ws in enumerate(wsList):
        # print type(ws)
        list1, list2 = readWs(ws)  # list1 = wsRange, list2 = headers
        wsRange.append(list1)
        headers.append(list2)
        # print headers[0]
        #print type(wsRange)
        #wsRange[i(ws)][j][k] = k item in row j of table/book i
        for j, wsRow in enumerate(wsRange):
            # if len(wsRange[i][j]) < 7:
            #     mismatch = 7-len(wsRange[i][j])
            #     while mismatch > 0:
            #         wsRange[i][j].append(0)
            #         mismatch = mismatch - 1

            purchOrders = purchaseOrder(
                                        description = wsRange[i][j][0].value,
                                        skuNum = wsRange[i][j][1].value,
                                        eanBarcode = wsRange[i][j][2].value,
                                        quantity = wsRange[i][j][3].value,
                                        costPrice = wsRange[i][j][4].value,
                                        totalCost = wsRange[i][j][5].value,
                                        gst = wsRange[i][j][6].value,
                                        )
    session.add(purchOrders)
    session.commit()

readPurchaseOrder(purchDirectory, dbSession)

class SalesData(Base):
    __tablename__ = 'SalesData'

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

# def readSalesData(session, cells):
#     for i in range(len(cells)):
#         ordersExport = SalesData(
#             nameID=Column(String, primary_key=True),
#             email = Column(String)
#             paymentStatus = Column(String)
#             timePaid = Column(DateTime)
#             fulfillmentStatus = Column(String)
#             fulfillmentTime = Column(DateTime)
#             acceptMarketing = Column(String)
#             currency = Column(String)
#             priceSubtotal = Column(Float)
#             priceShipping = Column(Float)
#             priceTaxes = Column(Float)
#             priceTotal = Column(Float)
#             discountCode = Column(String)
#             discountAmount = Column(Float)
#             shippingMethod = Column(String)
#             timeEntryCreated = Column(DateTime)
#             lineitemQty = Column(Integer)
#             lineitemName = Column(String)
#             lineitemPrice = Column(Float)
#             lineitemComparePrice = Column(Float)  # what is this?
#             lineitemSku = Column(String)
#             lineitemReqShipping = Column(Boolean)
#             lineitemTaxable = Column(Boolean)
#             lineitemFulfillmentStatus = Column(String)
#             billingName = Column(String)
#             billingStreet = Column(String)
#             billingAddress1 = Column(String)
#             billingAddress2 = Column(String)
#             billingCompany = Column(String)
#             billingCity = Column(String)
#             billingZip = Column(String)
#             billingProvince = Column(String)
#             billingCountry = Column(String)
#             billingPhone = Column(String)
#             shippingName = Column(String)
#             shippingStreet = Column(String)
#             shippingAddress1 = Column(String)
#             shippingAddress2 = Column(String)
#             shippingCompany = Column(String)
#             shippingCity = Column(String)
#             shippingZip = Column(String)
#             shippingProvince = Column(String)
#             shippingCountry = Column(String)
#             shippingPhone = Column(String)
#             notes = Column(String)
#             noteAttributes = Column(String)
#             timeCancelled = Column(DateTime)
#             paymentMethod = Column(String)
#             paymentRef = Column(String)
#             refundAmount = Column(String)
#             vendor = Column(String)
#             ID = Column(Integer)
#             tags = Column(String)
#             riskLevel = Column(String)
#             source = Column(String)
#             lineitemDiscount = Column(Float)
#             tax1Name = Column(String)
#             tax1Value = Column(Float)
#             tax2Name = Column(String)
#             tax2Value = Column(Float)
#             tax3Name = Column(String)
#             tax3Value = Column(Float)
#             tax4Name = Column(String)
#             tax4Value = Column(Float)
#             tax5Name = Column(String)
#             tax5Value = Column(Float)
#         )
#

    # session.add(ordersExport)
    # session.commit()
