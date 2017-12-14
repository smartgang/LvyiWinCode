# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np


rawdata=pd.read_csv('SHFE.RB600result.csv')
date=rawdata.opentime
month=date.str.slice(0,7)
rawdata['month']=month
print rawdata.month
rawdata['ret_r_1']=rawdata['ret_r']+1
grouped_ret_r=rawdata['ret_r_1'].groupby(rawdata['month'])
ret_r_prod=grouped_ret_r.prod()
print ret_r_prod

