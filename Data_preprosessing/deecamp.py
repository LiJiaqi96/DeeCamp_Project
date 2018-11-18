#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import csv
os.chdir("/Users/ljq/Desktop/word2vec-master/outs")
file = csv.reader(open("/Users/ljq/Desktop/word2vec-master/movie_clean2.csv",'r'))
lines = [row for row in file]
# mid name director scriptwriter mainPlayers categories productCountry tags ratingCount star5 star4 star3 star2 star1 language
nationalities = {}
nation_index = 0
languages = {}
language_index = 0
categories = {}
category_index = 0
for line in lines[1:]:
#     print(line)
    line_info = []
    line_info.append(int(line[0]))   # Add mid info
    
    if((line[6] == '日本;' or line[6] == '香港;') and len(line[1].split(' ')) > 1):
        name_temp = line[1].split(' ')
#         print(name_temp)
        name = name_temp[:int(len(name_temp)/2)][0]
#         print(name)
    else:
        name = line[1]
#         print(name)
    line_info.append(name)   # Add name info, if there are repeat names, select the first one
    if(name == ''):
        pass
    else:
        f_w = open("words.txt",'a')
        f_w.write(name+'\t')
        f_w.close()   # Write name into words
    
    line_info.append(line[2])   # Add director info
    if(line[2] == ''):
        pass
    else:
        f_w = open("words.txt",'a')
        f_w.write(line[2]+'\t')
        f_w.close()   # Write director into words
    
    line_info.append(line[3])   # Add scriptwriter info
    if(line[3] == ''):
        pass
    else:
        f_w = open("words.txt",'a')
        f_w.write(line[3]+'\t')
        f_w.close()   # Write scriptwriter into words
        
    if(len(line[4].split(' ')) > 1):
        actors = line[4].split(' ')
    elif(len(line[4].split('、')) > 1):
        actors = line[4].split('、')
    else:
        actors = [line[4]]
    line_info.append(actors)   # Add actors info
    if(line[4] == ''):
        pass
    else:
        f_w = open("words.txt",'a')
        for actor in actors:
            f_w.write(actor+'\t')
        f_w.close()   # Write actors into words
    
    if(line[5] in categories):
        line_info.append(categories[line[5]])
    else:
        categories[line[5]] = category_index
        line_info.append(category_index)   # Add category info
        category_index += 1
    
    if(line[6] in nationalities):
        line_info.append(nationalities[line[6]])
    else:
        nationalities[line[6]] = nation_index
        line_info.append(nation_index)   # Add productcountry info
        nation_index += 1
    
    tags = line[7].split(';')[:-1]
    line_info.append(tags)   # Add tags info
    if(tags == []):
        pass
    else:
        f_w = open("words.txt",'a')
        for tag in tags:
            f_w.write(tag+'\t')
        f_w.close()   # Write tags into words
    
    line_info.append(float(line[8]))   # Add ratingcounts info
    line_info.append(float(line[9]))   # Add star1 info
    line_info.append(float(line[10]))   # Add star2 info
    line_info.append(float(line[11]))   # Add star3 info
    line_info.append(float(line[12]))   # Add star4 info
    line_info.append(float(line[13]))   # Add star5 info
      
    if(line[14] in languages):
        line_info.append(languages[line[14]])
    else:
        languages[line[14]] = language_index
        line_info.append(language_index)   # Add language info
        language_index += 1
print('done')


# In[128]:


import os
import csv
os.chdir("/Users/ljq/Desktop/word2vec-master/outs")
file = csv.reader(open("/Users/ljq/Desktop/word2vec-master/movie_clean2.csv",'r'))
lines = [row for row in file]
# mid name director scriptwriter mainPlayers categories productCountry tags ratingCount star5 star4 star3 star2 star1 language
nationalities = {}
languages = {}
types = {}
for line in lines[1:1000]:
    print(line)
    line_info = []
    line_info.append(int(line[0]))   # Add mid info
    if(len(line[4].split(' ')) > 1):
        actors = line[4].split(' ')
    elif(len(line[4].split('、')) > 1):
        actors = line[4].split('、')
    else:
        actors = [line[4]]
#     print(actors)
#     for actor in actors:
#         print(actor)


# In[132]:


from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
import multiprocessing

inp = '/Users/ljq/Desktop/word2vec-master/outs/words.txt'
model = Word2Vec(LineSentence(inp), size=100, window=10, min_count=3,
            workers=multiprocessing.cpu_count(), sg=1, iter=10, negative=20)
out = '/Users/ljq/Desktop/word2vec-master/outs/vector_words.txt'
model.wv.save_word2vec_format(out, binary=False)
# model = Word2Vec.load("D:/data/wiki2vector/en_1000_no_stem/en.model")
print(model.similarity('国家地理', '纪录片'))


# In[127]:


from gensim.models import Word2Vec
print(model['alice'])


# In[151]:


