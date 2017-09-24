import numpy as np
import pandas as pd
import csv
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def pareto_frontier(Xs, Ys, maxX = True, maxY = True): # http://oco-carbon.com/metrics/find-pareto-frontiers-in-python/
# Sort the list in either ascending or descending order of X
    myList = sorted([[Xs[i], Ys[i]] for i in range(len(Xs))], reverse=maxX)
    # Start the Pareto frontier with the first value in the sorted list
    p_front = [myList[0]]
    # Loop through the sorted list
    for pair in myList[1:]:
        if maxY:
            if pair[1] >= p_front[-1][1]:
                p_front.append(pair)
        else:
            if pair[1] <= p_front[-1][1]:
                p_front.append(pair)
    # Turn resulting pairs back into a list of Xs and Ys
    p_frontX = [pair[0] for pair in p_front]
    p_frontY = [pair[1] for pair in p_front]
    return p_frontX, p_frontY



def makePlot(xAxis, yAxis, titleStr, xLabel, yLabel, plotType):
    # Create dataframe
    plotDF = pd.DataFrame({"xAxis": xAxis, "yAxis": yAxis})
    plotDF.sort_values(by="xAxis", inplace=True)
    if plotType.lower() == "scatter":
        plt.scatter(xAxis,yAxis, s=0.5)
    else:
        plt.plot(xAxis, yAxis)
    plt.title(titleStr)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)


