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

# #资产收益率
# zcsyl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[cz_ylnl01(1|0.15)]&p=1&jn=PjxcQEPi&ps=40&s=cz_ylnl01(1|0.15)&st=-1&r=1507351655919'
#
# #3年净利润增长10%以上
# lrzzl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[cz_ylnl01(1|0.15)][cz_cznl06(1|0.1)]&p=1&jn=qnbTLhLx&ps=40&s=cz_cznl06(1|0.1)&st=-1&r=1507351729913'
#
# #股价连续上涨3天
# lxsz3Day = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[cz_ylnl01(1|0.15)][cz_cznl06(1|0.1)][cz20(1|100y)][cz_hqzb07(4|3)]&p=1&jn=fcDVFSUc&ps=40&s=cz_hqzb07(4|3)&st=-1&r=1507351771770'

#净资产收益率12%  3年利润增长率10% 80亿市值以上
mostValueableStockUrl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[cz_ylnl01(1|0.12)][cz_cznl06(1|0.1)][cz20(1|100y)]&p=1&jn=pUnYlfVk&ps=100&s=cz20(1|100y)&st=-1&r=1507352123438'

#公司市值下限
companySzDownLimit = 50
companyHslDownLimit = 1.0

def getHtmlFromUrl(url,utf8coding=False):
    # setCookie2()
    # req = urllib2.Request(url,None,header)
    ret = urllib.urlopen(url)
    if utf8coding:
        return ret.read().decode('gbk', 'ignore').encode('utf-8')
    else:
        return ret.read()

def getJsonObj(obj):
    #"var moJuuzHq="{"Results":["2,300672,国科微,是","2,300676,华大基因,是","1,603612,索通发展,是","1,603707,健友股份,是","2,002888,惠威科技,是","2,300678,中科信息,是","2,002889,东方嘉盛,是","1,603860,中公高科,是","2,300685,艾德生物,是","2,300687,赛意信息,是","1,603880,南卫股份,是","2,300689,澄天伟业,是","1,603602,纵横通信,是","2,300688,创业黑马,是","1,603721,中广天择,是","2,300691,联合光电,是","1,601326,秦港股份,是","1,603776,永安行,是","2,002892,科力尔,是","1,603129,春风动力,是","1,603557,起步股份,是"],"AllCount":"21","PageCount":"1","AtPage":"1","PageSize":"40","ErrMsg":"","UpdateTime":"2017/8/19 13:37:03","TimeOut":"3ms"}"
    # newobj = obj.split('=')[1]  #//必须要将前面的= 去掉
    # return  simplejson.loads(newobj)
    newobj = "{" + obj.split('={')[1]
    return simplejson.loads(newobj)

def getJsonObj2(obj):
    partern = re.compile("data:.*?\"]")
    list = re.findall(partern, obj)

    if list and len(list) > 0:
        s = list[0]
        sepString = s.split(':')[1]
        return simplejson.loads(sepString)
    else:
        return None

def getJsonObj3(obj):
    partern = re.compile("data:.*?\"]")
    list = re.findall(partern, obj)

    if list and len(list) > 0:
        s = list[0]
        sepString = s.split(':[')[1]
        return simplejson.loads('[' + sepString)
    else:
        return None
def getJsonObj4(obj):
    partern = re.compile("rank:.*?\"]")
    list = re.findall(partern, obj)

    if list and len(list) > 0:
        s = list[0]
        sepString = s.split(':[')[1]
        return simplejson.loads('[' + sepString)
    else:
        return None

def getJsonObj5(obj):
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

def getGloRank():
    '''目标涨幅排行'''
    res = getHtmlFromUrl(mbzfRank)
    soup = BeautifulSoup(res)
    soup.find()


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
    def __init__(self,code,name,jzcsyl,fhjlrzzl,sz):
        super(MostValueableCompanyInfo,self).__init__(code,name)
        self.jzcsyl = jzcsyl
        self.fhjlrzzl = fhjlrzzl
        self.sz = sz

    #如果要排序，就需要实现该方法
    def __lt__(self, other):
        return float(self.fhjlrzzl.strip('%')) > float(other.fhjlrzzl.strip('%'))

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


    @classmethod
    def getMostValueableStockList(self):
        '''价值投资股票列表'''
        res = getHtmlFromUrl(mostValueableStockUrl)
        companyListObj = getJsonObj(res)
        if companyListObj:
            list =  companyListObj['Results']
            cList = []
            if list and len(list):
                for item in list:
                    stockInfo = item.split(',')
                    jzcsyl = str(float(stockInfo[3].split('(')[0]) * 100) + '%'
                    fhlrzzl = str(float(stockInfo[4].split('(')[0]) * 100) + '%'
                    sz = str(int(float(stockInfo[5])/10000/10000))
                    cinfo = MostValueableCompanyInfo(stockInfo[1],stockInfo[2],jzcsyl,fhlrzzl,sz)
                    cList.append(cinfo)

                #   根据3年利润复合增长率递增排序
                    cList.sort()

                return cList

        return  None

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


