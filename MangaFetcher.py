import os
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures.thread as thread
import shutil
from bs4 import BeautifulSoup
import requests
import sys
import argparse
from PIL import Image
import math


def set_args():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("manga",
                        help="manga to download from https://mangalife.us/.\nExample: https://mangalife.us/manga/Onepunch-Man -> Onepunch-Man")
    parser.add_argument("-s", "--start", help='(Default: 1)\n Sets the first chapter. \n (Decimal with Point .)')
    parser.add_argument("-e", "--end", help='(Default is the last Chapter)\n Sets the last chapter (inclusive)\n (Decimal with Point)')
    parser.add_argument("-m", "--mobi", help='If set, a MOBI E-Book of the manga will be exported at the end (can be set together with --epub)\nNEEDS KindleGen to be installed!\nhttps://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211', action="store_true")
    parser.add_argument("-p", "--epub", help='If set, a EPUB E-Book of the manga will be exported at the end (can be set together with --mobi)', action="store_true")
    parser.add_argument("-o", "--override",
                        help="If set, removes corrupted Images after the download (no attempted redownload)\nMight help with generation of E-Books that contain corrupted uploaded images",
                        action="store_true")
    args = parser.parse_args()


def print_t(t):
    print(t + "\n")


def increaseStarted():
    global started
    started += 1
    sys.stdout.write("\r" + "Pages " + str(finished) + "/" + str(started))
    sys.stdout.flush()


def increaseFinished():
    global finished
    finished += 1
    sys.stdout.write("\r" + "Pages " + str(finished) + "/" + str(started))
    sys.stdout.flush()


def initialize():
    global started
    global finished
    global manga
    global html_stem
    global manga_prefix
    global read_prefix
    global chapter_list_class
    global page_select_class
    global image_class
    global chapter_prefix
    global page_prefix
    global html_suffix
    global manga_name
    global start_chapter
    global end_chapter

    set_args()

    started = int(0)
    finished = int(0)
    manga = args.manga
    html_stem = "https://mangalife.us"
    manga_prefix = "/manga/"
    read_prefix = "/read-online/"
    chapter_list_class = "list chapter-list"
    page_select_class = "PageSelect"
    image_class = "CurImage"
    chapter_prefix = "-chapter-"
    page_prefix = "-page-"
    html_suffix = ".html"

    try:
        start_chapter = float(args.start)
        if start_chapter is None:
            start_chapter = 0
    except Exception:
        start_chapter = 0

    try:
        end_chapter = float(args.end)
        if end_chapter is None:
            end_chapter = math.inf
    except Exception:
        end_chapter = math.inf

    title_class = "SeriesName"  # h1
    manga_name = ""

    url = html_stem + manga_prefix + manga
    html = requests.get(url, timeout=60).content
    mainpage = BeautifulSoup(html, "lxml")
    page_title = mainpage.find('h1', {"class": title_class})
    if page_title is None:
        print(
            "Could not find the Manga\nMake sure you look for a manga on https://mangalife.us\nIf you find a Manga go to the title Page of the Manga\nExample: https://mangalife.us/manga/Onepunch-Man\nThen use the last part of the URL as the manga parameter\nIn the Example: Onepunch-Man")
        sys.exit()

    if not os.path.exists(manga):
        os.makedirs(manga)

    manga_name = page_title.text
    print(manga_name + "\n")
    chapter = mainpage.find_all('a', href=True, chapter=True)
    for c in chapter:
        number = float(c['chapter'])
        if number < start_chapter or number > end_chapter:
            continue
        futures.append(executor.submit(getChapter, c['chapter'], c['href']))


def getChapter(chapter, href):
    try:
        url = html_stem + href
        html = requests.get(url, timeout=60).content
        chapter_page = BeautifulSoup(html, "lxml")
        pages_select = chapter_page.find('select', {"class": page_select_class})
        pages = pages_select.find_all('option', value=True)

        folder = manga + "/Chapter" + chapter
        if not os.path.exists(folder):
            os.makedirs(folder)

        for p in pages:
            futures.append(executor.submit(getPage, chapter, p['value']))
            printer.submit(increaseStarted)
    except:
        printer.submit(print_t, "Error fetching Chapter " + chapter)


def removeImageIfCorrupted(path):
    try:
        img = Image.open(path)
        img.verify()
    except FileNotFoundError:
        return
    except:
        os.remove(path)


def getPage(chapter, page):
    file = manga + "/Chapter" + chapter + "/Page" + page + ".png"

    removeImageIfCorrupted(file)
    if os.path.exists(file):
        printer.submit(increaseFinished)
        return

    try:
        url = html_stem + read_prefix + manga + chapter_prefix + chapter + page_prefix + page + html_suffix
        html = requests.get(url, timeout=60).content
        page_soup = BeautifulSoup(html, "lxml")
        image_url = page_soup.find("img", {"class": image_class}, src=True)['src']
        image_stream = requests.get(image_url, stream=True, timeout=60)
        with open(file, 'wb') as out_file:
            shutil.copyfileobj(image_stream.raw, out_file)
    except:
        printer.submit(print_t, "Error fetching Chapter " + chapter + " Page " + page)

    if args.override:
        removeImageIfCorrupted(file)
    printer.submit(increaseFinished)


if __name__ == "__main__":
    try:
        global executor
        global printer
        global futures

        executor = ThreadPoolExecutor(20)
        printer = ThreadPoolExecutor(1)
        futures = []

        initialize()

        while (1):
            futures[0].result()
            futures.pop(0)

            if futures.__len__() == 0:
                break

        if not args.mobi:
            if not args.epub:
                sys.exit()

        ebook = []
        print("")

        if args.mobi:
            ebook.append(['--hq', '--upscale', '--format=MOBI', '--batchsplit=0', '--title', manga_name, manga])
        if args.epub:
            ebook.append(['--hq', '--upscale', '--format=EPUB', '--batchsplit=0', '--title', manga_name, manga])

        from kindlecomicconverter.comic2ebook import main as manga2ebook
        from multiprocessing import freeze_support

        freeze_support()

        for e in ebook:
            manga2ebook(e)
    except KeyboardInterrupt:
        printer._threads.clear()
        executor._threads.clear()
        thread._threads_queues.clear()
        print("\nInterrupted Fetching\nExiting now!")
        sys.exit()
