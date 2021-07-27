from test_circuit_class import Test_circuit

def main():
    import test_case_files.test_parallel as test_config1
    # テストするファイルパス取得
    test1 = Test_circuit(test_config1.test_file, test_config1.test_case)
    test1.run_all_tests()
    df_list=test1.get_df_list()
    print(df_list)
    print("Done")


if __name__ == "__main__":
    main()
