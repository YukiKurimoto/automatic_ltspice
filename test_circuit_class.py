from circuit_class import Circuit
import subprocess
import ltspice
import pandas as pd
import functools

## テスト回路クラス
class Test_circuit(Circuit):
    def __init__(self, test_file, test_cases):
        super().__init__(test_file)
        self.test_cases = test_cases # テストケース辞書


    ################################
    # UTils
    ################################

    # 各テストケースでfuncを実行する
    def loop_test(self, func):
        test_cases = self.test_cases
        test_file = self.cir_file
        for test_key in test_cases.keys():
            # テストするパラメータの値を取得
            for test_value in test_cases[test_key]:
                func(test_file, test_key, test_value)

    # テスト名のリストを取得する
    def get_test_names(self):
        return self.dfs.keys()

    # テスト名からdfを取得する
    def get_df_by_test_name(self, test_name):
        return self.dfs[test_name]


    ################################
    # 基本関数(loopに入れる用)
    ################################

    # .cirファイル(回路のNetlist)からテストケースごとのcirファイルを作成する
    # 新cirファイルの作成先は元のcirファイルと同じディレクトリ
    def create_test(self, test_file, test_key, test_value):
        # テストネーム
        test_name = f"{test_key}={test_value}"

        # 書き込み用テキストデータ用意
        data_lines = ''
        # テスト元のcirファイルの読み込み
        f = open(test_file+".cir", encoding="UTF-16LE")

        # 全行走査→置換
        line = f.readline()
        while line:
            if f".param {test_key}=" in line:
                data_lines += f".param {test_name}\n"
            else:
                data_lines+= line
            line = f.readline()

        # ファイル名で保存
        with open(test_file+f"_{test_name}.cir", mode="w", encoding="UTF-16LE") as f:
            f.write(data_lines)

    # テストケースのcirファイルを実行する
    def run_test(self, test_file, test_key, test_value):
        # テストネーム
        test_name = f"{test_key}={test_value}"
        cir_file = f"{test_file}_{test_name}"
        self.run(cir_file)

    def get_df_test(self, test_file, test_key, test_value):
        # テストネーム
        test_name = f"{test_key}={test_value}"
        cir_file = f"{test_file}_{test_name}"
        self.get_df(cir_file=cir_file, df_name=test_name)


    ################################
    # Batch関数
    ################################

    # 全てのテストcirファイルを作成する
    def create_all_tests(self):
        self.loop_test(self.create_test)

    # 全てのテストcirファイルを実行する
    def run_all_tests(self):
        self.create_all_tests()
        self.loop_test(self.run_test)

    # テスト結果からdataframeのリストを取得する
    def get_dfs(self, get_value=None):
        self.dfs = {}
        if get_value is not None:
            self.get_value = get_value
        self.loop_test(self.get_df_test)
        return self.dfs
