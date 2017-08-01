# setwd('D:\\Documents\\uoa\\EngSci\\4th Year Projs\\2017\\TimB')
setwd('C:\\Users\\admin\\Desktop\\Files\\Uni\\4thYear\\Project\\4thYrDatabase-master\\salesData')
rawdata = read.csv('RawSalesData.csv', header=T)
#rawdata = rawdata[rawdata$salesQ >= 10,]

# Import new data
invData = read.csv('B2CData.csv', header = T)
bulkData = read.csv('B2BData.csv', header = T)

library(fitdistrplus)

# order and take the unique sale dates
salesDates = unique(rawdata$Date[order(rawdata$Date)])

# join together matrices, sales gaps 
salesGaps = cbind(salesDates[-1], data.frame(diff(as.matrix(as.Date(salesDates, format="%Y-%m-%d")))))
colnames(salesGaps) = c("Date", "Gap")

salesQuantities = aggregate(rawdata$salesQ, by=list(Category=rawdata$Date), FUN=sum)
colnames(salesQuantities) = c("Date", "Quantity")

# Create data frame w dates, qty and gap
procdata = merge(x = salesGaps, y = salesQuantities, by = "Date", all.y = TRUE)

# Count the number of days
salesCount = data.frame(table(rawdata$Date))
colnames(salesCount) = c("Date", "Count")

# Add sales count
procdata = merge(x = procdata, y = salesCount, by = "Date", all.y = TRUE)

#procdata = procdata[procdata$Quantity > 3, ]
#procdata = procdata[procdata$Quantity <= 3, ]

# Individual raw data
indrawdata = rawdata[rawdata$salesQ == 1,]
inddata = procdata[procdata$Quantity == procdata$Count, ]

# Bulk raw data
bulkrawdata = rawdata[rawdata$salesQ > 1,]
bulkdata = procdata[procdata$Quantity != procdata$Count, ]

#par(mfrow = c(2, 2))
#hist(rawdata$salesQ, breaks=168)
#hist(procdata$Gap, breaks=150)
#hist(procdata$Quantity, breaks=1500)
#hist(procdata$Count, breaks=60)

# Create multi-pannel plot
par(mfrow = c(2, 4))
hist(indrawdata$salesQ)
hist(inddata$Gap)
hist(inddata$Quantity)
hist(inddata$Count)
hist(bulkrawdata$salesQ)
hist(bulkdata$Gap)
hist(bulkdata$Quantity)
hist(bulkdata$Count)

# reformat dates
procdata$Date = as.Date(procdata$Date, format = "%Y-%m-%d")

oldest = min(procdata$Date)

#convert dates into number of days since first order
cordata = procdata[,]
cordata[,1] = as.numeric(difftime(cordata[,1], oldest, units = c("days")))

cor(cordata[-1,])

dev.new()

# Below is from https://cran.r-project.org/web/packages/fitdistrplus/vignettes/paper2JSS.pdf
library(MASS)
library(survival)
library(fitdistrplus)

#col = bulkrawdata$salesQ
#disc = T
#sizeest = 200
##Fitting of the distribution ' lnorm ' by maximum likelihood 
##Parameters:
##         estimate Std. Error
##meanlog 2.1823809 0.02778910
##sdlog   0.9111265 0.01964975
##round(rlnorm(20, meanlog=2.1823809, sdlog=0.9111265))

#col = bulkdata$Quantity
#disc = T
#sizeest = 2000
##Fitting of the distribution ' lnorm ' by maximum likelihood 
##Parameters:
##         estimate Std. Error
##meanlog 6.0233308 0.10477309
##sdlog   0.5738658 0.07408475
##round(rlnorm(20, meanlog=6.0233308, sdlog=0.5738658))

#col = bulkdata$Gap[-1]
#disc = T
#sizeest = 200
##Fitting of the distribution ' weibull ' by maximum likelihood 
##Parameters:
##       estimate Std. Error
##shape  1.122629  0.1572999
##scale 32.951921  5.7403120
##ceiling(rweibull(20, shape=1.122629, scale=32.951921))

#col = bulkdata$Count
#disc = T
#sizeest = 80
##Fitting of the distribution ' weibull ' by maximum likelihood 
##Parameters:
##       estimate Std. Error
##shape  4.535298  0.6881055
##scale 41.684586  1.7382180
##ceiling(rweibull(20, shape=4.535298, scale=41.684586))

#col = inddata$Gap
#disc = T
#sizeest = 15
##Fitting of the distribution ' pois ' by maximum likelihood 
##Parameters:
##       estimate Std. Error
##lambda 3.333333  0.4714045
#rpois(20, lambda=3.333333)


# Distribution for individual orders time

col = invData$TimeBetweenOrders[-1]
disc = T
# Unsure what this does
sizeest = 10000

# Fitting the column to known distributions
fe = fitdist(col, "exp")
fw = fitdist(col, "weibull")
fg = fitdist(col, "gamma")
fn = fitdist(col, "norm")
fln = fitdist(col, "lnorm")

#
if (disc) {
fb = fitdist(col, "binom",
fix.arg=list(size=sizeest), start=list(prob=0.5))
fnb = fitdist(col, "nbinom")
fgm = fitdist(col, "geom")
fp = fitdist(col, "pois", discrete=T)
}
par(mfrow = c(2, 2))
dlist = list(
fe,
fw,
fn,
fln,
fg 
)
dleg = c(
"exponential",
"Weibull",
"normal",
"lognormal",
"gamma"
)
if (disc) {
ddlist = list(
fe,
fw,
fln,
fg,
fb,
fnb,
fgm,
fp
)
ddleg = c(
"exponential",
"Weibull",
"lognormal",
"gamma",
"binomial",
"neg. binom.",
"geometrical",
"Poisson"
)
}
denscomp(dlist, legendtext = dleg, cex=0.5)
if (disc) {
  qqcomp(ddlist, legendtext = ddleg, cex=0.5)
} else {
  qqcomp(dlist, legendtext = dleg)
}
if (disc) {
  cdfcomp(ddlist, discrete=T, legendtext = ddleg, cex=0.5)
} else {
  cdfcomp(dlist, discrete=T, legendtext = dleg)
}
if (disc) {
  ppcomp(ddlist, legendtext = ddleg, cex=0.5)
} else {
  ppcomp(dlist, legendtext = dleg)
}
if (disc) {
  gofstat(ddlist)
} else {
  gofstat(dlist)
}

dev.new()
if (disc) {
  cdfcomp(ddlist, discrete=T, legendtext = ddleg, cex=0.8)
} else {
  cdfcomp(dlist, discrete=T, legendtext = dleg)
}

n = 10
# Gap
gaps = ceiling(rweibull(n, shape=1.122629, scale=32.951921))
days = cumsum(gaps)
# Count
counts = ceiling(rweibull(n, shape=4.535298, scale=41.684586))

boot = data.frame(c())
for (i in 1:length(days)) {
  day   = days[i]
  count = counts[i]
  for (c in 1:count) {
    sales = round(rlnorm(1, meanlog=2.1823809, sdlog=0.9111265))
    boot = rbind(boot, c(day, sales))
  }
}
colnames(boot) = c("Day", "salesQ")

