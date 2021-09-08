# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:interestingcn01(interestingcn01@gmail.com)

import json,configparser,time,requests,sys,os,re
from bs4 import BeautifulSoup

def welcome():
    msg = '''
============================================================
 _____ _____ _____       _____ _____ _____ 
|   __|  |  |   __|     |  _  |   __|  _  | SKE-PSA Agent
|__   |    -|   __|     |   __|__   |     |  Version：21.9.7
|_____|__|__|_____|_____|__|  |_____|__|__|  

============================================================                                    
    '''
    print(msg)

def getConfig(category,value):
    config = configparser.ConfigParser()
    try:
        config.read("config.ini", encoding="utf-8-sig")
        return config.get(category, value)
    except:
        print('检查config.ini配置文件是否存在以及是否有权限访问！')
        sys.exit()

# 预备环境文件检测
def checkEnv():
    debugInfo('创建预备环境')
    if os.path.exists(getConfig('SYSTEM','dataPath')):
        pass
    else:
        os.makedirs(getConfig('SYSTEM','dataPath'))


# 用于提取页面中CSRF信息
def get_CSRF(text):
    csrf = {}
    bs = BeautifulSoup(text, 'lxml')
    # 将隐藏域内容写入表单
    hidden = bs.find_all(type='hidden')
    for i in hidden:
        bs2 = BeautifulSoup(str(i), 'lxml')
        csrf[bs2.input['id']] = bs2.input['value']
    return csrf


def displayMsg(text):
    timenow = time.asctime(time.localtime(time.time()))
    msg = f'{timenow} - {str(text)} '
    print(msg)

def debugInfo(text):
    timenow = time.asctime(time.localtime(time.time()))
    msg = f'{timenow} - [DEBUG] -{str(text)} '
    if getConfig('SYSTEM','debug') == '1':
        print(msg)

    # 登录操作
def getLoginCookies():
    headers = {"User-Agent": "WFUST-LIB SKE-PSA 21.9.7"}
    session = requests.session()
    TargetUrl = getConfig('SKESERVER','address')+'InLibraryReaderInfo.aspx'
    resp = session.get(TargetUrl,headers=headers)
    form_data = get_CSRF(resp.text)
    form_data['Textbox_name1'] = getConfig('SKESERVER','username')
    form_data['TextBox_password'] = getConfig('SKESERVER','password')
    form_data['Button1'] = '确认'
    # 登陆验证操作
    ValidateUrl = getConfig('SKESERVER', 'address') + 'Validate.aspx'

    attempts = 0
    success = False

    while attempts <= 20 and not success:
        try:
            vaild = session.post(ValidateUrl, form_data, headers=headers)
            success = True
        except:
            attempts += 1
            time.sleep(2)
            if attempts >= 20:
                return False

    if checkLoginStatus(vaild) == 1:
        displayMsg('登陆成功')
        # 注意此处获取cookies为服务器下发cookies时的请求而非任意请求
        cookies = resp.cookies
        return requests.utils.dict_from_cookiejar(cookies)
    else:
        displayMsg('登陆失败')
        input('按回车键退出程序（Enter）')
        exit()

# 检查登录状态
def checkLoginStatus(context):
    bs = BeautifulSoup(context.text, 'lxml')
    res = bs.find_all(text='请输入用户名和密码进行认证')
    if len(res) == 0:
        return 1
    else:
        return 0

def freeTime():
    # 非工作时段清空在场数据库信息
    nowHour = time.strftime("%H", time.localtime())
    if int(nowHour) < int(getConfig('SCAN','freetime')):
        displayMsg('非工作时段！')
        return 1
    else:
        return 0


# 获取人员列表HTML页面
def getInfoContext(cookie):
    # 第二次提交 添加类型部门区域信息
    # 添加目标对象到列表中
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
    TargetUrl = getConfig('SKESERVER','address')+'InLibraryReaderInfo.aspx'
    resp = requests.get(TargetUrl, headers=headers, cookies=cookie)
    # 反馈查询结果到页面
    form_data = get_CSRF(resp.text)
    form_data['button_do'] = '统计'
    return requests.post(TargetUrl, form_data, headers=headers, cookies=cookie)  # 此处包含查询结果


def mainWork(context,now):
    # 信息全部获取完毕，开始本地处理
    bs = BeautifulSoup(context.text, 'lxml')
    # 获取人数信息
    num = bs.find(id='Label_num').string[4:-1]
    displayMsg('当前在馆人数:' + num)

    year = time.strftime("%Y", now)
    month = time.strftime("%m", now)
    day = time.strftime("%d", now)
    hour = time.strftime("%H", now)
    minute = time.strftime("%M", now)
    second = time.strftime("%S", now)

    already = False
    if os.path.exists(os.path.join(getConfig('SYSTEM', 'dataPath'),year + month + day + '.txt')):
        # 判断当前时间段是否已经写入
        with open(os.path.join(getConfig('SYSTEM', 'dataPath'),year + month + day + '.txt'), 'r') as file:
            line = file.readlines()
            for i in line:
                if i[:i.find('=>')] == str(year+month+day+hour+minute):
                    already = True
                    displayMsg('当前时间点已写入')
            file.close()

    if already == False:
        with open(os.path.join(getConfig('SYSTEM', 'dataPath'),year + month + day + '.txt'),'a+') as file:
            body = year + month + day + hour + minute + '=>' + num + '\n'
            file.write(body)
        file.close()


if __name__ == '__main__':
    # 打印欢迎消息
    welcome()
    checkEnv()
    while True:
        displayMsg('正在尝试登录')
        # 获取登录会话
        cookie = getLoginCookies()
        print('============================================================')
        while True:
            # 检查是否处于非工作时间
            if freeTime() == 1:
                sleepTime = 60 - int(time.strftime("%S", time.localtime()))
                time.sleep(sleepTime)
                continue

            # 进入指定页面 判断登录状态
            context = getInfoContext(cookie)
            if checkLoginStatus(context) == 0:
                displayMsg('登录失效尝试重新登录')
                break

            # 开始时间 传入函数内使用
            now = time.localtime()

            # 将指定页面内容进行处理
            userInfoList = mainWork(context,now)

            # 结束时间  定时器:每分钟的0秒开始运行
            sleepTime = 60 - int(time.strftime("%S", time.localtime()))
            time.sleep(sleepTime)