import os
import csv
import json
os.chdir("/Users/ljq/Desktop/deecamp/movie_convert_info")
file = csv.reader(open("/Users/ljq/Desktop/word2vec-master/movie_clean2.csv",'r'))
lines = [row for row in file]
# mid name director scriptwriter mainPlayers categories productCountry tags ratingCount star5 star4 star3 star2 star1 language
movies = {}
movie_index = 1
names = {}
name_index = 1
directors = {}
director_index = 1
scriptwriters = {}
scriptwriter_index = 1
mainplayers = {}
mainplayer_index = 1
categories = {}
category_index = 1
nationalities = {}
nation_index = 1
movietags = {}
movietag_index = 1
languages = {}
language_index = 1

for line in lines[1:]:
#     print(line)
    line_info = []
    if(line[0] in movies):
        line_info.append(str(movies[line[0]]))
    else:
        if(line[0] == ''):
            continue
        movies[line[0]] = movie_index
        line_info.append(str(movie_index))   
        movie_index += 1   # Add mid info
    
    if(line[1] in names):
        line_info.append(str(names[line[1]]))
    else:
        if(line[1] == ''):
            line_info.append('0')
        else:
            names[line[1]] = name_index
            line_info.append(str(name_index))
            name_index += 1   # Add name info
            
    if(line[2] in directors):
        line_info.append(str(directors[line[2]]))
    else:
        if(line[2] == ''):
            line_info.append('0')
        else:
            directors[line[2]] = director_index
            line_info.append(str(director_index))  
            director_index += 1   # Add director info
            
    if(line[3] in scriptwriters):
        line_info.append(str(scriptwriters[line[3]]))
    else:
        if(line[3] == ''):
            line_info.append('0')
        else:
            scriptwriters[line[3]] = scriptwriter_index
            line_info.append(str(scriptwriter_index))   
            scriptwriter_index += 1   # Add scriptwriter info
        
    if(len(line[4].split(' ')) > 1):
        actors = line[4].split(' ')
    elif(len(line[4].split('、')) > 1):
        actors = line[4].split('、')
    else:
        actors = [line[4]]
    for actor in actors:
        if(actor in mainplayers):
            pass
        else:
            mainplayers[actor] = mainplayer_index
            mainplayer_index += 1   # Add mainactor info
    actor_info = []
    if(len(actors)>1):
        for actor in actors:
            actor_info.append(str(mainplayers[actor]))
            actor_info.append('|')
        actor_info = actor_info[:-1]
        line_info.append(''.join(actor_info))
    elif(len(actors) == 1):
        line_info.append(str(mainplayers[actors[0]]))
    else:
        line_info.append(str(0))
    
    if(line[5] in categories):
        line_info.append(str(categories[line[5]]))
    else:
        if(line[5] == ''):
            line_info.append('0')
        else:
            categories[line[5]] = category_index
            line_info.append(str(category_index))  
            category_index += 1   # Add category info
    
    if(line[6] in nationalities):
        line_info.append(str(nationalities[line[6]]))
    else:
        if(line[6] == ''):
            line_info.append('0')
        else:
            nationalities[line[6]] = nation_index
            line_info.append(str(nation_index))  
            nation_index += 1   # Add productcountry info
    
    tags = line[7].split(';')[:-1]
    for tag in tags:
        if(tag in movietags):
            pass
        else:
            movietags[tag] = movietag_index
            movietag_index += 1   # Add mainactor info
    tag_info = []
    if(len(tags)>1):
        for tag in tags:
            tag_info.append(str(movietags[tag]))
            tag_info.append('|')
        tag_info = tag_info[:-1]
        line_info.append(''.join(tag_info))
    elif(len(tags) == 1):
        line_info.append(str(movietags[tags[0]]))
    else:
        line_info.append(str(0))
    
    line_info.append(line[8])   # Add ratingcounts info
    line_info.append(line[9])   # Add star1 info
    line_info.append(line[10])   # Add star2 info
    line_info.append(line[11])   # Add star3 info
    line_info.append(line[12])   # Add star4 info
    line_info.append(line[13])   # Add star5 info
    
    if(line[14] in languages):
        line_info.append(str(languages[line[14]]))
    else:
        if(line[14] == ''):
            line_info.append('0')
        else:
            languages[line[14]] = language_index
            line_info.append(str(language_index)) 
            language_index += 1   # Add productcountry info
    f_w = open("movie_info.txt",'a')
    f_w.write('\t'.join(line_info) + '\n')
    f_w.close()   # Write lininfo into txt
    print(line_info)
    print(' '.join(line_info))

with open('movie_dict'+'.json','a') as outfile_m:
    json.dump(movies,outfile_m,ensure_ascii=False)
with open('name_dict'+'.json','a') as outfile_n:
    json.dump(names,outfile_n,ensure_ascii=False)
with open('director_dict'+'.json','a') as outfile_d:
    json.dump(directors,outfile_d,ensure_ascii=False)
with open('scripwriter_dict'+'.json','a') as outfile_s:
    json.dump(scriptwriters,outfile_s,ensure_ascii=False)
