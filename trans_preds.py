#建立反向字典
movieId_dic=open('movie_dict.json','r').read()
movieId_dic=eval(movieId_dic)
userId_dic=open('user_dict.json','r').read()
userId_dic=eval(userId_dic)
re_movie_dict={}
re_user_dict={}

for key,values in movieId_dic.items():
    re_movie_dict[values]=key
for key,values in userId_dic.items():
    re_user_dict[values]=key

#读写数据
one_data=[]
with open('xDeepFM/OUT/test_out.csv','r') as preds:
    all_data=preds.readlines()
    i=0
    for item in all_data:
        item.strip()
        data=eval(item)
        one_data.extend([x[1] for x in data])
        i+=1
        print(i)

movieId_dic=re_movie_dict
userId_dic=re_user_dict


print('new_test')
my_object=[]
with open('xDeepFM/ex_data/new_test.csv','r') as dataset3:
    line=dataset3.readline()
    line=dataset3.readline()
    i=0
    while(line):
        linelist=line.split(',')
        uid=int(linelist[0])
        mid=int(linelist[1])
        real_uid=userId_dic[uid]
        real_mid=movieId_dic[mid]
        my_object.append((real_uid,real_mid,one_data[i]))
        i=i+1
        line=dataset3.readline()


#kill trainset
with open('UserMovie_train.txt','r') as f:
    usermovie_train=f.readlines()
    usermovie_dic={}
    for line in usermovie_train:
        line=line.strip().split('\t')
        if line[0] not in usermovie_dic:
            usermovie_dic[line[0]]=[line[1]]
        else:
            usermovie_dic[line[0]].append(line[1])
    new_object=[]
    for item in my_object:
        if (item[0] in usermovie_dic and item[1] in usermovie_dic[item[0]]):
            continue
        else:
            new_object.append(item)

        
#top50  
print('top50')
from operator import itemgetter
sort_object=sorted(new_object, key=itemgetter(0,2),reverse=True) #二维排序,从大到小排序
with open('Result/result.csv','w') as result:
    num=len(sort_object)
    record_id=0
    count=0
    for i in range(num):
        if(record_id != sort_object[i][0]):
            record_id=sort_object[i][0]
            count=0
            top50=','.join('%s' %li for li in sort_object[i])
            result.write(top50+'\n')
            count+=1
        else:
            if(count>=50):
                continue
            else:
                top50=','.join('%s' %li for li in sort_object[i])
                result.write(top50+'\n')
                count+=1
                
#merge
with open('Result/result.csv','r') as result:
    final_result=open('Result/final_result.csv','w')
    all_line=result.readlines()
    all_line.reverse()
    num=len(all_line)
    user_num=int(num/50)
    for i in range(user_num):
        line=all_line[i*50].split(',')
        uid=line[0]
        mid=[]
        for j in range(i*50,i*50+50):
            line=all_line[j].split(',')
            mid.append(line[1])
        line50 ='\t'.join('%s' %li for li in mid)
        final_result.write(uid+'\t'+line50+'\n')
    final_result.close()
                   