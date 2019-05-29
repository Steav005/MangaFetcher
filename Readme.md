# MangaFetcher

## Prerequirements
- Python 3
- (Optional for MOBI export) [KindleGen](https://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211) 

## Installation
1. Get yourself the repo
2. Run ``pip3 install -r requirements.txt`` in the repo folder

## Usage
```
usage: MangaFetcher.py [-h] [-m] [-e] manga

positional arguments:
  manga       manga to download from https://mangalife.us/. Example:
              https://mangalife.us/manga/Onepunch-Man -> Onepunch-Man

optional arguments:
  -h, --help  show this help message and exit
  -m, --mobi  If set, a MOBI E-Book of the manga will be exported at the end
              (can be set together with --epub)
  -e, --epub  If set, a EPUB E-Book of the manga will be exported at the end
              (can be set together with --mobi)
```
