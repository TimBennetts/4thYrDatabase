import os
import xlrd
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import datetime
import csv
import pandas as pd

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
            elif "SKU" in ws.cell(i,1).value or "Item Name" in ws.cell(i,1).value:
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
            if file.endswith(".xlsx") or file.endswith(".xls") :
                # print file
                fin = xlrd.open_workbook(os.path.abspath(os.path.join(directory,file)))
                #grab first worksheet
                wsList.append(fin.sheet_by_index(0))
    return wsList

def readStockWs(ws):
    startRow = 0
    startCol = 0
    endRow = 0
    #finding row range
    for i in range(0, ws.nrows):
        if type(ws.cell(i,0).value) == unicode:
            if "Item No." in ws.cell(i,0).value:
                startRow = i+1
            elif "" in ws.cell(i,0).value:
                endRow = i -1
    #finding col range
    for j in range(0, ws.ncols):
        if ws.cell(startRow,j).value == "":
            endCol = j - 1
        elif j == ws.ncols - 1:
            endCol = j

    wsRange = getCellRange(startCol, startRow, endCol, endRow, ws)
    headers = recordHeaders(startRow, endCol, ws)
    return wsRange, headers

def readSaleWs(ws):
    startRow = 1
    startCol = 0
    endRow = ws.nrows - 1
    endCol = ws.ncols - 1
    wsRange = getCellRange(startCol, startRow, endCol, endRow, ws)
    headers = recordHeaders(startRow, endCol, ws)
    return wsRange, headers


def dateTimeConv(xlDate):
    if type(xlDate) == unicode:
        if xlDate == "":
            #setting empty dates to start of datetime can then filter those out
            dt = datetime.datetime.utcfromtimestamp(0)
        else:
            #convert strings of type 25-04-1996 to datetime
            try:
                dt = datetime.datetime.strptime(xlDate, "%d/%m/%Y")
            except ValueError:
                try:
                    dt = datetime.datetime.strptime(xlDate, "%Y-%m-%d")
                except ValueError:
                    try:
                        dt = datetime.datetime.strptime(xlDate, "%m/%d/%y")
                    except ValueError:
                        try:
                            if "T" in xlDate:
                                xlDate = xlDate.replace("T", " ")
                                xlDate = xlDate.replace("Z", "")
                                xlDate = xlDate[0:10]
                                dt = datetime.datetime.strptime(xlDate, "%Y-%m-%d")

                        except ValueError as detail:
                            print detail
                            print xlDate

    elif type(xlDate) == float:
        dateTuple = xldate_as_tuple(xlDate, 0)
        dt = datetime.datetime(*dateTuple[0:6])
    else:
        print "else:"
        print xlDate
        print type(xlDate)
    return dt

def readWarehouse(inputDir):
    # Check input directory
    if inputDir == "":
        print "No input directory"
        return
    else:
        print inputDir

    #initialise
    fileList = [] # Should be
    numFiles = 0
    os.chdir(inputDir)
    # Import warehouse csvs
    for root, dirs, files in os.walk(inputDir):
        for file in files:
            invDoc = []
            # print files
            if file.endswith(".csv"):
                with open(file) as f:
                    readCSV = csv.reader(f, delimiter=',')
                    numFiles += 1
                    for row in readCSV:
                        invDoc.append(row)
            fileList.append(invDoc)
    # print fileList

    # get relevant data
    Qty = []
    Desc = []
    Unit = []
    Total = []
    fileDate = []
    Record = False
    for i in range(len(fileList)): # invoice
        for j in range(len(fileList[i])): # row
            # Find date
            if fileList[i][j][0].lower() == "work completed week ending":
                invoiceDate = fileList[i][j+1][0]
            # End recording
            if fileList[i][j][1] == "":
                Record = False
            # Record things
            if Record:
                # Find if Qty is empty or not
                if fileList[i][j][0] == "":
                    Qty.append(1)
                else:
                    Qty.append(int(fileList[i][j][0].replace('$',"").replace(',',"")))
                Desc.append((fileList[i][j][1]).lower())
                if fileList[i][j][4] == "":
                    Unit.append(float(fileList[i][j][7].replace('$',"").replace(',',"")))
                else:
                    Unit.append(float(fileList[i][j][4].replace('$',"").replace(',',"")))
                try:
                    Total.append(float(fileList[i][j][7].replace('$',"").replace(',',"")))
                except ValueError:
                    # print "The float conversion failed on: " + fileList[i][j][7] - All errors are caused by ""
                    Total.append(0)
                fileDate.append(datetime.datetime.strptime(invoiceDate, '%d-%m-%Y'))
                # print invoiceDate
            # Find starting point
            if fileList[i][j][0] == "QTY":
                Record = True

    warehouseDF = pd.DataFrame({
        "Quantity": Qty,
        "Description": Desc,
        "Unit": Unit,
        "Total": Total,
        "Date": fileDate
    })

    # Sum unique descriptions
    sumTotals = []
    for i in warehouseDF.Description.str.lower().unique():
        sumTotals.append(sum(warehouseDF.Total[warehouseDF.Description.str.lower() == i]))

    sumDF = pd.DataFrame({
        "SumTotals": sumTotals,
        "Description": warehouseDF.Description.str.lower().unique()
    })

    sumDF.sort_values('SumTotals', inplace=True)

    warehouseDF = warehouseDF[warehouseDF.Description.isin((sumDF.Description[sumDF.SumTotals > 0.01 * sum(sumDF.SumTotals)]).as_matrix()) == True]
    warehouseDF = warehouseDF.reset_index(drop=True)

    return warehouseDF


if __name__ == '__main__':
    filePath = "CAM MIKE DATA\Costings\Warehouse"
    warehouseDir = os.path.abspath(os.path.join(filePath))
    warehouseDF = readWarehouse(warehouseDir)






