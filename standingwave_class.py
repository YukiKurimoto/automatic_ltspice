from circuit_class import Circuit
import numpy as np

def get_peaks(get_value, df):
    # df['diff_sign']は微分係数の符号
    df['diff_sign'] = np.sign(df[get_value].diff()/df['t'].diff())
    # 山の部分だけ抽出
    df_peak = df[(df['diff_sign']<0) & (df['diff_sign'].diff()<0) | (df['diff_sign']==0)]
    return df_peak


# 整定後波形解析
class Standingwave(Circuit):
    def __init__(self, file_path):
        super().__init__(file_path)

    # 指定した減衰率の閾値(atte_limit)より振幅の変化が一定回数(standing_judge_count)下回った以降のデータをカットする
    def cut_standingwave(self, atte_limit, standing_judge_count=50):
        dfs = self.dfs
        cutted = {}
        for get_value in dfs.keys():
            cutted[get_value] = {}
            for df_name in dfs[get_value]:
                df = dfs[get_value][df_name]
                df_peak = get_peaks(get_value, df)
                df_peak.loc[:,'under_atte'] = ((df_peak.loc[:,get_value].pct_change()>(-1.0*atte_limit))&(df_peak.loc[:,get_value].pct_change()<atte_limit))
                cut_t = df_peak['t'].min()
                under_count = 0
                for row in df_peak.itertuples():
                    if(row.under_atte==True):
                        under_count+=1
                    else:
                        under_count = 0
                    if under_count > standing_judge_count:
                        cut_t = row.t
                        break
                cutted[get_value][df_name] = df[cut_t<df.t]
        self.dfs = cutted
        return cutted

    # dfs内の各データに関して、振幅の平均値を取得する
    def get_amp_means(self):
        dfs = self.dfs
        amp_dict = {}
        for get_value in dfs.keys():
            amp_dict[get_value] = {}
            for df_name in dfs[get_value].keys():
                peaks = get_peaks(get_value, dfs[get_value][df_name])
                amp_dict[get_value][df_name] = peaks[get_value].mean()
        return amp_dict

    # 減衰率が閾値(atte_limit)より下回り十分振幅が一定になった後の振幅の平均リストを取得
    def get_standing_amps(self, atte_limit, standing_judge_count=50):
        self.cut_standingwave(atte_limit, standing_judge_count)
        return self.get_amp_means()
