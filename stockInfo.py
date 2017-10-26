#!/usr/bin/python
# -*- coding: utf-8 -*-
#author:蔡董
#date:2017.8.16

import  os
import  sys
import  urllib
import  re
import simplejson
import  time
from datetime import datetime
import os.path as fpath
from bs4 import BeautifulSoup
from mysqlOperation import mysqlOp
from constant import stockDetailTableList,stocklistName

reload(sys)
sys.setdefaultencoding('utf8')


#数据库，股票code为主键，保存，股票开盘价格，闭市价格，最高，最低，涨幅，所属于的概念，助理流入资金，需要3天的这种数据
#行业涨跌情况最近5天的数据
#股票和行业对应起来

#东方财富网-今日最高
todayMaxPriceUrl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[hqzb03]&p=1&jn=moJuuzHq&ps=100&s=hqzb03&st=-1&r=1503071461051'
#3日新高
threeDaysMaxPriceUrl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[hqzb05(1|3)]&p=1&jn=EYOfLXHJ&ps=40&s=hqzb05(1|3)&st=-1&r=1507347185807'

#5日新高
fiveDaysMaxPriceUrl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[hqzb05(1|5)]&p=1&jn=JODmOFXH&ps=40&s=hqzb05(1|5)&st=-1&r=1507347434465'

#连续涨3天以上
# moreAndMoreMaxPriceUrl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[hqzb07(4|3)]&p=1&jn=xiZaGiTW&ps=300&s=hqzb07(4|3)&st=-1'

#行业研报
hangyeReportUrl = 'http://datainterface.eastmoney.com//EM_DataCenter/js.aspx?type=SR&sty=HYSR&mkt=0&stat=0&cmd=4&code=&sc=&ps=100&p=1&js=var%20WPaQnqfN={%22data%22:[(x)],%22pages%22:%22(pc)%22,%22update%22:%22(ud)%22,%22count%22:%22(count)%22}&rt=50102402'

#资金流入排行
#zjlrRank = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx/JS.aspx?type=ct&st=(BalFlowMain)&sr=-1&p=%d&ps=100&js=var%20ZGdnEqhJ={pages:(pc),date:%222014-10-22%22,data:[(x)]}&token=894050c76af8597a853f5b408b759f5d&cmd=C._AB&sty=DCFFITA&rt=50102411'
zjlrPrefix = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx/JS.aspx?type=ct&st=(BalFlowMain)&sr=-1&p='
zjlrSuffix = '&ps=100&js=var%20ZGdnEqhJ={pages:(pc),date:%222014-10-22%22,data:[(x)]}&token=894050c76af8597a853f5b408b759f5d&cmd=C._AB&sty=DCFFITA&rt=50102411'

#东方财富网-公司被调研次数
dytjBaseUrl = 'http://data.eastmoney.com/DataCenter_V3/jgdy/gsjsdy.ashx?pagesize=100&page=1&js=var%20MavaIUBM&param=&sortRule=-1&sortType=2'

#东方财富网-券商推荐公司
tjgsBaseUrl = 'http://datainterface.eastmoney.com//EM_DataCenter/js.aspx?type=SR&sty=GGSR&js=var%20jXudgyZA={%22data%22:[(x)],%22pages%22:%22(pc)%22,%22update%22:%22(ud)%22,%22count%22:%22(count)%22}&ps=100&p=1&mkt=0&stat=0&cmd=2&code='

#公司推荐次数排行
reommendRankUrl = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._A&sty=GEMCPF&st=(AllNum)&sr=-1&p=1&ps=100&cb=&js=var%20vCvDXueG={%22data%22:[(x)],%22pages%22:%22(pc)%22}&token=3a965a43f705cf1d9ad7e1a3e429d622&rt=50248407'

#东方财富网-股东增持
gdzcBaseUrl = 'http://data.eastmoney.com/DataCenter_V3/gdzjc.ashx?pagesize=100&page=1&js=var%20ukjJZiRW&param=&sortRule=-1&sortType=BDJZ&tabid=jzc&code=&name=&rt=50102353'

