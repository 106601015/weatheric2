'''
我的conda爬蟲環境需求：
requests=2.24.0
bs4=2.9.1
lxml=4.5.1

此function開著就會定期執行下載任務
無針對動態網站做滾動視窗等等功能,
無headers做去訪問限制,
無防爬蟲機制(目前網站基本不會鎖:))

個別設計的func. API下載，一個API對應一個資料夾
'''
import requests
from bs4 import BeautifulSoup
import json
import os
import shutil
import datetime
import threading
import time

# 解析target_url的內容並用BeautifulSoup解碼回傳
def parsing(target_url):
    res = requests.get(target_url)
    return BeautifulSoup(res.text, 'lxml')
# 觀察target_url中所有img的fname --> 找出圖片網址並印出
def look(target_url):
    print(target_url)
    soup = parsing(target_url)
    for img in soup.select('img'):
        fpath = img['src']
        fname = img['src'].split('/')[-1]
        print('fpath:', fpath)
        print('fname:', fname)
    print()

# https://www.cwb.gov.tw/Data/radar/CV1_3600_202012080250.png
# https://www.cwb.gov.tw/Data/radar/CV2_3600_202012080250.png
# 下載cwb有地形無地形雷達資料 --> radar(資料解析度10分鐘一筆)(降水雷達時間非線性難抓先不設計，要抓特殊事件再手動處理)
def download_cwb_radar(beginning_time, ending_time):
    print('download_cwb_radar init')
    #做資料夾確認，在不同平台可移植
    pic_root_url = 'https://www.cwb.gov.tw'
    root = os.getcwd()
    store_path = os.path.join(root, 'radar')
    if not os.path.isdir(store_path):
        os.mkdir(store_path)

    radar_data_url_dict = {
        'terrain':'/CV2_1000_',
        'no_terrain':'/CV1_1000_',
    }

    time = beginning_time
    while time < ending_time:
        # 特製時間處理
        minute = time.strftime("%M")
        str_time = time.strftime("%Y%m%d%H")
        str_time = str_time+ str(int(minute)//10) +'0'
        try:
            for item in radar_data_url_dict.keys():
                url = pic_root_url+'/Data/radar{}{}.png'.format(radar_data_url_dict[item], str_time)
                print(url)
                png_res = requests.get(url, stream=True)
                # 404 no found, 圖片可能尚未上傳就跳過
                if png_res.status_code == 404:
                    print('!!! radar download 404 !!!')
                    continue
                f = open(os.path.join(store_path, 'radar_{}_{}.png'.format(item, str_time)) , 'wb')
                shutil.copyfileobj(png_res.raw, f)
                f.close()
        except:
            print('!!! radar download error !!!')
        ten_minutes = datetime.timedelta(minutes=10)
        time += ten_minutes

# https://www.cwb.gov.tw/Data/rainfall/2020-12-08_1500.QZJ8.jpg
# https://www.cwb.gov.tw/Data/rainfall/2020-12-08_0200.QZT8.jpg
# 下載cwb逐時+日累積降水資料 --> rainfall(資料解析度一小時一筆)
def download_cwb_rainfall(beginning_time, ending_time):
    print('download_cwb_rainfall init')
    #做資料夾確認，在不同平台可移植
    pic_root_url = 'https://www.cwb.gov.tw'
    root = os.getcwd()
    store_path = os.path.join(root, 'rainfall')
    if not os.path.isdir(store_path):
        os.mkdir(store_path)

    rainfall_data_url_dict = {
        'daily':'.QZJ8',
        'hourly':'.QZT8',
    }

    time = beginning_time
    while time < ending_time:
        # 特製時間處理
        str_time = time.strftime("%Y-%m-%d_%H00")
        try:
            for item in rainfall_data_url_dict.keys():
                url = '{}/Data/rainfall/{}{}.jpg'.format(pic_root_url, str_time, rainfall_data_url_dict[item])
                print(url)
                png_res = requests.get(url, stream=True)
                # 404 no found, 圖片可能尚未上傳就跳過
                if png_res.status_code == 404:
                    print('!!! rainfall download 404 !!!')
                    continue
                f = open(os.path.join(store_path, 'rainfall_{}_{}.jpg'.format(item, str_time)) , 'wb')
                shutil.copyfileobj(png_res.raw, f)
                f.close()
        except:
            print('!!! rainfall download error !!!')
        one_hour = datetime.timedelta(hours=1)
        time += one_hour

# https://www.cwb.gov.tw/Data/satellite/TWI_VIS_Gray_1350/TWI_VIS_Gray_1350-2020-12-07-10-00.jpg
# https://www.cwb.gov.tw/Data/satellite/TWI_VIS_TRGB_1375/TWI_VIS_TRGB_1375-2020-12-08-02-00.jpg
# https://www.cwb.gov.tw/Data/satellite/TWI_IR1_CR_800/TWI_IR1_CR_800-2020-12-08-02-10.jpg
# 下載cwb可見光+彩色+真實色雲圖 --> satellite(資料解析度10分鐘一筆)
def download_cwb_satellite(beginning_time, ending_time):
    print('download_cwb_satellite init')
    #做資料夾確認，在不同平台可移植
    pic_root_url = 'https://www.cwb.gov.tw'
    root = os.getcwd()
    store_path = os.path.join(root, 'satellite')
    if not os.path.isdir(store_path):
        os.mkdir(store_path)

    satellite_data_url_dict = {
        'visible':'/TWI_VIS_Gray_1350',
        'color':'/TWI_IR1_CR_800',
        'real':'/TWI_VIS_TRGB_1375',
    }

    time = beginning_time
    while time < ending_time:
        # 特製時間處理
        minute = time.strftime("%M")
        str_time = time.strftime("%Y-%m-%d-%H")
        str_time = str_time+'-' + str(int(minute)//10) +'0'
        try:
            for item in satellite_data_url_dict.keys():
                url = '{}/Data/satellite{}-{}.jpg'.format(pic_root_url, satellite_data_url_dict[item]*2, str_time)
                print(url)
                png_res = requests.get(url, stream=True)
                # 404 no found, 圖片可能尚未上傳就跳過
                if png_res.status_code == 404:
                    print('!!! satellite download 404 !!!')
                    continue
                f = open(os.path.join(store_path, 'satellite_{}_{}.png'.format(item, str_time)) , 'wb')
                shutil.copyfileobj(png_res.raw, f)
                f.close()
        except:
            print('!!! satellite download error !!!')
        ten_minutes = datetime.timedelta(minutes=10)
        time += ten_minutes

# https://www.cwb.gov.tw/Data/temperature/2020-12-08_1500.GTP8.jpg
# 下載溫度分布圖 --> temp(資料解析度一小時一筆)
def download_cwb_temp(beginning_time, ending_time):
    print('download_cwb_temp init')
    #做資料夾確認，在不同平台可移植
    pic_root_url = 'https://www.cwb.gov.tw'
    root = os.getcwd()
    store_path = os.path.join(root, 'temp')
    if not os.path.isdir(store_path):
        os.mkdir(store_path)

    temp_data_url_dict = {
        'temp':'.GTP8',
    }

    time = beginning_time
    while time < ending_time:
        # 特製時間處理
        str_time = time.strftime("%Y-%m-%d_%H00")
        try:
            for item in temp_data_url_dict.keys():
                url = '{}/Data/temperature/{}{}.jpg'.format(pic_root_url, str_time, temp_data_url_dict[item])
                print(url)
                png_res = requests.get(url, stream=True)
                # 404 no found, 圖片可能尚未上傳就跳過
                if png_res.status_code == 404:
                    print('!!! temp download 404 !!!')
                    continue
                f = open(os.path.join(store_path, 'temp_{}_{}.png'.format(item, str_time)) , 'wb')
                shutil.copyfileobj(png_res.raw, f)
                f.close()
        except:
            print('!!! temp download error !!!')
        one_hour = datetime.timedelta(hours=1)
        time += one_hour

# https://npd.cwb.gov.tw/NPD/irisme_data/Weather/HLAnalysis/GRA___000_20120612_005.gif
# 下載數值天氣預報.觀測分析場all圖 --> obs(資料解析度地面6小時高空探空12小時一筆，存約一個禮拜)
def download_cwb_obs(beginning_time, ending_time):
    print('download_cwb_obs init')
    #做資料夾確認，在不同平台可移植
    pic_root_url = 'https://npd.cwb.gov.tw/NPD/irisme_data/Weather'
    root = os.getcwd()
    store_path = os.path.join(root, 'obs')
    if not os.path.isdir(store_path):
        os.mkdir(store_path)

    time = beginning_time
    while time < ending_time:
        year = time.strftime("%Y")[0:2]
        if int(time.strftime("%H")) < 12:
            str_time = time.strftime("%m%d00")
        else:
            str_time = time.strftime("%m%d12")
        str_time = year+str_time

        obs_data_url_dict = {
            'suf':'/Analysis/GRA___000_{}_103.gif'.format(str_time),
            '850':'/HLAnalysis/GRA___000_{}_001.gif'.format(str_time),
            '700':'/HLAnalysis/GRA___000_{}_002.gif'.format(str_time),
            '500':'/HLAnalysis/GRA___000_{}_003.gif'.format(str_time),
            '300':'/HLAnalysis/GRA___000_{}_004.gif'.format(str_time),
            '200':'/HLAnalysis/GRA___000_{}_005.gif'.format(str_time),
            '925':'/HLAnalysis/GRA___000_{}_022.gif'.format(str_time),
            'SkewT':'/SkewT/SKW___000_{}_46692.gif'.format(str_time),
        }
        try:
            for item in obs_data_url_dict.keys():
                url = '{}{}'.format(pic_root_url, obs_data_url_dict[item])
                print(url)
                png_res = requests.get(url, stream=True)
                # 404 no found, 圖片可能尚未上傳就跳過
                if png_res.status_code == 404:
                    print('!!! obs download 404 !!!')
                    continue
                # 加上下載時間戳記以防cover
                download_time = ending_time.strftime('%m-%d-%H-%M')
                f = open(os.path.join(store_path, 'obs_{}_{}_{}.gif'.format(item, str_time, download_time)) , 'wb')
                shutil.copyfileobj(png_res.raw, f)
                f.close()
        except Exception as e:
            print('!!! obs download error !!!', e)

        twelve_hours = datetime.timedelta(hours=12)
        time += twelve_hours

# https://www.jma.go.jp/jp/metcht/pdf/kosou/aupn30_00.pdf
# https://www.jma.go.jp/en/g3/images/asia/20120721.png
# 下載jma所有圖資 --> jma(資料12小時刷新，以防萬一六小時更新一次)
def download_jma(ending_time):
    print('download_jma init')
    #做資料夾確認，在不同平台可移植
    pic_root_url = 'https://www.jma.go.jp'
    root = os.getcwd()
    store_path = os.path.join(root, 'jma')
    if not os.path.isdir(store_path):
        os.mkdir(store_path)

    jma_data_url_dict = {
        '200':'/jp/metcht/pdf/kosou/aupa20_',
        '250':'/jp/metcht/pdf/kosou/aupa25_',
        '300':'/jp/metcht/pdf/kosou/aupn30_',
        '300500':'/jp/metcht/pdf/kosou/aupq35_',
        '700850':'/jp/metcht/pdf/kosou/aupq78_',
    }

    try:
        for item in jma_data_url_dict.keys():
            for time in ['00', '12']:
                url = '{}{}{}.pdf'.format(pic_root_url, jma_data_url_dict[item], time)
                print(url)
                png_res = requests.get(url, stream=True)
                # 404 no found, 圖片可能尚未上傳就跳過
                if png_res.status_code == 404:
                    print('!!! jma download 404 !!!')
                    continue
                # 加上下載時間戳記以防cover
                download_time = ending_time.strftime('%m-%d-%H')
                f = open(os.path.join(store_path, 'jma_{}_{}_{}.pdf'.format(item, time, download_time)) , 'wb')
                shutil.copyfileobj(png_res.raw, f)
                f.close()

        h_list = ['03', '09', '15', '21']

        year = ending_time.strftime("%Y")[0:2]
        str_time = ending_time.strftime("%m%d")
        for h in h_list:
            url = '{}/jp/g3/images/asia/{}{}{}.png'.format(pic_root_url, year, str_time, h)
            print(url)
            png_res = requests.get(url, stream=True)
            # 404 no found, 圖片可能尚未上傳就跳過
            if png_res.status_code == 404:
                print('!!! jma2 download 404 !!!')
                continue
            # 加上下載時間戳記以防cover
            download_time = ending_time.strftime('%m-%d-%H')
            f = open(os.path.join(store_path, 'jma_suf_{}_{}.png'.format(download_time, h)) , 'wb')
            shutil.copyfileobj(png_res.raw, f)
            f.close()

        year = (ending_time - datetime.timedelta(days=1)).strftime("%Y")[0:2]
        str_time = (ending_time - datetime.timedelta(days=1)).strftime("%m%d")
        for h in h_list:
            url = '{}/jp/g3/images/asia/{}{}{}.png'.format(pic_root_url, year, str_time, h)
            print(url)
            png_res = requests.get(url, stream=True)
            # 404 no found, 圖片可能尚未上傳就跳過
            if png_res.status_code == 404:
                print('!!! jma2 download 404 !!!')
                continue
            # 加上下載時間戳記以防cover
            download_time = (ending_time - datetime.timedelta(days=1)).strftime('%m-%d-%H')
            f = open(os.path.join(store_path, 'jma_suf_{}_{}.png'.format(download_time, h)) , 'wb')
            shutil.copyfileobj(png_res.raw, f)
            f.close()
    except:
        print('!!! jma download error !!!')

# https://airtw.epa.gov.tw/ModelSimulate/20201205/output_AQI_20201205170000.png
# 下載環保署AQI圖 --> aqi(資料解析度一小時一筆)
def download_aqi(beginning_time, ending_time):
    print('download_aqi init')
    #做資料夾確認，在不同平台可移植
    pic_root_url = 'https://airtw.epa.gov.tw/'
    root = os.getcwd()
    store_path = os.path.join(root, 'aqi')
    if not os.path.isdir(store_path):
        os.mkdir(store_path)

    time = beginning_time
    while time < ending_time:
        # 特製時間處理
        str_time = time.strftime("%Y%m%d")
        try:
            url = '{}/ModelSimulate/{}/output_AQI_{}0000.png'.format(pic_root_url, str_time, str_time+time.strftime("%H"))
            print(url)
            png_res = requests.get(url, stream=True)
            # 404 no found, 圖片可能尚未上傳就跳過
            if png_res.status_code == 404:
                print('!!! aqi download 404 !!!')
                continue
            f = open(os.path.join(store_path, 'aqi_{}.png'.format(str_time+time.strftime("%H"))) , 'wb')
            shutil.copyfileobj(png_res.raw, f)
            f.close()
        except:
            print('!!! aqi download error !!!')
        one_hour = datetime.timedelta(hours=1)
        time += one_hour


def main():
    print("main again:)")
    # run main per 60*60 seconds
    timer = threading.Timer(60*60, main)
    timer.start()

    # 設定cwb抓圖區間
    ending_time = datetime.datetime.now()

    three_day = datetime.timedelta(days=3)
    three_hours = datetime.timedelta(hours=5)
    print(ending_time.strftime('%Y-%m-%d-%H-%M-%S'))

    # call function
    download_cwb_radar(ending_time-three_hours, ending_time) # unit test ok, timedelta~1day(pre 10mins)
    download_cwb_rainfall(ending_time-three_hours, ending_time) # unit test ok, timedelta~5day
    download_cwb_satellite(ending_time-three_hours, ending_time) # unit test ok, timedelta~2day
    download_cwb_temp(ending_time-three_hours, ending_time) # unit test ok, timedelta~4day
    download_cwb_obs(ending_time-three_day, ending_time)# unit test ok, timedelta~1week
    download_jma(ending_time) # unit test ok, no store
    download_aqi(ending_time-three_hours, ending_time)# unit test ok, timedelta>1mouth

# 開始定時器
if __name__ == '__main__':
    timer = threading.Timer(0, main)
    timer.start()

    #TODO:jma pdf -> png/jpg