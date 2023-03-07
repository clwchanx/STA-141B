#!/usr/bin/env python
# coding: utf-8

# In[32]:



import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup 
import nltk
import numpy as np
import re
from nltk.corpus import wordnet
from selenium import webdriver


# In[33]:


def raw_text(url):
    """Takes a URL as input and performs web scrapping to retrieve the body of the
    webpage (in this case a Linkedin ad)"""
    ad = requests.get(url) #Retrieve webpage
    Html = BeautifulSoup(ad.text, 'html.parser') #Convert html into a nicer format
    text_body = Html.find_all('div', 
                              {'class':"show-more-less-html__markup show-more-less-html__markup--clamp-after-5"})
    text_body = text_body[0].text
    return text_body
def clean_text(doc):
    """Take an unstructured document and tokenize it into a list of words. 
    Then standardize it by lowercasing and lemmatizing each word"""
    words = re.findall(r'(?:[a-zA-Z]|#|"+")+',doc) #Find all alphabetical words (Preserve + and # for C++ and C#)
    clean = [i for i in words if i.isupper() or i.islower()] #Retrieve all words that aren't glued to each other
    dirty = [i for i in words if not i.islower() and not i.isupper()] #Retrieve words stuck together
    dirty = [re.findall('[a-zA-Z][^A-Z]*',i) for i in dirty] #Split all the tangled words ie split 'ThisExample' into ['This','Example']
    clean2 = [j for i in dirty for j in i] #Unlist the list of lists
    words = clean + clean2 #Combine all the words together
    stopwords = nltk.corpus.stopwords.words("english")
    words = [i.lower() for i in words] #Lowercase all words
    words = [i for i in words if i not in stopwords] #Filter out stopwords
    tag_words = nltk.pos_tag(words) #Begin lemmatizing by tagging each word
    tag_words = [(i, wordnet_pos(j)) for (i, j) in tag_words] #Convert the tags into something the lemmatizer understands
    lemmatizer = nltk.WordNetLemmatizer()
    clean_words = [lemmatizer.lemmatize(i, j) for i, j in tag_words] #Lemmatize the words
    #Document should be cleaned up
    return clean_words
def wordnet_pos(tag):
    """Map a Brown POS tag to a WordNet POS tag."""
    
    table = {"N": wordnet.NOUN, "V": wordnet.VERB, "R": wordnet.ADV, "J": wordnet.ADJ}
    
    # Default to a noun.
    return table.get(tag[0], wordnet.NOUN) #Function created by Bo Ning in Week 6-2
def lang_count(TXT):
    """ Take a body of clean text and count the number of programming languages present"""
    languages = ['python','r','sql','sa','c',
                 'c++','c#','java','javascript',
                 'julia','matlab','swift','tableau'
                'microsoft','github'] #SAS turns into sa after lemmatization
    #ADD MORE LANGUAGES IF NECESSARY
    count = sum([i in TXT for i in languages]) #Check if each language is in the ad
    #And sum the number of programming languages present
    return count
def get_salary(TXT):
    """From a body of raw text, retrieve the salary"""
    salaries = re.findall(r"(\$\d+\,\d+\.\d{1,2})",TXT) #Find all numbers with $ , and .
    if salaries != []:
        return salaries[-1] #Let's work with the maximum salary
    else:
        salaries = re.findall(r"(\$\d+\,\d+)",TXT)  #Account for no decimals too!
        if salaries != []:
            return salaries[-1]
        else: #If list is empty no salary is present and return NA
            return "NaN"
def ML_skill(TXT):
    """Using a body of clean text, check whether the words machine learning is present
    to see if it is a required skill"""
    if ('machine' in TXT and 'learn' in TXT) or ('ml' in TXT): #Check for the words related to machine learning
        return 'Yes' #If it's present return yes as in machine learning is required
    else:
        return 'No'
def get_edu(TXT):
    """Using a body of raw text, retrieve the highest education level"""
    if "PhD" in TXT or 'Ph.D' in TXT: #Start looking for PhD to see if it's the highest education listed
        return "PhD"
    elif "Master" in TXT or 'MS' in TXT or 'MA' in TXT:#If PhD is absent do the same thing with masters
        return "Master"
    elif "Bachelor" in TXT or 'BS' in TXT or 'BA' in TXT:
        return "Bachelor"
    else:
        return "NaN" #No education specified
