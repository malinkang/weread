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
from bs4 import BeautifulSoup
TAG_ICON_URL = "https://www.notion.so/icons/tag_gray.svg"
USER_ICON_URL = "https://www.notion.so/icons/user-circle-filled_gray.svg"
BOOK_ICON_URL = "https://www.notion.so/icons/book_gray.svg"

def search_neodb(title, isbn):
    query = title if isbn == None or isbn.strip() == "" else isbn
    print(f"search_neodb {title} {isbn} ")
    params = {"query": query, "page": "1", "category": "book"}
    r = requests.get("https://neodb.social/api/catalog/search", params=params)
    books = r.json().get("data")
    if len(books) == 0:
        return None
    results = list(filter(lambda x: x.get("isbn") == query, books))
    if len(results) == 0:
        results = list(filter(lambda x: x.get("display_title") == query, books))
    if len(results) == 0:
        return None
    result = results[0]
    douban_url = list(
        filter(
            lambda x: x.get("url").startswith("https://book.douban.com"),
            result.get("external_resources", []),
        )
    )
    return {
        "neodb_url": result.get("id"),
        "douban_url": None if (len(douban_url) == 0) else douban_url[0].get("url"),
        "author": result.get("author", []),
    }
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def get_douban_cover(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content)
    cover =  soup.find(id="mainpic").img["src"]
    return cover

def insert_book_to_notion(books, index, bookId):
    """插入Book到Notion"""
    book = {}
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
    if(book.get("author")=="公众号"):
        if not book.get("cover").startswith("http"):
           book["cover"] = BOOK_ICON_URL
        if book.get("cover").startswith("http") and not book.get("cover").endswith(".jpg"):
           book["cover"] = f"{book.get('cover')}.jpg"
        book["author"] = ["公众号"]
    else:
        neodb_book = search_neodb(book.get("title"),book.get("isbn"))
        if neodb_book:
            book.update(neodb_book)
            if not book.get("cover").endswith(".jpg"):
                book["cover"] = get_douban_cover(book.get("douban_url"))
        else:
             book["cover"] = book.get("cover").replace('/s_', '/t7_');
             book["author"] = book.get("author").split(" ")
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
        for x in book.get("author")
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
        notion_helper.get_date_relation(
            properties,
            pendulum.from_timestamp(book.get("date"), tz="Asia/Shanghai"),
        )
    print(f"正在插入《{book.get('title')}》,一共{len(books)}本，当前是第{index+1}本。")
    parent = {"database_id": notion_helper.book_database_id, "type": "database_id"}
    if bookId in notion_books:
        notion_helper.update_page(
            page_id=notion_books.get(bookId).get("pageId"),
            properties=properties,
            icon=utils.get_icon(book.get("cover")),
        )
    else:
        notion_helper.create_page(
            parent=parent,
            properties=properties,
            icon=utils.get_icon(book.get("cover")),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    options = parser.parse_args()
    weread_cookie = os.getenv("WEREAD_COOKIE")
    branch = os.getenv("REF").split("/")[-1]
    repository = os.getenv("REPOSITORY")
    weread_api = WeReadApi()
    notion_helper = NotionHelper()
    notion_books = notion_helper.get_all_book()
    bookshelf_books = weread_api.get_bookshelf()
    bookProgress = bookshelf_books.get("bookProgress")
    bookProgress = {book.get("bookId"): book for book in bookProgress}
    archive_dict = {}
    for archive in bookshelf_books.get("archive"):
        name = archive.get("name")
        bookIds = archive.get("bookIds")
        archive_dict.update({bookId: name for bookId in bookIds})
    not_need_sync = []
    for key, value in notion_books.items():
        if (
            key not in bookProgress
            or value.get("readingTime") == bookProgress.get(key).get("readingTime")
        ) and archive_dict.get(key) == value.get("category"):
            not_need_sync.append(key)
    notebooks = weread_api.get_notebooklist()
    notebooks = [d["bookId"] for d in notebooks if "bookId" in d]
    books = bookshelf_books.get("books")
    books = [d["bookId"] for d in books if "bookId" in d]
    books = list((set(notebooks) | set(books)) - set(not_need_sync))
    for index, bookId in enumerate(books):
        insert_book_to_notion(books, index, bookId)
