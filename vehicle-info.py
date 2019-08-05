import pytesseract
import argparse
import sys
import re
import os
import requests
import cv2
import json 
import numpy as np
from time import sleep
try:
    import Image
except ImportError:
    from PIL import Image, ImageEnhance
from bs4 import BeautifulSoup, SoupStrainer
from urllib import urlretrieve
from io import BytesIO


app_url = 'https://vahan.nic.in/nrservices/faces/user/searchstatus.xhtml'
captcha_image_url = 'https://vahan.nic.in/nrservices/cap_img.jsp'
number = sys.argv[1]


r = requests.get(url=app_url)
cookies = r.cookies
soup = BeautifulSoup(r.text, 'html.parser')
viewstate = soup.select('input[name="javax.faces.ViewState"]')[0]['value']

iresponse = requests.get(captcha_image_url)
img = Image.open(BytesIO(iresponse.content))
img.save("downloadedpng.png")

def resolve(img):
	enhancedImage = enhance()
	return pytesseract.image_to_string(enhancedImage)

def enhance():
	img = cv2.imread('downloadedpng.png', 0)
	kernel = np.ones((2,2), np.uint8)
	img_erosion = cv2.erode(img, kernel, iterations=1)
	img_dilation = cv2.dilate(img, kernel, iterations=1)
	erosion_again = cv2.erode(img_dilation, kernel, iterations=1)
	final = cv2.GaussianBlur(erosion_again, (1, 1), 0)
	return final


print('Resolving Captcha')
captcha_text = resolve(img)
extracted_text = captcha_text.replace(" ", "").replace("\n", "")
print("OCR Result => ", extracted_text)
print(extracted_text)
button = soup.find("button",{"type": "submit"})

encodedViewState = viewstate.replace("/", "%2F").replace("+", "%2B").replace("=", "%3D")
data = {
'javax.faces.partial.ajax':'true',
'javax.faces.source': button['id'],
'javax.faces.partial.execute':'@all',
'javax.faces.partial.render': 'rcDetailsPanel resultPanel userMessages capatcha txt_ALPHA_NUMERIC',
button['id']:button['id'],
'masterLayout':'masterLayout',
'regn_no1_exact': number,
'txt_ALPHA_NUMERIC': extracted_text,
'javax.faces.ViewState': viewstate,
'j_idt32':''
}
query = "javax.faces.partial.ajax=true&javax.faces.source=%s&javax.faces.partial.execute=%s&javax.faces.partial.render=rcDetailsPanel+resultPanel+userMessages+capatcha+txt_ALPHA_NUMERIC&j_idt42=j_idt42&masterLayout=masterLayout&j_idt32=&regn_no1_exact=%s&txt_ALPHA_NUMERIC=%s&javax.faces.ViewState=%s"%(button['id'], '%40all', number, extracted_text, encodedViewState)
for i in cookies:
	print(i)
headers = {
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Accept': 'application/xml, text/xml, */*; q=0.01',
	'Accept-Language': 'en-us',
	'Accept-Encoding': 'gzip, deflate, br',
	'Host': 'vahan.nic.in',
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15',
	'Cookie': 'JSESSIONID=%s; SERVERID_7081=vahanapi_7081; SERVERID_7082=nrservice_7082' % cookies['JSESSIONID'],
	'X-Requested-With':'XMLHttpRequest',
	'Faces-Request':'partial/ajax',
	'Origin':'https://vahan.nic.in',
	'Referer':'https://vahan.nic.in/nrservices/faces/user/searchstatus.xhtml',
    'Connection':'keep-alive'
    # 'User-Agent': 'python-requests/0.8.0',
    # 'Access-Control-Allow-Origin':'*',
}
print(headers)

print("\n\nCookie JSESSIONID =>")
print(cookies['JSESSIONID'])
print("\nData => \n")
print(data)
sleep(2.0)
req = requests.post(url=app_url, data=data, headers=headers, cookies=cookies)
print("\n\nRequest =>\n")
print(req)
rsoup = BeautifulSoup(req.text, 'html.parser')
print("Mark: request soup => ")
print(rsoup.prettify())

table = SoupStrainer('tr')
tsoup = BeautifulSoup(rsoup.get_text(), 'html.parser', parse_only=table)

print("Table Soup => ")
print(tsoup.prettify())
#MARK: Result Table not appending to the response data
#Fix Needed



