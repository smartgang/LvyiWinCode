# -*- coding: utf-8 -*-
'''
逐月绘制ricequant和myquant的K线数据进行对比
每个月一张图，上图ricequnt，下图myquant
'''
import PlotLib
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import time
import os
import numpy

#def draw(axes,df,opropendf,oprclosedf,oprbeginindex,title='K-Line'):
def draw(axes,df,title='K-Line'):
    high = df['high']
    low = df['low']
    open = df['open']
    close = df['close']
    _xsize = len(high)
    phigh = high.max()
    plow = low.min()
    yhighlimUp = int(phigh / 10) * 10 + 10  # K线子图 Y 轴最大坐标,5%最大波动,调整为10的倍数
    ylowlimUp = int(plow / 10) * 10  # K线子图 Y 轴最小坐标

    xAxisUp = axes.get_xaxis()
    yAxisUp = axes.get_yaxis()

    axes.set_title(title, fontsize=4)
    PlotLib.setup_Axes(axes)
    PlotLib.setup_xAxis(df['strtime'], axes, xAxisUp, _xsize, isvisible=True)
    PlotLib.setup_yAxis(axes, yAxisUp, yhighlimUp, ylowlimUp)
    PlotLib.drawK(axes, open, high, low, close)
    #PlotLib.drawOprline(axes, opropendf,oprclosedf, ylowlimUp, numpy.array(low), oprbeginindex)

def draw_wave(axes,df,wavename):
    _xsize=df.shape[0]
    PlotLib.setup_Axes(axes)
    xAxisMid1 = axes.get_xaxis()
    yAxisMid1 = axes.get_yaxis()
    PlotLib.setup_xAxis(df['strtime'], axes, xAxisMid1, _xsize)
    if wavename is 'price_wave':
        yhighlimMid1=3
        ylowlimMid1=0.01
    else:
        yhighlimMid1 = df[wavename].max()
        ylowlimMid1 = df[wavename].min()
    PlotLib.setup_yAxis(axes, yAxisMid1, yhighlimMid1, ylowlimMid1)
    PlotLib.drawMA(axes, df[wavename])

