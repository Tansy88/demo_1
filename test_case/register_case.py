# -*- coding: utf-8 -*-
# @Time  : 2019/3/23 16:33
# @Author: Tansy_Xiaoming
# @Email : 279244228@qq.com
# @File  : register_case.py
import unittest
from ddt import ddt,data,unpack
import json
from class_0313_api_practice_4.common.do_excel import DoExcel
from class_0313_api_practice_4.common.my_log import MyLog
from class_0313_api_practice_4.common.http_request import HttpRequest
from class_0313_api_practice_4.common.check_database import CheckDB
from class_0313_api_practice_4.common.read_config import ReadConfig

wb = DoExcel('Register')    # 实例化一个excel对象
test_data = wb.read_all_data() # 读取注册的需要运行的全部用例
url = ReadConfig().get_str('TestData','URL') + '/member/register'  # 根绝配置文件定义的URL去调对应地址的注册接口


@ddt
class RegisterCase(unittest.TestCase):
    '''定义注册用例的逻辑'''
    def setUp(self):
        print('---------注册用例开始执行了----------')
        self.my_logger = MyLog()
        self.db = CheckDB(session='DBConnect_QA')

    def tearDown(self):
        print('----------注册用例执行结束了----------')

    @data(*test_data)
    @unpack
    def test_register(self,caseId,method,params,expectedResult,sql,**kwargs):
        if params.find('${mobile}') != -1:      # 如果语句中发现变量，则用Tel表格中电话号码去替换sql和params
            new_tel = DoExcel('Tel').read_one_data(2,2)
            while True:                 # 进行循环查询，直至查询到未注册手机号
                new_sql = sql.replace('${mobile}', str(new_tel))
                res = self.db.get_one_result(new_sql)  # 替换完成后去执行sql，查询此号码是否已被注册
                if res is None:        # 当结果为None时，表示电话号码未被注册
                    params = params.replace('${mobile}',str(new_tel))  # 未被注册时就将手机号替换到参数中
                    DoExcel('Tel').update_excel(2,2,new_tel+1)   # 同时将数据加1写回文件中并跳出循环
                    break
                else:
                    new_tel += 1  # 当查询到数据已经被注册后，就将数据加1并继续循环
        self.my_logger.info_log('正在执行第{}条注册用例，参数为{}'.format(caseId,params))
        actual_result = HttpRequest().send_request(url=url,method=method,params=eval(params)).json() # 去发起http请求
        actual_result.pop('data') # 注册用例中，data数据无意义，可以不进行比较
        try:
            self.assertDictEqual(actual_result,eval(expectedResult))  # 将实际结果与期望结果进行对比
            if sql is not None:          # 断言成功后检查是否有sql需要查询
                res = self.db.get_one_result(sql.replace('${mobile}', str(new_tel))) # 查询数据库，此手机号是否已注册
                try:
                    self.assertEqual(len(res),1)    # 比较是否已查询到此注册账号
                    test_result = 'Pass'         # 查询到结果为Pass
                    self.my_logger.info_log('{}已注册并保存到数据库中'.format(new_tel))
                except Exception as e:
                    test_result = 'Fail'    # 未查询到结果为Fail
                    self.my_logger.error_log('接口返回正确，但数据未插入数据库中')
                    raise e
            else:
                test_result = 'Pass'   # 不需要查询数据库时，结果直接为Pass
        except Exception as e:     # 断言比较错误时，直接不进行数据库查询,直接Fail
            test_result = 'Fail'
            self.my_logger.error_log('接口返回不一致，错误为{}'.format(e))
            raise e
        finally:
            actual_result = json.dumps(actual_result,ensure_ascii=False) # 将响应转换为字符串格式
            wb.update_excel(int(caseId)+1,7,actual_result)
            wb.update_excel(int(caseId)+1,8,test_result)  # 将结果写回excel中


if __name__ == '__main__':
    unittest.main()



