# -*- coding: utf-8 -*-
# @Time  : 2019/3/25 9:41
# @Author: Tansy_Xiaoming
# @Email : 279244228@qq.com
# @File  : login_case.py
import unittest
from ddt import ddt,data,unpack
import json
# from class_0313_api_practice_4.common import *
from class_0313_api_practice_4.common.do_excel import DoExcel
from class_0313_api_practice_4.common.my_log import MyLog
from class_0313_api_practice_4.common.http_request import HttpRequest
from class_0313_api_practice_4.common.check_database import CheckDB
from class_0313_api_practice_4.common.read_config import ReadConfig

wb = DoExcel('Login')
test_data = wb.read_all_data()
url = ReadConfig().get_str('TestData','URL') + '/member/login'


@ddt
class LoginCase(unittest.TestCase):
    '''定义登录用例的逻辑'''
    def setUp(self):
        self.my_logger = MyLog()
        self.my_logger.info_log('-------登录用例开始执行了-------')
        print('-----------登录用例开始执行了-----------')

    def tearDown(self):
        # self.my_logger = MyLog()
        self.my_logger.info_log('--------登录用例执行结束了--------')
        print('-----------登录用例执行结束了-----------')

    @data(*test_data)
    @unpack
    def test_login(self,caseId,method,params,expectedResult,**kwargs):
        if params.find('${mobile}') != -1:
            register_tel = DoExcel('Tel').read_one_data(3,2)
            register_pwd = DoExcel('Tel').read_one_data(3,3)
            params = params.replace('${mobile}',str(register_tel)).replace('${pwd}',register_pwd)
        self.my_logger.info_log('正在执行第{}条用例，参数为{}'.format(caseId,params))
        actual_result = HttpRequest().send_request(url=url,params=eval(params),method=method).json()
        actual_result.pop('data')
        try:
            self.assertDictEqual(actual_result,eval(expectedResult))
            test_result = 'Pass'
        except Exception as e:
            self.my_logger.error_log('实际结果与期望结果一致，错误为{}'.format(e))
            test_result = 'Fail'
            raise e
        finally:
            actual_result = json.dumps(actual_result, ensure_ascii=False)  # 将响应转换为字符串格式
            wb.update_excel(int(caseId) + 1, 7, actual_result)
            wb.update_excel(int(caseId) + 1, 8, test_result)  # 将结果写回excel中


if __name__ == '__main__':
    unittest.main()