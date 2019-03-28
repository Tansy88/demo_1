# -*- coding: utf-8 -*-
# @Time  : 2019/3/23 17:57
# @Author: Tansy_Xiaoming
# @Email : 279244228@qq.com
# @File  : common_data.py


class CommonData:
    '''存放公共参数'''
    start_leave_amount = None
    end_leave_amount = None
    cookie = None


if __name__ == '__main__':
    # setattr(CommonData,'end_leave_amount','123456')
    print(CommonData.end_leave_amount)