def szyjl(code):
    return  StockUtils().getSylDetailDataForCode(code)

def szyjlString(model):
    return u'市值:'+ model.sz +u'亿' + u'  市盈率:'+model.syl + u'  市净率:'+model.sjl + u'  换手率:'+model.hsl

def mostValueableCompanyString(model):
    return ('净资产收益率:'+model.jzcsyl).ljust(15,' ') + (u'  3年利润复合增长率:'+model.fhjlrzzl).ljust(21,' ')


def percentToFloat(s):
    return float(s.strip("%"))

def mainMethod():
    util = StockUtils()
    sqlins = mysqlOp()

    # 当天创新高
    print '\n===========================当日新高==================================='
    print '====================可能当日开始突破、也可能已经突破了数日===================='
    li = util.getTodayMaxStockList()
    for item in li:
        model = szyjl(item.code)
        if int(model.sz) < companySzDownLimit or percentToFloat(model.hsl) < companyHslDownLimit :continue
        print item.name, item.code,szyjlString(model)
    #
    # #最近3天创新高
    print '\n============================近3天创新高=================================='
    th = util.getThreeDaysMaxStockList()
    for item in th:
        model = szyjl(item.code)
        if int(model.sz) < companySzDownLimit or percentToFloat(model.hsl) < companyHslDownLimit: continue
        print item.name,item.code,szyjlString(model)

    # #最近5天创新高
    print '\n=============================近5天创新高=================================='
    th = util.getFiveDaysMaxStockList()
    for item in th:
        model = szyjl(item.code)
        if int(model.sz) < companySzDownLimit or percentToFloat(model.hsl) < companyHslDownLimit: continue
        print item.name,item.code,szyjlString(model)

    #价值投资选股
    print '\n=============================价值投资股票=================================='
    th = util.getMostValueableStockList()
    for item in th:
        model = szyjl(item.code)
        #不需要过滤换手率以及市值，价值投资
        print item.name.ljust(6,' '),item.code.ljust(7,' '),mostValueableCompanyString(item),szyjlString(model)


    # #调研次数
    print '\n=========================机构调研次数排行=========================='
    dy = util.getCompanyResearchRank()
    for item in dy:
        print item.name, item.code, item.time, item.desc, item.sum
    #
    # #推荐公司
    print '\n=========================利好公司推荐=============================='
    tj = util.getRcommandedCompanyList()
    for item in tj:
        print item.code, item.name, item.time, item.org, item.reason, item.advice

    # #股东增持
    print '\n===========================股东增持================================='
    gd = util.getStockholderHoldsStocks()
    for item in gd:
        print item

    # #行业报告
    print '\n====================行业涨幅分析报告========================='
    hy = util.getIndustryReport()
    for item in hy:
        print item.split(',')[10],item.split(',')[-1],'   ', item

    #行业资金流入排行
    print '\n====================行业资金流入排行=========================='
    lit = util.getHyzfRank()
    for item in lit:
        print item

    # #概念排行
    print '\n====================概念涨幅排行=========================='
    lit = util.getIndustryRank()
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
    print '\n====================资金流入排行=========================='
    startPage = 1
    while True:
        infl = util.getInflowRankForPage(startPage)
        if len(infl) > 0:
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
                sqlins.executeSQL(sql)
                sqlins.executeSQL(listsql)
        if len(infl) < 100:
            break
        startPage += 1

    # 沪深A 股的详细数据
    print '\n====================沪深A股详细数据======================='
    startPage = 1
    while True:
        li = util.getDetailStockInfo(startPage)
        if len(li) > 0:
            for item in li:
                array = item.split(',')
                # code1  name2   zhangfu5, startPrice10，max11，min12
                code = str(array[1])
                #市盈率、市净率、市值
                valueModel = util.getSylDetailDataForCode(code)
                sql = 'update  %s set startPrice = \'%s\',maxPrice=\'%s\',minPrice=\'%s\',syl = \'%s\',sjl=\'%s\',sz=\'%s\',hsl=\'%s\' WHERE  code = \'%s\'' % (
                stockDetailTableList[-1],str(array[10]), str(array[11]), str(array[12]),valueModel.syl,valueModel.sjl,valueModel.sz,valueModel.hsl,str(array[1]))
                sqlins.executeSQL(sql)
        if len(li) < 100:
            break
        startPage += 1

    # 提交更新
    sqlins.cur.close()
    sqlins.conn.commit()
    sqlins.conn.close()
    # ============================end===============================
    print '\n\n\n\n\n\n\n\n\n'

if __name__ == '__main__':
    mainMethod()


