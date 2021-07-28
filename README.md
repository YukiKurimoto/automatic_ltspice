# auto_ltspice
LTspiceのバッチ処理や各種処理の自動化

# 使用方法
テストケースを設定するファイルを`test_case_files/test_case_sample`の形式で`~.json`という名前で作成する

ここではテストする.cirファイルの絶対パスとテストケースの辞書を設定する.

そしたらあとは.ipynbファイル等で`test_circuit_class.py`から`Test_circuit`クラスを呼び出して利用する. 各メソッドの内容はそこに記載されている.