def aggregateResults():
    maxQstar = max(resultsDF.Qstar)
    minQstar = min(resultsDF.Qstar)
    maxReorder = max(resultsDF.reorderPoint)
    minReorder = min(resultsDF.reorderPoint)
    reorderRange = range(minReorder, maxReorder+(maxReorder-minReorder)/(len(resultsDF.reorderPoint.unique())-1), (maxReorder-minReorder)/(len(resultsDF.reorderPoint.unique())-1))
    QstarRange = range(minQstar, maxQstar+(maxQstar-minQstar)/(len(resultsDF.Qstar.unique())-1), (maxQstar-minQstar)/(len(resultsDF.Qstar.unique())-1)) #Range of Qstar (1500-3950)

    #Initialise list averages
    avgCost = []
    avgMsdSales = []
    avgMsdDays =[]
    smlstMsdSale = []
    lrgstMsdSale = []
    QstarAgr = []
    reorderAgr = []

    for i in range(0, len(resultsDF.reorderPoint.unique())*len(resultsDF.Qstar.unique())):
        avgCost.append(np.mean(resultsDF.Cost[i*100:100+i*100]))
        avgMsdSales.append(np.mean(resultsDF.missedSales[i*100:100+i*100]))
        avgMsdDays.append(np.mean(resultsDF.missedDays[i*100:100+i*100]))
        smlstMsdSale.append(min(resultsDF.smallestMissedSale[i*100:100+i*100]))
        lrgstMsdSale.append(max(resultsDF.Cost[i*100:100+i*100]))
        QstarAgr.append(resultsDF.Qstar[i*100])
        reorderAgr.append(resultsDF.reorderPoint[i*100])

    myArray = [avgMsdSales, avgCost]


    makePlot(avgCost, avgMsdSales, "Cost vs missed sales", "Total cost", "Missed sales", "scatter")
    p_front = pareto_frontier(avgCost, avgMsdSales, maxX=False, maxY=False)
    # Then plot the Pareto frontier on top
    plt.plot(p_front[0], p_front[1], c='r')
    # plt.show()
    plt.clf()

    paretoDF = pd.DataFrame({"avgCost":p_front[0], "msdSales": p_front[1]})
    paretoDF.to_csv("paretoFrontier.csv", index=False)


    #Create aggregate dataframe
    agrDF = pd.DataFrame({
                        "avgCost": avgCost,
                        "avgMsdSales": avgMsdSales,
                        "avgMsdDays":   avgMsdDays,
                        "smallMsdSale": smlstMsdSale,
                        "largeMsdSales": lrgstMsdSale,
                        "Qstar": QstarAgr,
                        "reorderPoint": reorderAgr
    })

    makePlot(agrDF.Qstar[agrDF.avgMsdSales==0], agrDF.reorderPoint[agrDF.avgMsdSales==0], "Order policies with no missed sales", "Order quantity", "Reorder point", "scatter")
    # plt.show()
    plt.clf()

    allQstarCost = []
    allQstarMsdSales = []
    for i in resultsDF.Qstar.unique():
        allQstarCost.append(np.mean(resultsDF.Cost[resultsDF.Qstar==i]))
        allQstarMsdSales.append(np.mean(resultsDF.missedSales[resultsDF.Qstar==i]))

    makePlot(QstarRange, allQstarCost, "Average yearly cost for all reorder points at a single order quantity", "Order quantity", "Average cost of all simulations", "scatter")
    # makePlot(allQstarMsdSales, QstarRange, "Average missed sales for all reorder points at a single order quantity", "Average missed sales of all simulations", "Order quantity", "scatter")
    # plt.clf()
    plt.show()

    allReorderCost = []
    allReorderMsdSales = []
    avgReorderMsdSales = []
    for i in resultsDF.reorderPoint.unique():
        allReorderCost.append(np.mean(resultsDF.Cost[resultsDF.reorderPoint==i]))
        allReorderMsdSales.append(sum(resultsDF.missedSales[resultsDF.reorderPoint==i]))
        avgReorderMsdSales.append(np.mean(resultsDF.missedSales[resultsDF.reorderPoint==i]))

    makePlot(reorderRange, allReorderCost, "Average yearly cost for all order quantities at a single reorder point", "Reorder point", "Average cost of all simulations", "scatter")
    # plt.legend(["Q* range", "Reorder range"])
    # makePlot(allReorderMsdSales, reorderRange, "Total missed sales for all order quantities at a single reorder point", "Total missed sales over all simulations", "Reorder point", "scatter")
    # plt.clf()
    plt.show()

    reorderCostM = (reorderRange[30]-reorderRange[10])/(allReorderCost[30]-allReorderCost[10]) # rise/run
    QstarCostM = (QstarRange[30]-QstarRange[10])/(allQstarCost[30]-allQstarCost[10]) # rise/run
    reorderCostC = reorderRange[10] -reorderCostM*allReorderCost[10]
    QstarCostC = QstarRange[10] -QstarCostM*allQstarCost[10]

    # print "Reorder point = " +str(reorderCostM) + " * avg cost + " + str(reorderCostC)
    # print "avg cost = (Q* x " +  str(QstarCostC) + ")/" + str(QstarCostM)

    # make 3D plot
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.scatter(agrDF.Qstar[agrDF.avgMsdSales == 0], agrDF.reorderPoint[agrDF.avgMsdSales == 0], agrDF.avgCost[agrDF.avgMsdSales == 0])
    ax.set_xlabel("Order quantity")
    ax.set_ylabel("Reorder point")
    ax.set_zlabel("Cost")
    ax.set_title("Cost vs order policy with no missed sales")
    # plt.show()
    plt.clf()


    # print "Optimal order quantity for no missed sales = " + str(agrDF.Qstar[min(agrDF.avgCost[agrDF.avgMsdSales==0])==agrDF.avgCost])
    # print "Optimal reorder point for no missed sales = " + str(agrDF.reorderPoint[min(agrDF.avgCost[agrDF.avgMsdSales==0])==agrDF.avgCost])
    # print "For an average cost of: " + str(min(agrDF.avgCost[agrDF.avgMsdSales==0]))






if __name__ == '__main__':
    startRunTime = time.time()

    resultsDF = pd.read_csv("SimulationResultsLarge.csv")

    aggregateResults()

    print("--- %s seconds ---" % (time.time() - startRunTime))