#概念涨幅排行
gnzfBaseUrl = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?cmd=C._BKGN&type=ct&st=(ChangePercent)&sr=-1&p=1&ps=100&js=var%20vXdHFFJl={pages:(pc),data:[(x)]}&token=894050c76af8597a853f5b408b759f5d&sty=DCFFITABK&rt=50102372'


#5日资金流入
hyzf = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?cmd=C._BKHY&type=ct&st=(BalFlowMainNet5)&sr=-1&p=1&ps=100&js=var%20yJcNkasY={pages:(pc),data:[(x)]}&token=894050c76af8597a853f5b408b759f5d&sty=DCFFITABK5&rt=50142870'

#沪深A股价格相关数据
xxsjPrefixUrl = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._A&sty=FCOIATA&sortType=C&sortRule=-1&page='
xxsjSuffix = '&pageSize=100&js=var%20quote_123%3d{rank:[(x)],pages:(pc)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.681840105810047'

#沪深A股市盈率、市净率、市值相关数据
sylDetailPrefixUrl = 'http://nuff.eastmoney.com/EM_Finance2015TradeInterface/JS.ashx?id='
sylDetailSuffixUrl = '&token=4f1862fc3b5e77c150a2b985b12db0fd&cb=jQuery183041202991002070233_1505234287664&_=1505234288231'

#涨幅空间排行
mbzfRank = 'http://q.stock.sohu.com/jlp/rank/priceExpect.up'

#净资产收益率12%  3年利润增长率10% 100亿市值以上
#mostValueableStockUrl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[cz_ylnl01(1|0.12)][cz_cznl06(1|0.1)][cz20(1|100y)]&p=1&jn=pUnYlfVk&ps=100&s=cz20(1|100y)&st=-1&r=1507352123438'
#净资产收益率12%  3年利润增长率10%，利润同比增长率
#mostValueableStockUrl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[cz_ylnl01(1|0.12)][cz_cznl06(1|0.1)][cz_jgcg01][cznl05(4|0.1)][cz19(1|100y)]&p=1&jn=DvMQgnCP&ps=100&r=1507563206241'
#3年净利润增长率10以上，资产收益率大于8%，市值超过210亿
mostValueableStockUrl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[cznl06(1|0.1)][cz_jgcg01][cz_ylnl01(4|0.08,5|1.00)][cz19(4|2400000w)]&p=%s&jn=qVlwdjPQ&ps=100&s=cz_jgcg01&st=-1&r=1507621522335'


#ROE 投资回报率
ROEOfStockUrl = 'http://data.eastmoney.com/DataCenter_V3/stockdata/cwzy.ashx?code=%s'
#code = sh601318
ROEOfStockUrl2 = 'http://emweb.securities.eastmoney.com/PC_HSF10/FinanceAnalysis/FinanceAnalysisAjax?code=%s&ctype=2'
#公司经营业务  sz000001
bussinessDetailUrl = 'http://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/CoreConceptionAjax?code=%s'

#近4个月k线走势
last4MonthKLineUrl = 'http://pifm.eastmoney.com/EM_Finance2014PictureInterface/Index.aspx?ID=%s&UnitWidth=-5&imageType=KXL&EF=&Formula=RSI&AT=1&&type=&token=44c9d251add88e27b65ed86506f6e5da&_=0.7768000600639573'

#近4年k线走势
last4YearKLineUrl = 'http://pifm.eastmoney.com/EM_Finance2014PictureInterface/Index.aspx?ID=%s&UnitWidth=-6&imageType=KXL&EF=&Formula=RSI&AT=1&&type=M&token=44c9d251add88e27b65ed86506f6e5da&_=0.4133575449252702'

#公司市值下限
companySzDownLimit = 50
companyHslDownLimit = 1.0
pageSize  = 100

def getHtmlFromUrl(url,utf8coding=False):
    try:
        ret = urllib.urlopen(url)
        res = None
        if utf8coding:
            res = ret.read().decode('gbk', 'ignore').encode('utf-8')
        else:
            res = ret.read()
    except  Exception:
            print 'exception  occur'
    finally:
        return res

def hasHTML(obj):
    return obj.startswith('<!DOCTYPE HTML PUBLIC')


