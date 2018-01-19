# -*- coding: utf-8 -*-

import pandas as pd

def parasetGenerator():
    setlist=[]
    mashort=0
    malong=0
    kdj_n=0
    dmi_n=0
    i=0
    for ms in range(3,8,1):
        for ml in range(8,31,1):
            for kn in range(6,32,2):
                for dn in range(6,32,2):
                    setname='Set'+str(i)+' MS'+str(ms)+' ML'+str(ml)+' KN'+str(kn)+' DN'+str(dn)
                    l=[setname,ms,ml, kn ,dn]
                    setlist.append(l)
                    i+=1

    setpd=pd.DataFrame(setlist,columns=['Setname','MA_Short','MA_Long','KDJ_N','DMI_N'])
    setpd.to_csv('ParameterOptSet_1.csv')

def rankwinSetGenerator():
    setlist=[]
    rankset=range(1,8,1)
    winset=range(1,13,1)
    for r in rankset:
        for w in winset:
            setname=("_Rank%d_win%d_oprResult"%(r,w))
            setlist.append(setname)
    setpd=pd.DataFrame(setlist,columns=['Setname'])
    setpd.to_csv('RankWinSet.csv')

if __name__ == '__main__':
    #parasetGenerator()
    rankwinSetGenerator()