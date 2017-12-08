# -*- coding: utf-8 -*-
import datetime
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, FormatStrFormatter, MultipleLocator

__color_lightsalmon__ = '#ffa07a'
__color_pink__ = '#ffc0cb'
__color_navy__ = '#000080'
__color_gold__ = '#FDDB05'
__color_gray30__ = '0.3'
__color_gray70__ = '0.7'
__color_lightblue__ = 'lightblue'


#1.读取数据
#2.画3相框架
#3.画图1，K线和MA20，买卖点

#======================================================================================================================
#以下图框架准备
_figfacecolor = __color_pink__
_figedgecolor = __color_navy__
_figdpi = 200
_figlinewidth = 1.0
_xfactor = 0.025  # x size * x factor = x length
_yfactor = 0.025  # y size * y factor = y length

_xlength = 8
_ylength = 4

#坐标轴网格====================================================================================
def setup_Axes(axes):
    axes.set_axisbelow(True)  # 网格线放在底层
    axes.grid(True, 'major', color='0.5', linestyle='solid', linewidth=0.1)
    axes.grid(True, 'major', color='0.5', linestyle='solid', linewidth=0.1)

#设置X轴=======================================================================================
def setup_xAxis(timeindex,axes,xAxis,xsize,isvisible=False):
    axes.set_xlim(0, xsize)
    xAxis.set_label('price')
    xAxis.set_label_position('top')

    timetmp = []
    for t in timeindex: timetmp.append(t[11:19])
    timelist = [datetime.time(int(hr), int(ms), int(sc)) for hr, ms, sc in
                [dstr.split(':') for dstr in timetmp]]
    '''
    i = 0
    minindex = []
    for min in timelist:
        if min.minute % 20 == 0: minindex.append(i)
        i += 1
    '''
    xMajorLocator = FixedLocator((numpy.arange(0,xsize,20)))
    wdindex = numpy.arange(xsize)
    xMinorLocator = FixedLocator(wdindex)

    # 确定 X 轴的 MajorFormatter 和 MinorFormatter
    def x_major_formatter(idx, pos=None):
        #if idx<_xsize:return timelist[int(idx)].strftime('%H:%M')
        #else:return pos
        if idx<_xsize:return timeindex[int(idx)][0:16]
        else:return pos

    def x_minor_formatter(idx, pos=None):
        if idx<_xsize:return timelist[int(idx)].strftime('%M:%S')
        else:return pos

    xMajorFormatter = FuncFormatter(x_major_formatter)
    xMinorFormatter = FuncFormatter(x_minor_formatter)
    # 设定 X 轴的 Locator 和 Formatter
    xAxis.set_major_locator(xMajorLocator)
    xAxis.set_major_formatter(xMajorFormatter)
    xAxis.set_minor_locator(xMinorLocator)
    xAxis.set_minor_formatter(xMinorFormatter)

    # 设置 X 轴标签的显示样式。
    for mal in axes.get_xticklabels(minor=False):
        mal.set_fontsize(3)
        mal.set_horizontalalignment('center')
        mal.set_rotation('90')
        if isvisible:mal.set_visible(True)
        else: mal.set_visible(False)

    for mil in axes.get_xticklabels(minor=True):
        mil.set_fontsize(3)
        mil.set_horizontalalignment('right')
        mil.set_rotation('90')
        mil.set_visible(False)

#设置Y轴===============================================================================================
def setup_yAxis(axes,yAxis,yhighlim,ylowlim):
    yAxis.set_label_position('left')
    ylimgap = yhighlim - ylowlim
    #   主要坐标点
    # ----------------------------------------------------------------------------
    #        majors = [ylowlim]
    #        while majors[-1] < yhighlim: majors.append(majors[-1] * 1.1)
    majors = numpy.arange(ylowlim, yhighlim, ylimgap / 5)
    minors = numpy.arange(ylowlim, yhighlim, ylimgap / 10)
    #   辅助坐标点
    # ----------------------------------------------------------------------------
    #        minors = [ylowlim * 1.1 ** 0.5]
    #        while minors[-1] < yhighlim: minors.append(minors[-1] * 1.1)
    majorticks = [round(loc,3) for loc in majors if loc > ylowlim and loc < yhighlim]  # 注意，第一项（ylowlim）被排除掉了
    minorticks = [round(loc,3) for loc in minors if loc > ylowlim and loc < yhighlim]

    #   设定 Y 轴坐标的范围
    axes.set_ylim(ylowlim, yhighlim)

    #   设定 Y 轴上的坐标
    #   主要坐标点
    # ----------------------------------------------------------------------------
    yMajorLocator = FixedLocator(numpy.array(majorticks))

    # 确定 Y 轴的 MajorFormatter
    def y_major_formatter(num, pos=None):
        return str(num)

    yMajorFormatter = FuncFormatter(y_major_formatter)

    # 设定 X 轴的 Locator 和 Formatter
    yAxis.set_major_locator(yMajorLocator)
    yAxis.set_major_formatter(yMajorFormatter)

    # 设定 Y 轴主要坐标点与辅助坐标点的样式
    fsize = 4
    for mal in axes.get_yticklabels(minor=False):
        mal.set_fontsize(fsize)

    # 辅助坐标点
    # ----------------------------------------------------------------------------
    yMinorLocator = FixedLocator(numpy.array(minorticks))

    # 确定 Y 轴的 MinorFormatter
    def y_minor_formatter(num, pos=None):
        return str(num)

    yMinorFormatter = FuncFormatter(y_minor_formatter)

    # 设定 Y 轴的 Locator 和 Formatter
    yAxis.set_minor_locator(yMinorLocator)
    yAxis.set_minor_formatter(yMinorFormatter)
    # 设定 Y 轴辅助坐标点的样式
    for mil in axes.get_yticklabels(minor=True):
        mil.set_visible(False)

