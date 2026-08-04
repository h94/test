from TCZB import  Globals
from ddt import data,unpack,ddt
from inspect import isgeneratorfunction
import unittest
import traceback
import AppSettings
import DataTransformer
import Merge
import Compair


class logger(object):
    def PostLog(self, _, msg):print(msg)
class send_msg(object):
    def send_msg(self, level = "Error", msg = ""):print(traceback.format_exc())

Globals.Globals.CrawlerData = AppSettings.settings
logger = logger()
send_msg = send_msg().send_msg


#=======================================除了import,以上不動=======================================
#初始化要測的.py
transformer_test = DataTransformer.DataTransformer(send_msg)
compair_test = Compair.Compair(send_msg)
Merge_test = Merge.Merge(send_msg)

@ddt
class CalculatorTestCase(unittest.TestCase):
    # @data(  #return多個結果,若return無使用[],則預設為tuple->()
    #     [4, 2, (8, 2.0)],
    #     [5, 0, "err"],
    #     )
    # def test_ut2(self, data_list):
    #     self.get_test_result(transformer_test.ut2, data_list)


    # @data(  #yield單一結果,結果請用list包裝起來(就算只有一個結果), [first_result, second_result,.....]
    #     [1, [0]],
    #     [5, [0, 1, 2, 3, "err"]]
    #     )
    # def test_ut3(self, data_list):
    #     self.get_test_result(transformer_test.ut3, data_list)


    # @data(   #yield多個結果,結果請用list包裝起來(就算只有一個結果), [[first_result1, first_result2], [second_result1, second_result2]...]
    #          #注意yield是否用list包起,若否->[(first_result1, first_result2), (second_result1, second_result2)...]
    #     [1, [[0, 1]]],
    #     [2, [[0, 1], [1, 2]]],
    #     [4, [[0, 1], [1, 2], [2, 3], "err"]],
    #     )
    # def test_ut4(self, data_list):
    #     self.get_test_result(transformer_test.ut4, data_list)


    # @data(  #可使用Appsettin的參數,.py裡要設定正確
    #     ["ut", "utOK"],
    #     )
    # def test_ut5(self, data_list):
    #     self.get_test_result(transformer_test.ut5, data_list)


    # @data(  #函式可使用多個預設值, 但預設值的部分要特別寫出->{"kwargs":{your parameter}}
    #     [1, 2, 13],  #1+2+預設10=13
    #     [1, 2, {"kwargs":{"square":True}} , 169], #1+2+預設10=13 再平方=169
    #     [1, 2, {"kwargs":{"x10":True}} , 130], #1+2+預設10=13 再x10 = 130
    #     [1, 2, {"kwargs":{"z":50,"x10":True}} , 530], #1+2+預設更動50=53 再X10 = 530
    #     [1, 2, {"kwargs":{"square":True,"x10":True}} , 1690], #1+2+預設10=13 再平方=169 再X10 = 1690
    #     )
    # def test_ut6(self, data_list):
    #     self.get_test_result(transformer_test.ut6, data_list)


    #參數太長可以先抽到data上面
    cache1 = merge1 = {'HA': {'1+50': {'H': '6.9', 'A': '1.07'}}}
    match1 = {'HA': {'1+50': {'H': '7.0', 'A': '1.07'}}}
    merge1 = {'HA': {'1+50': {'H': '6.9', 'A': '1.07'}}}
    ans1 = {'HA': {'1+50': {'H': '7.0', 'A': '1.07'}}}

    cache2 = merge2 = {'HA':{'1-50':{'H':'5.0','A':'1.2'}}}
    match2 = {'HA':{'2+50':{'H':'4.0','A':'1.1'}}}
    ans2 = {'HA':{'2+50':{'H':'4.0','A':'1.1'}}}

    cache3 = merge3 = {'HA':{'1X2':{'H':'6.9','A':'1.07'},'1-50':{'H':'5.0','A':'1.2'}}}
    match3 = {'HA':{'1X2':{'H':'6.9','A':'1.08'},'2+50':{'H':'4.0','A':'1.1'}}}
    ans3 = {'HA':{'1X2':{'H':'6.9','A':'1.08'},'2+50':{'H':'4.0','A':'1.1'}}}

    cache4 = merge4 = {'HA':{'1+50':{'H':'6.9','A':'1.07'},'1-50':{'H':'5.0','A':'1.2'}}}
    match4 = {'HA':{'1+50':{'H':'6.9','A':'1.07'},'2+50':{'H':'4.0','A':'1.1'}}}
    ans4 = {'HA':{'1+50':{'H':'6.9','A':'1.07'},'1-50':{'H':'-1','A':'-1'},'2+50':{'H':'4.0','A':'1.1'}}}

    cache5 = merge5 = {'HA': {'1+50': {'H': '2.1', 'A': '1.02'}, '1-50': {'H': '1.03', 'A': '2.5'}}, 'OU': {'1': {'O': '2.1', 'U': '1.1'}}}
    match5 = {'OU': {'2': {'O': '2.1', 'U': '1.1'}}}
    ans5 = {'HA': {'1+50': {'H': '-1', 'A': '-1'}, '1-50': {'H': '-1', 'A': '-1'}}, 'OU': {'2': {'O': '2.1', 'U': '1.1'}}}

    cache6 = merge6 = {'HA': {'1+50': {'H': '6.9', 'A': '1.07'}, '1-50': {'H': '2.9', 'A': '0.07'}}, 'OU': {'1': {'O': '2.1', 'U': '1.1'}}}
    match6 = {}
    ans6 = {'HA': {'1+50': {'H': '-1', 'A': '-1'}, '1-50': {'H': '-1', 'A': '-1'}}, 'OU': {'1': {'O': '-1', 'U': '-1'}}}
    @data(
        [cache1,match1,merge1,ans1],
        [cache2,match2,merge2,ans2],
        [cache3,match3,merge3,ans3],
        [cache4,match4,merge4,ans4],
        [cache5,match5,merge5,ans5],
        [cache6,match6,merge6,ans6],
        )
    def test_compair_odd(self, data_list):
        self.get_test_result(compair_test.get_new_odd, data_list)

    @data(
        [{'RBHA': {'4': {'H': '0.5', 'A': '0.6'}}}, {'RBHA': {'4': {'H': '-1', 'A': '-1'}, '3': {'H': '0.5', 'A': '0.6'}}}, {'RBHA': {'4': {'H': '-1', 'A': '-1'}, '3': {'H': '0.5', 'A': '0.6'}}}],
        [{'RBHA': {'2': {'H': '2.5', 'A': '2.6'}}}, {'RBHA': {'4': {'H': '-1', 'A': '-1'}, '3': {'H': '3.5', 'A': '3.6'}}},  {'RBHA': {'2': {'H': '2.5', 'A': '2.6'}, '4': {'H': '-1', 'A': '-1'}, '3': {'H': '3.5', 'A': '3.6'}}}],
        )
    def test_update_odds(self, data_list):
        self.get_test_result(Merge_test.update_odds, data_list)

    @data(
        [{'OU': {'10.5': {'O': '0.5', 'U': '0.8', 'O-Spread': '10.5'}, '7.5': {'O': '-1', 'U': '-1', 'O-Spread': '7.5'}}, 'Others-Correct Score': {'3-0': {'Value': '-1','O-Spread': '3-1'}}}, {'OU': {'10.5': {'O': '0.5', 'U': '0.8', 'O-Spread': '10.5'}}}],
        )
    def test_remove_close(self, data_list):
        self.get_test_result(Merge_test.remove_close, data_list)

#=======================================以下不動=======================================
    def get_test_result(self, function, data_list):
        if any(["kwargs" in data for data in data_list if type(data) == dict]):
            *args, kwargs, expected = data_list
            kwargs = kwargs["kwargs"]
        else:
            *args, expected = data_list
            kwargs = {}
        if isgeneratorfunction(function):
            results = list(function(*args, **kwargs))
        else:
            results = function(*args, **kwargs)
        if results == None:
            self.assertEqual(expected, args[0])
        else:
            self.assertEqual(expected, results)
unittest.main(verbosity=2)
