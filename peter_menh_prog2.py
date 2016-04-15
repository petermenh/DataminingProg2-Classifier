'''
Peter Menh
CSE 4334
Spring 2016
Programming Assignment 2

References used:
http://www.nltk.org/index.html
http://www.nltk.org/book/ch01.html

Tokenizer from programming assignment 1 solution
'''
import math
import time
import os
from math import log10, sqrt
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import pandas
import csv as csv

mytokenizer = RegexpTokenizer(r'[a-zA-Z0-9]+')
stemmer = PorterStemmer()
sortedstopwords = sorted(stopwords.words('english'))
trainPuidDict = {}
puidDict = {}
brandTok = []
brand = 'brand'
prior = 0
terms = 'terms'
totRel = 'totRel'
aveRel = 'aveRel'
numofP = 'numofP'

def tokenize(doc):
    tokens = mytokenizer.tokenize(doc)
    lowertokens = [token.lower() for token in tokens]
    filteredtokens = [stemmer.stem(token) for token in lowertokens if not token in sortedstopwords]
    return filteredtokens


#---------------Main-----------------

os.system('cls')
#-----train
print('Training...')
start_time = time.time()
train_csv = pandas.read_csv('train.csv', encoding="ISO-8859-1")
count = 0

for i in range(0,len(train_csv)):
    count +=1
    if count == 10000:
        print('%{0:.0f} done...'.format((i/len(train_csv))*100) )
        count = 0

    if type(train_csv.search_term[i])==float:
        if math.isnan(csvAtt.name[i]):
            searchTok = tokenize(" ")
    else:
        searchTok = tokenize(train_csv.search_term[i])

    if type(train_csv.product_title[i])==float:
        if math.isnan(csvAtt.name[i]):
            prod_titleTok = tokenize(" ")
    else:
        prod_titleTok = tokenize(train_csv.product_title[i])

    train_termsTok = searchTok+prod_titleTok

    if train_csv.product_uid[i] not in trainPuidDict:
        trainPuidDict[train_csv.product_uid[i]] = {terms:train_termsTok,numofP:1, totRel:train_csv.relevance[i], aveRel:0}
        tempAve = trainPuidDict[train_csv.product_uid[i]][totRel]/(3*trainPuidDict[train_csv.product_uid[i]][numofP])
        trainPuidDict[train_csv.product_uid[i]][aveRel] = tempAve
    else:
        trainPuidDict[train_csv.product_uid[i]][terms] = trainPuidDict[train_csv.product_uid[i]][terms]+train_termsTok
        trainPuidDict[train_csv.product_uid[i]][numofP] +=1
        trainPuidDict[train_csv.product_uid[i]][totRel] += train_csv.relevance[i]
        tempAve = trainPuidDict[train_csv.product_uid[i]][totRel]/(3*trainPuidDict[train_csv.product_uid[i]][numofP])
        trainPuidDict[train_csv.product_uid[i]][aveRel] = tempAve

print('Training time: ', time.time()-start_time)
print()


#-----Attribute
print('Start attribute read')
start_time = time.time()
count = 0
att_csv = pandas.read_csv('attributes.csv', sep=",", encoding="ISO-8859-1")
print('%0 done...')

for i in range(0,len(att_csv)):
    count +=1
    brandTok = []

    if count == 100000:
        print('%{0:.0f} done...'.format((i/len(att_csv))*100) )
        count = 0

    if type(att_csv.name[i])==float:
        if math.isnan(att_csv.name[i]):
            nameTok = tokenize(" ")
    elif att_csv.name[i]=='MFG Brand Name':
        if type(att_csv.value[i])==float:
            if math.isnan(att_csv.value[i]):
                valueTok = tokenize(" ")
        else:
            brandTok = tokenize(att_csv.value[i])

    if type(att_csv.value[i])==float:
        if math.isnan(att_csv.value[i]):
            valueTok = tokenize(" ")
    else:
        valueTok = tokenize(att_csv.value[i])

    if att_csv.product_uid[i] not in puidDict:
        puidDict[att_csv.product_uid[i]] = {terms:valueTok, brand:brandTok}
    else:
        puidDict[att_csv.product_uid[i]][terms] += valueTok
        puidDict[att_csv.product_uid[i]][brand] += brandTok

print('%100 done')
print('Attribute time: ', time.time()-start_time)
print()


#-----Product Description
print('Start product description read')
start_time = time.time()
count = 0
pro_des_csv = pandas.read_csv('product_descriptions.csv', sep=",", encoding="ISO-8859-1")
print('%0 done...')

for i in range(0,len(pro_des_csv)):
    count +=1

    if count == 12000:
        print('%{0:.0f} done...'.format((i/len(pro_des_csv))*100) )
        count = 0

    if type(pro_des_csv.product_description[i])==float:
        if math.isnan(pro_des_csv.product_description[i]):
            valueTok = tokenize(" ")
    else:
        valueTok = tokenize(pro_des_csv.product_description[i])

    if pro_des_csv.product_uid[i] not in puidDict:
        puidDict[pro_des_csv.product_uid[i]] = {terms:valueTok, brand:[]}
    else:
        puidDict[pro_des_csv.product_uid[i]][terms] += valueTok

print('%100 done')
print('Product description time: ', time.time()-start_time)
print()

#-----read test and output result
print('Start testing and output results')
start_time = time.time()

test_csv = pandas.read_csv('test.csv', sep=",", encoding="ISO-8859-1")

with open('result.csv', 'w', newline='') as outfile:
    writer = csv.writer(outfile, delimiter=',', quotechar = "'")
    writer.writerow(['"id"']+['"relevance"'])
    for i in range(0,len(test_csv)):
        score = 1
        searchTok = tokenize(test_csv.search_term[i])
        test_id = test_csv.id[i]
        test_puid = test_csv.product_uid[i]
        test_title = test_csv.product_title[i]
        search_titleTok = tokenize(test_csv.product_title[i])
        for i in searchTok:
            if i in search_titleTok:
                score += 1


        if (test_puid in puidDict) and (test_puid in trainPuidDict):
            for t in searchTok:
                prior = 1
                if t in puidDict[test_puid][brand]:
                    score +=1
                    if score >= 3.0:
                        score = 3.0

                else:
                    if t in trainPuidDict[test_puid][terms]:
                        prior = trainPuidDict[test_puid][aveRel]

                    tTop = puidDict[test_puid][terms].count(t)+1
                    tBot = len(puidDict[test_puid][terms]) + len(set(puidDict[test_puid][terms]))
                    condProb = tTop/tBot
                    score += (prior * condProb)
                    if score >= 3:
                        score = 3.0

        if score >= 3:
            score = 3.0
        writer.writerow([test_id, '%.2f'%score])

print('test time: ', time.time()-start_time)
print()
print('Results outputted')
