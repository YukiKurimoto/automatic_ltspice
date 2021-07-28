import json

def convert_test_cases(test_file_path):
    test_json = json.load(open(test_file_path, 'r'))
    if test_json['test_case']['type'] == 'cross':
        return convert_cross_test(test_json['test_case']['data'])
    elif test_json['test_case']['type'] == 'set':
        return convert_set_test(test_json['test_case']['data'])
    else:
        raise Exception('Error: 適切なtestタイプを指定してください。')

def for_test_data(test_data, test_cases, now_count, count_list):
    if (len(test_data)-1) != now_count:
        for i in range(len(test_data[now_count]['val'])):
            count_list[now_count] = i
            for_test_data(test_data, test_cases, now_count+1, count_list)
    else:
        for i in range(len(test_data[now_count]['val'])):
            temp = {}
            for k in range(len(test_data)-1):
                temp[test_data[k]['element']] = str(test_data[k]['val'][count_list[k]])+test_data[k]['order']
            temp[test_data[now_count]['element']] = str(test_data[now_count-1]['val'][i])+test_data[now_count]['order']
            test_cases.append(temp)

def convert_cross_test(test_data):
    test_cases = []
    for_test_data(test_data, test_cases, 0, [0]*(len(test_data)-1))
    return test_cases

def convert_set_test(test_data):
    len_list = list(map(lambda x: len(x['val']), test_data))
    if (len(list(set(len_list))) != 1):
        raise Exception('Error: テストケースの数が不正です。')
    else:
        test_cases = []
        for i in range(len(test_data[0]['val'])):
            temp = {}
            for element in test_data:
                temp[element['element']]=str(element['val'][i])+element['order']
            test_cases.append(temp)
        return test_cases

def convert_val(order, val):
    return val*(10**SI_order_dict[order])

SI_order_dict = {
    "": 0,
    "T": 12,
    "G": 9,
    "Meg": 6,
    "k": 3,
    "m": -3,
    "u": -6,
    "n": -9,
    "p": -12,
    "f": -15
}
