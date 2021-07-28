import json
from circuit_class import Circuit
import subprocess
import ltspice
import pandas as pd
import functools
import test_process

## テスト回路クラス
class Test_circuit(Circuit):
    def __init__(self, file_path):
        test_json = json.load(open(file_path, 'r'))
        super().__init__(test_json['test_file'])
        self.test_cases = test_process.convert_test_cases(file_path) # テストケース辞書


    ################################
    # UTils
    ################################

    # 各テストケースでfuncを実行する
    def loop_test(self, func):
        test_cases = self.test_cases
        for test_case in test_cases:
            func(test_case)

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
    def create_test(self, test_case):
        test_file = self.cir_file
        # テストネーム
        test_name = ""

        # 書き込み用テキストデータ用意
        data_lines = ''
        # テスト元のcirファイルの読み込み
        f = open(test_file+".cir", encoding="UTF-16LE")

        for element in test_case.keys():
            set_name = f"{element}={test_case[element]}"
            test_name += set_name
        # 全行走査→置換
        line = f.readline()
        while line:
            flag=0
            for element in test_case.keys():
                if f".param {element}=" in line:
                    flag=1
                    data_lines += f".param {element}={test_case[element]}\n"
            if flag!=1:
                data_lines+= line
            line = f.readline()

        # ファイル名で保存
        with open(test_file+f"_{test_name}.cir", mode="w", encoding="UTF-16LE") as f:
            f.write(data_lines)

    # テストケースのcirファイルを実行する
    def run_test(self, test_case):
        test_file = self.cir_file
        # テストネーム
        test_name = ''
        for element in test_case.keys():
            set_name = f"{element}={test_case[element]}"
            test_name += set_name
        cir_file = f"{test_file}_{test_name}"
        self.run(cir_file)

    def get_df_test(self, test_case):
        test_file = self.cir_file
        # テストネーム
        test_name = ''
        for element in test_case.keys():
            set_name = f"{element}={test_case[element]}"
            test_name += set_name
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