def getJsonObj(obj):
    if not obj:return None
    if hasHTML(obj):return None
    #"var moJuuzHq="{"Results":["2,300672,国科微,是","2,300676,华大基因,是","1,603612,索通发展,是","1,603707,健友股份,是","2,002888,惠威科技,是","2,300678,中科信息,是","2,002889,东方嘉盛,是","1,603860,中公高科,是","2,300685,艾德生物,是","2,300687,赛意信息,是","1,603880,南卫股份,是","2,300689,澄天伟业,是","1,603602,纵横通信,是","2,300688,创业黑马,是","1,603721,中广天择,是","2,300691,联合光电,是","1,601326,秦港股份,是","1,603776,永安行,是","2,002892,科力尔,是","1,603129,春风动力,是","1,603557,起步股份,是"],"AllCount":"21","PageCount":"1","AtPage":"1","PageSize":"40","ErrMsg":"","UpdateTime":"2017/8/19 13:37:03","TimeOut":"3ms"}"
    # newobj = obj.split('=')[1]  #//必须要将前面的= 去掉
    # return  simplejson.loads(newobj)
    newobj = "{" + obj.split('={')[1]
    return simplejson.loads(newobj)


def getJsonObjOrigin(obj):
    if not obj:return None
    if hasHTML(obj): return None
    o = None

    try:
        o = simplejson.loads(obj)
    except Exception:
        print  Exception.__name__,Exception
    return o

def getJsonList(obj):
    '''解析列表,[ 开头'''
    if obj and obj.startswith('['):
        return simplejson.loads(obj)
    else:
        return None

def getJsonObj2(obj):
    if not obj: return None
    if hasHTML(obj): return None
    partern = re.compile("data:.*?\"]")
    list = re.findall(partern, obj)
    if list and len(list) > 0:
        s = list[0]
        sepString = s.split(':')[1]
        return simplejson.loads(sepString)
    else:
        return None

def getJsonObj3(obj):
    if not obj: return None
    if hasHTML(obj): return None
    partern = re.compile("data:.*?\"]")
    list = re.findall(partern, obj)
    if list and len(list) > 0:
        s = list[0]
        sepString = s.split(':[')[1]
        return simplejson.loads('[' + sepString)
    else:
        return None
def getJsonObj4(obj):
    if not obj: return None
    if hasHTML(obj): return None
    partern = re.compile("rank:.*?\"]")
    list = re.findall(partern, obj)
    if list and len(list) > 0:
        s = list[0]
        sepString = s.split(':[')[1]
        return simplejson.loads('[' + sepString)
    else:
        return None

def getJsonObj5(obj):
    if not obj: return None
    if hasHTML(obj): return None
    partern = re.compile("\"Value\":.*?\"]")
    list = re.findall(partern, obj)
    if list and len(list) > 0:
        s = list[0]
        sepString = s.split(':[')[1]
        return simplejson.loads('[' + sepString)
    else:
        return None

def getMarketId(code):
    subCode = code[0:3]
    if subCode == '009' or subCode == '126' or subCode == '110':
        return '1'
    else:
        fCode = subCode[0:1]
        if fCode =='5' or fCode == '6' or fCode == '9':
            return '1'
        else:
            return '2'

def getMarketCode(code,prefix = False):
    ret = getMarketId(code)
    if prefix:
        if ret == '1':
            return  'sh' + code
        else:
            return  'sz' + code
    else:
        if ret == '1':
            return  code + '.SH'
        else:
            return  code + '.SZ'


class CompanyInfo(object):
    def __init__(self,code,name):
        super(CompanyInfo,self).__init__()
        self.code = code
        self.name = name

class CompanyResearchReport(CompanyInfo):
    def __init__(self,code,name ,startTime = None,desc = None,sum = None):
        super(CompanyResearchReport,self).__init__(code,name)
        self.time = startTime
        self.desc  = desc
        self.sum = sum

class CompanyRecommandInfo(CompanyInfo):
    def __init__(self,code,name,time = None,zqgs = None,reason = None,advice = None):
        super(CompanyRecommandInfo,self).__init__(code,name)
        self.time = time
        self.org = zqgs
        self.reason = reason
        self.advice = advice

