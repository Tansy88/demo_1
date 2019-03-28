# -*- coding: utf-8 -*-
# @Time  : 2019/3/25 15:10
# @Author: Tansy_Xiaoming
# @Email : 279244228@qq.com
# @File  : recharge_case.py
import unittest
from ddt import ddt,data,unpack
import json
from class_0313_api_practice_4.common.do_excel import DoExcel
from class_0313_api_practice_4.common.my_log import MyLog
from class_0313_api_practice_4.common.http_request import HttpRequest
from class_0313_api_practice_4.common.check_database import CheckDB
from class_0313_api_practice_4.common.read_config import ReadConfig
from class_0313_api_practice_4.common.common_data import CommonData

wb = DoExcel('Recharge')
test_data = wb.read_all_data()
url = ReadConfig().get_str('TestData','URL') + '/member/recharge'
login_url = ReadConfig().get_str('TestData','URL') + '/member/login'


@ddt
class RechargeCase(unittest.TestCase):
    '''实现充值的用例逻辑'''
    def setUp(self):
        self.my_logger = MyLog()
        self.db = CheckDB(session='DBConnect_QA')
        self.my_logger.info_log('---------充值用例开始执行----------')

    def tearDown(self):
        self.my_logger.info_log('-----------充值用例执行结束---------')

    @data(*test_data)
    @unpack
    def test_recharge(self,caseId,method,params,expectedResult,sql,**kwargs):
        register_tel = DoExcel('Tel').read_one_data(3, 2)  # 从excel中将已注册的手机号及密码取出来
        register_pwd = DoExcel('Tel').read_one_data(3, 3)
        cookie = HttpRequest().send_request(url=login_url, method='get',params={'mobilephone': register_tel,
                                            'pwd': register_pwd}).cookies      # 使用已注册的手机号调取登录接口并获取cookie
        setattr(CommonData, 'cookie', cookie)  # 将cookie存入全局变量
        if params.find('${mobile}') != -1:  # 如果在参数中发现mobile变量，则用已注册手机号替换
            params = params.replace('${mobile}',str(register_tel))
        self.my_logger.info_log('第{}条充值用例正在执行中，请求参数为{}'.format(caseId,params))
        actual_result = HttpRequest().send_request(url=url,method=method,
                                                   params=eval(params),cookies=CommonData.cookie).json() # 发送请求并获取响应正文
        if sql is not None:         # 如果有sql的话，就去查询sql并将结果写入全局变量中
            sql = sql.replace('${mobile}',str(register_tel))
            leave_amount = self.db.get_one_result(sql)[0]
            setattr(CommonData, 'end_leave_amount', leave_amount)
            self.my_logger.debug_log('充值后的金额为{}'.format(leave_amount))
            if expectedResult.find('${leaveamount}') != -1:   # 如果期望结果中有参数的话，用查询结果代替
                expectedResult = expectedResult.replace('${leaveamount}',str(leave_amount))
        else:
            actual_result.pop('data')    # 如果没有需要替代的数据，则把data去掉不进行比较
        expectedResult = eval(expectedResult) # 将期望结果转换为字典格式，以便于比较
        try:
            self.assertDictEqual(actual_result,expectedResult)
            test_result = 'Pass'
        except Exception as e:
            test_result = 'Fail'
            self.my_logger.error_log('期望结果与实际结果不一致，错误为{}'.format(e))
            raise e
        finally:
            actual_result = json.dumps(actual_result, ensure_ascii=False)  # 将响应转换为字符串格式
            wb.update_excel(int(caseId) + 1, 7, actual_result)
            wb.update_excel(int(caseId) + 1, 8, test_result)  # 将结果写回excel中


if __name__ == '__main__':
    unittest.main()


