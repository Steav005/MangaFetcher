# MangaFetcher

## Prerequirements
- Python 3
- (Optional for MOBI export) [KindleGen](https://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211) 

## Installation
1. Get yourself the repo
2. Run ``pip3 install -r requirements.txt`` in the repo folder

## Usage
```
usage: MangaFetcher.py [-h] [-s START] [-e END] [-m] [-p] [-o] manga

positional arguments:
  manga                 manga to download from https://mangalife.us/. Example:
                        https://mangalife.us/manga/Onepunch-Man -> Onepunch-
                        Man

optional arguments:
  -h, --help            show this help message and exit
  -s START, --start START
                        (Default: 1) Sets the first chapter. (Decimal with
                        Point .)
  -e END, --end END     (Default is the last Chapter) Sets the last chapter
                        (inclusive) (Decimal with Point)
  -m, --mobi            If set, a MOBI E-Book of the manga will be exported at
                        the end (can be set together with --epub) NEEDS
                        KindleGen to be installed! https://www.amazon.com/gp/f
                        eature.html?ie=UTF8&docId=1000765211
  -p, --epub            If set, a EPUB E-Book of the manga will be exported at
                        the end (can be set together with --mobi)
  -o, --override        If set, removes corrupted Images after the download
                        (no attempted redownload) Might help with generation
                        of E-Books that contain corrupted uploaded images
```

### Example
``python MangaFetcher.py -s 15 -e 32 -m Onepunch-Man``
