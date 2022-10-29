import os
os.environ["OMP_NUM_THREADS"] = '1'
import numpy as np
import pandas as pd
import feather

# DFS 
import jdfs
import data_core
from data_core import GenericTabularData


class TCMGen(object):
    ''' Generate transaction cost related data. '''
    
    def __init__(self, argv):
        self.univ = argv[0]
        self.sdate = int(str(argv[1]).replace('-', ''))
        self.edate = int(str(argv[2]).replace('-', ''))
        self.RCH_DIR = argv[3]

        if self.univ == 'HKGUniv.EqTOP500':
            self.region_asset = data_core.constructor_set_region_asset("hkg", "eq")

        self.full_date_list = self.get_full_date_list()
        self.gen_date_list  = self.get_date_list(self.sdate, self.edate)
        self.key_converter = np.vectorize(self.jkey2skey)
        
    
    def get_full_date_list(self):
        ''' Get trading dates. '''
    
        if self.univ[:3] == 'CHN': 
            full_date_list = jdfs.read_file('/com_md_eq_cn/date_info_jq/trading_dates.csv', 'com_md_eq_cn', 'date_info_jq')
            full_date_list = list(full_date_list['date'])
        elif self.univ == 'HKGUniv.EqTOP500':
            full_date_list = self.region_asset.dates.get_trading_dates(20170102, self.edate, fmt='int')
            
        full_date_list = np.array(full_date_list)    
        return full_date_list
        
        
    def get_date_list(self, sdate, edate):    
        ''' Get dates for data generation. ''' 
       
        date_list = self.full_date_list[(self.full_date_list >= sdate) & (self.full_date_list <= edate)]
        return date_list
        
        
    def add_day(self, date, offset):
        full_date_list = list(self.full_date_list)
        return int(full_date_list[full_date_list.index(date) + offset])

    
    def jkey2skey(self, jkey):
        skey = str(int(str(jkey)[1:])) + '.XHKG'
        return skey
       
        
    def tcm_gen(self, date):
        ''' Get the avg close price, trading amount of past 63 days, and avg spread of past 21 days. '''
        
        sdate = str(date)
        sdate = sdate[:4] + '-' + sdate[4:6] + '-' + sdate[6:8]
        l_mkt = []
        l_mkt_iday = []
        sub_list_63 = self.full_date_list[(self.full_date_list >= self.add_day(date, -63)) & (self.full_date_list <= date)]
        sub_list_21 = self.full_date_list[(self.full_date_list >= self.add_day(date, -21)) & (self.full_date_list <= date)]
        
        if self.univ[:3] == 'CHN':
        
            for day in sub_list_63:
                sday = str(day)
                sday = sday[:4] + '-' + sday[4:6] + '-' + sday[6:8]
                df_mkt = pd.read_csv(os.path.join(self.RCH_DIR, "raw/marketData_TR/dailyData/stock/%s/stock_%s.csv.gz" %(sday[0:4], sday)))
                df_mkt = df_mkt[['ID', 'date', 'close', 'amount', 'marketValue']]    
                df_mkt['date'] = day        
                l_mkt.append(df_mkt)
                
            for day in sub_list_21:
                sday = str(day)
                sday = sday[:4] + '-' + sday[4:6] + '-' + sday[6:8]
                df_mkt_iday = feather.read_dataframe(os.path.join(self.RCH_DIR, "raw/marketData_TR/idayData/stock/1min/%s/stock_%s.feather" %(sday[0:4], sday)))  
                df_mkt_iday = df_mkt_iday.loc[(df_mkt_iday['ask1p']>df_mkt_iday['bid1p'])&(df_mkt_iday['bid1p']>0)]
                df_mkt_iday['mid'] = (df_mkt_iday['ask1p']+df_mkt_iday['bid1p'])/2
                df_mkt_iday['spread'] = (df_mkt_iday['ask1p']-df_mkt_iday['bid1p'])/ df_mkt_iday['mid']
                df_mkt_iday['date'] = date
                df_mkt_iday = df_mkt_iday[['ID','date', 'ask1p', 'bid1p', 'mid', 'spread']]
                l_mkt_iday.append(df_mkt_iday)
                
        elif self.univ[:3] == 'HKG':
            region_asset = data_core.constructor_set_region_asset("hkg", "eq")
        
            for day in sub_list_63:
                day = int(day)
                stock_member = region_asset.univs.get_all_jkeys("HKGUniv.EqALL", day, day)
                config_params = GenericTabularData.ConfigParams()
                df_mkt = GenericTabularData(
                    region = "hkg",
                    asset = "eq",
                    dataset="md_eod",
                    univ=stock_member,
                    start_date=day,
                    end_date=day,
                    config_params=config_params).as_data_frame()
                df_mkt['date'] = day
                l_mkt.append(df_mkt)
                
            for day in sub_list_21:
                day = int(day)
                stock_member = region_asset.univs.get_all_jkeys("HKGUniv.EqALL", day, day)
                config_params = GenericTabularData.ConfigParams()
                config_params.freq = "1MIN"
                df_mkt_iday = GenericTabularData(
                    region = "hkg",
                    asset = "eq",
                    dataset="md_bar1m",
                    univ=stock_member,
                    start_date=day,
                    end_date=day,
                    config_params=config_params).as_data_frame()
                df_mkt_iday = df_mkt_iday.loc[(df_mkt_iday['ask1_opx']>df_mkt_iday['bid1_opx'])&(df_mkt_iday['bid1_opx']>0)]
                df_mkt_iday['mid'] = (df_mkt_iday['ask1_opx']+df_mkt_iday['bid1_opx'])/2
                df_mkt_iday['spread'] = (df_mkt_iday['ask1_opx']-df_mkt_iday['bid1_opx'])/ df_mkt_iday['mid']
                df_mkt_iday['date'] = day
                df_mkt_iday = df_mkt_iday[['jkey','date', 'ask1_opx', 'bid1_opx', 'mid', 'spread']]
                l_mkt_iday.append(df_mkt_iday)
                
        df_mkt = pd.concat(l_mkt)
        df_mkt_iday = pd.concat(l_mkt_iday)  ## load data
        df_mkt = df_mkt.rename(columns = {'ID':'skey', 'jkey':'skey', 'market_value': 'marketValue'})  
        df_mkt_iday = df_mkt_iday.rename(columns = {'ID':'skey', 'jkey':'skey'})  
        df_today = df_mkt.loc[df_mkt['date']==date,].copy()
        df_today['mv'] = df_today['marketValue']           
        df = df_mkt.groupby('skey')[['close', 'amount']].mean()
        df.reset_index(inplace = True)   
        df_iday_21 = df_mkt_iday.loc[(df_mkt_iday['date']<=date) & (df_mkt_iday['date']>=self.add_day(date, -21)),]
        df_iday = df_iday_21.groupby('skey')[['spread', 'mid']].mean()
        df_iday.reset_index(inplace = True)

        if self.univ[:3] == 'HKG':
            df_today['skey'] = self.key_converter(df_today['skey'])
            df['skey'] = self.key_converter(df['skey'])
            df_iday['skey'] = self.key_converter(df_iday['skey'])
        
        if self.univ[:3] == 'CHN':  ## get risk data, currently not used 
            df_risk = pd.read_csv(os.path.join(self.RCH_DIR, "raw/msci/CNE5S/daily/csv/%s/CNE5S_100_Asset_Data.%s.csv.gz" %(sdate[0:4], sdate)))
            df_risk.drop_duplicates(subset=['skey'], keep='first', inplace = True)
        elif self.univ[:3] == 'HKG':
            df_risk = pd.read_csv(os.path.join(self.RCH_DIR, "raw/msci/CXE1S/daily/csv/%s/CXE1S_100_Asset_Data.%s.csv.gz" %(sdate[0:4], sdate)))
            df_risk.drop_duplicates(subset=['skey'], keep='first', inplace = True)
            df_risk = df_risk[df_risk['skey'].str[:2] == 'HK']
            df_risk['skey'] = df_risk.skey.str[2:] + '.XHKG'
            
        df_risk['TotalRisk'] /= (244**0.5)
        df_risk['SpecRisk'] /= (244**0.5)
        df = df.merge(df_risk[['skey','TotalRisk', 'SpecRisk' ]], on = 'skey', how = "inner")
        df = df.merge(df_iday, on = 'skey', how = 'left')
        df = df.rename(columns = {"spread":"avgSprd","close":"close63","amount":"adv63", "TotalRisk":"trisk","SpecRisk":"srisk"}) 
        df = df.merge(df_today[['skey','mv' ]], on = 'skey', how = "left")
        Df_mb = []
        
        if self.univ[:3] == 'CHN':
            Univs = ['CHNUniv.EqIF','CHNUniv.EqIC','CHNUniv.EqCSI1000','CHNUniv.EqCSIRest']   
                     
            for univ in Univs:
                idxmb_path = os.path.join(self.RCH_DIR, 'raw/secData_TR/index_member/member_table_%s_%s.csv.gz' % (univ.replace('CHNUniv.Eq', ''), sdate))
                df_mb = pd.read_csv(idxmb_path)
                Df_mb.append(df_mb)

            df_mb = pd.concat(Df_mb)
                
        elif self.univ[:3] == 'HKG':
            
            valid_keys = region_asset.univs.get_all_jkeys("HKGUniv.EqTOP500", date, date)
            df_mb = pd.DataFrame({'skey': valid_keys})
            df_mb['skey'] = self.key_converter(df_mb['skey'])

        df_mb = df_mb.rename(columns = {'ID' : 'skey'})
        df['inUniv'] = df['skey'].isin(set(df_mb['skey']))
        df['hasAllData'] = ~(df.isna().any(axis = 1))
        df['isFitUniv'] = (df['inUniv'] & df['hasAllData']).astype(int)
        df['mv.B'] = np.minimum(df['mv'], np.quantile(df.loc[df['isFitUniv']==1,]['mv'].dropna(), 0.99))
        df['close63.B'] = np.minimum(df['close63'], np.quantile(df.loc[df['isFitUniv']==1,]['close63'].dropna(), 0.99))
        df['adv63.B'] = np.minimum(df['adv63'], np.quantile(df.loc[df['isFitUniv']==1,]['adv63'].dropna(), 0.99))
        df['trisk.B'] = np.minimum(df['trisk'], np.quantile(df.loc[df['isFitUniv']==1,]['trisk'].dropna(), 0.99))
        df['srisk.B'] = np.minimum(df['srisk'], np.quantile(df.loc[df['isFitUniv']==1,]['srisk'].dropna(), 0.99))
        df['date'] = sdate
        df = df[['skey', 'date', 'isFitUniv', 'avgSprd',  'close63', 'adv63','mv', 'srisk', 'trisk', 'close63.B', 'adv63.B','mv.B','srisk.B','trisk.B']]
        df = df.sort_values('skey')

        return df
