import numpy as np
import pandas as pd
import scipy.stats
import scipy.spatial
from sklearn.cross_validation import KFold
import random
from sklearn.metrics import mean_squared_error
from math import sqrt
import math
import warnings
import sys
import json
from functools import reduce 
from sklearn.feature_extraction import DictVectorizer
#from sklearn.utils.extmath import np.dot

warnings.simplefilter("error")

users = 48765
items = 94877

#threshold = 3      选取阈值法
required_cnt = 900  #每个用户采集900个负例，使得正负例比例为1：5 
#required_cnt = 540  #使得正负例比例为1：3

def readingFile(filename):
    f = open(filename,"r")
    data = []
    for row in f:
        r = row.split('\t')
        e = [int(r[0]), int(r[1]), str(r[2]), float(r[3])]
        data.append(e)
    return data


def pca():
    udata = pd.read_table('UserMovie_train2.txt')
    uid = udata['uid'].unique()

    # user_movie = {}

    # for i in uid:
    #   user_movie[i] = []

    # for index, row in udata.iterrows():
    #    if index%1000==0:
    #        print(index)
    #    user_movie[row['uid']].append(row['mid'])

    uid_pca = dict()
    count = 1
    for key in uid:
        uid_pca[key] = count
        count += 1
    # uid_pca = sorted(uid_pca.items(),key = lambda x:x[1],reverse = False)
    data = pd.read_table('Movie.txt')
    mid = data['mid'].unique()

    # udata = pd.read_table('UserMovie_train.txt')
    mid2 = udata['mid'].unique()

    movie = set()

    for i in mid:
        movie.add(i)

    for i in mid2:
        movie.add(i)

    # movie_list = list(movie)
    # movie = pd.read_csv('Movie.txt',delimiter='\t')
    # df2 = pd.DataFrame(movie)
    # mid = df2['mid'].values
    # mid.sort()
    mid_pca = dict()
    count2 = 1
    for key in movie:
        mid_pca[key] = count2
        count2 += 1
    # mid_pca = sorted(mid_pca.items(),key = lambda x:x[1],reverse = False)

    return uid, movie, uid_pca, mid_pca

def similarity_item(data):
    print ('Hello')
    #f_i_d = open("sim_item_based.txt","w")
    item_similarity_cosine = np.zeros((items,items))
    item_similarity_jaccard = np.zeros((items,items))
    item_similarity_pearson = np.zeros((items,items))
    for item1 in range(items):
        print (item1)
        for item2 in range(items):
            if np.count_nonzero(data[:,item1]) and np.count_nonzero(data[:,item2]):
                item_similarity_cosine[item1][item2] = 1-scipy.spatial.distance.cosine(data[:,item1],data[:,item2])
                item_similarity_jaccard[item1][item2] = 1-scipy.spatial.distance.jaccard(data[:,item1],data[:,item2])
                try:
                    if not math.isnan(scipy.stats.pearsonr(data[:,item1],data[:,item2])[0]):
                        item_similarity_pearson[item1][item2] = scipy.stats.pearsonr(data[:,item1],data[:,item2])[0]
                    else:
                        item_similarity_pearson[item1][item2] = 0
                except:
                    item_similarity_pearson[item1][item2] = 0

            #f_i_d.write(str(item1) + "," + str(item2) + "," + str(item_similarity_cosine[item1][item2]) + "," + str(item_similarity_jaccard[item1][item2]) + "," + str(item_similarity_pearson[item1][item2]) + "\n")
    #f_i_d.close()
    return item_similarity_cosine, item_similarity_jaccard, item_similarity_pearson


