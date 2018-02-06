# -*- coding: utf-8 -*-
'''
验证模拟tick和真实tick的效果差异
DSL和OWNL分开对比，视结果如有必要再结合
时间：2017-10-01 —— 2017-12-01

读取dsl/ownl平仓数据，并按验证时间截取
计算dsl/ownl的原始ret,new_ret,ret_delta
读取真实tick平仓数据，计算真实tick的new_ret,retdelta
每组参数保存一个总数，计算真实和虚拟new_ret的差值
'''
import DATA_CONSTANTS as DC
import pandas as pd

if __name__ =='__main__':
    #参数配置
    exchange_id = 'SHFE'
    sec_id='RB'
    symbol = '.'.join([exchange_id, sec_id])
    K_MIN = 600
    topN=5000
    pricetick=DC.getPriceTick(symbol)
    slip=pricetick
    starttime='2017-09-01'
    endtime='2017-12-11'
    tickstarttime='2017-10-01'
    tickendtime='2017-12-01'