import requests
import json
import re
from bs4 import BeautifulSoup

header = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'}


#Scrapes all subjects from UTS Subject List URL, accepts url and course name to write json file as parameters
def scrapeSubject(url, course):

  r = requests.get(url,headers=header)
  
  if r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    subjects = soup.find('div',attrs={"class":"ie-images"})
    subjects.find('h1').decompose()
    for elementP in subjects.find_all('p'):
      elementP.decompose()

    # Grabs links
    linkTags = [a.get('href') for a in subjects.find_all('a', href=True)]

    # Grabs subject iD stores them into list
    linkIDs = subjects.find_all('a')
    idList = []
    for link in linkIDs:
      idList.append(str(link.text))

    # Gets only the subject names
    for elementA in subjects.find_all('a'):

      elementA.decompose()
    
    # Regular Expressions to regulate formatting
    linkTags = str(linkTags).replace('u\'', '\'').replace('\'', '').strip('][').split(', ')
    subjects = str(subjects.text)
    finalText = re.split("[\r\n]+", subjects)

    while ' ' and '' in finalText:
      finalText.remove(' ')
      finalText.remove('')
      
    # Loops through our variables and stores into data properties into json file
    result = []
    subjectDescription = None
    for (subjectID, name,link) in zip(idList, finalText, linkTags):
      subjectDescription = descriptionScrape(link)
      single = {'id': subjectID, 'name': name, 'link': link, 'description': subjectDescription }
      print(single);
      result.append(single)
      with open(f'{course}.json','w') as f:
        json.dump(result,f,indent=4)

  else:
    print(r.status_code)


# Scrapes Descriptions from a UTS Subject Link
def descriptionScrape(link):
  html = requests.get(link,headers=header)
  soup = BeautifulSoup(html.content, 'html.parser')
  try:
    soup = soup.select('h3 + p')[0]
    description = str(soup.text)
    return description
  except:
    description = "This subject does not have a description."
  
  return description

# Scrapes Major from a UTS Major Link
def majorScrape(link, major):
  html = requests.get(link,headers=header)
  soup = BeautifulSoup(html.content, 'html.parser')

  # Grabs all subject links
  subjectLinks = soup.find('table')
  linkTags = [a.get('href') for a in subjectLinks.find_all('a', href=True)]
  #Grab subject iDs
  linkiDs = []
  for iD in subjectLinks.find_all('a'):
      linkiDs.append(iD.text)

  #Remove subject links and only get subject Name
  #if a link is not found it might not be a subject major and just a line of text so we can remove it.
  subjectNames = soup.select('td:nth-child(1)')
  majorSubjectList = []
  for subject in subjectNames:
    try:
      subject.find('a').decompose()
      majorSubjectList.append(str(subject.text).replace('\xa0', ''))
    except:
      subject.decompose()

  result = []
  subjectDescription = None
  for (subjectID, name,link) in zip(linkiDs, majorSubjectList, linkTags):
    subjectDescription = descriptionScrape(link)
    single = {'id': subjectID, 'name': name, 'link': link, 'description': subjectDescription }
    result.append(single)
    print(single)
    with open(f'major/{major}.json','w') as f:
      json.dump(result,f,indent=4)


scrapeSubject("https://www.handbook.uts.edu.au/bus/lists/alpha.html", "business")
# majorScrape("https://handbook.uts.edu.au/directory/maj03445.html", "NandC")