class CompanyRecommandRankInfo(CompanyInfo):
    def __init__(self,code,name,count,buyCount,addCount):
        super(CompanyRecommandRankInfo,self).__init__(code,name)
        self.count = count
        self.buyCount = buyCount
        self.addCount = addCount

class StockEachDayInfo(CompanyInfo):
    '''每一天的数据行情'''
    def __init__(self,code,name,startPrice,endPrice,maxPrice,minPrice,inflowCount,concept):
        super(StockEachDayInfo,self).__init__(code,name)
        self.startPrice = startPrice
        self.endPrice = endPrice
        self.maxPrice = maxPrice
        self.minPrice = minPrice
        self.inflowCount = inflowCount
        self.concept = concept

class CompanyValueInfo(CompanyInfo):
    def __init__(self,code,name,syl,sjl,sz,hsl):
        '''代码，名字，市盈率，市净率，市值、换手率'''
        super(CompanyValueInfo,self).__init__(code,name)
        self.syl = syl
        self.sjl = sjl
        self.sz = sz
        self.hsl = hsl

class StockLatestInfo(CompanyInfo):
    '''股票最近数据行情,保存的是 StockEachDayInfo 的数据'''
    def __init__(self,eachDayInfo):
        super(StockLatestInfo,self)
        self.stockInfo = []
        self.stockInfo.append(eachDayInfo)

    def addStockDayInfo(self,dayInfo):
        self.stockInfo.append(dayInfo)

class MostValueableCompanyInfo(CompanyInfo):
    '''最可投资价值股票,净资产收益率>15%，3年净利润复合增长率>10%'''
    def __init__(self,code,name,jzcsyl,fhjlrzzl,orgCount,sz):
        super(MostValueableCompanyInfo,self).__init__(code,name)
        self.jzcsyl = jzcsyl
        self.fhjlrzzl = fhjlrzzl
        self.orgCount = orgCount
        self.sz = sz

    #如果要排序，就需要实现该方法
    def __lt__(self, other):
        return float(self.orgCount) > float(other.orgCount)

class RoeModel(object):
    '''日期，roe，利润增长率,收入增长率，总收入，总利润'''
    def __init__(self,date,roe,profitRate,incomeRate,income,profit,):
        super(RoeModel,self).__init__()
        self.dateOfRoe = date
        self.roe = roe
        self.profitRate = profitRate
        self.incomeRate = incomeRate
        self.income = income
        self.profit = profit

class  CompanyProfitRankModel(CompanyInfo):
    def __init__(self,code,name,profit):
        super(CompanyProfitRankModel,self).__init__(code,name)
        self.profit = profit

