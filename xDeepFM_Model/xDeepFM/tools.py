from sklearn.metrics import roc_auc_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

#评估函数，直接根据真实值（必须是二值）、预测值（可以是0/1, 也可以是proba值）计算出auc值
def auc_score(preds, labels, label_size):
    preds = [x[label_size - 1] for x in preds]
    labels = [x[label_size - 1] for x in labels]
    roc_score = roc_auc_score(labels, preds)
    preds = [int(item>0.5) for  item in preds]
    precision=accuracy_score(labels, preds)
    recall=precision_score(labels, preds)
    accuracy=recall_score(labels, preds)
    return roc_score,accuracy,precision,recall

#将文本按行储存到列表中
def _get_data(data_dir):
    data = []
    with open(data_dir, 'r') as f:
        line = f.readline()
        while line:
            data.append(line)
            line = f.readline()
    return data

#对列表元素进行分割
def _get_conf():
    with open('data_conf.txt', 'r') as f:
        line = f.readline()
    line = line.split('\t')
    return int(line[0]), int(line[1]), int(line[2]), int(line[3])

#将[0/1]  转换为 one hot式的两位表达 
def get_label(labels, label_size):
    final_label = []
    for v in labels:
        temp_label = [0] * label_size
        temp_label[v] = 1
        final_label.append(temp_label)
    return final_label