def setup_yAxisForRet(axes,yAxis):
    axes.set_ylim(-3, 3)
    yAxis.set_major_locator(MultipleLocator(0.3))
    yAxis.set_major_formatter(FormatStrFormatter('%1.2f') )
    fsize = 4
    for mal in axes.get_yticklabels(minor=False):
        mal.set_fontsize(fsize)

#画收益率=============================================================
#def drawRET_R(axes,longdf,shortdf,beginindex):
def drawRET_R(axes,oprdf,xsize):
    #生成两个序列，一个序列是值，一个序列是位置
    #longindex = numpy.array(longdf['Unnamed: 0'] - beginindex)
    #shortindex= numpy.array(shortdf['Unnamed: 0'] - beginindex)
    #longvalue = numpy.array(longdf['ret_r'])
    #shortvalue = numpy.array(shortdf['ret_r'])
    longindex=numpy.array(oprdf.loc[oprdf['tradetype']==1].index)
    shortindex = numpy.array(oprdf.loc[oprdf['tradetype'] == -1].index)
    longvalue = numpy.array(oprdf.loc[oprdf['tradetype'] == 1]['ret_r'])
    shortvalue = numpy.array(oprdf.loc[oprdf['tradetype'] == -1]['ret_r'])
    for i in numpy.arange(len(longindex)):
        value=longvalue[i]*100
        axes.vlines(longindex[i],0,value,edgecolor='red', linewidth=0.5)
    for i in numpy.arange(len(shortindex)):
        value = shortvalue[i]*100
        axes.vlines(shortindex[i],0,value,edgecolor='blue', linewidth=0.5)
    pass

