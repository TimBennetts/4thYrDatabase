import os
import xlrd
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

from sqlalchemy import *
from xlrd import *


def getCellRange(start_col, start_row, end_col, end_row, ws):
    return [ws.row_slice(row, start_colx=start_col, end_colx=end_col + 1) for row in xrange(start_row, end_row + 1)]

def recordHeaders(startRow, endCol, ws):
    headers = []
    counter = 0
    while counter < endCol:
        headers.append(ws.cell(startRow-1, counter))
        counter = counter + 1
    return headers

def readWs(ws):
    #inputs = worksheet
    startCol= 0
    endCol = ws.ncols
    #endCol = 7
    #finding row range
    for i in range(0, ws.nrows):
        if ws.cell(i, 0).value == "DESCRIPTION":
            startRow = i + 1
        elif ws.cell(i, 0).value == "TOTAL":
            endRow = i - 1
    wsRange = getCellRange(startCol, startRow, 6, endRow, ws)
    headers = recordHeaders(startRow, endCol, ws) #list of headers

    return wsRange, headers


def readFiles(directory):
    i = 0
    wsList = []
    #importing all files in directory
    for root,dirs,files in os.walk(directory):
        for file in files:
            if file.endswith(".xlsx"):
                # print file
                fin = xlrd.open_workbook(os.path.abspath(os.path.join(directory,file)))
                # print file

                #grab first worksheet
                wsList.append(fin.sheet_by_index(0))

                #= fin.sheet_by_index(0)
                #wsRange = readWs(ws)
                #print wsRange
    #return wsRange
    # print ws
    return(wsList)

# class purchaseOrder(Base):
#     __tablename__ = 'purchaseOrders'
#
#     description = Column(String)
#     skuNum = Column(String, primary_key=True)
#     eanBarcode = Column(String)
#     quantity = Column(Integer)
#     costPrice = Column(Float)
#     totalCost = Column(Float)
#     gst = Column(Float)
#
#
# filePath = "CAM MIKE DATA\B2B\THE ACTIVE PO"
# directory = os.path.abspath(os.path.join(filePath))
# print directory
# wsRange = []
# headers = []
# wsList = readFiles(directory)
#     # print type(wsList) #List
# for i,ws in enumerate(wsList):
#     #print i
#     list1, list2 = readWs(ws) #list1 = wsRange, list2 = headers
#     wsRange.append(list1)
#     headers.append(list2)
# purchaseOrders = ["DESCRIPTION", "SKU_Number", "Quantity_Cost", "Price_EXC_GST", "Total_Cost_EXC_GST"]
#
# print type(wsRange[0][0][4].value)
# print type(wsRange[0][0][4])
# wsRange[0][0].append(0)
# print type(wsRange[0][0][5].value)




