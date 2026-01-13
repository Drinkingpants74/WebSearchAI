import httpx
from bs4 import BeautifulSoup
import traceback
from urllib.parse import urlparse
from readability import Document
import re

import Settings

sentenceEndings = r"[.!?]\s+"
bannedURLs = ["youtube", "duckduckgo", "google", "bing"]
usedURLs = []
idToURL = {}
previousInfo = {}
# {
#   "ID": int
#   "CHUNK": str
# }

chunkID = 0

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
searchURLs = [
    ("DuckDuckGo", "https://html.duckduckgo.com/html/?q=", ".result__url"),
    ("Brave", "https://search.brave.com/search?q=", ".snippet a"),
    ("Startpage", "https://www.startpage.com/do/search?language=english&cat=web&q=", "h3.clk a"),
    ("Qwant", "https://www.qwant.com/?q=", "[data-testid=webResult] a"),
    ("Bing", "https://www.bing.com/search?q=", "li.b_algo h2 a"),
    # ("Searx", "https://priv.au/search?q=", "&format=json"), # Needs new Instance to stop '429 Too Many Requests' Error
]

def search(query):
    urls = []
    for name, baseURL, selector in searchURLs:
        try:
            if name != "Searx":
                response = httpx.get(baseURL + query, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                urls = [a["href"] for a in soup.select(selector)] # pass all URLS | Sort and Filter in cleanup()
                if urls:
                    break
            else:
                response = httpx.get(baseURL + query + selector, headers=headers)
                response.raise_for_status()
                results = response.json().get("results", [])
                urls = [r.get("url") for r in results]  # pass all URLS | Sort and Filter in cleanup()
                if urls:
                    break
        except Exception as e:  # Broader catch for debugging
            print(f"Request failed for {name}: {e}")
            # traceback.print_exc()
            continue

    if urls:
        return cleanup(urls)
    return None

def cleanup(urls):
    global previousInfo, usedURLs, chunkID, bannedURLs, idToURL
    content = []
    urlCount = 0
    for url in urls:
        if (urlCount >= 5):
            break
        if (url in usedURLs):
            continue
        banned = False
        for i in bannedURLs:
            if (str(i) in url.lower()):
                banned = True
                break
        for i in Settings.userBlacklist:
            if (str(i) in url.lower()):
                # print(f"BANNING: {str(i)}")
                banned = True
                break
        if (banned):
            continue
        if (urlparse(url).scheme not in ("http", "https")) or (not urlparse(url).netloc):
            continue
        try:
            page = httpx.get(url, headers=headers)
            # Block Redirects and Trackers
            if (page.status_code in (301, 302, 303, 307, 308)):
                continue
            page.raise_for_status()
            html = page.text
            doc = Document(html)
            cleanHTML = doc.summary()
            soup = BeautifulSoup(cleanHTML, "lxml")
            main_content = soup.get_text(strip=True)
            main_content_split = main_content.split("\n")
            for chunk in main_content_split:
                if (chunk.strip() != ""):
                    if (len(chunk.split()) >= 350):
                        for miniChunk in split_into_sentences(chunk):
                            content.append({"ID": chunkID, "CHUNK": miniChunk})
                            previousInfo[chunkID] = miniChunk
                            usedURLs.append(url)
                            idToURL[chunkID] = url
                            chunkID += 1
                    else:
                        content.append({"ID": chunkID, "CHUNK": chunk})
                        previousInfo[chunkID] = chunk
                        usedURLs.append(url)
                        idToURL[chunkID] = url
                        chunkID += 1
            urlCount += 1
        except Exception as e:
            print(f"Cleanup failed for {url}: {e}")
            traceback.print_exc()
            continue
    # print("CONTENT: ", type(content))
    return content if content else None


def split_into_sentences(text: str):
    sentences = re.split(sentenceEndings, text)
    result = []
    sentID = 0
    newChunk = ""
    prevChunk = ""
    for sentence in sentences:
        sentID += 1
        # print(f"{sentID}: {sentence}")
        newChunk += sentence + " "
        if (len(newChunk.split(" ")) >= 200) and (len(newChunk.split(" ")) <= 300):
            result.append(newChunk)
            newChunk = ""
            prevChunk = ""
        elif (len(newChunk.split(" ")) > 300):
            result.append(prevChunk)
            newChunk = sentence
            prevChunk = ""
        else:
            prevChunk += sentence

    if (newChunk != ""):
        result.append(newChunk)
        newChunk = ""

    return result