def benefits(TXT):
    """Using a body of raw text, check if benefits are included"""
    if 'Benefit' in TXT or 'benefit' in TXT: #Check if benefit is in the ad to determine whether benefits are included
        return 'Yes'
    else:
        return 'No'
def exp(TXT):
    """Using a body of raw text, check if experience is required/preferred"""
    sentences = nltk.sent_tokenize(TXT) #Split text into sentences
    years = [re.findall(r"\d+.*year", i) for i in sentences] #Find sentences with years in it
    for items in years:
        if items != []:
            years = [i for i in years if i != []][0][0] #Get rid of empty values and turn the years of experience into a string
            year = re.findall(r'\d+',years)[0]
            return year
    return "NaN" #If we make it through the loop years of experience is absent and return NA
def collect_data(url):
    """Input a URL for a Linkedin Ad and retrieve all relevant data"""
    raw = raw_text(url)
    clean = clean_text(raw)
    return {'Languages':lang_count(clean),
            'Salary':get_salary(raw),
            'Machine Learning':ML_skill(clean),
            'Education':get_edu(raw),
            'Benefits':benefits(raw),
            'Experience':exp(raw),
            'url':url}


# In[34]:


url = 'https://www.linkedin.com/jobs/view/3495686468/?alternateChannel=search&refId=bUuSO67FACleck0qLIsOEw%3D%3D&trackingId=SnethqT%2B4%2Fa89lESpJllDw%3D%3D&trk=d_flagship3_search_srp_jobs'
collect_data(url)


# In[35]:


