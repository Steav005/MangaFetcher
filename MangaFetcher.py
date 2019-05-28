import os
from concurrent.futures import ThreadPoolExecutor
import shutil
from bs4 import BeautifulSoup
import requests
import sys
import time

started = int(0)
finished = int(0)
manga = sys.argv[1]
html_stem = "https://mangalife.us"
manga_prefix = "/manga/"
read_prefix = "/read-online/"
chapter_list_class = "list chapter-list"
page_select_class = "PageSelect"
image_class = "CurImage"
chapter_prefix = "-chapter-"
page_prefix = "-page-"
html_suffix = ".html"

title_class = "SeriesName" #h1
manga_name = ""

executor = ThreadPoolExecutor(20)
printer = ThreadPoolExecutor(1)

if not os.path.exists(manga):
    os.makedirs(manga)

def print_t(t):
    print(t)

def increaseStarted():
    global started
    started += 1
    print("Pages " + str(finished) + "/" + str(started))

def increaseFinished():
    global finished
    finished += 1
    print("Pages " + str(finished) + "/" + str(started))


def initialize():
    url = html_stem + manga_prefix + manga
    html = requests.get(url, timeout=60).content
    mainpage = BeautifulSoup(html)
    global manga_name
    manga_name = mainpage.find('h1', {"class": title_class}).text
    print(manga_name)
    chapter = mainpage.find_all('a', href=True, chapter=True)
    for c in chapter:
        executor.submit(getChapter, c['chapter'], c['href'])

def getChapter(chapter, href):
    try:
        url = html_stem + href
        html = requests.get(url, timeout=60).content
        chapter_page = BeautifulSoup(html)
        pages_select = chapter_page.find('select', {"class": page_select_class})
        pages = pages_select.find_all('option', value=True)

        folder = manga + "/Chapter" + chapter
        if not os.path.exists(folder):
            os.makedirs(folder)

        for p in pages:
            executor.submit(getPage, chapter, p['value'])
            printer.submit(increaseStarted)
    except:
        printer.submit(print_t, "Error fetching Chapter " + chapter)


def getPage(chapter, page):
    file = manga + "/Chapter" + chapter + "/Page" + page + ".png"
    if os.path.exists(file):
        printer.submit(increaseFinished)
        return

    try:
        url = html_stem + read_prefix + manga + chapter_prefix + chapter + page_prefix + page + html_suffix
        html = requests.get(url, timeout=60).content
        page_soup = BeautifulSoup(html)
        image_url = page_soup.find("img", {"class": image_class}, src=True)['src']
        image_stream = requests.get(image_url, stream=True)
        with open(file, 'wb') as out_file:
            shutil.copyfileobj(image_stream.raw, out_file)
    except:
        printer.submit(print_t, "Error fetching Chapter " + chapter + " Page " + page)

    #ConvertGrayToPNG8(file)

    printer.submit(increaseFinished)

if __name__ == "__main__":
    initialize()

    while(1):
        if executor._work_queue.empty():
            break

        time.sleep(2)

    manga_args = ['--hq', '--upscale', '--format=EPUB', '--batchsplit=0', '--title', manga_name, manga]

    from kindlecomicconverter.comic2ebook import main as manga2ebook
    from multiprocessing import freeze_support

    freeze_support()
    manga2ebook(manga_args)




