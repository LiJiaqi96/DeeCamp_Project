"""
    author:yang yiqing 2018年07月13日16:04:16
    - 数据处理，数值型必须是float,离散型必须是int,多值离散是str中间用|隔开，eg. "1|2|3"
    - 暂时不能有缺失值

"""

import Config
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


class Parse(object):
    def __init__(self):
        self.global_emb_idx = 0
        self.label_num = 0
        self.single_num = 0
        self.multi_num = 0
        #self.train = pd.read_csv(Config.train_file, index_col=0)
        #self.valid = pd.read_csv(Config.valid_file, index_col=0)
        #self.test = pd.read_csv(Config.test_file, index_col=0)
        self.train = pd.read_csv(Config.train_file)
        self.valid = pd.read_csv(Config.valid_file)
        self.test = pd.read_csv(Config.test_file)
        scalar = MinMaxScaler()  #标准化数据特征到0，1
        all_data = pd.concat([self.train, self.valid, self.test]) #数据合并
        print('transform data...')
        #缩放数据
        for s in Config.numeric_features:
            scalar.fit(all_data[s].values.reshape(-1,1))
            self.train[s] = scalar.transform(self.train[s].values.reshape(-1,1)) #.values返回array格式,  .reshape[-1,1] 返回矩阵列数为1
            self.valid[s] = scalar.transform(self.valid[s].values.reshape(-1,1))
            self.test[s] = scalar.transform(self.test[s].values.reshape(-1,1))
        self.check()#检查数据格式是否相同
        self.num_features = Config.numeric_features
        self.single_features = Config.single_features
        self.multi_features = Config.multi_features
        self.backup_dict = {} #每类型留出一个索引号，处理特殊情况（不在字典中的值和缺省值）

        self.num_dict = {} #数值型
        self.single_dict = {} #离散型
        self.multi_dict = {} #多值离散型
        self.get_dict()
        self.trans_data(self.train, Config.train_save_file)
        self.trans_data(self.valid, Config.valid_save_file)
        self.trans_data(self.test, Config.test_save_file)
        self.save_conf() #保存数据处理的信息大小

    #embedding建立字典索引
    def get_dict(self):
        print('prepare dict...')
        self.global_emb_idx = 0
        if self.num_features and Config.num_embedding:
            for s in self.num_features:
                self.num_dict[s] = self.global_emb_idx
                self.global_emb_idx += 1
                # for NaN
                self.backup_dict[s] = self.global_emb_idx
                self.global_emb_idx += 1
        #print(self.num_dict)

        if self.single_features:
            for s in self.single_features:
                # every filed
                frequency_dict = {} #类型频率字典
                current_dict = {}
                values = pd.concat([self.train, self.valid, self.test])[s]
                for v in values:
                    if v in frequency_dict:
                        frequency_dict[v] += 1
                    else:
                        frequency_dict[v] = 1
                for k, v in frequency_dict.items():
                    #如果某项出现频率大于阈值、截止频率，则建立索引
                    if v > Config.single_feature_frequency:
                        current_dict[k] = self.global_emb_idx
                        self.global_emb_idx += 1
                self.single_dict[s] = current_dict
                self.backup_dict[s] = self.global_emb_idx
                # for NaN and low frequency word
                # 为每个field留出2个emb的位置来处理不在词典中的值和缺失值
                self.global_emb_idx += 1
        #print(self.single_dict)

        if self.multi_features:
            for s in self.multi_features:
                # every field
                frequency_dict = {}
                current_dict = {}
                values = pd.concat([self.train, self.valid, self.test])[s]
                for vs in values:
                    for v in vs.split('|'):
                        v = int(v)
                        if v in frequency_dict:
                            frequency_dict[v] += 1
                        else:
                            frequency_dict[v] = 1
                for k, v in frequency_dict.items():
                    if v > Config.multi_feature_frequency:
                        current_dict[k] = self.global_emb_idx
                        self.global_emb_idx += 1
                self.multi_dict[s] = current_dict
                self.backup_dict[s] = self.global_emb_idx
                # for NaN and low frequency word
                # 为每个field留出2个emb的位置来处理不在词典中的值和缺失值
                # self.global_emb_idx += 1
        #print(self.multi_dict)
        #print(self.backup_dict)
    
    #将数值转换成索引，调整了列顺序
    def trans_data(self, data, save_file):
        print('trans data...' + save_file)
        # label index1:value1 index2:value2
        with open(save_file, 'w') as f:
            # label, index : 值
            def write_to_file(line):
                label = line[Config.label_name]
                f.write(str(label) + ',')
                self.label_num += 1
                for s in self.single_features:
                    now_v = line[s]
                    if now_v in self.single_dict[s]:
                        now_idx = self.single_dict[s][now_v]
                    else:
                        #处理异常值
                        now_idx = self.backup_dict[s]
                    f.write(str(now_idx) + ':' + str(1) + ',')
                    self.single_num += 1
                for s in self.num_features:
                    now_v = line[s]
                    f.write(str(self.num_dict[s]) + ':' + str(now_v) + ',')
                    self.single_num += 1
                for s in self.multi_features:
                    now_v = line[s]
                    if '|' not in now_v:
                        idxs = [now_v]
                    else:
                        idxs = now_v.split('|')
                    #idxs = [x for x in idxs if int(x) in self.multi_dict[s]] #是否写错，应转换成索引
                    idxs = [str(self.multi_dict[s][int(x)]) for x in idxs if int(x) in self.multi_dict[s]]
                    #print(idxs)
                    if idxs:
                        f.write(str('|'.join(idxs)) + ':' + str(1) + ',')
                    else:
                        f.write(str(self.backup_dict[s]) + ':' + str(1) + ',')
                        #print(idxs)
                    self.multi_num += 1
                f.write('\n')
            #.apply Apply a function along an axis of the DataFrame   
            data.apply(lambda x: write_to_file(x), axis=1) 
            
    #检查数据格式是否相同,shape[1]返回第一行列数
    def check(self):
        if self.train.shape[1] == self.valid.shape[1] == self.test.shape[1]:
            return True
        else:
            print('error , all dataset must have same shape')

    # 保存数据处理的信息 总的embedding大小，单值离散特征数量，数值型特征数量，多值离散特征数量
    def save_conf(self):
        with open('data_conf.txt', 'w') as f:
            f.write(str(self.global_emb_idx) + '\t')
            f.write(str(len(self.single_features)) + '\t')
            f.write(str(len(self.num_features)) + '\t')
            f.write(str(len(self.multi_features)))


if __name__ == '__main__':
    pa = Parse()