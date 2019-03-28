# -*- coding: utf-8 -*-
# @Time  : 2019/3/26 10:32
# @Author: Tansy_Xiaoming
# @Email : 279244228@qq.com
# @File  : bidloan_case.py
import unittest
from ddt import ddt,data,unpack
import json
from class_0313_api_practice_4.common.do_excel import DoExcel
from class_0313_api_practice_4.common.my_log import MyLog
from class_0313_api_practice_4.common.http_request import HttpRequest
from class_0313_api_practice_4.common.check_database import CheckDB
from class_0313_api_practice_4.common.read_config import ReadConfig
from class_0313_api_practice_4.common.common_data import CommonData

wb = DoExcel('BidLoan')
test_data = wb.read_all_data()
url = ReadConfig().get_str('TestData','URL') + '/member/bidLoan'
login_url = ReadConfig().get_str('TestData','URL') + '/member/login'


@ddt
class BidLoanCase(unittest.TestCase):
    '''定义投资的用例实现'''
    def setUp(self):
        self.my_logger = MyLog()
        self.db = CheckDB(session='DBConnect_QA')
        self.my_logger.info_log('---------投资用例开始执行----------')

    def tearDown(self):
        self.my_logger.info_log('---------投资用例结束执行-----------')

    @data(*test_data)
    @unpack
    def test_bidloan(self,caseId,method,params,expectedResult,sql,**kwargs):
        register_tel = DoExcel('Tel').read_one_data(3,2)
        register_pwd = DoExcel('Tel').read_one_data(3,3)
        # register_memberid = DoExcel('Tel').read_one_data(3,4) # 从excel中读出已注册的手机号和密码作为投资人
        cookie = HttpRequest().send_request(url=login_url, method='get',
                                            params={'mobilephone': register_tel, 'pwd': register_pwd}).cookies
        setattr(CommonData, 'cookie', cookie)  # 将cookie存入全局变量
        if sql is not None and sql.find('${mobile}') != -1:   # 如果sql存在的话，就去查数据库并进行替换
            sql = eval(sql)               # 将sql从字符串还原到字典格式
            loanid = self.db.get_one_result(sql['sql_1'])[0]  # 字典中sql_1对应的是loanid的查询语句
            sql_2 = sql['sql_2'].replace('${mobile}',str(register_tel))  # 先对sql_2的手机号进行替换，再去查询
            memberid = self.db.get_one_result(sql_2)[0]     # 获取当前登录账号的memberId
            before_amount = self.db.get_one_result(sql_2)[1]  # 获取当前登录账号的起始余额
            params = params.replace('${loanId}',str(loanid))\
                .replace('${memberId}',str(memberid)).replace('${pwd}',register_pwd)  # 将请求参数中的变量进行替换
            actual_result = HttpRequest().send_request(url=url,method=method,params=eval(params),cookies=cookie).json()
            expected_amount = before_amount - eval(params)['amount']
            after_amount = self.db.get_one_result(sql_2)[1]
            try:
                self.assertEqual(after_amount,expected_amount)
                self.my_logger.debug_log('投资前金额为{}，投资后期望金额为{}，投资后实际金额为{}'.format(before_amount,expected_amount,after_amount))
            except Exception as e:
                self.my_logger.error_log('充值后，期望余额和数据库中余额不一致，期望余额为{}，实际余额为{},错误为{}'.format(expected_amount,after_amount,e))
                raise e
        else:
            actual_result = HttpRequest().send_request(url=url, method=method, params=eval(params),
                                                       cookies=cookie).json()
        actual_result.pop('data')
        try:
            self.assertDictEqual(actual_result,eval(expectedResult))
            self.my_logger.info_log('实际结果与期望结果一致')
            test_result = 'Pass'
        except Exception as e:
            self.my_logger.error_log('实际结果与期望结果不一致，错误为{}'.format(e))
            test_result = 'Fail'
            raise e
        finally:
            actual_result = json.dumps(actual_result,ensure_ascii=False)
            wb.update_excel(int(caseId)+1,7,actual_result)
            wb.update_excel(int(caseId)+1,8,test_result)


if __name__ == '__main__':
    unittest.main()



