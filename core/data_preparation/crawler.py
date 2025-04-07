import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from urllib.parse import urljoin
import os
import re
from RAG.config import Config
from RAG.utils.logger import logger

# 定义HEADERS字典，包含了 HTTP 请求头信息：
HEADERS = {
    # User-Agent：设置请求的用户代理，模拟浏览器访问。
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    # Accept-Language：设置接受的语言。
    'Accept-Language': 'zh-CN,zh;q=0.9',
    # Referer：设置请求的来源页面，这里是中北大学官网。
    'Referer': 'https://www.nuc.edu.cn/'
}

# 用于获取指定 URL 的页面内容
def fetch_page(url, max_retries=3):
    # 当前重试次数
    retries = 0
    # 循环进行请求，直到达到最大重试次数
    while retries < max_retries:
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)  #循环进行请求，直到达到最大重试次数。
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'lxml')
            logger.warning(f"请求页面 {url} 返回状态码：{response.status_code}")  #如果响应状态码不是 200，记录警告日志。
        except Exception as e:
            logger.error(f"请求页面 {url} 失败，第 {retries + 1} 次重试: {str(e)}")
        retries += 1
    return None

# 用于获取新闻列表
def get_news_list(base_url):
    # 用于存储新闻信息的列表
    news_items = []
    page = 1
    start_date = datetime.strptime(Config.START_DATE, "%Y-%m-%d")  # 加载配置时间

    while True:
        if page == 1:
            url = urljoin(base_url, "zbxw.htm")  # 首页
        else:
            url = urljoin(base_url, f"zbxw/{page}.htm")  # 后续页

        logger.info(f"正在抓取页面：{url}")
        # 调用fetch_page函数获取页面内容并解析
        soup = fetch_page(url)
        if not soup:
            break
        news_list = soup.select('.list_con ul li')  # 根据页面选择正确的 CSS 选择器
        if not news_list:
            logger.warning(f"第 {page} 页未找到新闻条目")
            break

        # 遍历新闻列表项
        for item in news_list:
            try:
                a_tag = item.select_one('a')
                date_tag = item.select_one('span')
                if not a_tag or not date_tag:
                    continue
                # 获取标题
                title = a_tag.get('title', a_tag.text).strip()
                # str->datetime
                date_str = date_tag.text.strip()
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                if date_obj < start_date:
                    continue  # 跳过旧新闻
                # 获取链接
                link = urljoin(base_url, a_tag['href'].split('#')[0])
                # 创建包含新闻标题、链接和日期的字典，并添加到news_items列表中
                news_item = {
                    'title': title,
                    'link': link,
                    'date': date_obj.strftime("%Y-%m-%d")
                }
                news_items.append(news_item)
            except Exception as e:
                logger.error(f"解析条目失败: {str(e)}\n原始HTML：{item.prettify()}")
                continue

        if page >= 261:  # 最多抓5页
            break
        page += 1

    return news_items
# 用于清洗新闻正文内容
def clean_content(text):
    # 使用正则表达式去除 < script > ，<style>标签及其内容
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)
    # 去除HTML注释
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # 去除特定的文本、实体和空白字符
    text = re.sub(r'【返回】|返回顶部|&[a-z]+;|\xa0|\t', '', text)
    # 将连续的多个空白字符替换为单个空格，并去除两端的空白字符，返回清洗后的文本
    return re.sub(r'\s{2,}', ' ', text).strip()


# 用于获取新闻详情
def get_news_detail(url):
    soup = fetch_page(url)
    if not soup:
        logger.warning(f"无法获取页面: {url}")
        return ''
    try:
        content_div = soup.select_one('#vsb_content_4')
        if not content_div:
            logger.warning(f"未找到正文内容: {url}")
            return ''
        # 遍历并移除新闻正文中的无关标签
        for tag in content_div.select('script, style, div, a, img, iframe'):
            tag.decompose()
        # 获取新闻正文文本内容，使用换行符作为分隔符，并去除两端的空白字符
        content = content_div.get_text(separator='\n', strip=True)
        return clean_content(content)
    except Exception as e:
        logger.error(f"获取详情失败 {url}: {str(e)}")
        return ''

# 用于执行新闻抓取的主要逻辑
def crawl_news():
    try:
        # NEWS_URL = "https://www.nuc.edu.cn/index/zbxw.htm"
        base_url = Config.NEWS_URL
        # 如果基础URL没有协议头（http: // 或https: // ），添加https: // 协议头
        if not base_url.startswith(('http://', 'https://')):
            base_url = f"https://{base_url}"
        if "nuc.edu.cn" not in base_url:
            raise ValueError("必须使用中北大学官网域名")

        logger.info("开始抓取中北大学新闻...")
        news_list = get_news_list(base_url)
        logger.info(f"共找到{len(news_list)}条新闻条目")
        # 导入ThreadPoolExecutor用于多线程处理
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=5) as executor: #创建一个最大工作线程数为 5 的线程池
            #使用线程池并发地获取新闻详情
            futures = [executor.submit(get_news_detail, news['link']) for news in news_list]
            # 遍历每个新闻详情的获取结果
            for i, future in enumerate(futures):
                try:
                    news_list[i]['content'] = future.result() #将获取到的新闻正文内容添加到新闻列表项中
                    logger.debug(f"已处理：{news_list[i]['title']}")
                except Exception as e:
                    logger.error(f"处理失败：{news_list[i]['title']} - {str(e)}")
                    news_list[i]['content'] = ''
        if news_list:
            df = pd.DataFrame(news_list) #如果新闻列表不为空
            save_path = os.path.abspath(Config.RAW_DATA_PATH)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            df.to_csv(save_path, index=False, encoding='utf-8-sig')
            logger.info(f"成功保存{len(df)}条新闻至：{save_path}")
        else:
            logger.warning("有效新闻数据为空")

    except Exception as e:
        logger.error(f"抓取过程发生严重错误: {str(e)}", exc_info=True)


if __name__ == "__main__":
    crawl_news()
