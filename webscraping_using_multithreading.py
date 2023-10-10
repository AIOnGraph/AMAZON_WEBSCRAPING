from bs4 import BeautifulSoup
import requests
import csv
import time
import threading
import concurrent.futures
lock = threading.Lock()
# headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.example.com/',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

count=0   
def isObjectEmpty(productdetailname):
    if productdetailname:
        return productdetailname.text
    else:
        return None
listOfDict=[]
def scrapProductDetails(url):
    dict1={}
    res=requests.get(url,headers=headers)
    soup=BeautifulSoup(res.text,"html.parser")
    fullcontainer=soup.find(class_="a-container")
    title=fullcontainer.find(id="productTitle")

    if title:
        
        imagecontainer=fullcontainer.find(id="imgTagWrapperId")
        images=imagecontainer.find_all("img")
        image=images[0]['src']
        price=fullcontainer.find(class_="a-price-whole")
        price=isObjectEmpty(price)
        mrp=fullcontainer.find(class_="a-price a-text-price")
        mrp1=isObjectEmpty(mrp)
        finalmrp=None
        if mrp1:
            finalmrp=mrp.find(class_="a-offscreen")
            finalmrp=isObjectEmpty(finalmrp)
        ratingcontainer=fullcontainer.find(id="averageCustomerReviews")
        ratingcontainer1=isObjectEmpty(ratingcontainer)
        rating=None
        if ratingcontainer1:
            rating=ratingcontainer.find(class_='a-size-base a-color-base')
            rating=isObjectEmpty(rating)
        listofdes=fullcontainer.find(class_="a-unordered-list a-vertical a-spacing-mini")
        listofdes=isObjectEmpty(listofdes)
        dict1["PRODUCT TITLE"]=title.text
        dict1["Images"]=image
        dict1["MRP"]=finalmrp
        dict1["PRICE"]=price
        dict1["RATING"]=rating
        dict1["DESCRIPTION"]=listofdes
        listOfDict.append(dict1)
        if len(listOfDict)>=19: 
            with lock:
                result=writeInFile(listOfDict)
                listOfDict.clear()
                print(result)
    return True

def writeInFile(listOfDict):
    '''It takes the details of a particular product in a dict and writes that to a CSV file.'''
    with open("/home/ongraph/Desktop/practice/webscrap06.csv",mode="a",encoding="utf-8") as file:
        fieldnames = listOfDict[0].keys()
        productfile = csv.DictWriter(file, fieldnames=fieldnames)
        global count
        if count == 0:
            productfile.writeheader()
            count = count + 1
        for item in listOfDict:  
            productfile.writerow(item)
    return f"Wrote results for 19 products in file"


def getAllPagesHref(keyword,no_of_pages):
    listOfEveryPageUrls = []
    url = f"https://www.amazon.in/s?k={keyword}&page=1"
    res = requests.get(url, headers=headers)
    time.sleep(1)
    soup1 = BeautifulSoup(res.text, "html.parser")
    hrefsclass = soup1.find_all(class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")
    if hrefsclass:
        maxPages = int(soup1.find(class_="s-pagination-item s-pagination-disabled").text)
        if no_of_pages is None:
            no_of_pages = maxPages  
        elif 1 <= no_of_pages <= maxPages:
            pass  
        else:
            return f"Number of pages entered are invalid"
        
        for i in range(1, no_of_pages + 1):
            url = f"https://www.amazon.in/s?k={keyword}&page={i}"
            listOfEveryPageUrls.append(url)
        result= fetchEveryPageProductHref(listOfEveryPageUrls)
        return result
   
    else:
        return f"No results for {keyword} try checking your spelling or retry after some time"
   

    
def fetchEveryPageProductHref(listOfEveryPageUrls):
    listOfProductLinks=[]
    index=0
    for i in range(0, len(listOfEveryPageUrls)):
        onePageUrl=listOfEveryPageUrls[i]
        res=requests.get(onePageUrl,headers=headers)
        time.sleep(1)
        print(f"Page no {i+1} is started ")
        soup1=BeautifulSoup(res.text,"html.parser")
        hrefsclasses=soup1.find_all(class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal" )
        for hrefclass in hrefsclasses:
            link=hrefclass.get("href")
            prefix="https://www.amazon.in"
            url=f"{prefix}{link}"
            listOfProductLinks.append(url)
            if len(listOfProductLinks)>=index+20:
                result_for_20_Multithreaded_product=doMultithreading(listOfProductLinks[index:index+20])
                print(result_for_20_Multithreaded_product)
                index=index+20
    return f"Scrapped the details of {len(listOfProductLinks)} products"

def doMultithreading(listOfProductLinks):
    max_threads = 4
    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
        results = [executor.submit(scrapProductDetails, productlink) for productlink in listOfProductLinks]
        concurrent.futures.wait(results)

    return f"Multithreading completed for current batch"
        


def enterKeyword():  
    '''It takes input from keyboard for searching and call the searchProduct(input)''' 
    keyword=input("SEARCH HERE----------> ") 
    no_of_pages=int(input("ENTER NO. OF PAGES TO SCRAP----------> "))
    start=time.perf_counter()
    result=getAllPagesHref(keyword,no_of_pages)
    print(result)
    elapsed=time.perf_counter()-start
    return f"{elapsed} sec spent on scrapping the result"


 
if __name__ == "__main__":
    result=enterKeyword()
    print(result)