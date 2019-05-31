from datetime import datetime
import json
import os.path

import twnews.common as common

def get_cache_path(item, datestr):
    cache_dir = common.get_cache_dir('twse')
    return '%s/%s-%s.json' % (cache_dir, item, datestr)

def has_cache(item, datestr):
    cache_path = get_cache_path(item, datestr)
    return os.path.isfile(cache_path)

def load_cache(item, datestr):
    content = None
    cache_path = get_cache_path(item, datestr)
    with open(cache_path, 'r') as f_cache:
        content = json.load(f_cache)
    return content

def save_cache(item, datestr, content):
    cache_path = get_cache_path(item, datestr)
    with open(cache_path, 'w') as f_cache:
        json.dump(content, f_cache)

def sync_margin_trading(datestr):
    """
    融資融券
    """
    dsitem = 'margin_trading'
    logger = common.get_logger('finance')

    # 快取處理
    if has_cache(dsitem, datestr):
        logger.info('載入 %s 的融資融券', datestr)
        ds = load_cache(dsitem, datestr)
    else:
        logger.info('沒有 %s 的融資融券', datestr)
        session = common.get_session(False)
        url = 'http://www.twse.com.tw/exchangeReport/MI_MARGN?response=json&date=%s&selectType=ALL' % datestr
        resp = session.get(url)
        ds = resp.json()
        status = ds['stat']
        # 注意! 即使發生問題, HTTP 回應碼也是 200, 必須依 JSON 分辨成功或失敗
        # 成功: OK
        # 失敗: 查詢日期大於可查詢最大日期，請重新查詢!
        #      很抱歉，目前線上人數過多，請您稍候再試
        if status == 'OK':
            logger.info('儲存 %s 的融資融券', datestr)
            save_cache(dsitem, datestr, ds)
        else:
            logger.error('無法取的 %s 的融資融券資料, 原因: %s', datestr, status)
            return

    for detail in ds['data']:
        print('[%s %s] 前日融資: %s 今日融資: %s, 前日融券: %s 今日融券: %s' % (
            detail[0],
            detail[1].strip(),
            int(detail[5].replace(',', '')),
            int(detail[6].replace(',', '')),
            int(detail[11].replace(',', '')),
            int(detail[12].replace(',', ''))
        ))

def sync_block_trading(datestr):
    """
    鉅額交易
    """
    dsitem = 'block_trading'
    logger = common.get_logger('finance')

    # 快取處理
    if has_cache(dsitem, datestr):
        logger.info('載入 %s 的鉅額交易', datestr)
        ds = load_cache(dsitem, datestr)
    else:
        logger.info('沒有 %s 的鉅額交易', datestr)
        session = common.get_session(False)
        url = 'http://www.twse.com.tw/block/BFIAUU?response=json&date=%s&selectType=S' % datestr
        resp = session.get(url)
        ds = resp.json()
        status = ds['stat']
        # 注意! 即使發生問題, HTTP 回應碼也是 200, 必須依 JSON 分辨成功或失敗
        # 成功: OK
        # 失敗: 查詢日期大於可查詢最大日期，請重新查詢!
        #      很抱歉，目前線上人數過多，請您稍候再試
        if status == 'OK':
            logger.info('儲存 %s 的鉅額交易', datestr)
            save_cache(dsitem, datestr, ds)
        else:
            logger.error('無法取的 %s 的鉅額交易資料, 原因: %s', datestr, status)
            return

    for trade in ds['data']:
        if trade[0] != '總計':
            print('[%s %s] %s 成交價: %s 股數: %s 金額: %s' % (
                trade[0],
                trade[1],
                trade[2],
                trade[3].replace(',', ''),
                trade[4].replace(',', ''),
                trade[5].replace(',', '')
            ))

