import subprocess
import ltspice
import pandas as pd


## 回路クラス
class Circuit:
    def __init__(self, cir_file):

        self.cir_file = cir_file # テストファイルのパス
        self.get_value = "V(test)" # 取得する値
        self.dfs = {}

    # 回路シミュレーションの実行
    def run(self, cir_file=None):
        if cir_file is None:
            cir_file = self.cir_file
        subprocess.call(["/Applications/LTspice.app/Contents/MacOS/LTspice", "-b", f"{cir_file}.cir"])
        print(f"Run.: {cir_file}")

    # 回路シミュレーションの結果をpandasのdataframeの形式で取得し、リストに保存する
    def get_df(self, cir_file=None, get_value=None, df_name=None):
        if cir_file is None:
            cir_file = self.cir_file
        if get_value is None:
            get_value =self.get_value
        if df_name is None:
            df_name = self.cir_file

        l = ltspice.Ltspice(f"{cir_file}.raw")
        l.parse()

        time = l.get_time()
        value = l.get_data(get_value)
        df = pd.DataFrame({'t': time, get_value: value})
        self.get_value = get_value
        self.dfs[df_name] = df
        return df

    # dataframeのリスト全てをplot表示する
    def plot_dfs(self):
        dfs = self.dfs
        get_value = self.get_value
        for df_key in dfs.keys():
            dfs[df_key].plot(
                x="t",
                y=get_value,
                title=df_key,
                grid=True
            )

    # dataframeのデータのt(時間)に制限をかける
    def t_cut(self, start=None, end=None):
        dfs = self.dfs
        cutted = {}
        for df_key in dfs.keys():
            df = dfs[df_key]
            if (start is not None and end is not None):
                cutted[df_key] = df[(df.t >= start) & (df.t <= end)]
            elif start is not None:
                cutted[df_key] = df[df.t >= start]
            elif end is not None:
                cutted[df_key] = df[df.t <= end]
            else:
                cutted[df_key] = df

        self.dfs = cutted
        return cutted
