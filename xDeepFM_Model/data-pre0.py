# -*- coding: utf-8 -*-
"""
Created on Sun Aug 19 22:15:28 2018

@author: HCHO
"""

#测试集拼接
def test_pre0():
    w1=open('UserMovie_test2.txt','r')
    w2=open('movie_candidates.csv','r')
    w3=open('Folder/1000test.csv','w')
    
    list1000=w2.readlines()
    list_uid=w1.readlines()
    
    for uid in list_uid:
        uid=uid.strip()
        for mid in list1000:
            mid=mid.strip()
            w3.write(str(uid)+','+str(mid)+'\n')
    w1.close()
    w2.close()
    w3.close()


#测试集数据整合、索引
def test_pre1():
    w3=open('Folder/1000test.csv','r')
    w4=open('xDeepFM/ex_data/new_test.csv','w')
    w4.write('uid,mid,label,director,scriptwriter,mainPlayers,categories,productCountry,tags,language'+'\n')
    
    movie=open("movie_info.txt",'r').readlines()
    
    movieId_dic=open('movie_dict.json','r').read()
    movieId_dic=eval(movieId_dic)
    userId_dic=open('user_dict.json','r').read()
    userId_dic=eval(userId_dic)
    
    reline=w3.readline()
    error=0
    while(reline):
        reline=reline.strip().split(',')
        try:
            uid=reline[0]
            mid=reline[1]
            uindex=userId_dic[uid]
            mindex=movieId_dic[mid]
    
            oneline=movie[mindex-1].split('\t')
            line=oneline[2:8]
            line.append(oneline[14].strip())
            strline=','.join('%s' %li for li in line)
    
            w4.write(str(uindex)+','+str(mindex)+',0,'+strline+'\n')
        except:
            error+=1
        reline=w3.readline()
    print('error num:',error)
    w3.close()
    w4.close()
    
#负例数据处理，并对后两项置零。与UserMovie_train.txt文件混合    
def train_pre0():
    w1=open('foo1.txt','r')    
    w3=open('UserMovie_train.txt','r')
    w4=open('Folder/usermovie_train.txt','w')
    
    w3.readline()
    example1=w3.readlines()
    example0=w1.readlines()
    
    for a in example1:
        line=a.split('\t')
        w4.write(line[0]+'\t'+line[1]+'\t'+'1\n')
    for b in example0:
        line=b.split('\t')
        w4.write(line[0]+'\t'+line[1]+'\t'+'0\n')    
              
    w1.close()
    w3.close()
    w4.close()

#训练集数据整合索引
def train_pre1():
    w0=open('Folder/usermovie_train.txt','r')
    w1=open('Folder/new_user_train.txt','w')
    w1.write('uid,mid,label,director,scriptwriter,mainPlayers,categories,productCountry,tags,language'+'\n')
    movie=open("movie_info.txt",'r').readlines()
    
    movieId_dic=open('movie_dict.json','r').read()
    movieId_dic=eval(movieId_dic)
    userId_dic=open('user_dict.json','r').read()
    userId_dic=eval(userId_dic)
    
    reline=w0.readline()
    error=0
    while(reline):
        reline=reline.strip().split('\t')
        try:
            uid=reline[0]
            mid=reline[1]
            uindex=userId_dic[uid]
            mindex=movieId_dic[mid]
    
            oneline=movie[mindex-1].split('\t')
            line=oneline[2:8]
            line.append(oneline[14].strip())
            strline=','.join('%s' %li for li in line)
    
            w1.write(str(uindex)+','+str(mindex)+','+reline[2]+','+strline+'\n')
        except:
            error+=1
        reline=w0.readline()
    print('error num:',error)
    w0.close()
    w1.close()
    
#数据打混
import random
def train_pre2():
    with open('Folder/new_user_train.txt','r') as data:
        f=open('Folder/mix_new_user_train.txt','w')
        f.write(data.readline())
        all_data=data.readlines()
        random.shuffle(all_data)   
        for i in all_data:
            f.write(i)
        f.close()
        
#分出训练集、验证集
def train_pre3():
    data=open('Folder/mix_new_user_train.txt','r')
    w1=open('xDeepFM/ex_data/new_train.csv','w')
    w2=open('xDeepFM/ex_data/new_valid.csv','w')
    
    line=data.readline()
    i=0
    w1.write('uid,mid,label,director,scriptwriter,mainPlayers,categories,productCountry,tags,language'+'\n')
    w2.write('uid,mid,label,director,scriptwriter,mainPlayers,categories,productCountry,tags,language'+'\n')
    line=data.readline()
    while(line):
        if (i%50 ==0):
            w2.write(line)
        else:
            w1.write(line)
        line=data.readline()
        i=i+1
        if(i%500000==0):
            print(i)
    
    data.close()
    w1.close()
    w2.close()
    
if __name__ == '__main__':
    #test_pre0()
    #test_pre1()
    #train_pre0()
    train_pre1()
    train_pre2()
    train_pre3()