if __name__ == '__main__':
    _figfacecolor = PlotLib.__color_pink__
    _figedgecolor = PlotLib.__color_navy__
    _figdpi = 200
    _figlinewidth = 1.0
    _xfactor = 0.025  # x size * x factor = x length
    _yfactor = 0.025  # y size * y factor = y length
    _xlength = 8
    _ylength = 4

    _Fig = plt.figure(figsize=(_xlength, _ylength), dpi=_figdpi,
                      facecolor=_figfacecolor,
                      edgecolor=_figedgecolor, linewidth=_figlinewidth)  # Figure 对象
    axesUp= _Fig.add_axes([0.1, 0.6, 0.8, 0.3],facecolor='black')
    axesMid= _Fig.add_axes([0.1, 0.3, 0.8, 0.25], facecolor='black')
    axesDown = _Fig.add_axes([0.1, 0.02, 0.8, 0.25], facecolor='black')

    riceoprpath="D:\\002 MakeLive\myquant\LvyiWin\Results\SHFE RB 600 ricequant\\"
    ricedatapath = "D:\\002 MakeLive\DataCollection\\bar data\SHFE.RB\\"
    #myquantoprpath="D:\\002 MakeLive\myquant\LvyiWin\Results\DCE I600 slip\\"


    #myquantpath=ricedatapath+"myquant\\"
    os.chdir(ricedatapath)
    os.mkdir('RiceKline-RB-pricewaveing')

    symbol="SHFE.RB"
    K_MIN=600
    ricedata=pd.read_csv(ricedatapath+symbol+' '+str(K_MIN)+'_wave.csv')
    #myquantdata=pd.read_csv(myquantpath+symbol+' '+str(K_MIN)+'.csv')


    #setname="SHFE.RB600 Set6213 MS4 ML21 KN24 DN30 result.csv"
    #riceoprdf=pd.read_csv(riceoprpath+setname)
    #myquantoprdf=pd.read_csv(myquantoprpath+setname)

    #按周的的K线+opr对比
    #weeklist = [datetime.strftime(x, '%Y-%m-%d') for x in list(pd.date_range(start='2016-01-04', end='2017-12-06', freq='7D'))]
    #print weeklist
    monthlist = [datetime.strftime(x, '%Y-%m-%d') for x in list(pd.date_range(start='2010-01-01', end='2018-01-01', freq='7D'))]
    monthlist.append('2018-01-01')
    for i in range(len(monthlist)-1):
        print monthlist[i]
        starttime=monthlist[i]+' 00:00:00'
        endtime=monthlist[i+1]+' 00:00:00'
        startutc=float(time.mktime(time.strptime(starttime, "%Y-%m-%d %H:%M:%S")))
        endutc = float(time.mktime(time.strptime(endtime, "%Y-%m-%d %H:%M:%S")))
        ricedf=ricedata.loc[(ricedata['utc_time'] >= startutc) & (ricedata['utc_time'] < endutc)]
        ricedf = ricedf.reset_index(drop=True)
        #myquantdf = myquantdata.loc[(myquantdata['utc_time'] >= startutc) & (myquantdata['utc_time'] < endutc)]
        #myquantdf = myquantdf.reset_index(drop=True)

        #riceopenopr = riceoprdf.loc[(riceoprdf['openutc'] >= startutc) & (riceoprdf['openutc'] < endutc)]
        #riceipenopr = riceopenopr.reset_index(drop=True)
        #ricecloseopr = riceoprdf.loc[(riceoprdf['closeutc'] >= startutc) & (riceoprdf['closeutc'] < endutc)]
        #ricecloseopr = ricecloseopr.reset_index(drop=True)
        if ricedf.shape[0]==0:continue
        #ricebegginindex=ricedf.ix[0, 'Unnamed: 0'] #DCE.I是23,SHFE.RB是0

        
        #myquantopenopr = myquantoprdf.loc[(myquantoprdf['openutc'] >= startutc) & (myquantoprdf['openutc'] < endutc)]
        #myquantopenopr = myquantopenopr.reset_index(drop=True)
        #myquantcloseopr = myquantoprdf.loc[(myquantoprdf['closeutc'] >= startutc) & (myquantoprdf['closeutc'] < endutc)]
        #myquantcloseopr = myquantcloseopr.reset_index(drop=True)
        #myquantbeginindex=myquantdf.ix[0,'Unnamed: 0']-76

        draw(axesUp,ricedf,"K-Line To MA waveing"+monthlist[i])
        draw_wave(axesMid,ricedf,'price_wave')
        draw_wave(axesDown,ricedf,'volume_wave')
        #draw(axesUp,ricedf,riceipenopr,ricecloseopr,ricebegginindex,'rice-K-Set6213-'+monthlist[i]+'--'+monthlist[i+1])
        #draw(axesDown, myquantdf,myquantopenopr,myquantcloseopr,myquantbeginindex, 'myquant-K '+weeklist[i]+'--'+weeklist[i+1])

        _Fig.savefig('RiceKline-RB-pricewaveing\\rice-RB-waving'+monthlist[i]+'.png',dip=500)
        axesUp.cla()
        axesMid.cla()
        axesDown.cla()
        #axesDown.cla()

    '''
    #按周的K线对比
    monthlist = [datetime.strftime(x, '%Y-%m') for x in list(pd.date_range(start='2010-01-01', end='2018-01-01', freq='M'))]
    monthlist.append('2018-01')
    print monthlist
    for i in range(len(monthlist)-1):
        print monthlist[i]
        starttime=monthlist[i]+'-01 00:00:00'
        endtime=monthlist[i+1]+'-01 00:00:00'
        startutc=float(time.mktime(time.strptime(starttime, "%Y-%m-%d %H:%M:%S")))
        endutc = float(time.mktime(time.strptime(endtime, "%Y-%m-%d %H:%M:%S")))
        ricedf=ricedata.loc[(ricedata['utc_time'] >= startutc) & (ricedata['utc_time'] < endutc)]
        ricedf = ricedf.reset_index(drop=True)
        #myquantdf = myquantdata.loc[(myquantdata['utc_time'] >= startutc) & (myquantdata['utc_time'] < endutc)]
        #myquantdf = myquantdf.reset_index(drop=True)

        draw(axesUp,ricedf,'rice-K-RB-'+monthlist[i])
        #draw(axesDown, myquantdf, 'myquant-K')

        _Fig.savefig('RiceKline-RB\\'+'rice-K-RB-'+monthlist[i]+'.png',dip=500)
        axesUp.cla()
        #axesDown.cla()
    '''