class StockUtils(object):
    def __init__(self):
        super(StockUtils,self).__init__()

    @classmethod
    def getTodayMaxStockList(self):
        '''当日创新高'''
        res =  getHtmlFromUrl(todayMaxPriceUrl)
        companyListObj = getJsonObj(res)
        if companyListObj:
            list =  companyListObj['Results']
            cList = []
            if list and len(list):
                for item in list:
                    '''item 是字符串，应该分割处理'''
                    stockInfo = item.split(',')
                    cinfo = CompanyInfo(stockInfo[1],stockInfo[2])
                    cList.append(cinfo)
                return cList
        return  None

    @classmethod
    def getThreeDaysMaxStockList(self):
        '''最近三天创新高'''
        res = getHtmlFromUrl(threeDaysMaxPriceUrl)
        companyListObj = getJsonObj(res)
        if companyListObj:
            list =  companyListObj['Results']
            cList = []
            if list and len(list):
                for item in list:
                    stockInfo = item.split(',')
                    cinfo = CompanyInfo(stockInfo[1],stockInfo[2])
                    cList.append(cinfo)
                return cList

        return  None

    @classmethod
    def getFiveDaysMaxStockList(self):
        '''最近5天创新高'''
        res = getHtmlFromUrl(fiveDaysMaxPriceUrl)
        companyListObj = getJsonObj(res)
        if companyListObj:
            list =  companyListObj['Results']
            cList = []
            if list and len(list):
                for item in list:
                    stockInfo = item.split(',')
                    cinfo = CompanyInfo(stockInfo[1],stockInfo[2])
                    cList.append(cinfo)
                return cList
        return  None

    def getCompanyBussinessDetailString(self,code):
        res = getHtmlFromUrl((bussinessDetailUrl % getMarketCode(code)))
        obj = getJsonObjOrigin(res)
        if obj:
            li = obj['hxtc']
            if li and len(li) > 2:
                return li[0]['ydnr'] + '\n' + li[1]['ydnr']
        return None

    @classmethod
    def getMostValueableStockList(self):
        '''价值投资股票列表'''
        page = 1
        cList = []
        while True:
            res = getHtmlFromUrl(mostValueableStockUrl % page)
            if res:page += 1
            companyListObj = getJsonObj(res)
            if companyListObj:
                list =  companyListObj['Results']
                if list and len(list):
                    for item in list:
                        stockInfo = item.split(',')
                        jzcsyl = str(float(stockInfo[5].split('(')[0]) * 100) + '%'
                        fhlrzzl = str(float(stockInfo[3].split('(')[0]) * 100) + '%'
                        orgCount = stockInfo[4].split('(')[0]
                        sz = str(int(float(stockInfo[6])/10000/10000))
                        cinfo = MostValueableCompanyInfo(stockInfo[1],stockInfo[2],jzcsyl,fhlrzzl,orgCount,sz)
                        cList.append(cinfo)
                    if len(list) < pageSize:break
                    #如果将要获取的页码比总共的页码大，那么直接退出
                    if int(companyListObj['PageCount']) < page:break
                else:break
            else:break
        return cList

    @classmethod
    def getRoeModelListOfStockForCode(self,code):
        '''价值投资股票信息'''
        #url = ROEOfStockUrl % (getMarketCode(code,prefix=False))
        url = ROEOfStockUrl2 % (getMarketCode(code,prefix=True))
        res = getHtmlFromUrl(url,False)
        #ROEList = getJsonList(res)
        obj = getJsonObjOrigin(res)
        if not obj:return None
        ROEList = obj['Result']['zyzb']
        if isinstance(ROEList,list) and len(ROEList) > 0:
            cList = []
            for item in ROEList:
                m = RoeModel(item['date'],item['jqjzcsyl'],item['gsjlrtbzz'],item['yyzsrtbzz'], item['yyzsr'],item['kfjlr'])
                cList.append(m)
            return cList
        else:
            return  None

    @classmethod
    def roeStringForCode(self,code):
        li = self.getRoeModelListOfStockForCode(code)
        s = ''
        if li and len(li) > 0:
            for item in li:
                s += (u'季报:' + item.dateOfRoe).ljust(15,' ') + (u'净资产收益率:' + item.roe + '%').ljust(15,' ') + (u'收入同比增长率:' + item.incomeRate + '%').ljust(17,' ') + (u'净利润同比增长率:' + item.profitRate + '%').ljust(18,' ') + (u'总收入:' + item.income).ljust(12,' ')  + (u' 总利润:' + item.profit).ljust(12,' ')
                s += '\n'
            return s
        else:
            return None

    @classmethod
    def profitRankForCode(self,code):
        li = self.getRoeModelListOfStockForCode(code)
        s = ''
        if li and len(li) > 0:
            return li[0].profit
        else:
            return None

    @classmethod
    def getIndustryReport(self):
        '''行业调研'''
        res = getHtmlFromUrl(hangyeReportUrl)
        companyListObj = getJsonObj(res)
        if companyListObj:
            list = companyListObj['data']
            cList = []
            if list and len(list):
                for item in list:
                    cList.append(item)
                return cList
        return None

    @classmethod
    def getCompanyResearchRank(self):
        '''公司被调研次数排行'''
        res = getHtmlFromUrl(dytjBaseUrl,True)
        companyListObj = getJsonObj(res)
        if companyListObj:
            list = companyListObj['data']
            cList = []
            if list and len(list):
                for item in list:
                    cinfo = CompanyResearchReport(item['CompanyCode'],item['CompanyName'], item['StartDate'],item['Description'],item['OrgSum'])
                    cList.append(cinfo)
                return cList
        else:
            return None


    @classmethod
    def getRcommandedCompanyList(cls):
        '''券商推荐'''
        res = getHtmlFromUrl(tjgsBaseUrl)
        companyListObj = getJsonObj(res)
        if companyListObj:
            list = companyListObj['data']
            cList = []
            if list and len(list):
                for item in list:
                    '''item 是字符串，应该分割处理'''
                    info = CompanyRecommandInfo(item['secuFullCode'],
                        item['secuName'],item['datetime'],item['insName'], item['title'],item['rate'])
                    cList.append(info)
                return cList
        return None

    @classmethod
    def getRcommandRankList(self):
        '''券商推荐次数排行'''
        res = getHtmlFromUrl(reommendRankUrl)
        companyListObj = getJsonObj(res)
        if companyListObj:
            list = companyListObj['data']
            cList = []
            if list and len(list):
                for item in list:
                    li = item.split(',')
                    info = CompanyRecommandRankInfo(li[1],
                        li[2],li[5],li[6], li[7])
                    cList.append(info)
                return cList
        return None

    @classmethod
    def getMbzfRank(cls):
        '''目标涨幅空间'''
        res = getHtmlFromUrl(mbzfRank)


    @classmethod
    def getStockholderHoldsStocks(self):
        '''股东增持'''
        res = getHtmlFromUrl(gdzcBaseUrl,True)
        companyList = getJsonObj2(res)
        if companyList and len(companyList):
            cList = []
            for item in companyList:
                '''item 是字符串，应该分割处理'''

                cList.append(item)
            return cList
        return None

    @classmethod
    def getIndustryRank(self):
        '''概念涨幅'''

        res = getHtmlFromUrl(gnzfBaseUrl)
        companyListObj = getJsonObj2(res)
        if companyListObj and len(companyListObj):
            cList = []
            for item in companyListObj:
                cList.append(item)
            return cList
        return None

    @classmethod
    def getHyzfRank(self):
        '''近5日行业资金流入'''
        res = getHtmlFromUrl(hyzf)
        listobj = getJsonObj2(res)
        if listobj and len(listobj):
            clist = []
            for item in listobj:
                clist.append(item)
            return clist
        return None


    @classmethod
    def getDetailStockInfo(self,page):
        '''资金流入排行'''
        res = getHtmlFromUrl(xxsjPrefixUrl + str(page) + xxsjSuffix)
        companyListObj = getJsonObj4(res)
        if companyListObj and len(companyListObj):
            cList = []
            for item in companyListObj:
                cList.append(item)
            return cList
        return None

    @classmethod
    def getInflowRankForPage(self,page):
        '''资金流入排行'''

        url = zjlrPrefix + str(page) + zjlrSuffix
        res = getHtmlFromUrl(url)
        companyListObj = getJsonObj3(res)
        if companyListObj and len(companyListObj):
            cList = []
            for item in companyListObj:
                cList.append(item)
            return cList
        return None
    @classmethod
    def getSylDetailDataForCode(self,code):
        '''市盈率、市值相关数据'''
        url = sylDetailPrefixUrl + code + getMarketId(code)+sylDetailSuffixUrl
        res = getHtmlFromUrl(url)
        valueList =  getJsonObj5(res)
        if valueList and len(valueList) > 0:
           return CompanyValueInfo(valueList[1],valueList[2],valueList[-15],valueList[-10],str(long(valueList[-7])/10000/10000), valueList[-16]+'%')
        return None

    def getLast4MonthKLine(self,code):
        '''近4个月k线图'''
        url = last4MonthKLineUrl % (code + getMarketId(code))
        # res = getHtmlFromUrl(url)
        return  url

    def getLast4YearKLine(self,code):
        url = last4YearKLineUrl % (code + getMarketId(code))
        # res = getHtmlFromUrl(url)
        return  url