def crossValidation(uid_pca, mid_pca, data):
    # 构建了评分矩阵
    k_fold = KFold(n=len(data), n_folds=10)

    Mat = np.zeros((users, items))
    for e in data:
        print(e[0], e[1])
        Mat[uid_pca[e[0]] - 1][mid_pca[e[1]] - 1] = e[3]

    # 根据公式计算出三个矩阵，item*item大小的矩阵，矩阵中的数值表示了item1与item2之间的余弦相似度，jaccard相似度，pearson相似度
    sim_item_cosine, sim_item_jaccard, sim_item_pearson = similarity_item(Mat)
    # sim_item_cosine, sim_item_jaccard, sim_item_pearson = np.random.rand(items,items), np.random.rand(items,items), np.random.rand(items,items)

    # 初始化三个评估参数的均方根误差
    rmse_cosine = []
    rmse_jaccard = []
    rmse_pearson = []

    for train_indices, test_indices in k_fold:
        train = [data[i] for i in train_indices]
        test = [data[i] for i in test_indices]

        # M是训练集的矩阵，与Mat有所不同
        M = np.zeros((users, items))

        for e in train:
            M[uid_pca[e[0]] - 1][mid_pca[e[1]] - 1] = e[3]

        true_rate = []
        pred_rate_cosine = []
        pred_rate_jaccard = []
        pred_rate_pearson = []

        for e in test:
            # 测试集的数据初始化
            user = uid_pca[e[0]]
            item = mid_pca[e[1]]
            true_rate.append(e[3])

            pred_cosine = 3.0
            pred_jaccard = 3.0
            pred_pearson = 3.0

            # item-based
            if np.count_nonzero(M[:, item - 1]):  # 找到训练集中对应item（找到有评分的数目），
                sim_cosine = sim_item_cosine[item - 1]
                sim_jaccard = sim_item_jaccard[item - 1]
                sim_pearson = sim_item_pearson[item - 1]
                ind = (M[user - 1] > 0)
                # ind[item-1] = False
                normal_cosine = np.sum(np.absolute(sim_cosine[ind]))  # 该测试集用户，对该用户打过分的电影的余弦值进行相加（绝对值相加）
                normal_jaccard = np.sum(np.absolute(sim_jaccard[ind]))
                normal_pearson = np.sum(np.absolute(sim_pearson[ind]))
                if normal_cosine > 0:
                    pred_cosine = np.dot(sim_cosine, M[user - 1]) / normal_cosine  # dot点乘，将数据进行点乘得到预估的pred

                if normal_jaccard > 0:
                    pred_jaccard = np.dot(sim_jaccard, M[user - 1]) / normal_jaccard

                if normal_pearson > 0:
                    pred_pearson = np.dot(sim_pearson, M[user - 1]) / normal_pearson

            if pred_cosine < 0:
                pred_cosine = 0

            if pred_cosine > 5:
                pred_cosine = 5

            if pred_jaccard < 0:
                pred_jaccard = 0

            if pred_jaccard > 5:
                pred_jaccard = 5

            if pred_pearson < 0:
                pred_pearson = 0

            if pred_pearson > 5:
                pred_pearson = 5

            print(str(user) + "\t" + str(item) + "\t" + str(e[2]) + "\t" + str(pred_cosine) + "\t" + str(
                pred_jaccard) + "\t" + str(pred_pearson))
            pred_rate_cosine.append(pred_cosine)
            pred_rate_jaccard.append(pred_jaccard)
            pred_rate_pearson.append(pred_pearson)  # 加入到pred_rate数组之中

        rmse_cosine.append(sqrt(mean_squared_error(true_rate, pred_rate_cosine)))
        rmse_jaccard.append(sqrt(mean_squared_error(true_rate, pred_rate_jaccard)))
        rmse_pearson.append(sqrt(mean_squared_error(true_rate, pred_rate_pearson)))  # 计算均方根误差

        print(str(sqrt(mean_squared_error(true_rate, pred_rate_cosine))) + "\t" + str(
            sqrt(mean_squared_error(true_rate, pred_rate_jaccard))) + "\t" + str(
            sqrt(mean_squared_error(true_rate, pred_rate_pearson))))
        # raw_input()

    # print sum(rms) / float(len(rms))
    rmse_cosine = sum(rmse_cosine) / float(len(rmse_cosine))
    rmse_pearson = sum(rmse_pearson) / float(len(rmse_pearson))
    rmse_jaccard = sum(rmse_jaccard) / float(len(rmse_jaccard))

    print(str(rmse_cosine) + "\t" + str(rmse_jaccard) + "\t" + str(rmse_pearson))

    f_rmse = open("rmse_item.txt", "w")
    f_rmse.write(str(rmse_cosine) + "\t" + str(rmse_jaccard) + "\t" + str(rmse_pearson) + "\n")

    rmse = [rmse_cosine, rmse_jaccard, rmse_pearson]
    req_sim = rmse.index(min(rmse))  # 选择最小均方根的req_sim（这个应该是选择最好的计算距离方法）

    print(req_sim)
    f_rmse.write(str(req_sim))
    f_rmse.close()

    if req_sim == 0:
        sim_mat_item = sim_item_cosine

    if req_sim == 1:
        sim_mat_item = sim_item_jaccard

    if req_sim == 2:
        sim_mat_item = sim_item_pearson

    # predictRating(Mat, sim_mat_item)
    return Mat, sim_mat_item


def create_negative(recommend_data):
    uid, set2, uid_pca, mid_pca = pca()
    M, sim_item = crossValidation(uid_pca, mid_pca, recommend_data)

    # f = open("toBeRated.csv","r")
    # f = open(sys.argv[2],"r")
    # toBeRated = {"user":[], "item":[]}
    train = pd.read_csv('UserMovie_train2.txt', delimiter='\t')
    df = pd.DataFrame(train)
    df['recommend'] = 1
    df.to_csv('UserMovie_train.csv', index=False)
    # movie
    # set = df['uid'].values.flatten()
    # set2 = df2['mid'].values.flatten()
    newRow = pd.DataFrame(columns=['uid', 'mid', 'timeStamp', 'star', 'recommend', 'rated'])
    # insertRow = pd.DataFrame([[0.,20.,3.,4.]],columns=['date','temperature','wind','humidity'])
    # df = df.append(insertRow,ignore_index=True)
    # print(set.shape)
    # print(set2.shape)
    # index = 0

    for user in uid:
        item_rated = dict()
        user = uid_pca[user]
        for item in set2:
            pred = 3.0

            # item-based
            item = mid_pca[item]
            if np.count_nonzero(M[:, item - 1]):
                sim = sim_item[item - 1]
                ind = (M[user - 1] > 0)
                # ind[item-1] = False
                normal = np.sum(np.absolute(sim[ind]))
                if normal > 0:
                    pred = np.dot(sim, M[user - 1]) / normal
            # if pred < 0:
            # pred = 0

            # if pred > 5:
            # pred = 5

            item_rated[item] = pred

        after = sorted(item_rated.items(), key=lambda x: x[1], reverse=False)
        cnt = 0
        for movie_name, value in after.items():
            cnt += 1
            if cnt > required_cnt:
                break
            real_user = list(uid_pca.keys())[list(uid_pca.values()).index(user)]
            real_movie = list(mid_pca.keys())[list(mid_pca.values()).index(movie_name)]
            insertRow = pd.DataFrame([[real_user, real_movie, np.nan, 1, 0, value]],
                                     columns=['uid', 'mid', 'timeStamp', 'star', 'recommend', 'rated'])
            newRow = newRow.append(insertRow, ignore_index=True)
    newRow.to_csv('result.csv', index=False, header=False)


recommend_data = readingFile('UserMovie_train.txt')
create_negative(recommend_data)