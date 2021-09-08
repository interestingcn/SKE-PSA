# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:interestingcn01(interestingcn01@gmail.com)

import configparser,time,sys,os,datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def welcome():
    msg = '''
============================================================
 _____ _____ _____       _____ _____ _____ 
|   __|  |  |   __|     |  _  |   __|  _  | SKE-PSA Analysis
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
    if os.path.exists(getConfig('SYSTEM','dataPath')):
        pass
    else:
        os.makedirs(getConfig('SYSTEM','dataPath'))
    if os.path.exists(getConfig('SYSTEM','imgPath')):
        pass
    else:
        os.makedirs(getConfig('SYSTEM','imgPath'))

def displayMsg(text):
    timenow = time.asctime(time.localtime(time.time()))
    msg = f'{timenow} - {str(text)} '
    print(msg)

# 载入数据文件为字典形式
def loadData(filename):
    data = {}
    if os.path.exists(os.path.join(getConfig('SYSTEM', 'dataPath'), filename + '.txt')):
        pass
    else:
        return False

    file = os.path.join(getConfig('SYSTEM', 'dataPath'), filename + '.txt')
    with open(file,'r') as f:
        line = f.readlines()
        for i in line:
            i = i.replace('\n','').split('=>')
            data[i[0]] = i[1]
    return data


# 创建指定数据文件数据图片
def generateImage(data,filename):
    # 支持中文显示
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    x_data = []
    y_data = []
    for info in data:
        x_data.append(info[8:-2]+':'+info[-2:])
        y_data.append(int(data[info]))

    #   画布尺寸
    fig, ax = plt.subplots(1, 1,figsize=(12,6))

    ax.yaxis.set_major_locator(ticker.MultipleLocator(base=int(getConfig('IMG', 'yBase'))))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(base=int(getConfig('IMG', 'xBase'))))

    # x,y数据
    plt.plot(x_data, y_data,linewidth=2.0,label="在馆人数")
    plt.xlabel("时间")
    plt.ylabel("人数")

    plt.title(getConfig('IMG', 'title'))

    # 隐藏上 右侧 边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    if getConfig('IMG','textInfo') == 'True':
        # 等比坐标轴数据放置注释文字
        plt.text(min(x_data), max(y_data)*0.95, '记录时间: '+filename[:4] +'年' + filename[4:6] +'月'+ filename[6:] + '日')
        plt.text(min(x_data), max(y_data)*0.9, f'峰值人数: {str(max(y_data))}（{str(x_data[y_data.index(max(y_data))])}）')

    if getConfig('IMG','markMax') == 'True':
        plt.annotate(xy=(str(x_data[y_data.index(max(y_data))]), max(y_data)),xytext=(str(x_data[y_data.index(max(y_data))]), max(y_data)*0.90),  text='MAX',arrowprops=dict(arrowstyle=getConfig('IMG', 'arrowstyle')))


    # y轴倾斜45度
    # plt.xticks(rotation=45)
    plt.legend() # 角标
    plt.grid() # 背景网格线
    # plt.show()  # 显示图片
    plt.savefig(os.path.join(getConfig('SYSTEM', 'imgPath'),filename +'.jpg'), dpi = int(getConfig('IMG', 'dpi')))


def getBrforeDayDate(dayNum):
    dayNum = int(dayNum) +1
    today = datetime.date.today()
    dateList = []
    for i in range(dayNum):
        day = datetime.timedelta(days=i)
        dateList.append(today - day)
    list = []
    for i in dateList:
        list.append(str(i).replace('-',''))
    return list


# 获取近几天数据 传入天数列表
def generateRecentWeekImage(daysList):

    # 支持中文显示
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    fig, ax = plt.subplots(1, 1)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(base=50))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(base=30))

    print(daysList[0])
    exit()
    for line in daysList:
        x_data = []
        y_data = []

        lineInfo = loadData(line)

        for info in lineInfo:
            x_data.append(info[8:-2] + ':' + info[-2:])
            y_data.append(int(lineInfo[info]))
            plt.plot(x_data, y_data, color='red', linewidth=2.0, linestyle='--')
            plt.plot(x_data, y_data, linewidth=2.0, label=info[:4] + '年' + info[4:6] + '月' + info[6:8] + '日')

    plt.xlabel("时间")
    plt.ylabel("人数")
    plt.title(getConfig('IMG', 'title'))
    # 隐藏上 右侧 边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # y轴倾斜45度
    # plt.xticks(rotation=45)
    plt.legend()
    plt.grid() # 背景网格线
    plt.show()
    plt.savefig(os.path.join(getConfig('SYSTEM', 'imgPath'),'Last7Days.jpg'), dpi = int(getConfig('IMG', 'dpi')))


if __name__ == '__main__':

    # generateRecentWeekImage(getBrforeDayDate(1))
    #
    # exit()

    welcome()
    checkEnv()

    # 创建单日数据图片  仅创建近n条记录图片
    fileList = os.listdir(getConfig('SYSTEM', 'dataPath'))[-3:]

    for filename in fileList:
        filename = filename[:filename.find('.')]
        displayMsg('正在绘制数据图片：' + filename + '.jpg')
        generateImage(loadData(filename), filename)

    displayMsg('任务完成！')


