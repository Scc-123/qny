import pandas as pd
import numpy as np

class BranchMerge(object):
    def __init__(self, df_months):
        self.df_months = df_months
    def insert_branch_id(self,df_current):
        df_current['device_code'] = df_current['device_code'].apply(str)
        df_current['branch_no'] = df_current['branch_no'].apply(str)
        df_current.insert(loc=len(df_current.columns), column='branch_id', value=df_current['device_code'])
        index4 = df_current.index[df_current['branch_id'].str.len() > 0]
        df_current.loc[index4, ['branch_id']] = df_current.loc[index4, ['branch_id']] + '-'
        df_current.loc[index4, 'branch_id'] = df_current['branch_id'].str.cat(df_current['branch_no'])
        # 加入一列，组串名字
        return df_current
    def df_cvr_merge_zc(self):
        dfcvr_list = []
        for cvr in self.df_months:
            df_c = cvr['dfc']
            df_c = self.insert_branch_id(df_c)
            df_v = cvr['dfv']
            df_v = self.insert_branch_id(df_v)
            df_r = cvr['dfr']
            df_cv = df_c.merge(df_v, on=['time', 'branch_id'], how='left')

            df_cvr= df_cv.merge(df_r, on=['time'], how='left')
            # print(df_cvr.shape)
            n = df_cvr.columns.shape[0]-1
            df_cvr['radiance'] = df_cvr[df_cvr.columns[n]]#归一化辐照度的列名，方便多天concat
            df_cvr.drop(df_cvr.columns[n], axis=1, inplace=True)  # 删除一列
            df_cvr.head()
            dfcvr_list.append(df_cvr)
        df_cvrm = pd.DataFrame()
        for i in range(0,len(dfcvr_list)):
            if i ==0:
                df_cvrm = dfcvr_list[i]
            else:
                df = dfcvr_list[i]
                df_cvrm =pd.concat([df_cvrm , df],)
        return df_cvrm

    def df_cvr_merge_jz(self):
        dfcvr_list = []
        for cvr in self.df_months:
            df_c = cvr['dfc']
            df_c = self.insert_branch_id(df_c)
            df_v = cvr['dfv']
            df_v = pd.melt(df_v, id_vars=["time"], var_name="device_code", value_name="current")
            df_r = cvr['dfr']
            df_cv = df_c.merge(df_v, on=['time', 'device_code'], how='left')
            df_cvr= df_cv.merge(df_r, on=['time'], how='left')
            n = df_cvr.columns.shape[0]-1
            df_cvr['radiance'] = df_cvr[df_cvr.columns[n]]#归一化辐照度的列名，方便多天concat
            df_cvr.drop(df_cvr.columns[n], axis=1, inplace=True)  # 删除一列
            df_cvr.head()
            dfcvr_list.append(df_cvr)
        df_cvrm = pd.DataFrame()
        for i in range(0,len(dfcvr_list)):
            if i ==0:
                df_cvrm = dfcvr_list[i]
            else:
                df = dfcvr_list[i]
                df_cvrm =pd.concat([df_cvrm , df],)

        return df_cvrm








