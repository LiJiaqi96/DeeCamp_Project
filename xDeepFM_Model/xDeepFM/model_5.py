# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 14:22:29 2018

@author: HCHO
"""
import tensorflow as tf
import Config
from tools import _get_data, _get_conf, get_label,auc_score
import time
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
model_i=0
class xDeepFM(object):
    def __init__(self):
        self.total_emb, self.single_size, self.numerical_size, self.multi_size = _get_conf()
        self.field_size = self.single_size + self.numerical_size + self.multi_size
        self.embedding_length = self.field_size * Config.embedding_size
        
        self._init_data()
        self._init_placeholder()
        self._init_Variable()
        self._init_Model()

        self._train()

    #读取数据
    def _init_data(self):
        #self.train = _get_data(Config.train_save_file)
        #self.valid = _get_data(Config.valid_save_file)
        self.test = _get_data(Config.test_save_file)

    #获取batch，并对数据进行处理，存储到列表
    def _get_batch(self, data, idx):
        start = time.time()
        if idx == -1:
            batch_data = data
        #每次取一个batch数据
        elif (idx + 1) * Config.batch_size <= len(data):
            batch_data = data[idx*Config.batch_size:(idx+1)*Config.batch_size]
        else:
            batch_data = data[idx*Config.batch_size:]
        final_label = []
        final_single_index = []
        final_numerical_value = []
        final_numerical_index = []
        final_multi_sparse_index = []
        final_multi_sparse_value = []
        final_value = []
        for idx, line in enumerate(batch_data):
            line_index = []
            line_value = []
            line_numerical_value = []
            line_data = line.split(',')
            final_label.append(int(line_data[0]))
            
            if self.single_size:
                for i in range(1, 1 + self.single_size):
                    single_pair = line_data[i].split(':')
                    line_index.append(int(single_pair[0]))
                    line_value.append(float(single_pair[1]))
            final_single_index.append(line_index)
            line_index = []
            
            #if 是否有问题，仅需self.numerical_size?
            if self.single_size + self.numerical_size:
                for i in range(1 + self.single_size, 1 + self.single_size + self.numerical_size):
                    single_pair = line_data[i].split(':')
                    if not Config.use_numerical_embedding:
                        line_numerical_value.append(float(single_pair[1]))
                    if float(single_pair[1]) == 0:
                        line_index.append(int(9999)) #?
                        line_value.append(float(1)) #为何不能为0? 防止除0？
                    else:
                        line_index.append(int(single_pair[0]))
                        line_value.append(float(single_pair[1]))
            final_numerical_value.append(line_numerical_value)
            final_numerical_index.append(line_index)
            line_index = []
            
            total_length = 1 + self.single_size + self.numerical_size + self.multi_size
            if self.multi_size:
                for i in range(1 + self.single_size + self.numerical_size, total_length):
                    single_pair = line_data[i].split(':')
                    _multi = [int(x) for x in single_pair[0].split('|')]
                    line_index.append(_multi)
                    for v in _multi:
                        final_multi_sparse_index.append([idx, idx]) #为何存一对idx?
                        final_multi_sparse_value.append(v) 
                    line_value.append(float(single_pair[1]))
            final_value.append(line_value)
        end = time.time()
        return [final_label, final_single_index, final_numerical_index,final_numerical_value,final_multi_sparse_index, final_multi_sparse_value, final_value]
    
    #样本初始化
    def _init_placeholder(self):
        self.ph = {}
        self.ph['label'] = tf.placeholder(dtype=tf.int8, shape=[None, 2])
        self.train_phase = tf.placeholder(tf.bool, name="train_phase")
        self.ph['value'] = tf.placeholder(dtype=tf.float32,
                                          shape=[None, self.single_size + self.numerical_size + self.multi_size])#存值
        self.ph['single_index'] = tf.placeholder(dtype=tf.int32, shape=[None, self.single_size])#存索引
        self.ph['numerical_index'] = tf.placeholder(dtype=tf.int32, shape=[None, self.numerical_size])
        #如何存储多值离散型?
        for s in Config.multi_features:
            self.ph['multi_index_%s' % s] = tf.placeholder(dtype=tf.int64, shape=[None, 2])
            self.ph['multi_value_%s' % s] = tf.placeholder(dtype=tf.int64, shape=[None])
        #numerical型值不做embedding，则
        if not Config.use_numerical_embedding:
            self.ph['numerical_value'] = tf.placeholder(dtype=tf.float32,shape=[None,self.numerical_size])

    #变量初始化,每次一万行。关于embedding_size取值问题
    def _init_Variable(self):
        self.vr = {}
        self.vr['single_second_embedding'] = tf.get_variable(name='single_second_embedding',
                                                             shape=(200000, Config.embedding_size),
                                                             initializer=tf.glorot_uniform_initializer())
        self.vr['numerical_second_embedding'] = tf.get_variable(name='numerical_second_embedding',
                                                             shape=(10000, Config.embedding_size),
                                                             initializer=tf.glorot_uniform_initializer())
        for s in Config.multi_features:
            self.vr['multi_second_embedding_%s' % s] = tf.get_variable(name='multi_second_embedding_%s' % s,
                                                                       shape=(250000, Config.embedding_size),
                                                                       initializer=tf.glorot_uniform_initializer())

        self.vr['single_first_embedding'] = tf.get_variable(name='single_first_embedding',
                                                            shape=(200000, 1),
                                                            initializer=tf.glorot_uniform_initializer())
        self.vr['numerical_first_embedding'] = tf.get_variable(name='numerical_first_embedding',
                                                            shape=(10000, 1),
                                                            initializer=tf.glorot_uniform_initializer())
        for s in Config.multi_features:
            self.vr['multi_first_embedding_%s' % s] = tf.get_variable(name='multi_first_embedding_%s' % s,
                                                                      shape=(250000, 1),
                                                                      initializer=tf.glorot_uniform_initializer())
        # DNN part
        if Config.use_numerical_embedding:
            dnn_net = [self.embedding_length] + Config.dnn_net_size
        else:
            dnn_net = [self.embedding_length - self.numerical_size * Config.embedding_size + self.numerical_size] + Config.dnn_net_size
        for i in range(len(Config.dnn_net_size)):
            self.vr['W_%d' % i] = tf.get_variable(name='W_%d' % i, shape=[dnn_net[i], dnn_net[i + 1]],
                                                  initializer=tf.glorot_uniform_initializer())
            self.vr['b_%d' % i] = tf.get_variable(name='b_%d' % i, shape=[dnn_net[i + 1]],
                                                  initializer=tf.zeros_initializer())
        # output

    #模型初始化，进行embedding
    def _init_Model(self):
        # first embedding
        first_single_result = tf.reshape(tf.nn.embedding_lookup(self.vr['single_first_embedding'],
                                                                self.ph['single_index']),
                                         shape=[-1, self.single_size]
                                         )
        first_numerical_result = tf.reshape(tf.nn.embedding_lookup(self.vr['numerical_first_embedding'],
                                                                self.ph['numerical_index']),
                                         shape=[-1, self.numerical_size]
                                         )
        first_multi_result = []
        if Config.multi_features:
            for s in Config.multi_features:
                temp_multi_result = tf.nn.embedding_lookup_sparse(self.vr['multi_first_embedding_%s' % s],
                                                                  tf.SparseTensor(indices=self.ph['multi_index_%s' % s],
                                                                                  values=self.ph['multi_value_%s' % s],
                                                                                  dense_shape=(Config.batch_size,
                                                                                               Config.embedding_size)),
                                                                  None,
                                                                  combiner="sum"
                                                                  )
                first_multi_result.append(temp_multi_result)
                first_multi_result = tf.concat(first_multi_result, axis=1)
            first_embedding_output = tf.concat([first_single_result, first_numerical_result,first_multi_result], axis=1)
        else:
            first_embedding_output = tf.concat([first_single_result, first_numerical_result], axis=1)

        y_first_order = tf.multiply(first_embedding_output, self.ph['value'])

        # second embedding
        second_single_result = tf.reshape(tf.nn.embedding_lookup(self.vr['single_second_embedding'],
                                                                 self.ph['single_index']),
                                          shape=[-1, Config.embedding_size * self.single_size]
                                          )
        second_numerical_result = tf.reshape(tf.nn.embedding_lookup(self.vr['numerical_second_embedding'],
                                                                 self.ph['numerical_index']),
                                          shape=[-1, Config.embedding_size * self.numerical_size]
                                          )
        if Config.multi_features:
            second_multi_result = []
            for s in Config.multi_features:
                temp_multi_result = tf.nn.embedding_lookup_sparse(self.vr['multi_second_embedding_%s' % s],
                                                                  tf.SparseTensor(indices=self.ph['multi_index_%s' % s],
                                                                                  values=self.ph['multi_value_%s' % s],
                                                                                  dense_shape=(Config.batch_size,
                                                                                               Config.embedding_size)),
                                                                  None,
                                                                  combiner="sum"
                                                                  )
                second_multi_result.append(temp_multi_result)
                second_multi_result = tf.concat(second_multi_result, axis=1)
            # DNN input
            self.DNN_input = tf.concat([second_single_result,second_multi_result], axis=1)
        else:
            self.DNN_input = tf.concat([second_single_result], axis=1)
        self.middle_fm_input = tf.concat([self.DNN_input,second_numerical_result], axis=1)
        if Config.use_numerical_embedding:
            self.DNN_input = tf.concat([self.DNN_input,second_numerical_result], axis=1)
        else:
            self.DNN_input = tf.concat([self.DNN_input,self.ph['numerical_value']],axis=1)
        self.shape = tf.shape(self.DNN_input)
        # second output
        second_FM_input = tf.reshape(self.middle_fm_input, shape=[-1, self.single_size + self.numerical_size + self.multi_size,
                                                       Config.embedding_size])

        summed_features_emb = tf.reduce_sum(second_FM_input, 1)
        summed_features_emb_square = tf.square(summed_features_emb)
        squared_features_emb = tf.square(second_FM_input)
        squared_sum_features_emb = tf.reduce_sum(squared_features_emb, 1)
        y_second_order = 0.5 * tf.subtract(summed_features_emb_square, squared_sum_features_emb)

        dnn_output = self.DNN_input
        # DNN output
        for i in range(len(Config.dnn_net_size)):
            self.DNN_input = tf.add(tf.matmul(self.DNN_input, self.vr['W_%d' % i]), self.vr['b_%d' % i])
            self.DNN_input = tf.layers.batch_normalization(self.DNN_input,training=self.train_phase)
            dnn_output = tf.nn.relu(self.DNN_input)

        # CIN
        D = Config.embedding_size
        final_result = []
        final_len = 0
        field_nums = [self.field_size]
        if Config.multi_features:
            nn_input = tf.reshape(tf.concat([second_single_result, second_multi_result], axis=1),
                                  shape=[-1, self.field_size, Config.embedding_size])
        else:
            nn_input = tf.reshape(second_single_result,
                                  shape=[-1, self.field_size, Config.embedding_size])
        cin_layers = [nn_input]
        split_tensor_0 = tf.split(nn_input, D * [1], 2)
        for idx, layer_size in enumerate(Config.cross_layer_size):
            now_tensor = tf.split(cin_layers[-1], D * [1], 2)
            # Hk x m
            dot_result_m = tf.matmul(split_tensor_0, now_tensor, transpose_b=True)
            dot_result_o = tf.reshape(dot_result_m, shape=[D, -1, field_nums[0] * field_nums[-1]])
            dot_result = tf.transpose(dot_result_o, perm=[1, 0, 2])
            filters = tf.get_variable(name="f_" + str(idx), shape=[1, field_nums[-1] * field_nums[0], layer_size],
                                      dtype=tf.float32)
            curr_out = tf.nn.conv1d(dot_result, filters=filters, stride=1, padding='VALID')
            b = tf.get_variable(name="f_b" + str(idx), shape=[layer_size], dtype=tf.float32,
                                initializer=tf.zeros_initializer())
            curr_out = tf.nn.relu(tf.nn.bias_add(curr_out, b))
            curr_out = tf.transpose(curr_out, perm=[0, 2, 1])
            if Config.cross_direct:
                direct_connect = curr_out
                next_hidden = curr_out
                final_len += layer_size
                field_nums.append(int(layer_size))
            else:
                if idx != len(Config.cross_layer_size) - 1:
                    next_hidden, direct_connect = tf.split(curr_out, 2 * [int(layer_size / 2)], 1)
                    final_len += int(layer_size / 2)
                else:
                    direct_connect = curr_out
                    next_hidden = 0
                    final_len += layer_size

                field_nums.append(int(layer_size / 2))
            final_result.append(direct_connect)
            cin_layers.append(next_hidden)
        result = tf.concat(final_result, axis=1)
        result = tf.reduce_sum(result, -1)
        w_nn_output1 = tf.get_variable(name='w_nn_output1', shape=[final_len, Config.cross_output_size],
                                       dtype=tf.float32)
        b_nn_output1 = tf.get_variable(name='b_nn_output1', shape=[Config.cross_output_size], dtype=tf.float32,
                                       initializer=tf.zeros_initializer())
        CIN_out = tf.nn.xw_plus_b(result, w_nn_output1, b_nn_output1)

        # final output
        output_length = 0
        to_concat = []
        if Config.FM_layer:
            to_concat.append(y_first_order)
            to_concat.append(y_second_order)
            output_length += self.field_size + Config.embedding_size
        if Config.CIN_layer:
            to_concat.append(CIN_out)
            output_length += Config.cross_output_size
        if Config.DNN_layer:
            to_concat.append(dnn_output)
            output_length += Config.dnn_net_size[-1]

        output = tf.concat(to_concat, axis=1)

        self.vr['final_w'] = tf.get_variable(name='final_w', shape=[output_length, 2],
                                             initializer=tf.glorot_uniform_initializer())
        self.vr['final_b'] = tf.get_variable(name='final_b', shape=[2],
                                             initializer=tf.zeros_initializer())
        final_logits = tf.add(tf.matmul(output, self.vr['final_w']), self.vr['final_b'])
        self.softmax_output = tf.nn.softmax(final_logits)
        self.loss = tf.reduce_mean(
            tf.nn.softmax_cross_entropy_with_logits(labels=self.ph['label'], logits=final_logits))
        #self.optimizer = tf.train.AdagradOptimizer(learning_rate=Config.learning_rate).minimize(self.loss)
        self.optimizer = tf.train.AdamOptimizer(learning_rate=Config.learning_rate).minimize(self.loss)

    def _train(self):
        print('....')
        #设置GPU用量
        #config = tf.ConfigProto() 
        #config.gpu_options.per_process_gpu_memory_fraction = 0.9 # 占用GPU100%的显存 
        #session = tf.Session(config=config)
        #设置最小的GPU使用量
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        self.sess = tf.Session(config=config)
               
        print('start')
        saver=tf.train.Saver()     #保存模型   
        sess=tf.Session() 
        with tf.Session() as self.sess:
            self.sess.run(tf.global_variables_initializer())
            model_file=tf.train.get_checkpoint_state('ckpt/')
            path=model_file.all_model_checkpoint_paths[model_i]
            #print(path)
            saver.restore(self.sess,path)    
            
            allDataLength = len(self.test)
            num_batchs = int(allDataLength / Config.batch_size) + 1
            print('total step:%d'%(num_batchs))
            
            f=open('OUT/test_out.csv','w')
            for j in range(num_batchs):
                    print(j)
                    #测试集
                    self.test_batch = self._get_batch(self.test,j)                    
                    self.test_label = get_label(self.test_batch[0], 2)
                    self.test_dict = {
                                            self.ph['single_index']: self.test_batch[1],
                                            self.ph['numerical_index']: self.test_batch[2],
                                            self.ph['numerical_value']: self.test_batch[3],
                                            self.ph['value']: self.test_batch[-1],
                                            self.ph['label']: self.test_label,
                                            self.train_phase: False
                                        }
                    if Config.multi_features:
                        for idx, s in enumerate(Config.multi_features):
                            self.test_dict[self.ph['multi_index_%s' % s]] = self.test_batch[4]
                            self.test_dict[self.ph['multi_value_%s' % s]] = self.test_batch[5]
            
            
                    test_out= self.sess.run(self.softmax_output,feed_dict=self.test_dict)
                    test_output=test_out.tolist()
                    f.write(str(test_output)+'\n')
            f.close()

if __name__ == '__main__':
    tf.reset_default_graph()
    xdeep = xDeepFM()
