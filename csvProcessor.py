# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 11:51:19 2017

@author: dexter
"""
import datetime
import csv 
import re 
from tabulate import tabulate   

class Trade:
    def __init__(self,row):
        #defaults for testing purposes df
        self.dateTime = datetime.datetime.now() 
        self.quanity = 1.0 
        self.isBuy = False 
        self.tradeType = "Equity"
        self.price = 100.0
        self.commision = 10.0
        self.regFee = 10.0 
        self.netAmount = 80.0 #note that during initiation make sells automatically negative for quanity
        self.avgATR = 10.0
        self.symbol = "" 
        self.grossAmmount = 0 
        
        self.pRow(row)
    def getNumber(self,numStr):
        p = re.compile("[\d.]*")
        par = re.compile("\(")
        mult = 1
        if par.match(numStr):
            mult = -1 #checks to see if number is negative 
    
        for numStr in p.findall(numStr):
            if not numStr == "":
                return float(numStr)*mult   
        
    def pRow(self,row): #process a row of data 
    #data format 
    #[    0                    1         2                          3       4        5         6              7        8          9 ]
    #['Trade Date',          'Type', 'Market Symbol',          'Buy/Sell', 'QTY', 'Price', 'Gross Amount', 'Comm', 'Reg Fee', 'Net Amount']
    #['08/24/2017 1110ET', 'Option', 'SPXW  20170825P 2415.000', 'S',        '8', '$0.50 ', '$400.00 ', '($1.20)', '($0.33)', '$398.47 ']
        #process date 
        tmpStr = row[0]
        tmpStr = tmpStr.split("E")[0] #removes ET part of the string 
        #this checks for the occationally odd 09/29/2017 ET format is checked for by seeing if we can find " ET" 
        etCheck = re.compile("[\sET]*")
        #if(etCheck.match(row[0])):#checks for this odd format 
        #    tmpStr = tmpStr.split(" ")[0]
        #    self.datetime = datetime.datetime.strptime(tmpStr,"%m/%d/%Y")
        #else: 
        self.dateTime = datetime.datetime.strptime(tmpStr,"%m/%d/%Y %H%M") #TO DO, SET TO EASTERN TIMEZONE 
        #process option type
        self.tradeType = row[1]
        #process market symbol
        #tmpStrArray = row[2].split(" ")
        self.symbol = row[2]
        #if option tmpStrArray[1] and [2] have values DO LATER

        #process QTY 
        #turns it into a number
        self.quanity = float(row[4].replace(",", ""))
        if(row[3]=="S"): #if it is being sold short make quanity negative
            self.quanity = self.quanity*(-1.0)
        if(self.tradeType=="Option"): #the option quantities are in groups of 100 which is confusing 
            self.quanity*=100 
        self.price = self.getNumber(row[5]) 
        self.grossAmmount = self.getNumber(row[6]) 
        self.commision = self.getNumber(row[7])
        self.regFee = self.getNumber(row[8]) 
        self.netAmount = self.getNumber(row[9])
            
class FullTrade: 
    def __init__(self):
        self.symbol = ""
        self.tradeType = ""
        self.longOrShort = "long" 
        self.grossProfit = 0.0 
        self.netProfit = 0.0
        self.netQuanity = 0.0
        self.duration = datetime.timedelta(hours=1)
        self.netComission = 0.0
        self.listOfTrades = []
        self.startDate = datetime.datetime.min
        self.endDate = datetime.datetime.max  
        self.tradeNumber = 0
    def updateAtributes(self):
        self.symbol = "" 
        self.tradeType = "" 
        self.longOrShort = "" 
        self.grossProfit = 0.0
        self.netProfit = 0.0
        self.netQuanity = 0.0
        self.duration = datetime.timedelta(hours=1)
        self.netComission = 0.0
        self.startDate = datetime.datetime.max
        self.endDate = datetime.datetime.min
        self.tradeNumber = len(self.listOfTrades)
        if(self.tradeNumber>0):
            if(self.listOfTrades[0].quanity>0):
                self.longOrShort = "long"
            else:
                self.longOrShort = "short"
        #declare variables 
        for trades in self.listOfTrades:
            self.symbol = trades.symbol
            self.tradeType = trades.tradeType
            self.grossProfit += trades.grossAmmount 
            self.netProfit += trades.netAmount #trades.price*trades.quanity + trades.commision+trades.regFee
            self.netQuanity += trades.quanity 
            self.netComission += trades.commision
            if(self.startDate>trades.dateTime): #if tmpStartDate is greater than the trade datetime
                self.startDate = trades.dateTime 
            if(self.endDate<trades.dateTime):
                self.endDate = trades.dateTime
        self.duration = self.endDate - self.startDate 
    def addTrade(self,trade):
        self.listOfTrades.append(trade)
        self.updateAtributes()
    def getList(self):
        return [self.symbol, self.tradeType, self.longOrShort, self.grossProfit, self.netProfit, self.netQuanity, self.duration, self.netComission, self.startDate, self.endDate,self.tradeNumber]
    def getListNames(self):
        return ["symbol","trade type","long/short", "gross Profit", "netProfit","netQuanity","duration","netComission","start date","end date","trade number"]


class PerformanceSummary:
    def __init__(self,cTrades,inTrades):
        self.cTrades = cTrades 
    def printStats(self):
        #profit loss variables 
        gProfitLong = 0
        gProfitShort = 0 
        gLossLong = 0 
        gLossShort = 0 
        #counting variables 
        iProfitLong = 0
        iProfitShort = 0
        iLossLong = 0 
        iLossShort = 0 
        for l in [cTrades]:
            for key in l:
                t = l[key]
                if(t.longOrShort == "long"): #if long 
                    if(t.netProfit>0): #if Long 
                        gProfitLong += t.netProfit 
                        iProfitLong += 1
                    else:
                        gLossLong += t.netProfit
                        iLossLong += 1 
                else:
                    if(t.netProfit>0):
                        gProfitShort += t.netProfit
                        iProfitShort += 1 
                    else:
                        gLossShort += t.netProfit
                        iLossShort += 1 
        #profit calculations            
        netProfitLong = gProfitLong+gLossLong
        netProfitShort = gProfitShort+gLossShort
        netProfitTotal = netProfitLong+netProfitShort 
        gProfitTotal = gProfitShort +gProfitLong
        gLossTotal = gLossShort + gLossLong

        pfTotal = gProfitTotal/(abs(gLossTotal)+0.0)
        pfLong = gProfitLong/(abs(gLossLong)+0.0)
        pfShort = gProfitShort/(abs(gLossShort)+0.0)
        
        print tabulate([['Total Net Profit',netProfitTotal,netProfitLong,netProfitShort],
                        ['Gross Profit',gProfitTotal,gProfitLong,gProfitShort],
                        ['Gross Loss',gLossTotal,gLossLong,gLossShort],
                        ['Profit Factor',pfTotal,pfLong,pfShort]],
                        headers=['','All Trades','Long Trades','Short Trades'],tablefmt='pipe')
        print "\n"
        #counting calculations 
        iProfitTotal = iProfitLong+iProfitShort
        iLossTotal = iLossLong+iLossShort 
        
        iTotalLong = iProfitLong + iLossLong
        iTotalShort = iProfitShort+iLossShort 
        iTotalTotal = iTotalLong+iTotalShort
        
        ppLong = iProfitLong/(0.0+iTotalLong)*100 #percent profitable long 
        ppShort = iProfitShort/(0.0+iTotalShort)*100 #percent profitable short 
        ppTotal = iProfitTotal/(0.0+iTotalTotal)*100
        print tabulate([['Total Number of Trades',iTotalTotal,iTotalLong,iTotalShort],
                        ['Percent Profitable (%)',ppTotal,ppLong,ppShort],
                        ['Winning Trades',iProfitTotal,iProfitLong,iProfitShort],
                        ['Lossing Trades',iLossTotal,iLossLong,iLossShort]],
                        headers=['','All Trades','Long Trades','Short Trades'],tablefmt='pipe')
        
        
        
        
#main function 
#csvFileName = "ExecutionDetail.csv"  #69 accoutn 
csvFileName = "trades93.csv"
j = 0 
inTrades = {} #incomplete trades
cTrades = {} #complete trades 

csvFileLength = sum(1 for line in open(csvFileName)) #skips last line 

with open(csvFileName,'rb') as f: 
    reader = csv.reader(f)
    for row in reader: 
        j += 1 
        if(j>2 and j<csvFileLength): #need to find way to skip last line b/c that breaks things hence the 748
            newTrade = Trade(row)             
            if(newTrade.symbol in inTrades):
                tmpFullTrade = inTrades[newTrade.symbol]
                tmpFullTrade.addTrade(newTrade)
                tmpFullTrade.updateAtributes()
            else:
                tmpFullTrade = FullTrade()
                tmpFullTrade.addTrade(newTrade)
                inTrades[newTrade.symbol] = tmpFullTrade
                tmpFullTrade.updateAtributes()
            if(tmpFullTrade.netQuanity==0):
                del inTrades[newTrade.symbol]
                cTrades[newTrade.symbol] = tmpFullTrade 

#performance summary calculator 
pSum = PerformanceSummary(cTrades,inTrades)
pSum.printStats()


#saves all complete and incomplete trades to csv file 
with open('output.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, lineterminator = '\n')
    writer.writerow(FullTrade().getListNames())
    for key in cTrades:
        t  = cTrades[key]
        writer.writerow(t.getList())
    for key in inTrades:
        t = inTrades[key]
        writer.writerow(t.getList())