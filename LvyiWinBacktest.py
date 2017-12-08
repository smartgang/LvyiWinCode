# -*- coding: utf-8 -*-
'''
保留几份数据：
    1、dailyBar:每分钟的原始K线数据
    2、dailyBarMin:合成后的多分种周期K线数据（只有K线数据）
    3、MAdf:保存MA数据close,MA_Short,MA_Long,MA_True,MA_Cross
    4、DMIdf:保存DMI数据，A,B,C,TR,HD,LD,DMP,DMM,PDI,MDI,ADX,ADXR,DMI_True,DMI_GOLD_CROSS
    5、KDJdf:保存KDJ数据，KDJ_K,KDJ_D,KDJ_J,KDJ_True
    6、OprList：保存每次开平仓的数据 回测结后，由OpenOprList和CloseOprList合成opentime	openindex	openprice	closetime	closeindex	closeprice	tradetype	ret	ret_r
    几份数据同时更改，默认行与行之间是对齐的，不做专门的对齐判断
程序流程：
init中加载各参数
准备数据：加载前一周的数据，计算各个数据df
onbar:
    合成dailyBarMin
    计算MAdf
    计算DMIdf
    计算KDJdf
    判断MA叉点，如果是金叉
        是否有空仓，有则平仓
        判断是否满足开多条件，满足则开多
    如果是死叉
        是否有多仓，有则平仓
        判断是否满足开空条件，满足则开空
结束回测后，保存各份文件
'''
from gmsdk import *
import sys
import logging
import logging.config
import pandas as pd
import datetime
import MA
import DMI
import KDJ



class LvyiWinBacktest(StrategyBase):

    def __init__(self, *args, **kwargs):
        super(LvyiWinBacktest, self).__init__(*args, **kwargs)

        self.dailyBar = pd.DataFrame( columns=['strtime', 'utctime', 'open', 'high', 'low', 'close', 'position', 'volume'])  # 保存原始的1分钟Bar数据
        self.dailyBarMin=pd.DataFrame( columns=['strtime', 'utctime', 'open', 'high', 'low', 'close', 'position', 'volume'])
        self.MAdf = pd.DataFrame(columns=['close','MA_Short','MA_Long','MA_True','MA_Cross'])
        self.DMIdf = pd.DataFrame(columns=['A','B','C','TR','HD','LD','DMP','DMM','PDI','MDI','ADX','ADXR','DMI_True','DMI_GOLD_CROSS'])
        self.KDJdf = pd.DataFrame(columns=['KDJ_K','KDJ_D','KDJ_J','KDJ_True'])

        self.OpenOprList = pd.DataFrame(columns=['opentime','openindex','openprice','tradetype'])
        self.CloseOprList = pd.DataFrame(columns=['closetime','closeindex','closeprice','ret','ret_r'])

        self.buyFlag = 0  # 买卖标识，-1为卖，1为买
        self.positionHold = self.get_positions()

        self.stopLossRatio = self.config.getfloat('backtest', 'stoplossratio')
        # self.K_min=3 #采用多少分钟的K线，默认为3分钟，在on_bar中会判断并进行合并
        self.K_min = self.config.getint('backtest', 'bar_type')/60 or 3

        self.noticeMail = self.config.get('para', 'noticeMail')
        self.tradeStartHour = self.config.getint('para', 'tradeStartHour')
        self.tradeStartMin = self.config.getint('para', 'tradeStartMin')
        self.tradeEndHour = self.config.getint('para', 'tradeEndHour')
        self.tradeEndMin = self.config.getint('para', 'tradeEndMin')

        self.backwardDay = self.config.getint('para', 'backwardDay')
        self.position_hold=self.config.getfloat('backtest','position_hold')

        self.DMI_N = self.config.getint('para', 'DMI_N')
        self.DMI_M = self.config.getint('para', 'DMI_M')
        self.KDJ_N = self.config.getint('para', 'KDJ_N')
        self.KDJ_M = self.config.getint('para', 'KDJ_M')
        self.KDJ_HLim = self.config.getint('para', 'KDJ_HLim')
        self.KDJ_LLim = self.config.getint('para', 'KDJ_LLim')

        self.MA_Short = self.config.getint('para', 'MA_Short')
        self.MA_Long = self.config.getint('para', 'MA_Long')

        self.K_minCounter = 0  # 用来计算当前是合并周期内的第几根K线，在onBar中做判断使用
        self.last_update_time = datetime.datetime.now()  # 保存上一次 bar更新的时间，用来帮助判断是否出现空帧

        self.exchange_id, self.sec_id, buf = self.subscribe_symbols.split('.', 2)
        self.symbol_id=self.exchange_id+'.'+self.sec_id
        self.dataPrepare()

    def on_login(self):
        # 准备好数据
        pass

    def on_backtest_finish(self, indicator):
        self.dailyBar.to_csv('dailyBar RB900.csv')
        self.dailyBarMin.to_csv('dailyBarMin RB900.csv')
        self.MAdf.to_csv('MAdf RB900.csv')
        self.DMIdf.to_csv('DMIdf RB900.csv')
        self.KDJdf.to_csv('KDJdf RB900.csv')
        OprList=pd.concat([self.OpenOprList,self.CloseOprList],axis=1)
        OprList.to_csv('OprList RB900.csv')
        pass

    def on_bar(self, bar):
        #实时只能取1分钟的K线，所以要先将1分钟线合并成多分钟K线，具体多少分钟由参数K_min定义
        #每次on_bar调用，先用数据保存到dailyBar中，再判断是否达到多分钟合并时间，是则进行合并，并执行一系列操作
        timenow=datetime.datetime.fromtimestamp(bar.utc_time)

        rownum = self.update_dailyBar(bar)
        # barMin = int(bar.strtime[14:15])#取分钟数
        #barMin = int(timenow.minute)
        #if (barMin + 1) % self.K_min == 0 and self.K_minCounter >= self.K_min:
        self.update_dailyBarMin(bar)
        self.updateParadata()
        self.trendOpr()#趋势判断，在趋势判断中会给出buyFlag


    #开始运行时，准备好数据，主要是把当天的数据加载到缓存中
    def dataPrepare(self):
        startTime = datetime.time(self.tradeEndHour, self.tradeStartMin, 0).strftime("%H:%M:%S")
        if self.mode==4:
            d, t = self.start_time.split(' ', 1)
            y, m, d = d.split('-', 2)
            d = datetime.date(int(y), int(m), int(d))
            startDate=(d-datetime.timedelta(days=self.backwardDay)).strftime("%Y-%m-%d")
            endTime=self.start_time
        else:
            startDate=(datetime.date.today()-datetime.timedelta(days=self.backwardDay)).strftime("%Y-%m-%d")
            endTime=datetime.date.today().strftime("%Y-%m-%d")+' '+startTime
        sT=startDate+' '+startTime
        bars = self.get_bars(self.exchange_id+'.'+self.sec_id, self.K_min*60, sT, endTime)
        #这里数据只用来计算MA
        rownum=0
        for bar in bars:
            rownum = self.update_dailyBar(bar)
            if rownum % self.K_min == 0 and rownum >= self.K_min:
                self.update_dailyBarMin(bar)
        self.MAdf=MA.MA(self.dailyBarMin.close,self.MA_Short,self.MA_Long)
        self.DMIdf=DMI.DMI(self.dailyBarMin,self.DMI_N,self.DMI_M)
        kdjdf=KDJ.KDJ(self.dailyBarMin,self.KDJ_N,self.KDJ_M)
        kdjdf['KDJ_True'] = 0
        kdjdf.loc[(self.KDJ_HLim > kdjdf['KDJ_K']) & (kdjdf['KDJ_K'] > kdjdf['KDJ_D']), 'KDJ_True'] = 1
        kdjdf.loc[(self.KDJ_LLim < kdjdf['KDJ_K']) & (kdjdf['KDJ_K'] < kdjdf['KDJ_D']), 'KDJ_True'] = -1
        self.KDJdf=kdjdf

        #下面要再做实盘下当天数据的处理
        if self.mode==2:
            pass
        if rownum>0:
            self.last_update_time = datetime.datetime.fromtimestamp(self.dailyBar.iloc[-1].utctime)
        print("------------------------data prepared-----------------------------")
        pass

    #更新dailyBar
    def update_dailyBar(self,bar):
        rownum=self.dailyBar.shape[0]
        self.dailyBar.loc[rownum] =[bar.strtime,bar.utc_time, bar.open, bar.high, bar.low, bar.close, bar.position,bar.volume]
        self.K_minCounter += 1
        return rownum+1

    #更新dailyBarMin
    def update_dailyBarMin(self,bar):
        '''
        K线合并后，取第一根K线的时间作为合并后的K线时间
        :param bar:
        :return:
        '''
        self.dailyBarMin.loc[self.dailyBarMin.shape[0]] =self.dailyBar.iloc[-1]
        '''
        if rownum <self.K_min:return
        self.dailyBarMin.loc[self.dailyBarMin.shape[0]] = \
            [self.dailyBar.iloc[-self.K_min].strtime,
             self.dailyBar.iloc[-self.K_min].utctime,
             self.dailyBar.iloc[- self.K_min].open,  # 取合并周期内第一条K线的开盘
             self.dailyBar.iloc[- self.K_min:].high.max(),  # 合并周期内最高价
             self.dailyBar.iloc[- self.K_min:].low.min(),  # 合并周期内的最低价
             bar.close,  # 最后一条K线的收盘价
             bar.position, # 最后一条K线的仓位值
             self.dailyBar.iloc[ -self.K_min:].volume.sum() #v1.2版本加入成交量数据
             ]
        self.K_minCounter=0
        '''
        pass

    def updateParadata(self):
        #更新MA数据
        self.MAdf.loc[self.MAdf.shape[0]]=MA.newMA(self.dailyBarMin.close,self.MAdf,self.MA_Short,self.MA_Long)

        #更新DMI数据
        self.DMIdf.loc[self.DMIdf.shape[0]]=DMI.newDMI(self.dailyBarMin,self.DMIdf,self.DMI_N,self.DMI_M)

        #更新KDJ数据
        kdj=KDJ.newKDJ(self.dailyBarMin,self.KDJdf,self.KDJ_N,self.KDJ_M)
        newk=kdj[0]
        newd=kdj[1]
        KDJ_True=0
        if self.KDJ_HLim>newk and newk>newd:KDJ_True=1
        elif self.KDJ_LLim<newk and newk<newd:KDJ_True=-1
        kdj.append(KDJ_True)
        self.KDJdf.loc[self.KDJdf.shape[0]]=kdj

        pass

    def trendOpr(self):
        '''
        趋势判断：
        :param bar:
        :return:
        '''
        if self.MAdf.iloc[-1].MA_Cross==1:#出现金叉
            #平空仓
            pl = self.get_positions()
            for p in pl:
                if p.side == 2:
                    print 'close short'
                    self.close_short(self.exchange_id, self.sec_id, 0, p.volume)
                    closeprice=self.dailyBarMin.iloc[-1].close
                    ret=(self.OpenOprList.iloc[-1].openprice-closeprice)
                    ret_r=ret/self.OpenOprList.iloc[-1].openprice
                    self.CloseOprList.loc[self.CloseOprList.shape[0]] = [
                        self.dailyBarMin.iloc[-1].strtime,
                        self.dailyBarMin.iloc[-1].utctime,
                        closeprice,
                        ret,
                        ret_r
                        ]

            #判断是否开多仓
            if self.KDJdf.iloc[-1].KDJ_True==1 and self.DMIdf.iloc[-1].DMI_True==1:
                #开多仓
                print 'open long'

                cash=self.get_cash()
                positioncash=cash.nav*self.position_hold
                aviablecash=positioncash-cash.frozen-cash.order_frozen
                if aviablecash>0:#能用于持仓的钱要大于已经冻结的钱，说明还有余钱可以开仓
                    volume=int(aviablecash/(10*self.dailyBarMin.iloc[-1].close))
                    self.open_long(self.exchange_id, self.sec_id, 0, volume)
                    self.OpenOprList.loc[self.OpenOprList.shape[0]] =[
                        self.dailyBarMin.iloc[-1].strtime,
                        self.dailyBarMin.iloc[-1].utctime,
                        self.dailyBarMin.iloc[-1].close,
                        1]
            pass

        elif self.MAdf.iloc[-1].MA_Cross==-1:#出现死叉
            #平多仓
            pl = self.get_positions()
            for p in pl:
                if p.side == 1:
                    print 'close long'
                    self.close_long(self.exchange_id, self.sec_id, 0, p.volume)
                    closeprice=self.dailyBarMin.iloc[-1].close
                    ret=(closeprice-self.OpenOprList.iloc[-1].openprice)
                    ret_r=ret/self.OpenOprList.iloc[-1].openprice
                    self.CloseOprList.loc[self.CloseOprList.shape[0]] = [
                        self.dailyBarMin.iloc[-1].strtime,
                        self.dailyBarMin.iloc[-1].utctime,
                        closeprice,
                        ret,
                        ret_r
                        ]

            if self.KDJdf.iloc[-1].KDJ_True == -1 and self.DMIdf.iloc[-1].DMI_True == -1:
                #开空仓
                print 'open short'

                cash = self.get_cash()
                positioncash = cash.nav * self.position_hold
                aviablecash = positioncash - cash.frozen - cash.order_frozen
                if aviablecash > 0:  # 能用于持仓的钱要大于已经冻结的钱，说明还有余钱可以开仓
                    volume = int(aviablecash / (10 * self.dailyBarMin.iloc[-1].close))

                    self.open_short(self.exchange_id, self.sec_id, 0, volume)
                    self.OpenOprList.loc[self.OpenOprList.shape[0]] = [
                        self.dailyBarMin.iloc[-1].strtime,
                        self.dailyBarMin.iloc[-1].utctime,
                        self.dailyBarMin.iloc[-1].close,
                        -1]

if __name__ == '__main__':
    ''''
    myStrategy = Mystrategy(
        username='smartgang@126.com',
        password='39314656a',
        strategy_id='3ac57fd6-818b-11e7-8296-0019860005e9',
        subscribe_symbols='DCE.J.bar.60',
        mode=4,#2为实时行情，3为模拟行情,4为回测
        td_addr=''
    )
    '''
    ini_file = sys.argv[1] if len(sys.argv) > 1 else 'LvyiWinConfig.ini'
    logging.config.fileConfig(ini_file)
    myStrategy = LvyiWinBacktest(config_file=ini_file)
    ret = myStrategy.run()
    print('exit code: ', ret)