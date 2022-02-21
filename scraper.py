
from bs4 import BeautifulSoup
from numpy import NaN
import requests
import re
import pandas as pd
import requests
import re

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
}


# def parseScholar(url):
#     url='https://scholar.google.com/citations?user=2db-asAAAAAJ&hl=en'
#     googleScholarPage=soup.find('table',id="gsc_rsb_st")

def getGoogleUrl(keyword):

    # keyword=keyword.strip().replace(' ','+')
    googleSearchUrl='https://www.google.com/search?as_q=&as_epq=&as_oq={}&as_eq=&as_nlo=&as_nhi=&lr=&cr=&as_qdr=all&as_sitesearch=https%3A%2F%2Fscholar.google.com%2Fcitations&as_occt=any&as_filetype=&tbs='.format(keyword)
    page = requests.get(googleSearchUrl,headers=headers)
    html_doc= page.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    # print(soup.prettify)
    print(googleSearchUrl)
    googleScholarPage=soup.find_all('a',href=True)
    for i in googleScholarPage:
        if 'https://scholar.google.com/citations?'in i['href']:
            return i['href']
    return 0

def getNextPage(soup):
    nextPage=soup.find('a',title="Go to next page")
    if nextPage:
        return(nextPage['href'])
    else:
        return 0
    
#################################################################

# American University of Sharjah 
# https://scholar.google.com/citations?view_op=view_org&hl=en&org=15905138571532230398
# College of Engineering:
# https://www.aus.edu/college/cen/faculty

def AUS_scrapper(pdFullList):
    print("Starting AUS Scrapper")

    url='https://www.aus.edu/college/cen/faculty'

    while True:
        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
        profiles=soup.find_all('div', class_="node node-faculty-member college-teaser")
        pageCounter=1
        for item in profiles:
            profile={
            'entity':['American University of Sharjah'],       
            'name': [item.find('h4').text.strip()],
            'img': [item.find('img')['src']],
            'title': [item.find('div', class_='basic-info').find('div',class_="field-item even").text.strip()],
            'page': ["https://www.aus.edu"+ item.find('a', class_='read-more')['href']]
            }
            # betterName=profile['name'].split()
            # profile['scholarUrl']=getGoogleUrl(betterName[1]+' '+betterName[-1]) # remove prefix and middle names 
            # print(profile)
            pdProfile=pd.DataFrame.from_records(profile)
            # print(pdProfile)
            pdFullList=pd.concat([pdFullList,pdProfile],ignore_index=True)

        newPage=getNextPage(soup) 
        if not newPage: 
            break
        url='https://www.aus.edu'+getNextPage(soup) 
        pageCounter +=1

    print("AUS_screpaer Done!")
    return(pdFullList)


#################################################################
# Khalifa University 
# (No orgnizational number in google scholars)
# Faculty:
# https://www.ku.ac.ae/faculty-directory

def KU_scrapper(pdFullList):
    print("Starting KU Scrapper")
    url='https://www.ku.ac.ae/faculty-directory'

    page = requests.get(url,headers=headers).text
    soup = BeautifulSoup(page, 'html.parser')
    profiles=soup.find('div', class_="search-results clear").find_all('div',class_="blk clear")
 
    for item in profiles:
        try:
            name=item.find('span',class_="name").text.strip()
        except:
            name=NaN

        try:
            img=item.find('img')['src']
        except:
            img=NaN

        try:
            title=item.find('span',class_="title").text.strip()
        except:
            title=NaN

        try:
            email= item.find('span',class_="email").text.strip()
        except:
            email=NaN
        
        try:
            phone=item.find('span',class_="mobile").text.strip()
        except:
            phone=NaN

        try:
            page= item.find('a')['href']
            try:
                htmlDoc = requests.get(page,headers=headers).text
                soupDetailed = BeautifulSoup(htmlDoc, 'html.parser')
                scholarUrl=soupDetailed.find('div', class_="people-single-right").find('a')['href']
            except:
                scholarUrl=NaN
        except:
            page=NaN

        profile= pd.DataFrame({
        'entity':['Khalifa University'],       
        'name': [name],
        'img': [img],
        'title': [title],
        'email': [email],
        'phone': [phone],
        'page': [page], 
        'scholarUrl':[scholarUrl]
        })
        pdFullList=pd.concat([pdFullList,profile],ignore_index=True)

    print("KU_screpaer Done!")
    return(pdFullList)



def main():

    pdFullList=pd.DataFrame({
            'entity':[],       
            'name': [],
            'img': [],
            'title': [],
            'page': [],
            'email':[],
            'phone':[],
            'scholarUrl':[]
    })


    # pdFullList=AUS_scrapper(pdFullList)
    pdFullList=KU_scrapper(pdFullList)

    print(pdFullList)



if __name__=='__main__':
    main()





