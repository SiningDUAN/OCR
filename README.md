# ***Open CV***
Le principal axe de recherche de notre groupe est d'obtenir l'abstract du site web *Arxiv*. On essaie d'utiliser deux méthodes différentes (ici crawling directement sur html ou OCR) pour extraire les contenus de ce site web, telles que le titre et l'abstrait de chaque article. Et puis on va comparer les précisions de ces deux méthodes, quels sont les avantages et les inconvénients.

## *OCR*
* L’OCR (Optical character recognition),  c’est une idée de tirer le texte sur une image. 
* Il s'agit de l'utilisation de technologies optiques et informatiques pour lire un texte imprimé ou écrit sur le papier et convertir ce texte dans un format acceptable pour les ordinateurs et compréhensible pour les humains.

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
response = requests.get('http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=100')
feed = feedparser.parse(response.content)

urls=[]
results = {}
for entry in feed.entries:
   
    results[entry.id] = {"title": entry.title,
                         "abstract":entry.summary} 
    print(entry.id)
    urls.append(entry.id)
    #print(results[entry.id]['title'])
    print(results[entry.id]['title'],'abstract:')
    
```    
***ÉTAPE 2 : selenium***
```Python  
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # New import
import  time 
```
```Python
#selenium 
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ['enable-automation'])
options.add_experimental_option('prefs',  {
    "download.default_directory": r"C:\Users\dsnin\OneDrive\桌面\OpenCV\Scrapy\pdfs",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
    }
) 

#  Start up the marionette 
driver= webdriver.Chrome(options=options)

abstracts={}

# récupérer l'abstract du papier de recherche + l'url du pdf et télécharger ce pdf

for url in urls :
    # ouvrir la site web
    driver.get(url)
    # abstract et url du pdf
    ab=driver.find_element(By.NAME,'citation_abstract').get_attribute('content')
    purl=driver.find_element(By.NAME,'citation_pdf_url').get_attribute('content')
    abstracts[url]={'abstract':ab ,
                    'pdf_url':purl}
    driver.get(purl)
    abstract_path=os.path.join(r"C:\Users\dsnin\OneDrive\桌面\OpenCV\Scrapy\pdfs",url.split('/')[-1])
    abstract_path=os.path.join(abstract_path,".txt")
    print(abstracts[url])
    with open(abstract_path,"w+") as f:
        f.write(abstracts[url]['abstract'])
    time.sleep(15)
                                           
# quitter webdriver
driver.quit()
```

***2. deuxième méthode***
***2.1 decorator***
```Python
 - La fonction *clean* est définie pour l'outil d'extraction du code source *html* de l'outil.
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

***2.2 tesseract***
```Python
import os
import pytesseract
from PIL import Image

from pdf2image import convert_from_path
from PIL import Image
import pytesseract

import re 
 ```  

```Python
#tesseract ocr
filenames=os.listdir(r'C:\Users\dsnin\OneDrive\桌面\OpenCV\Scrapy\pdfs')  
path=r'C:\Users\dsnin\OneDrive\桌面\OpenCV\Scrapy\pdfs'
for file in filenames:
#file=filenames[0]
    if file.endswith('.pdf'):
        fileName=os.path.join(path, file)
        print(fileName)
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
        print(text)
        # Open text, clean it and time the operation
        # create dirty text
        text_path = fileName+".txt"
        text_clean_path=text_path+"_clean.txt"
        with open(text_path,"w+") as f:
            f.write(text)
        text_clean=clean_text(text_path)
        with open(text_clean_path,"w+") as f:
            f.write(text_clean)
        
        #print(text_clean)
 ```
 
# *Résolution*
* Visitez et acceptez la page web
* Extraction de données à partir de pages web
* transformer en texte l'abstract dans le pdf 

# *Conclusion*
* La première méthode est plus facile à mettre en œuvre et peut être extraite directement du code source dans html.
* La deuxième méthode présente certaines limites(dans notre opération, c'est difficile de trouver l'abstract dans différents pdfs, Le format de chaque article n'est pas tout à fait le même), mais elle est applicable à un groupe beaucoup plus large. 

# *Applications*
* Par ces données, on peut obtenir des informations claires et des données complètes de chaque pdf.
* On peut utiliser cet outil qui s'applique aussi aux autres sites.

# *Remerciements spéciaux*
* CSDN: une site nous permet de chercher la code
* Monsieur Kwirtz nous aide beaucoup sur la code en cours