with open('actor_dict'+'.json','a') as outfile_a:
    json.dump(mainplayers,outfile_a,ensure_ascii=False)
with open('category_dict'+'.json','a') as outfile_t:
    json.dump(categories,outfile_t,ensure_ascii=False)
with open('country_dict'+'.json','a') as outfile_c:
    json.dump(nationalities,outfile_c,ensure_ascii=False)
with open('tag_dict'+'.json','a') as outfile_l:
    json.dump(movietags,outfile_l,ensure_ascii=False)
with open('language_dict'+'.json','a') as outfile_w:
    json.dump(languages,outfile_w,ensure_ascii=False)

print('done')


# In[ ]:


import os
import csv
import json
os.chdir("/Users/ljq/Desktop/deecamp/movie_convert_info")
file = csv.reader(open("/Users/ljq/Desktop/word2vec-master/movie_clean2.csv",'r'))
lines = [row for row in file]
# mid name director scriptwriter mainPlayers categories productCountry tags ratingCount star5 star4 star3 star2 star1 language

names = {}
name_index = 1
directors = {}
director_index = 1
scriptwriters = {}
scriptwriter_index = 1
mainplayers = {}
mainplayer_index = 1
categories = {}
category_index = 1
movietags = {}
movietag_index = 1

for line in lines[1:]:
#     print(line)
    line_info.append(line[0])   # Add mid info
    
    if(line[1] in names):
        line_info.append(str(names[line[1]]))
    else:
        if(line[1] == ''):
            line_info.append('0')
        else:
            names[line[1]] = name_index
            line_info.append(str(name_index))
            name_index += 1   # Add name info
            
    if(line[2] in directors):
        line_info.append(str(directors[line[2]]))
    else:
        if(line[2] == ''):
            line_info.append('0')
        else:
            directors[line[2]] = director_index
            line_info.append(str(director_index))  
            director_index += 1   # Add director info
            
    if(line[3] in scriptwriters):
        line_info.append(str(scriptwriters[line[3]]))
    else:
        if(line[3] == ''):
            line_info.append('0')
        else:
            scriptwriters[line[3]] = scriptwriter_index
            line_info.append(str(scriptwriter_index))   
            scriptwriter_index += 1   # Add scriptwriter info
        
    if(len(line[4].split(' ')) > 1):
        actors = line[4].split(' ')
    elif(len(line[4].split('、')) > 1):
        actors = line[4].split('、')
    else:
        actors = [line[4]]
    for actor in actors:
        if(actor in mainplayers):
            pass
        else:
            mainplayers[actor] = mainplayer_index
            mainplayer_index += 1   # Add mainactor info
    actor_info = []
    if(len(actors)>1):
        for actor in actors:
            actor_info.append(str(mainplayers[actor]))
            actor_info.append('|')
        actor_info = actor_info[:-1]
        line_info.append(''.join(actor_info))
    elif(len(actors) == 1):
        line_info.append(str(mainplayers[actors[0]]))
    else:
        line_info.append(str(0))
    
    if(line[5] in categories):
        line_info.append(str(categories[line[5]]))
    else:
        if(line[5] == ''):
            line_info.append('0')
        else:
            categories[line[5]] = category_index
            line_info.append(str(category_index))  
            category_index += 1   # Add category info
    
    tags = line[7].split(';')[:-1]
    for tag in tags:
        if(tag in movietags):
            pass
        else:
            movietags[tag] = movietag_index
            movietag_index += 1   # Add mainactor info
    tag_info = []
    if(len(tags)>1):
        for tag in tags:
            tag_info.append(str(movietags[tag]))
            tag_info.append('|')
        tag_info = tag_info[:-1]
        line_info.append(''.join(tag_info))
    elif(len(tags) == 1):
        line_info.append(str(movietags[tags[0]]))
    else:
        line_info.append(str(0))

#     f_w = open("movie_info.txt",'a')
#     f_w.write('\t'.join(line_info) + '\n')
#     f_w.close()   # Write lininfo into txt
    print(line_info)
    print(' '.join(line_info))

# with open('name_dict'+'.json','a') as outfile_n:
#     json.dump(names,outfile_n,ensure_ascii=False)
# with open('director_dict'+'.json','a') as outfile_d:
#     json.dump(directors,outfile_d,ensure_ascii=False)
# with open('scripwriter_dict'+'.json','a') as outfile_s:
#     json.dump(scriptwriters,outfile_s,ensure_ascii=False)
# with open('actor_dict'+'.json','a') as outfile_a:
#     json.dump(mainplayers,outfile_a,ensure_ascii=False)
# with open('category_dict'+'.json','a') as outfile_t:
#     json.dump(categories,outfile_t,ensure_ascii=False)
# with open('tag_dict'+'.json','a') as outfile_l:
#     json.dump(movietags,outfile_l,ensure_ascii=False)

print('done')


# In[ ]:




