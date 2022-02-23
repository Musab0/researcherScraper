
from bs4 import BeautifulSoup
from numpy import NaN
import requests
import pandas as pd
from datetime import datetime 
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # disable warning for unverified http requests 
import validators

#http request header 
headers = {   
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
}

#decodes protected email address (AUS emails for example)
def cfDecodeEmail(encodedString):  
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email


def GSparser(profile):
    url=profile['GSurl']
    page = requests.get(url, verify=False, headers=headers).text.strip()
    soup = BeautifulSoup(page, 'html.parser')
    try: 
        labels =soup.find('div',class_="gsc_prf_il",id="gsc_prf_int").find_all('a',class_='gsc_prf_inta gs_ibl')
        profile['GSinterests']=''
        for item in labels:
            profile['GSinterests']=  profile['GSinterests']+', '+item.text.strip()
    except: 
        pass

    try:
        ranking =soup.find('table',id="gsc_rsb_st").find('tbody').find_all('td', class_="gsc_rsb_std")
        
        rankingList=[]
        for item in ranking:
            try:
                rankingList.append(item.text.strip())
            except: 
                rankingList.append(NaN)
    except:
        rankingList=[NaN,NaN,NaN,NaN,NaN,NaN]

    try:
        profile['GScitationAll']=rankingList[0]
        profile['GShindexAll']=[rankingList[2]]
        profile['GSi10indexAll']=rankingList[4]
        profile['GScitation5yr']=rankingList[1]
        profile['GShindex5yr']=rankingList[3]
        profile['GSi10index5yr']=rankingList[5]
    except:
        pass




    try:
        profile['GSname']=soup.find('div',id="gsc_prf_in").text.strip()
    except:
        pass

    try:    
        profile['GSphoto']= soup.find('img',id="gsc_prf_pup-img")['src']
    except:
        pass

    return(profile)


    

def getGoogleUrl(keyword):

    # keyword=keyword.strip().replace(' ','+')
    googleSearchUrl='https://www.google.com/search?as_q=&as_epq=&as_oq={}&as_eq=&as_nlo=&as_nhi=&lr=&cr=&as_qdr=all&as_sitesearch=https%3A%2F%2Fscholar.google.com%2Fcitations&as_occt=any&as_filetype=&tbs='.format(keyword)
    page = requests.get(googleSearchUrl, verify=False, headers=headers)
    html_doc= page.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    # print(soup.prettify)
    # print(googleSearchUrl)
    googleScholarPage=soup.find_all('a',href=True)
    for i in googleScholarPage:
        if 'https://scholar.google.com/citations?'in i['href']:
            return i['href']
    return NaN

def getNextPageAUS(soup):
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
        page = requests.get(url,verify=False).text
        soup = BeautifulSoup(page, 'html.parser')
        profiles=soup.find_all('div', class_="node node-faculty-member college-teaser")
        pageCounter=1
        for item in profiles:
            try:
                name= item.find('h4').text.strip()
            except: 
                name=NaN

            try:
                img= item.find('img')['src']
            except: 
                img=NaN

            try:
                title= item.find('div', class_='basic-info').find('div',class_="field-item even").text.strip()
            except: 
                title=NaN

            try:
                page= "https://www.aus.edu"+ item.find('a', class_='read-more')['href']
                try:
                    htmlDoc = requests.get(page,headers=headers,verify=False).text
                    soupDetailed = BeautifulSoup(htmlDoc, 'html.parser')
                    try:
                        phone=soupDetailed.find('div', class_="panel-pane pane-entity-field pane-node-field-faculty-phone").text
                    except: 
                        phone=NaN
                    try:
                        email=soupDetailed.find('div', class_="panel-pane pane-entity-field pane-node-field-faculty-email").find('a', class_='__cf_email__')['data-cfemail']
                        email= cfDecodeEmail(email)
                    except: 
                        email=NaN

                except:
                    GSurl=NaN                
            except: 
                page=NaN

            profile=pd.DataFrame({
            'entity':['American University of Sharjah'],       
            'name': [name],
            'img': [img],
            'title': [title],
            'page': [page],
            'email': [email],
            'phone': [phone],
            # 'college':[college]
            # 'department':[department]
            })

            # betterName=profile['name'].split()
            # profile['GSurl']=getGoogleUrl(betterName[1]+' '+betterName[-1]) # remove prefix and middle names 

            profile['GSurl']=getGoogleUrl(name) 

            pdProfile=pd.DataFrame.from_records(profile)
            pdFullList=pd.concat([pdFullList,pdProfile],ignore_index=True)

        newPage=getNextPageAUS(soup) # go to the next page if exist 
        if not newPage: 
            break
        url='https://www.aus.edu'+newPage
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

    page = requests.get(url,headers=headers,verify=False).text
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
                htmlDoc = requests.get(page,headers=headers,verify=False).text
                soupDetailed = BeautifulSoup(htmlDoc, 'html.parser')
                GSurl=soupDetailed.find('div', class_="people-single-right").find('a')['href']
                if 'google' not in GSurl:
                    GSurl=NaN

            except:
                GSurl=NaN
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
        'GSurl':[GSurl]
        })
        pdFullList=pd.concat([pdFullList,profile],ignore_index=True)
    print("KU_screpaer Done!")
    return(pdFullList)


#################################################################
# New York University Abu Dhabi
# ( orgnizational number in google scholars)
# Faculty:
# college of science:    https://nyuad.nyu.edu/en/academics/faculty.html?_charset_=UTF-8&division=science&program=&affiliation=&keywords=
# cooege of engineering: https://nyuad.nyu.edu/en/academics/faculty.html?_charset_=UTF-8&division=engineering&program=&affiliation=&keywords=
def NYUAD_scrapper(pdFullList):
    print("Starting NYUAD Scrapper")
    urls=['https://nyuad.nyu.edu/en/academics/faculty.html?_charset_=UTF-8&division=science&program=&affiliation=&keywords=',
    'https://nyuad.nyu.edu/en/academics/faculty.html?_charset_=UTF-8&division=engineering&program=&affiliation=&keywords='
    ]

    for url in urls:

        page = requests.get(url,headers=headers,verify=False).text
        soup = BeautifulSoup(page, 'html.parser')
        profiles=soup.find_all('div', class_="faculty-container")
    
        for item in profiles:
            try:
                name=item.find('span',itemprop="name").text.strip()
            except:
                name=NaN

            try:
                img='https://nyuad.nyu.edu/'+ item.find('a', class_='photo-link')['href']
            except:
                img=NaN

            try:
                title=item.find('span',itemprop="jobTitle").text.strip()
            except:
                title=NaN

            try:
                email= item.find('a',itemprop="email").text.strip()
            except:
                email=NaN

            try:
                page= 'https://nyuad.nyu.edu/'+ item.find('span',itemprop="name")['href']
            except:
                page=NaN

            profile= pd.DataFrame({
            'entity':['New York University Abu Dhabi'],       
            'name': [name],
            'img': [img],
            'title': [title],
            'email': [email],
            'page': [page], 
            })
            profile['GSurl']=getGoogleUrl(name) 

            pdFullList=pd.concat([pdFullList,profile],ignore_index=True)

    print("NYUAD_screpaer Done!")
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
            'GSurl':[],
            'GSname':[],
            'GSphoto':[],
            'GSinterests':[],
            'GScitationAll':[],
            'GScitation5yr':[],
            'GShindexAll':[],
            'GShindex5yr':[],
            'GSi10indexAll':[],
            'GSi10index5yr':[]

    })

    pdFullList=AUS_scrapper(pdFullList)
    # pdFullList=KU_scrapper(pdFullList)
    # pdFullList=NYUAD_scrapper(pdFullList)

    #parse google scholar page data for all scholars with available GS page
    for index, row in pdFullList.iterrows():
        if validators.url(row['GSurl']):  
            pdFullList[index:]=GSparser(row)

    pdFullList.to_csv('scraped{}.csv'.format(datetime.now().strftime('%Y%m%d%H%M')), index=False)
    
if __name__=='__main__':
    main()

