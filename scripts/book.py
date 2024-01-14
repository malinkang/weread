import argparse
import hashlib
import json
import os

import pendulum
import requests
from notion_helper import NotionHelper

from weread_api import WeReadApi
import utils
from config import (
    book_properties_name_dict,
    book_properties_type_dict,
)

TAG_ICON_URL = "https://www.notion.so/icons/tag_gray.svg"
USER_ICON_URL = "https://www.notion.so/icons/user-circle-filled_gray.svg"
TARGET_ICON_URL = "https://www.notion.so/icons/target_red.svg"
BOOKMARK_ICON_URL = "https://www.notion.so/icons/bookmark_gray.svg"
BOOK_ICON_URL = "https://www.notion.so/icons/book_gray.svg"

d = {
    "封面": "cover",
    "日期": "date",
    "阅读时长": "readingTime",
    "阅读进度": "readingProgress",
    "开始阅读时间": "beginReadingDate",
    "最后阅读时间": "lastReadingDate",
    "阅读进度": "readingProgress",
    "阅读天数": "totalReadDay",
}


# 创建新的评分数据库
# 新增列
def get_all_book():
    results = notion_helper.query_all(notion_helper.book_database_id)
    books_dict = {}
    for result in results:
        books_dict[
            utils.get_property_value(result.get("properties").get("BookId"))
        ] = result.get("id")
        return books_dict


def url_to_md5(url):
    # 创建一个md5哈希对象
    md5_hash = hashlib.md5()

    # 对URL进行编码，准备进行哈希处理
    # 默认使用utf-8编码
    encoded_url = url.encode('utf-8')

    # 更新哈希对象的状态
    md5_hash.update(encoded_url)

    # 获取十六进制的哈希表示
    hex_digest = md5_hash.hexdigest()

    return hex_digest

def download_image(url, save_dir="cover"):
    # 确保目录存在，如果不存在则创建
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 获取文件名，使用 URL 最后一个 '/' 之后的字符串
    file_name = url_to_md5(url) + ".jpg"
    save_path = os.path.join(save_dir, file_name)

    # 检查文件是否已经存在，如果存在则不进行下载
    if os.path.exists(save_path):
        print(f"File {file_name} already exists. Skipping download.")
        return save_path

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)
        print(f"Image downloaded successfully to {save_path}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")
    return save_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    options = parser.parse_args()
    weread_cookie = os.getenv("WEREAD_COOKIE")
    branch = os.getenv("REF").split("/")[-1]
    repository = os.getenv("REPOSITORY")
    weread_api = WeReadApi()
    notion_helper = NotionHelper()
    books_dict = get_all_book()
    # 书架的书
    bookshelf_books = weread_api.get_bookshelf()
    # 笔记中的书
    notebooks = weread_api.get_notebooklist()
    notebooks = [d["bookId"] for d in notebooks if "bookId" in d]
    # 删除sort
    archive_dict = {}
    for archive in bookshelf_books.get("archive"):
        name = archive.get("name")
        bookIds = archive.get("bookIds")
        archive_dict.update({bookId: name for bookId in bookIds})
    books = bookshelf_books.get("books")
    books = [d["bookId"] for d in books if "bookId" in d]
    books = list(set(notebooks + books))
    sum = 0
    for index, bookId in enumerate(books):
        book = {}
        book["bookId"] = bookId
        if bookId in archive_dict:
            book["archive"] = archive_dict.get(bookId)
        bookInfo = weread_api.get_bookinfo(bookId)
        if bookInfo != None:
            book.update(bookInfo)
        readInfo = weread_api.get_read_info(bookId)
        # 研究了下这个状态不知道什么情况有的虽然读了状态还是1 markedStatus = 1 想读 4 读完 其他为在读
        readInfo.update(readInfo.get("readDetail", {}))
        readInfo.update(readInfo.get("bookInfo", {}))
        book.update(readInfo)
        # 时间优先取完成阅读的时间
        book["readingProgress"] = (
            100 if (book.get("markedStatus") == 4) else book.get("readingProgress", 0)
        ) / 100
        status = {1: "想读", 4: "已读"}
        book["status"] = status.get(book.get("markedStatus"), "在读")
        date = None
        if book.get("finishedDate"):
            date = book.get("finishedDate")
        elif book.get("lastReadingDate"):
            date = book.get("lastReadingDate")
        elif book.get("readingBookDate"):
            date = book.get("readingBookDate")
        book["date"] = date
        book["author"] = [
            notion_helper.get_relation_id(
                x, notion_helper.author_database_id, USER_ICON_URL
            )
            for x in book.get("author").split(" ")
        ]
        book["url"] = utils.get_weread_url(bookId)
        if book.get("categories"):
            book["categories"] = [
                notion_helper.get_relation_id(
                    x.get("title"), notion_helper.category_database_id, TAG_ICON_URL
                )
                for x in book.get("categories")
            ]
        properties = utils.get_properties(
            book, book_properties_name_dict, book_properties_type_dict
        )
        if book.get("date"):
            print(pendulum.from_timestamp(book.get("date"), tz="Asia/Shanghai"))
            notion_helper.get_date_relation(
                properties,
                pendulum.from_timestamp(book.get("date"), tz="Asia/Shanghai"),
            )
        cover = book.get("cover")
        if cover is not None and cover.startswith("http") and not cover.endswith(".jpg"):
            path = download_image(cover)
            cover = f"https://raw.githubusercontent.com/{repository}/{branch}/{path}"
        elif cover is None or not cover.startswith("http"):
            cover = BOOK_ICON_URL
        book["cover"] = cover
        print(f"一共{len(books)}本，当前是第{index}本，正在同步{book.get('title')} cover = {cover}")
        parent = {"database_id": notion_helper.book_database_id, "type": "database_id"}
        if book.get("bookId") in books_dict:
            sum += 1
            notion_helper.update_page(
                page_id=books_dict.get(book.get("bookId")),
                properties=properties,
                icon=utils.get_icon(book.get("cover")),
            )
        else:
            notion_helper.create_page(
                parent=parent,
                properties=properties,
                icon=utils.get_icon(book.get("cover")),
            )
    print(f"已存在 {sum}本")
