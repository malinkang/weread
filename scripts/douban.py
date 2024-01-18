import json
import os
import requests
from bs4 import BeautifulSoup

from notion_helper import NotionHelper
from config import URL
from utils import (
    get_property_value,
    get_title,
    get_file,
    get_rich_text,
    get_icon,
)

# Environment variables
DOUBAN_API_HOST = os.getenv("DOUBAN_API_HOST", "frodo.douban.com")
DOUBAN_API_KEY = os.getenv("DOUBAN_API_KEY", "0ac44ae016490db2204ce0a042db2916")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def douban_book_parse(link):
    response = requests.get(link, headers=headers)
    soup = BeautifulSoup(response.content)
    result = {}
    result["书名"] = soup.find(property="v:itemreviewed").string
    result["封面"] = soup.find(id="mainpic").img["src"]
    info = soup.find(id="info")
    authors  = soup.find_all("li",class_="author")
    authors = [author.find("a",class_="name").string for author in authors]
    info = list(map(lambda x: x.replace(":", "").strip(), info.stripped_strings))
    print(info)
    result["作者"] = authors
    result["ISBN"] = info[info.index("ISBN") + 1 :][0]
    return result


def fetch_subjects(user, type_, status, offset):
    url = f"https://{DOUBAN_API_HOST}/api/v2/user/{user}/interests"

    # Set default value for status if not provided
    status = status or "done"

    # Prepare query parameters
    params = {
        "type": type_,
        "status": status,
        "count": 50,
        "start": offset,
        "apiKey": DOUBAN_API_KEY,
    }

    # Prepare headers
    headers = {
        "host": DOUBAN_API_HOST,
        "authorization": f"Bearer {AUTH_TOKEN}" if AUTH_TOKEN else "",
        "user-agent": "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.16(0x18001023) NetType/WIFI Language/zh_CN",
        "referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/84/page-frame.html",
    }

    # Send HTTP request
    response = requests.get(url, headers=headers, params=params)

    # Return the JSON response content
    return response.json()


def search():
    url = f"https://{DOUBAN_API_HOST}/api/v2/book/isbn"

    # Prepare query parameters
    params = {
        "q": "第二大脑",
        "apiKey": DOUBAN_API_KEY,
    }
    # Prepare headers
    headers = {
        "host": DOUBAN_API_HOST,
        "authorization": f"Bearer {AUTH_TOKEN}" if AUTH_TOKEN else "",
        "user-agent": "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.16(0x18001023) NetType/WIFI Language/zh_CN",
        "referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/84/page-frame.html",
    }

    # Send HTTP request
    response = requests.get(url, headers=headers, params=params)

    # Return the JSON response content
    return response.json()


def search_book():
    search_url = (
        "https://search.douban.com/book/subject_search?search_text=python&cat=1001"
    )
    response = requests.get(search_url, headers=headers)
    print(response.text)
    soup = BeautifulSoup(response.content, "html.parser")
    book_divs = soup.find_all("div", class_="item-root")
    # 遍历所有图书信息的元素
    for book_div in book_divs:
        # 提取图书标题
        title = book_div.find("div", class_="title").get_text(strip=True)
        # 提取图书链接
        link = book_div.find("a", class_="title-text")["href"]
        # 提取图书评分
        rating = (
            book_div.find("span", class_="rating_nums").get_text(strip=True)
            if book_div.find("span", class_="rating_nums")
            else "无评分"
        )
        # 提取图书评价人数
        rating_num = (
            book_div.find("span", class_="pl").get_text(strip=True)
            if book_div.find("span", class_="pl")
            else "少于10人评价"
        )
        # 提取图书封面图片链接
        img_src = (
            book_div.find("img", class_="cover")["src"]
            if book_div.find("img", class_="cover")
            else "无封面"
        )

        print(f"书名：{title}")
        print(f"链接：{link}")
        print(f"评分：{rating}")
        print(f"评价人数：{rating_num}")
        print(f"封面图片：{img_src}")
        print("---------------------------")


if __name__ == "__main__":
    print(douban_book_parse("https://book.douban.com/subject/26948148/"))
    # notion_helper = NotionHelper()
    # search_book()
    # print(fetch_subjects("malinkang","book","done",0))
    # print(search())
    # response = notion_helper.client.databases.retrieve(
    #     database_id=notion_helper.book_database_id
    # )
    # id = response.get("id")
    # properties = response.get("properties")
    # if properties.get("豆瓣链接") is not None and properties.get("豆瓣链接").get("type") == URL:
    #     filter = {
    #         "and": [
    #             {"property": "豆瓣链接", "url": {"is_not_empty": True}},
    #             {"property": "ISBN", "rich_text": {"is_empty": True}},
    #         ]
    #     }
    #     results = notion_helper.query_all_by_book(
    #         notion_helper.book_database_id, filter
    #     )
    #     for result in results:
    #         id  = result.get("id")
    #         url  = get_property_value(result.get("properties").get("豆瓣链接"))
    #         book = douban_book_parse(url)
    #         properties = {
    #             "书名":get_title(book.get("书名")),
    #             "封面":get_file(book.get("封面")),
    #             "ISBN":get_rich_text(book.get("ISBN"))
    #         }
    #         notion_helper.update_page(page_id=id,properties=properties,icon=get_icon(book.get("封面")))

    # else:
    #     print("你还没有创建豆瓣链接")
