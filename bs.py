# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 09:27:40 2022

@author: dsnin
"""

# APIs
import requests  
import feedparser

#selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # New import
import  time  # Limit the number of times we can crawl a page at a time

#tesseract
import os
import pytesseract
from PIL import Image

from pdf2image import convert_from_path
from PIL import Image
import pytesseract

import re  
import xlwt #writer of excel

urls=[]  
results = {}   
abstracts={} 
path=r"C:\Users\dsnin\OneDrive\桌面\OpenCV\Scrapy\ppp"

#récupérer l'info par API
def getByAPI(urlAPI):
    #uriliser l'API de arxiv
    response = requests.get(urlAPI)
    feed = feedparser.parse(response.content)  
    for entry in feed.entries:
        results[entry.id] = {"title": entry.title,
                             "abstract":entry.summary} 
        urls.append(entry.id) 
        
#récupérer l'abstracts et télécharger le pdfs par selenium 
def getBySelenium(urls,path) :
    options = webdriver.ChromeOptions()  
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_experimental_option('prefs',  {
        "download.default_directory":path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True   
        }
    ) 

    #  Start up the marionette 
    driver= webdriver.Chrome(options=options)


    # récupérer l'abstract du papier de recherche + l'url du pdf et télécharger ce pdf
   
    for url in urls :
        # ouvrir la site web
        driver.get(url)
        # abstract et url du pdf
        ab=driver.find_element(By.NAME,'citation_abstract').get_attribute('content')
        purl=driver.find_element(By.NAME,'citation_pdf_url').get_attribute('content')
        abstracts[url]={'abstract':ab ,
                        'pdf_url':purl}
        # télécharger pdf url
        driver.get(purl)
        abstract_path=os.path.join(path,url.split('/')[-1])            
        abstract_path+=".txt"    
        #print(abstract_path)
        #print(abstracts[url])
        with open(abstract_path,"w+") as f:
            f.write(abstracts[url]['abstract'])  
        time.sleep(3)
        
    # quitter webdriver
    driver.quit()

# New decorator to clean text
def clean(func):
    #clean(clean_text)
    def wrapper(*args):
        #wrapper(file_path)
        text = func(*args)
        #text=clean_text(file_path)
        text = re.sub(r'None'," ",text)
        text = re.sub(r'\n'," ",text)
        text = re.sub(r'\n      '," ",text)
        text = re.sub(r'\t'," ",text)
        text = re.sub(r'\t\t'," ",text)
        text = re.sub(r'\n\t\t'," ",text)
        text = re.sub(r'  +', ' ', text)
        text = re.sub('>\s<', '><', text)
        text = text.lower()
        return(text)
    return(wrapper)

# Open text, clean it and time the operation
@clean
def clean_text(file_path):
    with open(file_path,"r") as f:
        txt = f.read()
    return(txt)

    
def getByTesseract(path):
    filenames=os.listdir(path)  
    com=0
    for file in filenames:
        if file.endswith('.pdf'):
            fileName=os.path.join(path, file)
            # tranformer pdf en image
            pages = convert_from_path(fileName,poppler_path=r'C:\Program Files\poppler-0.68.0\bin')
            imageFile=fileName+".jpg"
            pages[0].save(imageFile,'JPEG')   
            # Extraction de texte à partir d'images
            image = Image.open(imageFile)
            text = pytesseract.image_to_string(image)  
            if not re.match('Abstract',text) == None : 
                text=re.split('Abstract',text,1)[1]     
            if not re.match('INTRODUCTION',text) == None : 
                text=re.split('INTRODUCTION',text,1)[0]  
            text_list=text.split(".")     
            text="" 
            if len(text_list)>10 :   
                for i in range(10):
                    text=text+"."+text_list[i]
            else:
                for i in range(len(text_list)): 
                    text=text+"."+text_list[i]
            # Open text, clean it and time the operation
            # create dirty text
            text_path = fileName+".txt"
            text_clean_path=text_path+"_clean.txt"
            with open(text_path,"w+") as f:
                f.write(text)
            text_clean=clean_text(text_path)
            with open(text_clean_path,"w+") as f:
                f.write(text_clean)
        print(com)
        com+=1
    
#récupérer les mots clés dans le fichier_abstract "path"
def loadKeyWords(path):  
    new_list=[]
    dic={}
    list_sort=[]
    with open(path,"r+") as f:
       txt=f.read()  
       txt=txt.lower()
       str_list=txt.split()
       for s in str_list :
           if s not in new_list and len(s)>3:
               new_list.append(s)
       #print(new_list)
       for s in new_list:
           dic[s]=str_list.count(s)
       list_sort=sorted(dic.items(),key=lambda item:item[1])
       #(index) start stop step
    return list_sort[-1:-11:-1]

#compte le nombre de présence de chaque mot de li dans le fichier_text_clean "path"
def countNP(path,li):
    l=[]
    with open(path,"r+") as f:
        txt=f.read()
        txt_list=txt.split()
        #tuple=(mot,nombre de présence)
        for tup in li:
           #print(txt_list.count(tup[0])/tup[1])
           #liste de 10 nombres de présence des mots
           l.append(txt_list.count(tup[0]))           
    return l                

#sauvegarder dans l'excel
def saveInExcel(urls, sheet_name,Epath,pathPDF):
    # create a new workbook
    workbook = xlwt.Workbook()  
    # add a sheet in workbook
    sheet = workbook.add_sheet(sheet_name)  
    i=0
    path=pathPDF

    for url in urls:
        abs_path=os.path.join(path,url.split('/')[-1])
        abs_path+=".txt" 
        txt_name=re.sub('v\d*', '', url.split('/')[-1])+".pdf.txt_clean.txt"
        txt_path=os.path.join(path,txt_name)
    
   
        list1=loadKeyWords(abs_path)
        if os.path.exists(txt_path):
            list2=countNP(txt_path,list1)
            sheet.write(i*6,0,str(i)+":"+url)
            sheet.write(i*6+1,0,"keyWords")
            sheet.write(i*6+2,0,"abstract[vrai_value]")
            sheet.write(i*6+3,0,"text_clean")
            sheet.write(i*6+4,0,"proportion")
            for j in range(10):
                sheet.write(i*6+1,j+1,list1[j][0])
                sheet.write(i*6+2,j+1,list1[j][1])
                sheet.write(i*6+3,j+1,list2[j])
                sheet.write(i*6+4,j+1,list2[j]/list1[j][1])
            # save workbook
            workbook.save(Epath)  
            i+=1
            time.sleep(3)
            print(i)

if __name__=="__main__":
    urls=getByAPI('http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=100')
    getBySelenium(urls, path)
    getByTesseract(path)
    saveInExcel(urls,"a",r"C:\Users\dsnin\OneDrive\桌面\OpenCV\Scrapy\excel\el.xls",path)