url = [
'https://www.linkedin.com/jobs/view/3480836400/?alternateChannel=search&refId=hzJz0m5p3LFO7tIxWaitKg%3D%3D&trackingId=vL57L5M%2B6bh2eEwBhn9fXg%3D%3D',
'https://www.linkedin.com/jobs/view/3482317582/?alternateChannel=search&refId=hzJz0m5p3LFO7tIxWaitKg%3D%3D&trackingId=oEP9Zl7sWKd6%2BCbdzJvrTQ%3D%3D',
'https://www.linkedin.com/jobs/view/3485598972/?alternateChannel=search&refId=hzJz0m5p3LFO7tIxWaitKg%3D%3D&trackingId=%2BTU10220%2FrTKY%2FORdVzoFA%3D%3D',
'https://www.linkedin.com/jobs/view/3474104997/?alternateChannel=search&refId=hzJz0m5p3LFO7tIxWaitKg%3D%3D&trackingId=3oumyc0qhUKfnDeF9Jl5LA%3D%3D',
'https://www.linkedin.com/jobs/view/3499243413/?alternateChannel=search&refId=%2BF%2BFXjeZ97mraoWZ%2F29HXA%3D%3D&trackingId=8eZmIdS%2F78n5ZkIhD6sS3g%3D%3D',
'https://www.linkedin.com/jobs/view/3497809413/?alternateChannel=search&refId=%2BF%2BFXjeZ97mraoWZ%2F29HXA%3D%3D&trackingId=ZbgEVG3%2FOsyrNrVUNE1IjA%3D%3D',
'https://www.linkedin.com/jobs/view/3485589284/?alternateChannel=search&refId=%2BF%2BFXjeZ97mraoWZ%2F29HXA%3D%3D&trackingId=qQyYXInBcNp5rdYhy9rkdQ%3D%3D',
'https://www.linkedin.com/jobs/view/3499231522/?alternateChannel=search&refId=%2BF%2BFXjeZ97mraoWZ%2F29HXA%3D%3D&trackingId=ofD3EYQQb4gt5yR9HmElTw%3D%3D',
'https://www.linkedin.com/jobs/view/3484736484/?alternateChannel=search&refId=%2BF%2BFXjeZ97mraoWZ%2F29HXA%3D%3D&trackingId=lDvm0eGr3I1LrHNr88YlcQ%3D%3D',
'https://www.linkedin.com/jobs/view/3482943863/?alternateChannel=search&refId=%2BF%2BFXjeZ97mraoWZ%2F29HXA%3D%3D&trackingId=PNxMNhkPfGTRgyNKYh59Ew%3D%3D',
'https://www.linkedin.com/jobs/view/3485092940/?alternateChannel=search&refId=%2BF%2BFXjeZ97mraoWZ%2F29HXA%3D%3D&trackingId=6kY%2FhRj3kumCi%2B6ZBhx9sA%3D%3D',
'https://www.linkedin.com/jobs/view/3498209260/?alternateChannel=search&refId=%2BF%2BFXjeZ97mraoWZ%2F29HXA%3D%3D&trackingId=HQTdn%2FYRljc9Bod%2FGyQbYQ%3D%3D',
'https://www.linkedin.com/jobs/view/3497410604/?alternateChannel=search&refId=%2BF%2BFXjeZ97mraoWZ%2F29HXA%3D%3D&trackingId=tq%2BWMz23cqOdhCoNHkfIIQ%3D%3D',
'https://www.linkedin.com/jobs/view/3482024773/?alternateChannel=search&refId=%2BF%2BFXjeZ97mraoWZ%2F29HXA%3D%3D&trackingId=zqtAx1bmrd%2BKKJHnbXQmdQ%3D%3D',
'https://www.linkedin.com/jobs/view/3497412440/?alternateChannel=search&refId=%2BF%2BFXjeZ97mraoWZ%2F29HXA%3D%3D&trackingId=ir%2F%2Bmpp8vuu%2FbxocH4pR2Q%3D%3D',
'https://www.linkedin.com/jobs/view/3477186036/?alternateChannel=search&refId=%2BF%2BFXjeZ97mraoWZ%2F29HXA%3D%3D&trackingId=4MWwcg6GDm7NtyeFhkgt2A%3D%3D',
'https://www.linkedin.com/jobs/view/3492905077/?alternateChannel=search&refId=%2BF%2BFXjeZ97mraoWZ%2F29HXA%3D%3D&trackingId=OzmSTSKMGPbd6TKlVTpEfw%3D%3D',
'https://www.linkedin.com/jobs/view/3495650895/?alternateChannel=search&refId=%2BF%2BFXjeZ97mraoWZ%2F29HXA%3D%3D&trackingId=8jppB5uBQwbM8ImGBexyLQ%3D%3D',
'https://www.linkedin.com/jobs/view/3477765885/?alternateChannel=search&refId=B74ZU7%2BKFa8WGBQqYfevCw%3D%3D&trackingId=BNvnbkeqXV0iaDexh5gvHQ%3D%3D',
'https://www.linkedin.com/jobs/view/3507858351/?alternateChannel=search&refId=B74ZU7%2BKFa8WGBQqYfevCw%3D%3D&trackingId=OhZB3Fhl%2FnHSkaHkS7tBtw%3D%3D',
'https://www.linkedin.com/jobs/view/3486730652/?alternateChannel=search&refId=B74ZU7%2BKFa8WGBQqYfevCw%3D%3D&trackingId=O%2Fm6o9%2FYtGkrUY11ny1L8g%3D%3D',
'https://www.linkedin.com/jobs/view/3510798014/?alternateChannel=search&refId=B74ZU7%2BKFa8WGBQqYfevCw%3D%3D&trackingId=ia6FFR3VCH6Z3Dfr6gR1sg%3D%3D',
'https://www.linkedin.com/jobs/view/3483520818/?alternateChannel=search&refId=lCMJLZ7NgJ94mbhHQMokqQ%3D%3D&trackingId=qBeQcuiOoOGUne5co8SBrw%3D%3D',
'https://www.linkedin.com/jobs/view/3502126460/?alternateChannel=search&refId=lCMJLZ7NgJ94mbhHQMokqQ%3D%3D&trackingId=yN1NUGfDMM%2BcsvZKStEznw%3D%3D',
'https://www.linkedin.com/jobs/view/3475904812/?alternateChannel=search&refId=lCMJLZ7NgJ94mbhHQMokqQ%3D%3D&trackingId=F5BfQgydWZKWJl8WAsQ2jw%3D%3D',
'https://www.linkedin.com/jobs/view/3497488989/?alternateChannel=search&refId=lCMJLZ7NgJ94mbhHQMokqQ%3D%3D&trackingId=rfvVUk2of0l%2FkGQYcNc7Qg%3D%3D'
'https://www.linkedin.com/jobs/view/3493573277/?alternateChannel=search&refId=lCMJLZ7NgJ94mbhHQMokqQ%3D%3D&trackingId=jqoNglC19Wk7gDjXBXktGw%3D%3D',
'https://www.linkedin.com/jobs/view/3487708421/?alternateChannel=search&refId=lCMJLZ7NgJ94mbhHQMokqQ%3D%3D&trackingId=svWgJo4BUqrwc5V%2FpG1BZg%3D%3D',
'https://www.linkedin.com/jobs/view/3490335163/?alternateChannel=search&refId=lCMJLZ7NgJ94mbhHQMokqQ%3D%3D&trackingId=AGJHzw6elSZvQ1Lbf4Pgmg%3D%3D',
'https://www.linkedin.com/jobs/view/3500300099/?alternateChannel=search&refId=tx24jCRLjQu2wAWhl8q2kw%3D%3D&trackingId=9PAhVDUO3huGX7Ve6aOE9w%3D%3D',
'https://www.linkedin.com/jobs/view/3493932962/?alternateChannel=search&refId=tx24jCRLjQu2wAWhl8q2kw%3D%3D&trackingId=gGcDWkoYF9IdTRsQT1uOJg%3D%3D',
'https://www.linkedin.com/jobs/view/3478642744/?alternateChannel=search&refId=tx24jCRLjQu2wAWhl8q2kw%3D%3D&trackingId=EYi2OTBP5HzO2mjtGeXLMg%3D%3D',
'https://www.linkedin.com/jobs/view/3478646349/?alternateChannel=search&refId=tx24jCRLjQu2wAWhl8q2kw%3D%3D&trackingId=ODhkdvq5VixPOMl9MWgdow%3D%3D',
'https://www.linkedin.com/jobs/view/3490315684/?alternateChannel=search&refId=tx24jCRLjQu2wAWhl8q2kw%3D%3D&trackingId=k%2BGJSb4h0UYwTjKOwZa4Fg%3D%3D',
'https://www.linkedin.com/jobs/view/3495947949/?alternateChannel=search&refId=J44dYJy3n8vrAe6BMWFWzA%3D%3D&trackingId=KUcOZWsom5U13KFGXhrzag%3D%3D',
'https://www.linkedin.com/jobs/view/3499198986/?alternateChannel=search&refId=J44dYJy3n8vrAe6BMWFWzA%3D%3D&trackingId=XG8Fp04161iejDebu4Giyg%3D%3D',
'https://www.linkedin.com/jobs/view/3483125003/?alternateChannel=search&refId=J44dYJy3n8vrAe6BMWFWzA%3D%3D&trackingId=8lAsH8cgjFfICzCE87XWVw%3D%3D',
'https://www.linkedin.com/jobs/view/3497996600/?alternateChannel=search&refId=J44dYJy3n8vrAe6BMWFWzA%3D%3D&trackingId=r%2FfYu1iL9shMRO5VfnTnaA%3D%3D',
'https://www.linkedin.com/jobs/view/3485531966/?alternateChannel=search&refId=J44dYJy3n8vrAe6BMWFWzA%3D%3D&trackingId=%2BMhKnG8wEHlLaReJVY%2BVEA%3D%3D',
'https://www.linkedin.com/jobs/view/3483162019/?alternateChannel=search&refId=J44dYJy3n8vrAe6BMWFWzA%3D%3D&trackingId=Vfvn3DB%2FZ6asJxPcHJ8oDA%3D%3D',
'https://www.linkedin.com/jobs/view/3491751485/?alternateChannel=search&refId=J44dYJy3n8vrAe6BMWFWzA%3D%3D&trackingId=QKY6Bhv2BCd0OerbFUKHOA%3D%3D',
'https://www.linkedin.com/jobs/view/3503247533/?alternateChannel=search&refId=J44dYJy3n8vrAe6BMWFWzA%3D%3D&trackingId=zp7oF5%2FsiOxwJYWjHU8FcQ%3D%3D',
'https://www.linkedin.com/jobs/view/3474104997/?alternateChannel=search&refId=GnHhQQXnnWxufh3U2wRtNQ%3D%3D&trackingId=W4fPMPJ%2FB68EVqR29ho8Sg%3D%3D',
'https://www.linkedin.com/jobs/view/3491480925/?alternateChannel=search&refId=GnHhQQXnnWxufh3U2wRtNQ%3D%3D&trackingId=obkwBm89NkGEyj1%2Fr%2BaguA%3D%3D',
'https://www.linkedin.com/jobs/view/3490390307/?alternateChannel=search&refId=GnHhQQXnnWxufh3U2wRtNQ%3D%3D&trackingId=64lJcJmFrjTb5LeG%2BGn3Qw%3D%3D',
'https://www.linkedin.com/jobs/view/3491783046/?alternateChannel=search&refId=GnHhQQXnnWxufh3U2wRtNQ%3D%3D&trackingId=tUvUd1HD2UP8QK%2B3m4PQtQ%3D%3D',
'https://www.linkedin.com/jobs/view/3482039211/?alternateChannel=search&refId=GnHhQQXnnWxufh3U2wRtNQ%3D%3D&trackingId=Kbwc7ZPi%2FZjeLTZDB2IPTg%3D%3D',
'https://www.linkedin.com/jobs/view/3494351211/?alternateChannel=search&refId=GnHhQQXnnWxufh3U2wRtNQ%3D%3D&trackingId=v67CAV0A%2B9u33k5OyBOsLw%3D%3D',
'https://www.linkedin.com/jobs/view/3479875781/?alternateChannel=search&refId=GnHhQQXnnWxufh3U2wRtNQ%3D%3D&trackingId=Nod2VquRNI7t9C75bpTCBg%3D%3D',
'https://www.linkedin.com/jobs/view/3487876716/?alternateChannel=search&refId=GnHhQQXnnWxufh3U2wRtNQ%3D%3D&trackingId=WW1s4SIM6oQyarzpf9dgXw%3D%3D',
'https://www.linkedin.com/jobs/view/3494440488/?alternateChannel=search&refId=GnHhQQXnnWxufh3U2wRtNQ%3D%3D&trackingId=AWWH3x5ZAAu7gv6mLRuzJQ%3D%3D',
'https://www.linkedin.com/jobs/view/3492155495/?alternateChannel=search&refId=GnHhQQXnnWxufh3U2wRtNQ%3D%3D&trackingId=Qvl5z3xEFYI8cmcmmUTEBg%3D%3D',
'https://www.linkedin.com/jobs/view/3490320222/?alternateChannel=search&refId=GnHhQQXnnWxufh3U2wRtNQ%3D%3D&trackingId=G3zzdX1yTfgoBqfieR4YtA%3D%3D',
'https://www.linkedin.com/jobs/view/3497740104/?alternateChannel=search&refId=GnHhQQXnnWxufh3U2wRtNQ%3D%3D&trackingId=L%2B1iMzPS31NpHXwzDxAwbw%3D%3D',
'https://www.linkedin.com/jobs/view/3478070149/?alternateChannel=search&refId=4A%2FyoMybD2%2FV2EKj0IOzvw%3D%3D&trackingId=MnneVlPxoIu1s8y6WFa6Lw%3D%3D',
'https://www.linkedin.com/jobs/view/3500236943/?alternateChannel=search&refId=4A%2FyoMybD2%2FV2EKj0IOzvw%3D%3D&trackingId=7yRQ%2Bv849NcnLrMGyPQIYw%3D%3D',
'https://www.linkedin.com/jobs/view/3487708185/?alternateChannel=search&refId=4A%2FyoMybD2%2FV2EKj0IOzvw%3D%3D&trackingId=UV0nErSDDQpgEFJMzQby1g%3D%3D',
'https://www.linkedin.com/jobs/view/3503257941/?alternateChannel=search&refId=4A%2FyoMybD2%2FV2EKj0IOzvw%3D%3D&trackingId=rYyBTplUJDJlXiIjDKT6pA%3D%3D',
'https://www.linkedin.com/jobs/view/3494092583/?alternateChannel=search&refId=giEumJfy6zBQ2wduDiKFlg%3D%3D&trackingId=eCfD%2FCz%2FMPx1IcCp2n7Afg%3D%3D',
'https://www.linkedin.com/jobs/view/3497865734/?alternateChannel=search&refId=giEumJfy6zBQ2wduDiKFlg%3D%3D&trackingId=sx6inYrSEzZFEcAf1SfZ2A%3D%3D',
'https://www.linkedin.com/jobs/view/3483751776/?alternateChannel=search&refId=giEumJfy6zBQ2wduDiKFlg%3D%3D&trackingId=X2bOp6l3v4DklEud2Qvv0w%3D%3D',
'https://www.linkedin.com/jobs/view/3482049975/?alternateChannel=search&refId=giEumJfy6zBQ2wduDiKFlg%3D%3D&trackingId=VWC4XDVhBktZ8exg5oUVEQ%3D%3D',
'https://www.linkedin.com/jobs/view/3490315892/?alternateChannel=search&refId=giEumJfy6zBQ2wduDiKFlg%3D%3D&trackingId=5qMC2qnJ%2FLtPk0xfMoJoIA%3D%3D',
'https://www.linkedin.com/jobs/view/3494496847/?alternateChannel=search&refId=giEumJfy6zBQ2wduDiKFlg%3D%3D&trackingId=xXXUGBFhhwfhjAg6tbzlvQ%3D%3D',
'https://www.linkedin.com/jobs/view/3490818587/?alternateChannel=search&refId=%2B2Fnmr3ZH8vYmtI5fkRwjw%3D%3D&trackingId=pJe0V5jYgsqm0YMIzCywcw%3D%3D',
'https://www.linkedin.com/jobs/view/3495956692/?alternateChannel=search&refId=%2B2Fnmr3ZH8vYmtI5fkRwjw%3D%3D&trackingId=kPmVEc22smQKkmdpQXj%2BTA%3D%3D',
'https://www.linkedin.com/jobs/view/3498714814/?alternateChannel=search&refId=%2B2Fnmr3ZH8vYmtI5fkRwjw%3D%3D&trackingId=YF0gseljilW%2BExWmO2%2BGVg%3D%3D',
'https://www.linkedin.com/jobs/view/3475943161/?alternateChannel=search&refId=15cszUJB8%2BvoFHkhHq4ZWw%3D%3D&trackingId=aU4V7xN89RTgQFXbh7fHdw%3D%3D',
'https://www.linkedin.com/jobs/view/3507105466/?alternateChannel=search&refId=15cszUJB8%2BvoFHkhHq4ZWw%3D%3D&trackingId=AvVlT4wTEUZYv8GxdiOyKw%3D%3D',
'https://www.linkedin.com/jobs/view/3441702869/?alternateChannel=search&refId=gGykCqqW7PR3%2BKGLlk4SSw%3D%3D&trackingId=P2r11%2Br0vjIFo9ZRz5inGQ%3D%3D',
'https://www.linkedin.com/jobs/view/3474339133/?alternateChannel=search&refId=gGykCqqW7PR3%2BKGLlk4SSw%3D%3D&trackingId=Mts%2F25J7MLiA08YiK21tqQ%3D%3D',
'https://www.linkedin.com/jobs/view/3296336105/?alternateChannel=search&refId=quOfBYU%2FKkLJrelEqLCmUw%3D%3D&trackingId=WwQZcMfAaJmm72jkKqUYlQ%3D%3D',
'https://www.linkedin.com/jobs/view/3305892542/?alternateChannel=search&refId=quOfBYU%2FKkLJrelEqLCmUw%3D%3D&trackingId=AxxBdK7B4HKj1Taq36gsXg%3D%3D',
'https://www.linkedin.com/jobs/view/3491905657/?alternateChannel=search&refId=AcP99l%2BE6W3E6YIU%2Bh0jrw%3D%3D&trackingId=XbMcwpxMo5p0cd8vANfJjg%3D%3D',
'https://www.linkedin.com/jobs/view/3443791832/?alternateChannel=search&refId=QT%2FkAD%2Bv4AoSyEjdkpypiA%3D%3D&trackingId=eMHIJwYWuzcbTiUFqbc%2Fpg%3D%3D',
'https://www.linkedin.com/jobs/view/3485843952/?alternateChannel=search&refId=QT%2FkAD%2Bv4AoSyEjdkpypiA%3D%3D&trackingId=2M4irBmza6LDnFM%2Fed8G7g%3D%3D',
'https://www.linkedin.com/jobs/view/3501408792/?alternateChannel=search&refId=THGmPp5pcLJ7BFAfN4Xycg%3D%3D&trackingId=Z1AruM82D7mwW162Qb%2B5Dg%3D%3D',
'https://www.linkedin.com/jobs/view/3476789804/?alternateChannel=search&refId=6%2BGdZbNLh2m956lisP0kXg%3D%3D&trackingId=GPpD61gLLNnlRavxc4nfhw%3D%3D',
'https://www.linkedin.com/jobs/view/3492929121/?alternateChannel=search&refId=6%2BGdZbNLh2m956lisP0kXg%3D%3D&trackingId=KZafzwPur%2F7%2FwFYiTR7vTw%3D%3D',
'https://www.linkedin.com/jobs/view/2914502/?alternateChannel=search&refId=DOcFFWyaGQugL7mUzLowFw%3D%3D&trackingId=F4mLHtD%2BuQlC0WBxo8GbVQ%3D%3D',
'https://www.linkedin.com/jobs/view/3480674131/?alternateChannel=search&refId=2qEPhgj%2FWEJYFnl6velTYA%3D%3D&trackingId=M1PvIplKKU%2FATmdKTfnZzw%3D%3D',
'https://www.linkedin.com/jobs/view/3487706839/?alternateChannel=search&refId=2qEPhgj%2FWEJYFnl6velTYA%3D%3D&trackingId=WoCl%2BCUZrl5qTvv2Sx7AsQ%3D%3D',
'https://www.linkedin.com/jobs/view/3457192628/?alternateChannel=search&refId=2qEPhgj%2FWEJYFnl6velTYA%3D%3D&trackingId=Xt2nLfjg8CP9lzsR7IBXkg%3D%3D',
'https://www.linkedin.com/jobs/view/3507857368/?alternateChannel=search&refId=IpiB3zTYY9qWEKZmoTHbPg%3D%3D&trackingId=NIsGJSaAT0pxrecD9bcUgA%3D%3D',
'https://www.linkedin.com/jobs/view/3479875781/?alternateChannel=search&refId=IpiB3zTYY9qWEKZmoTHbPg%3D%3D&trackingId=N%2FP4azAdlvcF6wngtVDSiQ%3D%3D',
'https://www.linkedin.com/jobs/view/3483757696/?alternateChannel=search&refId=IpiB3zTYY9qWEKZmoTHbPg%3D%3D&trackingId=%2FUGg9vALMFDJ0q6LSe7BCw%3D%3D',
'https://www.linkedin.com/jobs/view/3358202763/?alternateChannel=search&refId=SfcYnvpclbZDDJ7lPSrSPQ%3D%3D&trackingId=38ZGC9G35b2H733ekwiVnA%3D%3D',
'https://www.linkedin.com/jobs/view/3464653380/?alternateChannel=search&refId=SfcYnvpclbZDDJ7lPSrSPQ%3D%3D&trackingId=0JLSJguO6KpZdqKBiGN7JA%3D%3D',
'https://www.linkedin.com/jobs/view/3500478205/?alternateChannel=search&refId=PUPGvLaaEsPhdK8D0L0ygA%3D%3D&trackingId=dSnLGgpV4%2FxCwcKnuGKp2g%3D%3D',
'https://www.linkedin.com/jobs/view/3485589284/?alternateChannel=search&refId=pbtG%2BpKcSINrxQ2zyK%2BMig%3D%3D&trackingId=nK7VKXmHYxCpB%2FgAwTkDug%3D%3D',
'https://www.linkedin.com/jobs/view/3507569128/?alternateChannel=search&refId=IN0DvsJIujEd%2BWI%2FMhTRdg%3D%3D&trackingId=IEFExitPVuqQ0A7ZFKmLlA%3D%3D',
'https://www.linkedin.com/jobs/view/3483520818/?alternateChannel=search&refId=pGBsiuo3aY8Jo0jXvTu2HA%3D%3D&trackingId=O7KBgmRqudkuzNzDrDrqYw%3D%3D',
'https://www.linkedin.com/jobs/view/3467081732/?alternateChannel=search&refId=P1YoVgcPvPSH489r01dCiA%3D%3D&trackingId=xv4pQN75x0yLREEJ2R5TLA%3D%3D',
'https://www.linkedin.com/jobs/view/3249197629/?alternateChannel=search&refId=P1YoVgcPvPSH489r01dCiA%3D%3D&trackingId=HdrXOtAS9jn7JXAKm8y15w%3D%3D',
'https://www.linkedin.com/jobs/view/3458734550/?alternateChannel=search&refId=P1YoVgcPvPSH489r01dCiA%3D%3D&trackingId=VBZmvO2BWDS%2FdhuW%2FpwXVw%3D%3D',
'https://www.linkedin.com/jobs/view/3482023892/?alternateChannel=search&refId=Xo0kXhfdA3TH8SWtZR%2FdRw%3D%3D&trackingId=fjHxpeo%2B7gKgzdKsir0vEA%3D%3D',
'https://www.linkedin.com/jobs/view/3483125003/?alternateChannel=search&refId=BHDOKV6ZbYCYAKZAyrWYEw%3D%3D&trackingId=Cd0P9g%2BU4DLptZPdMYqPdA%3D%3D',
'https://www.linkedin.com/jobs/view/3485548898/?alternateChannel=search&refId=NsgoInM8U39LUKlfbCUrCA%3D%3D&trackingId=K64BxGUKjeWMA5I4hO9lKA%3D%3D',
'https://www.linkedin.com/jobs/view/3507782958/?alternateChannel=search&refId=rxVUjOGLI0qLqScASWLU%2Fg%3D%3D&trackingId=1wLGQGGg7vSB4JF1BbqZLA%3D%3D',
'https://www.linkedin.com/jobs/view/3494351211/?alternateChannel=search&refId=rxVUjOGLI0qLqScASWLU%2Fg%3D%3D&trackingId=UYX%2B4wjCr6R1o1JCSOGVYA%3D%3D',
'https://www.linkedin.com/jobs/view/3496401704/?alternateChannel=search&refId=ozUPHUao4HZPqC3GPYMfqA%3D%3D&trackingId=BEwE8a7%2Fnm3%2FdE3SeQGscw%3D%3D',]


