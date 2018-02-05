# -*- coding: utf-8 -*-
'''
采用相同周期K线
初始设定：
ma_mid=(ma_short+ma_long)/2
只计算回测结果中end cash排名top2000的参数组合
内容：
ma_short下穿ma_mid平多
ma_short上破ma_mid平空
计算过程：
读取回测结果，按end cash排名，取出top2000的参数组合名称
根据名称参数计算ma_mid，读取oprResult
读取bardata，对齐index,计算ma_mid,以及ma_short和ma_mid的cross（copy读法）
遍历oprResult，找到每一个opr中间的ma_mid_cross，返回strtime,utc_time,index,close
重新计算ret,ret_r
计算end cash结果并保存
final result要保存之前的end cash和新的end cash做对比
结果分析：
综合对比top2000的end cash结果，看总体是否有改善
挑选典型参数组(end cash最大、改善最大，改善最小），看策略生效的特征
'''
import pandas as pd
import DATA_CONSTANTS as DC
import MA
import multiprocessing
import os
def threeMACloseCal(sn,exchange_id,sec_id,K_MIN,oprset,slip,step,oprresultpath):
    print sn
    symbol = '.'.join([exchange_id, sec_id])
    initial_cash=20000
    margin_rate=0.2
    commission_ratio=0.00012

    #计算mamid，并计算ma和cross
    mashort=oprset['MA_Short']
    malong=oprset['MA_Long']
    #mamid=int((mashort+malong)/2)
    madelta=(malong-mashort)/4.0
    mamid=mashort+int(step*madelta)
    if mamid==malong:
        mamid-=1
    bardata=DC.getBarData(symbol,K_MIN,'2016-01-01 00:00:00','2018-01-01 00:00:00')
    df_MA = MA.MA(bardata['close'], mashort, mamid)
    df_MA.drop('close', axis=1, inplace=True)
    df = pd.concat([bardata, df_MA], axis=1)

    #读取opr
    oprfilename=symbol+str(K_MIN)+' '+oprset['Setname']+' result.csv'
    oprresult=pd.read_csv(oprresultpath+"\\"+oprfilename)
    oprresult['new_ret']=oprresult['ret']
    oprresult['new_ret_r']=oprresult['ret_r']
    oprresult['new_closetime']=oprresult['closetime']
    oprresult['new_closeindex'] = oprresult['closeindex']
    oprresult['new_closeutc'] = oprresult['closeutc']
    oprresult['new_closeprice'] = oprresult['closeprice']
    oprnum=oprresult.shape[0]
    for i in range(oprnum):
        #print i
        opr=oprresult.iloc[i]
        oprtype=opr['tradetype']
        openutc=opr['openutc']
        closeutc=opr['closeutc']
        #判断是否有mamid的交叉导致新的平仓
        crossdf=df.loc[(df['utc_time']>=openutc)&(df['utc_time']<=closeutc)]
        if oprtype==1:
            cross=crossdf.loc[crossdf['MA_Cross']==-1]
        else:
            cross=crossdf.loc[crossdf['MA_Cross']==1]
        if cross.shape[0]>0:
            c=cross.iloc[0]
            openprice=opr['openprice']
            newcloseprice=c['close']
            newclosetime=c['strtime']
            newcloseutc=c['utc_time']
            newcloseindex=c['Unnamed: 0']
            newret=((newcloseprice - openprice) * oprtype) - slip
            oprresult.ix[i,'new_ret'] = newret
            oprresult.ix[i,'new_ret_r']=newret/openprice
            oprresult.ix[i,'new_closetime'] = newclosetime
            oprresult.ix[i,'new_closeindex'] = newcloseindex
            oprresult.ix[i,'new_closeutc'] = newcloseutc
            oprresult.ix[i,'new_closeprice'] = newcloseprice

    firsttradecash = initial_cash / margin_rate
    # 2017-12-08:加入滑点
    oprresult['new_commission_fee'] = firsttradecash * commission_ratio * 2
    oprresult['new_per earn'] = 0  # 单笔盈亏
    oprresult['new_own cash'] = 0  # 自有资金线
    oprresult['new_trade money'] = 0  # 杠杆后的可交易资金线
    oprresult['new_retrace rate'] = 0  # 回撤率

    oprresult.ix[0,'new_per earn'] = firsttradecash * oprresult.ix[0,'new_ret_r']
    # 加入maxcash用于计算最大回撤
    maxcash = initial_cash + oprresult.ix[0,'new_per earn'] - oprresult.ix[0,'new_commission_fee']
    oprresult.ix[0,'new_own cash'] = maxcash
    oprresult.ix[0,'new_trade money'] = oprresult.ix[0,'new_own cash'] / margin_rate

    for i in range(1, oprnum):
        commission = oprresult.ix[i - 1,'new_trade money'] * commission_ratio * 2
        perearn = oprresult.ix[i - 1,'new_trade money'] * oprresult.iloc[i]['new_ret_r']
        owncash = oprresult.ix[i - 1,'new_own cash'] + perearn - commission
        maxcash = max(maxcash, owncash)
        retrace_rate = (maxcash - owncash) / maxcash
        oprresult.ix[i,'new_own cash'] = owncash
        oprresult.ix[i,'new_commission_fee'] = commission
        oprresult.ix[i,'new_per earn'] = perearn
        oprresult.ix[i,'new_trade money'] = owncash / margin_rate
        oprresult.ix[i,'new_retrace rate'] = retrace_rate

    endcash = oprresult.ix[oprnum - 1, 'own cash']
    newendcash = oprresult.ix[oprnum - 1, 'new_own cash']
    successrate = (oprresult.loc[oprresult['new_ret'] > 0]).shape[0] / float(oprnum)
    max_single_loss_rate = abs(oprresult['new_ret_r'].min())
    max_retrace_rate = oprresult['new_retrace rate'].max()

    oprresult.to_csv(oprresultpath+'\\ThreeMAClose'+str(step)+'to4\\'+symbol+str(K_MIN)+' '+oprset['Setname']+' 3MAresult'+str(step)+'.csv')

    return [oprset['Setname'],mamid,endcash,newendcash,successrate,max_single_loss_rate,max_retrace_rate]

if __name__ == '__main__':
    #参数配置
    exchange_id = 'SHFE'
    sec_id='RB'
    symbol = '.'.join([exchange_id, sec_id])
    K_MIN = 600
    topN=10000
    slip=DC.getPriceTick(symbol)
    #midsteplist=[1,2,3,4]
    midsteplist=[3]
    #文件路径
    upperpath=DC.getUpperPath(uppernume=2)
    resultpath=upperpath+"\\Results\\"
    foldername = ' '.join([exchange_id, sec_id, str(K_MIN)])
    oprresultpath=resultpath+foldername
    #print foldername
    #读取finalresult文件并排序，取前testnum个
    finalresult=pd.read_csv(oprresultpath+"\\"+symbol+str(K_MIN)+" finanlresults.csv")
    finalresult=finalresult.sort_values(by='end_cash',ascending=False)
    totalnum=finalresult.shape[0]
    #finalresult=finalresult.iloc[0:topN]
    os.chdir(oprresultpath)
    for step in midsteplist:
        #os.mkdir("ThreeMAClose"+str(step)+"to4")
        newresultlist = []
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        l = []

        for sn in range(topN,totalnum):
            opr = finalresult.iloc[sn]
            l.append(pool.apply_async(threeMACloseCal,
                                      (sn,exchange_id, sec_id, K_MIN, opr, slip, step,oprresultpath)))
        pool.close()
        pool.join()

        resultDf = pd.DataFrame(columns=['Setname','mamid', 'oldendcash','endcash','successrate','max_single_loss_rate','max_retrace_rate'])
        i = 0
        for res in l:
            resultDf.loc[i]=res.get()
            i+=1
        tofilename = (oprresultpath+'\\ThreeMAClose'+str(step)+'to4\\'+symbol+str(K_MIN)+' '+' 3MA finalresult'+str(step)+'.csv')
        resultDf.to_csv(tofilename)