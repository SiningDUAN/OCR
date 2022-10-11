# ***Open CV***



## *Crawling le contenu du site web des films*
* Le principal axe de recherche de notre groupe est de crawling le site web des film. Nous essayons d'utiliser nos outils pour extraire des données sur les films, telles que la date de sortie, le réalisateur, les acteurs, les étoiles et le genre de chaque film. Les données extraites seront ensuite utilisées pour recommander des films aux utilisateurs et choisir leurs films préférés sans marcher sur le tonnerre.
* Il en va de même pour les autres sites web. On peut utiliser cette méthode pour explorer n'importe quel site web.

# *Environnement de dévéloppement*
* macOS or Linux or Windows
* python (3.6+)

# *Paguets de dépendances*
* requests

# ***Source des données***
## *Description des sources de données*


## *Source des données pour ce projet*
Le lien vers les données spécifiques est le suivant:


# ***L'idée générale de crawler***
* Avant d'extraire les informations, il faut utiliser un outil *selenium* qui permet d'effectuer les tests automatisés sur les navigateurs Web (ici Google chrome). Ensuite, il faut installer un chauffeur Chromedrive
* Déterminer le chemin de l'url crawlée, le paramètre headers
* Envoyer une demande : En utilisant le module de demande de données requests et *headers*, nous envoyons une requête pour l'adresse url du paquet que nous trouvons et obtenons les données de la réponse
    * Le rôle de headers : utilisé pour déguiser le code python sans être reconnu comme un crawler
* Analyser les données : extraire le contenu des données que nous voulons
* Sauvegarder les données 

# *Mode d'emploi*
*Cet outil se compose de deux scripts:*

***1. ***
 - La fonction *clean* est définie dans *data.py* pour l'outil d'extraction du code source *html* de l'outil.
 - La fonction *clean* extrait : le titre du film, la note, la catégorie du film, le réalisateur, l'acteur et le synopsis via deux modules, *beautifulsoup* et *re*.
```Python
```Python
import requests  # Execute a URL request and get the HTML of the site
import feedparser
```
```Python
response = requests.get('http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=100')
feed = feedparser.parse(response.content)

urls=[]
results = {}
for entry in feed.entries:
   
    results[entry.id] = {"title": entry.title,
                         "abstract":entry.summary} 
    print(entry.id)
#{   url:    {"title":***,"abstract":***} }
    urls.append(entry.id)
    #print(results[entry.id]['title'])
    print(results[entry.id]['title'],'abstract:')
    
```    
***2. ***
 - C'est le programme principal de l'outil, qui définit une classe UGC, principalement utilisée pour récupérer les liens vers les films depuis ugc.fr et pour obtenir les détails *html* de chaque film.
 - La fonction *main*, qui est la fonction d'exécution de la classe UGC, appelle respectivement les fonctions suivantes:
      * Fonction *get_links* : ouvrir https://www.ugc.fr/cinema.html?id=30 via *selenium* et récupère tous les liens vers le film.
      * Chaque lien de film obtenu via *get_links* est donné à la fonction *get_info*, qui ouvrira le lien du film avec le module *requests* et récupérera le code source *HTML*.
      * Le code source *html* obtenu à partir de *get_info* est donné à la fonction *clean* de data.py, qui est utilisée pour extraire les informations du film.
      * Une fois que toutes les informations sur les films ont été extraites, la fonction *save_data* stocke les données dans le fichier *results.csv*.
  
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

***3. ***
```Python
# New decorator to clean text
def clean(func):
    #clean(clean_text)
    def wrapper(*args):
        #wrapper(file_path)
        text = func(*args)
        #text=clean_text(file_path)
        "3 1 ->2"
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

***4. ***
```Python
#tesseract
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
#file=filenames[60]
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
        #text_list=re.split(r'Abstract',text,flags=re.I) 
        #text_list=text_list[1]
        text_list=text.split(".")
        text=""
        #""+"."+"(Dated: today)"=".(Dated: today)"
        #text_list[0]->text_list[9]
        for i in range(10):
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
        
        print(text_clean)      
 ```
 
# *Résolution*
* Visitez et acceptez la page web
* Extraction de données à partir de pages web
* Sauvegarder les données localement 

# *Conclusion*
* Le type de *animation* obtient un nombre d'étoiles plus élevées.
* Les films qui sont sortis relativement tôt ont été mieux reçus.

# *Applications*
* Par ces données, on peut obtenir des informations claires et des données complètes de chaque film dans notre result.CSV qui nous permet de choisir un film préféré rapidement.
* On peut utiliser cet outil qui s'applique aussi aux autres sites.

# *Remerciements spéciaux*
* CSDN: une site nous permet de chercher la code
* Monsieur Pelletier nous aide beaucoup sur la code en cours