def szyjl(code):
    return  StockUtils().getSylDetailDataForCode(code)

def szyjlString(model):
    return u'市值:'+ model.sz +u'亿' + u'  市盈率:'+model.syl + u'  市净率:'+model.sjl + u'  换手率:'+model.hsl

def mostValueableCompanyString(model):
    return ('净资产收益率年增长率:'+model.jzcsyl).ljust(15,' ') + (u'  3年利润复合增长率:'+model.fhjlrzzl).ljust(21,' ') + ('  持仓机构数:' + model.orgCount)

def percentToFloat(s):
    return float(s.strip("%"))

def mainMethod():
    util = StockUtils()
    sqlins = mysqlOp()

    print '\n=======================%s=========================' % datetime.today()
    print '\n==============================当日新高======================================'
    print '=======================可能当日开始突破、也可能已经突破了数日======================='
    li = util.getTodayMaxStockList()
    if li and len(li) > 0:
        for item in li:
            model = szyjl(item.code)
            if not model:continue
            if int(model.sz) < companySzDownLimit or percentToFloat(model.hsl) < companyHslDownLimit :continue
            print item.name, item.code,szyjlString(model)
    #
    # #最近3天创新高
    print '\n=================================近3天创新高===================================='
    th = util.getThreeDaysMaxStockList()
    if th and len(th) > 0:
        for item in th:
            model = szyjl(item.code)
            if not model: continue
            if int(model.sz) < companySzDownLimit or percentToFloat(model.hsl) < companyHslDownLimit: continue
            print item.name,item.code,szyjlString(model)

    # #最近5天创新高
    print '\n=================================近5天创新高====================================='
    th = util.getFiveDaysMaxStockList()
    if th and len(th) > 0:
        for item in th:
            model = szyjl(item.code)
            if not model: continue
            if int(model.sz) < companySzDownLimit or percentToFloat(model.hsl) < companyHslDownLimit: continue
            print item.name,item.code,szyjlString(model)
            print '月K线图:' +  util.getLast4MonthKLine(item.code)
            print '年K线图:' +  util.getLast4YearKLine(item.code)

    #价值投资选股
    print '\n===============================价值投资股票========================================'
    th = util.getMostValueableStockList()
    if th and len(th) > 0:
        for item in th:
            model = szyjl(item.code)
            if not model: continue
            #不需要过滤换手率以及市值，价值投资
            print item.name.ljust(6,' '),item.code.ljust(7,' '),mostValueableCompanyString(item),szyjlString(model)
            print util.roeStringForCode(item.code)

    # #调研次数
    print '\n=================================机构调研次数排行==================================='
    dy = util.getCompanyResearchRank()
    if dy and len(dy):
        for item in dy:
            print item.name, item.code, item.time, item.desc, item.sum
    #
    # #推荐公司
    print '\n===============================券商推荐公司======================================='
    tj = util.getRcommandedCompanyList()
    if tj and len(tj):
        for item in tj:
            print item.code, item.name, item.time, item.org, item.reason, item.advice

    #推荐次数排行公司
    print '\n======================================券商推荐次数排行============================================='
    tj = util.getRcommandRankList()
    if tj and len(tj):
        for item in tj:
            print item.code.ljust(9,' '),item.name.ljust(8,' '),('券商推荐次数:'+item.count + '  买入评级:' + item.buyCount + '  增持评级:' + item.addCount)
            print util.roeStringForCode(item.code)
            print util.getCompanyBussinessDetailString(item.code)
            print '\n'

    # #股东增持
    print '\n====================================股东增持====================================='
    gd = util.getStockholderHoldsStocks()
    if gd and len(gd):
        for item in gd:
            companyInfo = item.split(',')
            print companyInfo[0],companyInfo[1], companyInfo[-4],u'至',companyInfo[-3], companyInfo[5],(companyInfo[6] + u'万').ljust(13,' '),u'占流通股的', (companyInfo[7] + '%')

    # #行业报告
    print '\n==================================行业涨幅分析报告================================='
    hy = util.getIndustryReport()
    if hy and len(hy):
        for item in hy:
            print item.split(',')[10],item.split(',')[-1],'   ', item

    #行业资金流入排行
    print '\n==============================行业资金流入排行====================================='
    lit = util.getHyzfRank()
    if lit and len(lit):
        for item in lit:
            print item

    # #概念排行
    print '\n=================================概念涨幅排行====================================='
    lit = util.getIndustryRank()
    if lit and len(lit):
        for item in lit:
            print item

    #如果是周六日，不执行
    day = time.strftime('%w')
    if day == '0' or day == '6':return

    #判断日期，如果是当天的重复数据，就只更新stock5DayDetailData，否则开始迁移表数据
    #=======================================================
    tstr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    hour = time.localtime().tm_hour
    sqlTime = sqlins.getNewestDate()
    if sqlTime and sqlTime not in tstr and hour >= 16 and hour <= 23:
        #下午4点到夜里23点才能更新数据
        # ================================================
        # 10天的数据，后9张表数据往前挪，所有的新数据插入到第5张表中
        sqlins.moveDataIntables(stockDetailTableList);
        # ================================================
        # ================================股票详细信息入库第5张表==================================
        # 先清理第10张表股票详细的数据
        sqlins.clearTableData(stockDetailTableList[9])
        # 清理股票列表，因为有新股更新
        sqlins.clearTableData(stocklistName)
    else:
        # 先清理，然后直接更新stock5DayDetailData的数据
        sqlins.clearTableData(stockDetailTableList[9])


    # 资金流入排行
    print '\n==============================资金流入排行======================================='
    startPage = 1
    profitModelList = []
    while True:
        infl = util.getInflowRankForPage(startPage)
        if infl and len(infl) > 0:
            for item in infl:
                # code，name，newestprice,zhangfu,zhuliliuru,riqi
                array = item.split(',')
                # print array[5] + 'w' + '  ', array[1],array[2],array[3],array[4],array[5],array[15],item
                value = '\'' + str(array[1]) + '\'' + ',' + '\'' + str(array[2]).encode(
                    'utf8') + '\'' + ',' + '\'' + str(array[3]) + '\'' + ',' + '\'' + str(
                    array[4]) + '\'' + ',' + '\'' + str(array[5]) + '\'' + ',' + '\'' + str(array[15]) + '\''
                # 资金流入sql
                sql = 'insert into %s(code,sname,endPrice,priceIncrementPercent, inflowCount,sdate) VALUE (%s)' % (stockDetailTableList[-1],value)
                # 证券列表sql
                listsql = 'insert into %s(code,name) value(\'%s\',\'%s\')' % (
                stocklistName, str(array[1]), str(array[2]))
                # sqlins.executeSQL(sql)
                # sqlins.executeSQL(listsql)
                p = util.profitRankForCode(array[1])
                pmodel = CompanyProfitRankModel(array[1],array[2],p)
                profitModelList.append(pmodel)
                print 'page = %s'%str(startPage)
        if infl and len(infl) < pageSize:
            sorted(profitModelList, key=lambda mo: mo.profit)
            for model in profitModelList:
                print model.code ,model.name,model.profit
            break
        startPage += 1

    # 沪深A 股的详细数据
    # print '\n================================沪深A股详细数据==================================='
    # startPage = 1
    # while True:
    #     li = util.getDetailStockInfo(startPage)
    #     if li and len(li) > 0:
    #         for item in li:
    #             array = item.split(',')
    #             # code1  name2   zhangfu5, startPrice10，max11，min12
    #             code = str(array[1])
    #             #市盈率、市净率、市值
    #             valueModel = util.getSylDetailDataForCode(code)
    #             if not valueModel:continue
    #             sql = 'update  %s set startPrice = \'%s\',maxPrice=\'%s\',minPrice=\'%s\',syl = \'%s\',sjl=\'%s\',sz=\'%s\',hsl=\'%s\' WHERE  code = \'%s\'' % (
    #             stockDetailTableList[-1],str(array[10]), str(array[11]), str(array[12]),valueModel.syl,valueModel.sjl,valueModel.sz,valueModel.hsl,str(array[1]))
    #             sqlins.executeSQL(sql)
    #     if len(li) < pageSize:
    #         break
    #     startPage += 1
    #
    # # 提交更新
    # sqlins.cur.close()
    # sqlins.conn.commit()
    # sqlins.conn.close()
    # # ============================end===============================
    print '\n\n\n\n\n\n\n\n\n'

if __name__ == '__main__':
    mainMethod()