#=============================================
if __name__ == '__main__':
    symbol='DCE.I'
    folder='DCE I 900\\'
    K_MIN = 900
    setdf=pd.read_excel('Results\\paraset.xlsx')
    setlist=setdf['setname']
    _Fig = plt.figure(figsize=(_xlength, _ylength), dpi=_figdpi,
                      facecolor=_figfacecolor,
                      edgecolor=_figedgecolor, linewidth=_figlinewidth)  # Figure 对象
    axesUp = _Fig.add_axes([0.05, 0.54, 0.8, 0.4], axis_bgcolor='black')
    # axesMid1= _Fig.add_axes([0.1, 0.44, 0.8, 0.2], axis_bgcolor='black')
    # axesMid2 = _Fig.add_axes([0.1, 0.22, 0.8, 0.2], axis_bgcolor='black')
    axesDown = _Fig.add_axes([0.05, 0.02, 0.8, 0.38], axis_bgcolor='black')
    axesText = _Fig.add_axes([0.88, 0.02, 0.1, 0.55])
    axesUp2 = axesUp.twinx()

    for set in setlist:
        print set
        filename='Results\\'+folder+symbol + str(K_MIN) +' '+set+ ' result.csv'
        oprraw=pd.read_csv(filename)
        oprraw.index=pd.to_datetime(oprraw['opentime'])
        oprraw = oprraw.tz_localize(tz='PRC')
        cutbefordate = ['2016-01-01', '2016-07-01', '2017-01-01', '2017-07-01']
        cutafterdate=['2016-07-01','2017-01-01','2017-07-01','2017-10-18']

        for l in numpy.arange(4):
            print cutafterdate[l]
            openoprraw= oprraw.truncate(before=cutbefordate[l],after=cutafterdate[l])
            price = openoprraw['openprice']
            funcuve= openoprraw['funcuve']

            _xsize =len(price)
            beginindex = openoprraw.ix[openoprraw.index[0], 'Unnamed: 0']

            #画上图：K线，买卖点，MA20均线
            print 'drawing price and funcuve'
            y1high=price.max()
            y1low=price.min()
            y1highlimUp = int(y1high / 10) * 10 + 10  # K线子图 Y 轴最大坐标,5%最大波动,调整为10的倍数
            y1lowlimUp = int(y1low / 10) * 10  # K线子图 Y 轴最小坐标


            xAxisUp = axesUp.get_xaxis()
            yAxisUp = axesUp.get_yaxis()

            #axesUp.set_title('K line', fontsize=4)
            setup_Axes(axesUp)
            setup_yAxis(axesUp,yAxisUp,y1highlimUp,y1lowlimUp)

            rarray_price = numpy.array(price)
            axesUp.plot(rarray_price,color='r',linewidth=0.5,label='price')
            axesUp.legend(loc='upper left', fontsize=4, shadow=False)
            axesUp.set_title(symbol+' '+set, fontsize=5)

            y2high = funcuve.max()
            y2low = funcuve.min()
            y2highlimUp = int(y2high / 10) * 10 + 10  # K线子图 Y 轴最大坐标,5%最大波动,调整为10的倍数
            y2lowlimUp = int(y2low / 10) * 10  # K线子图 Y 轴最小坐标
            y2AxisUp = axesUp2.get_yaxis()
            setup_yAxis(axesUp2, y2AxisUp, y2highlimUp, y2lowlimUp)
            rarray_funcuve = numpy.array(funcuve)
            axesUp2.plot(rarray_funcuve, color='blue', linewidth=0.5, label='funcuve')
            #注:设置双坐标轴，需要在画完两条轴的曲线后，再设置X轴，不然画出来的图X轴双边会有空白

            setup_xAxis(openoprraw['opentime'], axesUp, xAxisUp, _xsize, isvisible=True)
            axesUp2.legend(loc='upper right', fontsize=4, shadow=False)


            #显示统计数据：
            #按月统计：开多次数/成功率/开空次数/成功率
            print 'drawing table'
            openoprraw['month'] = '2016-01'
            for i in openoprraw.index:
                openoprraw.ix[i, 'month'] = openoprraw.ix[i, 'opentime'][0:7]
            L_POS_rgroued = openoprraw.loc[(openoprraw['ret_r'] > 0) & (openoprraw['tradetype'] == 1)]['ret_r'].groupby(
                openoprraw['month'])
            L_NEG_rgroued = openoprraw.loc[(openoprraw['ret_r'] <= 0) & (openoprraw['tradetype'] == 1)]['ret_r'].groupby(
                openoprraw['month'])
            S_POS_rgroued = openoprraw.loc[(openoprraw['ret_r'] > 0) & (openoprraw['tradetype'] == -1)]['ret_r'].groupby(
                openoprraw['month'])
            S_NeG_rgroued = openoprraw.loc[(openoprraw['ret_r'] <= 0) & (openoprraw['tradetype'] == -1)]['ret_r'].groupby(
                openoprraw['month'])
            a = L_POS_rgroued.count()
            b = L_NEG_rgroued.count()
            c = S_POS_rgroued.count()
            d = S_NeG_rgroued.count()
            monthlist = a.index
            statdf = pd.DataFrame({'L_POS': a})
            statdf['L_NEG'] = b
            statdf['S_POS'] = c
            statdf['S_NEG'] = d
            statdf = statdf.fillna(0)
            statdf['LT'] = statdf['L_POS'] + statdf['L_NEG']
            statdf['LTR'] = statdf['L_POS'] / statdf['LT']
            statdf['ST'] = statdf['S_POS'] + statdf['S_NEG']
            statdf['STR'] = statdf['S_POS'] / statdf['ST']

            axesText.get_yaxis().set_visible(False)
            axesText.get_xaxis().set_visible(False)
            col_labels = ['LT', 'LTR', 'ST','STR']
            row_labels = numpy.array(monthlist)
            table_vals = statdf.loc[:,'LT':'STR']
            tv=[]
            for i in numpy.arange(table_vals.shape[0]):
                tv.append([table_vals.ix[i,'LT'],round(table_vals.ix[i,'LTR']*100,0),table_vals.ix[i,'ST'],round(table_vals.ix[i,'STR']*100,0)])
            my_table = axesText.table(cellText=tv, colWidths=[0.2] * 4,
                                 rowLabels=row_labels, colLabels=col_labels,
                                 loc='best')

            # 画下图：买卖收益，在买点画柱状图，y轴是当前开仓的收益率
            print 'drawing ret'
            openoprraw = openoprraw.reset_index(drop=True)
            setup_Axes(axesDown)
            xAxisDown = axesDown.get_xaxis()
            yAxisDown = axesDown.get_yaxis()
            setup_xAxis(openoprraw['opentime'], axesDown, xAxisDown, _xsize)
            yhighlimDown = openoprraw['ret_r'].max()
            ylowlimDown = openoprraw['ret_r'].min()
            # axesDown.set_title('Return Rate(%)', fontsize=4)
            setup_yAxisForRet(axesDown, yAxisDown)
            drawRET_R(axesDown, openoprraw, _xsize)


            _Fig.savefig('Results\\'+folder+symbol + str(K_MIN) +' '+set+ cutafterdate[l]+' PNG.png', dip=500)
            axesUp.cla()
            axesUp2.cla()
            axesDown.cla()
            axesText.cla()
