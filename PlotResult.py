# -*- coding: utf-8 -*-
'''
画每次跑完的结果
读DCE.I600 finanlresults.csv文件，把setname列出来
setname+' result.csv'读每个文件的funcuve，列一条曲线
X轴用时间，纵轴固定-5~25万
标题用setname
'''

import datetime
import pandas as pd
import numpy
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, FormatStrFormatter, MultipleLocator

path='Results\\DCE I 600\\'
finalresult=pd.read_csv(path+'DCE.I600 finanlresults.csv')
setlist=finalresult.setname
for sn in setlist:
    filaname=path+'DCE.I600 '+sn+' result.csv'
    fundata=pd.read_csv(filaname)
    funcuve=fundata.funcuve
    plt.plot(funcuve)
    plt.title(sn)
    plt.savefig(path+sn+' funcuve.png', dip=500)
    plt.cla()