# In[36]:


len(url)


# In[37]:


data_scientist1= [collect_data(i) for i in url[0:10]] 


# In[38]:


data_scientist2 = [collect_data(i) for i in url[10:20]]


# In[39]:


data_scientist3 = [collect_data(i) for i in url[20:30]]


# In[ ]:


data_scientist4 = [collect_data(i) for i in url[30:40]]


# In[ ]:


data_scientist5 = [collect_data(i) for i in url[40:50]]


# In[ ]:


data_scientist6 = [collect_data(i) for i in url[50:60]]


# In[ ]:


data_scientist7 = [collect_data(i) for i in url[60:70]]


# In[ ]:


data_scientist8 = [collect_data(i) for i in url[70:80]]


# In[ ]:


data_scientist9 = [collect_data(i) for i in url[80:90]]


# In[ ]:


data_scientist10 = [collect_data(i) for i in url[90:100]]


# In[ ]:


#create one list
data_scientist_final =  (
    data_scientist1 + 
    data_scientist2 + 
    data_scientist3 +
    data_scientist4 +
    data_scientist5 +
    data_scientist6 +
    data_scientist7 +
    data_scientist8 +
    data_scientist9 +
    data_scientist10) #merge the data_analyst folds
len(data_scientist_final)


# In[ ]:



print(len(data_scientist1))
print(len(data_scientist2))
print(len(data_scientist3))
print(len(data_scientist4))
print(len(data_scientist5))
print(len(data_scientist6))
print(len(data_scientist7))
print(len(data_scientist8))
print(len(data_scientist9))
print(len(data_scientist10))


# In[ ]:


#creating csv file for 100 data anlyst postings
import csv

keys =data_scientist_final[0].keys()

with open('data_scientist.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(data_scientist_final)


# In[ ]:




