import subprocess
import ltspice
import pandas as pd

def get_test_name(change_elements): #change_elementsの例: {"L": "1.68u", "R": "5"}
    # テストネーム
    test_name = ""
    for element in change_elements.keys():
        val = change_elements[element]
        set_name = f"{element}={val}"
        test_name += set_name
    return test_name

def get_df_from_raw(raw_file, get_value):
    l = ltspice.Ltspice(raw_file)
    l.parse()
    time = l.get_time()
    value = l.get_data(get_value)
    df = pd.DataFrame({'t': time, get_value: value})
    return df


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
        # print(f"Run.: {cir_file}")

    # 回路シミュレーションの結果をpandasのdataframeの形式で取得し、リストに保存する
    def save_df(self, cir_file=None, get_value=None, df_name=None):
        if cir_file is None:
            cir_file = self.cir_file
        if get_value is None:
            get_value =self.get_value
        if df_name is None:
            df_name = cir_file

        df = self.get_df(cir_file, get_value)
        self.get_value = get_value
        # dfsの辞書型リストにget_valueのものがなかったら追加する
        if get_value not in self.dfs:
            self.dfs[get_value] = {}
        self.dfs[get_value][df_name] = df
        return df

    # 回路シミュレーションの結果をpandasのdataframeの形式で取得
    def get_df(self, cir_file=None, get_value=None):
        if cir_file is None:
            cir_file = self.cir_file
        if get_value is None:
            get_value =self.get_value
        return get_df_from_raw(f"{cir_file}.raw", get_value)

    # dataframeのリスト全てをplot表示する
    def plot_dfs(self, value=None):
        dfs = self.dfs
        if value is None:
            get_values = dfs.keys()
        else:
            get_values = [value]
        for get_value in get_values:
            for df_name in dfs[get_value].keys():
                dfs[get_value][df_name].plot(
                    x="t",
                    y=get_value,
                    title=df_name,
                    grid=True
                )

    # dataframeのデータのt(時間)に制限をかける
    def t_cut(self, start=None, end=None):
        dfs = self.dfs
        cutted = {}
        for get_value in dfs.keys():
            cutted[get_value] = {}
            for df_name in dfs[get_value].keys():
                df = dfs[get_value][df_name]
                if (start is not None and end is not None):
                    cutted[get_value][df_name] = df[(df.t >= start) & (df.t <= end)]
                elif start is not None:
                    cutted[get_value][df_name] = df[df.t >= start]
                elif end is not None:
                    cutted[get_value][df_name] = df[df.t <= end]
                else:
                    cutted[get_value][df_name] = df

        self.dfs = cutted
        return cutted

    # cirfileの素子値を変更してシミュレーションを実行する
    def change_element_run(self, change_elements):
        test_file = self.cir_file
        # テストネーム
        test_name = get_test_name(change_elements)

        # 書き込み用テキストデータ用意
        data_lines = ''
        # テスト元のcirファイルの読み込み
        f = open(test_file+".cir", encoding="UTF-16LE")

        # 全行走査→置換
        line = f.readline()
        while line:
            flag=0
            for element in change_elements.keys():
                if f".param {element}=" in line:
                    flag=1
                    val = change_elements[element]
                    data_lines += f".param {element}={val}\n"
            if flag!=1:
                data_lines+= line
            line = f.readline()

        # ファイル名で保存
        with open(test_file+f"_{test_name}.cir", mode="w", encoding="UTF-16LE") as f:
            f.write(data_lines)
        self.run(test_file+f"_{test_name}")

    #
    def change_element_df_save(self, change_elements, get_value=None):
        if get_value is None:
            get_value =self.get_value
        test_name=get_test_name(change_elements)
        file_name = self.cir_file+"_"+test_name
        self.save_df(cir_file=file_name, df_name = test_name, get_value=get_value)


    def get_W(self, I_name, V_name, cir_file=None, change_elements=None, df_name=None, t_cut_time=0.0049):
        if cir_file is None:
            cir_file = self.cir_file
        if change_elements is None:
            change_elements =self.get_value
        if df_name is None:
            test_name = get_test_name(change_elements)
            df_name = cir_file+f"_{test_name}"
        test_name = get_test_name(change_elements)
        file_name = cir_file+f"_{test_name}"
        self.save_df(file_name, I_name, test_name)
        self.save_df(file_name, V_name, test_name)
#         self.t_cut(t_cut_time)
        i_df = self.dfs[I_name][test_name]
        v_df = self.dfs[V_name][test_name]
        w_df = pd.merge(v_df, i_df)

        w_df['W'] = w_df[V_name]*w_df[I_name]

        return w_df.loc[:, ['t', 'W']]

