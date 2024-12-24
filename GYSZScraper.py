import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import argparse
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import time
import datetime
from multiprocessing import Pool
from orderAbbreviation import orderAbbreviation
from deleteDr import deleteDr

honapok = {
    "január": 1,
    "február": 2,
    "március": 3,
    "április": 4,
    "május": 5,
    "június": 6,
    "július": 7,
    "augusztus": 8,
    "szeptember": 9,
    "október": 10,
    "november": 11,
    "december": 12
}

def str2date(datum):
    reszek = [d.split(".")[0].strip() for d in datum.strip().split(" ")]
    return datetime.date(int(reszek[0]), honapok[reszek[1]], int(reszek[2]))

def processSeminarist(link, headless):
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    driver.get(link)

    driver.implicitly_wait(2)
    nonBreakSpace = u'\xa0'

    soup = BeautifulSoup(driver.page_source.replace("&nbsp;", " "), 'html.parser')
    driver.quit()

    imgSrc = ""
    
    try:
        imgSrc = soup.select_one("section a img").get("src")
    except:
        pass
    try:
        birth = str2date(soup.select_one("div.tiny p:first-of-type").text.split("Született: ")[1].split("Plébánia: ")[0].split(", ")[-1])
    except Exception as e:
        birth = None
        print(f"{link} - Failed to fetch birthdate.")
    return {
        "name": soup.select_one("header h1").text, 
        "seminarist": True, # Papnövendék,
        "img": imgSrc,
        "src": link,
        "birth": birth
    }


@deleteDr
@orderAbbreviation
def GYSZ(filename=None, year=None, headless = True):

    url = 'https://bjhf.hu/papnevelo-intezet/szemelyzet/kispapok'
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    driver.get(url)

    driver.implicitly_wait(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    kispapok = []
    for kispap in soup.select("a.card"): # Táblázat sorainak keresése
        kispapok.append(kispap['href']) # Papi oldalak linkjei

    kispaplista = []
    with Pool() as p:
        kispaplista = p.starmap(processSeminarist, [(kispap, headless) for kispap in kispapok])

    kispaplista = [x for x in kispaplista if x is not None]

    if filename == None:
        return kispaplista
    else:
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(kispaplista, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Győri Szeminárium papnövendékeinek adatai')
    parser.add_argument('--filename', required=False, action="store", default=None,
                        help="JSON to save. If not set, the result will be displayed on screen")

    args = parser.parse_args()

    if args.filename == None:
        print(GYSZ(args.filename, headless = False))
    else:
        GYSZ(args.filename, headless = False)
