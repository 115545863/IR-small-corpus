# 字典存储，{aueryID：[DocumentID,...]}
# 文件读取(q)
file_qrels = open('files/qrels.txt', encoding="UTF_8")
# 专家的结果，即相关文件，qrels
list_qrels = {}
# 遍历文件的每一行
for line in file_qrels:
    # text = file_read.readline()
    # 根据空格分割成列表
    text = line.replace("\n", "").split(' ')
    # text[0]是queryID，text[2]是documentID
    if text[0] not in list_qrels.keys():
        # 如果queryID已经储存在字典里了，只需要向储存的列表中添加新的document
        list_qrels[text[0]] = [text[2]]
    else:
        # 如果queryID还没有储存至字典，则创建值
        list_qrels[text[0]].append(text[2])
file_qrels.close()

# 获取result的，原理与qrels相似
# 文件读取(q)
file_result = open('files/result.txt', encoding="UTF_8")
# 计算机的结果
list_result = {}
for line in file_result:
    # text = file_read.readline()
    text = line.replace("\n", "").split(' ')
    if text[0] not in list_result.keys():
        list_result[text[0]] = [text[2]]
    else:
        list_result[text[0]].append(text[2])
file_result.close()

# 获取相同的，即既在result又在qrels中
# 查找相同的
# [[queryID,iteration,documentID,rank,score,runID,relevance]]
list_equal = {}
for queryID in list_qrels.keys():
    # 取交集
    equal =list(set(list_result[queryID]) & set(list_qrels[queryID]))
    list_equal[queryID] = equal

# 计算precision,recall
precision = 0
recall = 0
pre_10 = 0
r_precision = 0
map = 0
bpref = 0
for key in list_qrels.keys():
    # precision for per query
    precision = precision + len(list_equal[key])/len(list_result[key])
    # recall for per query
    recall = recall+len(list_equal[key])/len(list_qrels[key])
    # precision@10 for per query
    pre_10 = pre_10+ len(list(set(list_result[key][:10]) & set(list_qrels[key])))/10
    # r-precision for per query
    length = len(list_qrels[key])
    if length!=0 and length<=len(list_result[key]):
        # relevant <= 15
        r_precision = r_precision+ len(list(set(list_result[key][:length]) & set(list_qrels[key])))/length
    elif length==0:
        # relevant = 0
        r_precision = r_precision + 0
    else:
        # relevant > 15
        r_precision = r_precision + len(list(set(list_result[key]) & set(list_qrels[key]))) / length
    # map for per query
    map_pre = 0
    for element in list_equal[key]:
        # 对于每一个相同的元素，计算precision
        position = list_result[key].index(element)+1
        map_pre = map_pre+ len(list(set(list_result[key][:position]) & set(list_qrels[key])))/position
    map = map+map_pre/len(list_qrels[key])
    # bpref for per query
    bpref_per = 0
    for element in list_equal[key]:
        # 对于每一个相同的元素，计算1-(不相关文件数/相关文件数)
        rele_num = len(list_qrels[key])
        position = list_result[key].index(element)+1
        non_num = len(set(list_result[key][:position])-set(list_equal[key]))
        if non_num<=rele_num:
            # 如果不相关文件数小于相关文件数，则1-不相关/相关
            bpref_per = bpref_per+(1-non_num/rele_num)
        else:
            # 如果不相关文件数超过了相关文件数，取0
            bpref_per = bpref_per+0
    bpref = bpref + bpref_per/len(list_qrels[key])

# 取平均值
average_length = len(list_qrels.keys())
precision = precision/average_length
recall = recall/average_length
pre_10 = pre_10/average_length
r_precision = r_precision/average_length
map = map/average_length
bpref = bpref/average_length

print('Evaluation results:')
print('Precision: ',precision)
print('Recall: ',recall)
print('R-precision: ',r_precision)
print('P@10: ',pre_10)
print('MAP: ',map)
print('bpref: ',bpref)