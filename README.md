# ***OCR***
## *La comparaison entre OCR et Sélénium*
Le principal axe de recherche de notre groupe est d'obtenir l'abstract du site web *Arxiv*. On essaie d'utiliser deux méthodes différentes (ici crawling directement sur html ou OCR) pour extraire les contenus de ce site web, telles que le titre et l'abstrait de chaque article. Et puis on va comparer les précisions de ces deux méthodes, quels sont les avantages et les inconvénients

## *Le concept OCR*
* L’OCR (Optical character recognition),  c’est une idée de tirer le texte sur une image
* Il s'agit de l'utilisation de technologies optiques et informatiques pour lire un texte imprimé ou écrit sur le papier et convertir ce texte dans un format acceptable pour les ordinateurs et compréhensible pour les humains

# *Environnement de dévéloppement*
* macOS or Linux or Windows
* python (3.6+)

# *Paquets de dépendances*
* requests
* feedparser
* time
* os
* pytesseract
* re

# ***Source des données***
Le lien vers les données spécifiques est le suivant:
http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=100

# ***L'idée générale***
* Utiliser l'api arxiv pour récupérer les urls d'une centaine de papiers de recherche
* Utiliser sélénium avec un time.sleep(15) pour récupérer l'abstract du papier de recherche et l'url du pdf et puis télécharger ce pdf
* Utiliser tesseract pour transformer en texte l'abstract dans le pdf
* Comparer les performances de tesseract avec la "vraie valeur" de l'abstract : Extraire les mots-clés des fichiers PDF et écrire le nombre de mots-clés trouvés dans Excel

# *Mode d'emploi*
***ÉTAPE 0 : Chargez les paquets requis***
```Python
import requests 
import feedparser

#selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
import  time 

#tesseract
import os
import pytesseract
from PIL import Image

from pdf2image import convert_from_path
from PIL import Image
import pytesseract

import re  
import xlwt
```
***ÉTAPE 1 : APIs***
* Les API sont créées pour permettre l'accès aux données d'une manière contrôlée, telle que définie par les propriétaires des données
   - ouvrir http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=100 via *APIs*
   - Analyser tous les liens *urls* et trouver *l'abstract*  
```Python
"""
ouvrir l'api arxiv
"""
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
```    

***ÉTAPE 2 : crawling via selenium***
```Python
"""
1.récupérer l'abstract du papier de recherche et l'url du pdf 
2.télécharger ce pdf avec un time.sleep(15)
"""
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
        time.sleep(15)
        
    # quitter webdriver
    driver.quit()
```

***ÉTAPE 3 : decorator***
* L'utilisation d'un décorateur permet aux utilisateurs d'ajouter de nouvelles fonctionnalités à une fonction existante sans en modifier la structure
```Python
"""
Utilisez la fonction *clean* pour nettoyer le texte et le transformer en minuscules.
"""
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
```   

***ÉTAPE 4 : tesseract***
* Tesseract est un moteur de reconnaissance optique de caractères
* Dans notre processus,  nous avons utilisé le Tesseract pour réaliser cette idée OCR
```Python
"""
1.Convertir le première page du PDF en format jpg
2.Extraction le texte à partir d'images
3.Transformer en texte l'abstract dans le pdf
"""
#tesseract ocr
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
```
 
***ÉTAPE 5 : compter les mots-clés***
```Python
"""
1.Extraire les mots-clés du PDF 
2.Allez au mot-clé dans le txt
3.Inscrivez le nombre de mots-clés trouvés dans Excel
"""
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
 ```
 
***ÉTAPE 6 : Entrée du programme principal***
```Python
if __name__=="__main__":
    urls=getByAPI('http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=100')
    getBySelenium(urls, path)
    getByTesseract(path)
    saveInExcel(urls,"a",r"C:\Users\dsnin\OneDrive\桌面\OpenCV\Scrapy\excel\el.xls",path)
 ```
        
# *Résolution*
* Utilisation de *selenium*
* Utilisation de *tesseract* : transformer en texte l'abstract dans le pdf 
* Extraire les mots-clés du PDF et les mettre dans le pdf

# *Conclusion*
Après le calcul, nous obtenons une somme de proportions: 803.3337082, qui est pour tous les 99 articles. Avant, nous avons dit que si la somme des proportions des 10 mots clés d’un article est égale à 10, alors OCR et Sélénium n’ont pas de différence pour obtenir un texte, on peut choisir n’importe quelle.

Cependant, si cette somme est supérieure à 10, alors OCR est meilleure pour cet article. Par contre, c’est Sélénium qui est meilleure. Ici, la somme totale des 99 articles est 803, qui est inférieure à 990. Donc, en conclusion, sur la base des échantillons que nous avons pris, Sélénium est une meilleure méthode d'obtenir un texte

# *Difficultés*
Dans notre exploration, nous avons eu quelques difficultés à utiliser la méthode OCR pour capturer la partie ‘Abstract’ du PDF, et nous n'avons pas été en mesure de trouver une méthode plus précise et plus efficace pour capturer le paragraphe exact de l'abstract. 

C’est aussi la raison pour laquelle nos résultats ont également un certain biais.

Mais la méthode OCR est maintenant largement utilisée pour lire le texte dans l'image, et sera une méthode populaire à l'avenir.

# *Remerciements spéciaux*
* CSDN: une site nous permet de chercher la code
* Monsieur Kwirtz nous aide beaucoup sur la code en cours
