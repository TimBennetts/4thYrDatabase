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
    # print ws.cell(startRow-1, counter)
    # print startRow -1
    # print counter
    while counter < endCol:
        if ws.cell(startRow-1, counter).value == "":
            headers.append("empty")
        else:
            headers.append(ws.cell(startRow-1, counter))
        counter = counter + 1
    return headers

def readWs(ws):
    #inputs = worksheet
    startCol= 0
    startRow = 0
    #finding row range
    for i in range(0, ws.nrows):
        #if ws.cell(i, 0).value == "DESCRIPTION":
        # if ws.cell(i,2).value == "Supplier SKU": #need to find way to adapt this to all PO's
        if type(ws.cell(i,2).value) == unicode and type(ws.cell(i,0).value) == unicode and type(ws.cell(i,1).value) == unicode: #Below line does not like non-unicode types
            if "SKU" in ws.cell(i,2).value or "Item Name" in ws.cell(i,2).value: #hard-coding
                startRow = i + 1
                useCol = 2
            elif "SKU" in ws.cell(i,1).value or "Style Name" in ws.cell(i,1).value:
                startRow = i + 1
                useCol = 1
            elif "Item Name" in ws.cell(i,0).value:
                startRow = i + 1
                useCol = 0

        if startRow != 0:
            if ws.cell(i, useCol).value == "":
                endRow = i - 1
                break
            elif i == ws.nrows-1:
                endRow = i

    #finding col range
    for j in range(0, ws.ncols):
        # print ws.ncols
        #print ws.cell(startRow - 1, j).value
        if ws.cell(startRow-1, j).value == "":
            endCol = j - 1
            break
        elif j == ws.ncols - 1:
            endCol = j

    wsRange = getCellRange(startCol, startRow, endCol, endRow, ws)
    headers = recordHeaders(startRow, endCol, ws) #list of headers

    return wsRange, headers

def readFiles(directory):
    i = 0
    wsList = []
    #importing all files in directory
    for root,dirs,files in os.walk(directory):
        for file in files:
            if file.endswith(".xlsx") or file.endswith(".xls"):
                # print file
                fin = xlrd.open_workbook(os.path.abspath(os.path.join(directory,file)))
                #grab first worksheet
                wsList.append(fin.sheet_by_index(0))
    return wsList

def refineRange(wsRange, headers):
    wsRangeNew = []
    for i, header in enumerate(headers):
        for j, title in enumerate(header):
            # print i, title
            if title.value == "Item Name":
                print wsRange[i][j]
              # wsRangeNew[i][0] = wsRange[i][j]
            elif "SKU" in title.value:
                print i, j


    return wsRange

def readStockWs(ws):
    startRow = 0
    startCol = 0
    endRow = 0
    #finding row range
    for i in range(0, ws.nrows):
        if  type(ws.cell(i,0).value) == unicode:
            if "Item No." in ws.cell(i,0).value and i < ws.nrows-2:
                if "Owner" in ws.cell(i+1,0).value:
                    startRow = i+2
                elif startRow == 0:
                    startRow = i+1
            elif "Total for Category" in ws.cell(i,0).value:
                endRow = i - 1
            elif "Items" in ws.cell(i,0).value and endRow == 0:
                endRow = i - 1
    #finding col range
    for j in range(0, ws.ncols):
        if ws.cell(startRow,j).value == "":
            endCol = j - 1
        elif j == ws.ncols - 1:
            endCol = j

    wsRange = getCellRange(startCol, startRow, endCol, endRow, ws)
    headers = recordHeaders(startRow, endCol, ws)
    return wsRange, headers