def sync_institution_trading(datestr):
    """
    三大法人
    """
    dsitem = 'institution_trading'
    logger = common.get_logger('finance')

    # 快取處理
    if has_cache(dsitem, datestr):
        logger.info('載入 %s 的三大法人', datestr)
        ds = load_cache(dsitem, datestr)
    else:
        logger.info('沒有 %s 的三大法人', datestr)
        session = common.get_session(False)
        url = 'http://www.twse.com.tw/fund/T86?response=json&date=%s&selectType=ALL' % datestr
        resp = session.get(url)
        ds = resp.json()
        status = ds['stat']
        # 注意! 即使發生問題, HTTP 回應碼也是 200, 必須依 JSON 分辨成功或失敗
        # 成功: OK
        # 失敗: 查詢日期大於可查詢最大日期，請重新查詢!
        #      很抱歉，目前線上人數過多，請您稍候再試
        if status == 'OK':
            logger.info('儲存 %s 的三大法人', datestr)
            save_cache(dsitem, datestr, ds)
        else:
            logger.error('無法取的 %s 的三大法人資料, 原因: %s', datestr, status)
            return

    for detail in ds['data']:
        print('[%s %s] 外資: %s 投信: %s 自營商: %s' % (
            detail[0],
            detail[1].strip(),
            int(detail[4].replace(',', '')) // 1000,
            int(detail[7].replace(',', '')) // 1000,
            int(detail[8].replace(',', '')) // 1000
        ))

def sync_short_sell(datestr):
    """
    http://www.twse.com.tw/exchangeReport/TWT93U?response={{TWSE_EXPORT_FORMAT}}&date={{TWSE_EXPORT_DATE}}
    """
    pass

def sync_etf_net():
    """
    https://mis.twse.com.tw/stock/data/all_etf.txt
    {
      "a1": [
        {
          "msgArray": [
            {
              "a": "", 代碼
              "b": "", 名稱
              "c": "", 發行量
              "d": "", 與前日發行量變化
              "e": "", 成交價
              "f": "", 淨值
              "g": "", 折溢價率
              "h": "", 前日淨值
              "i": "", 日期
              "j": "", 時間
              "k": "", ETF 類型 (1~4)
            },
            ...
          ]
          "refURL": "https://www.kgifund.com.tw/ETF/RWD/Introduction.aspx",
          "userDelay": "15000",
          "rtMessage": "OK",
          "rtCode": "0000"
        },
        ...
        {} <-- 最後有一組空的
      ]
    }
    """
    logger = common.get_logger('finance')
    datestr = datetime.now().strftime('%Y%m%d')

    # 快取處理
    if has_cache('etf_net', datestr):
        logger.info('載入 %s 的 ETF 溢價率快取', datestr)
        ds = load_cache('etf_net', datestr)
    else:
        logger.info('沒有 %s 的 ETF 溢價率快取', datestr)
        session = common.get_session(False)
        resp = session.get('https://mis.twse.com.tw/stock/data/all_etf.txt')
        ds = resp.json()
        dsdate = ds['a1'][1]['msgArray'][0]['i']
        if datestr == dsdate:
            logger.info('儲存 %s 的 ETF 溢價率快取', datestr)
            save_cache('etf_net', datestr, ds)
        else:
            logger.info('無法取得 %s 的 ETF 溢價率資料', datestr)
            return

    # 來源資料轉換 key/value 形式
    etf_dict = {}
    for fund in ds['a1']:
        if 'msgArray' in fund:
            for etf in fund['msgArray']:
                etf_dict[etf['a']] = etf

    # 依證券代碼順序處理
    # TODO: 寫入 SQLite
    max_name_len = 0
    for k in sorted(etf_dict.keys()):
        etf = etf_dict[k]
        name_len = len(etf['b'])
        if name_len > max_name_len:
            max_name_len = name_len
        print('%s, %s, %s, %s%%' % (etf['a'], etf['b'], etf['f'], etf['g']))
    print(max_name_len)

if __name__ == '__main__':
    #sync_etf_net()
    #sync_institution_trading('20190529')
    #sync_margin_trading('20190529')
    #sync_block_trading('20190529')
