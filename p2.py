# result format: rankID, documentID, similarity

# BM25: 对于文档和测试中都有的词，总文档数(1400)，需要某词出现的文档数，词在文档中出现的次数，该文档的长度和全部文档的平均长度
# 假设：k=1，b=0.75

# read files and write to a new file
import os,re,json
from files import porter
from math import log
import datetime
starttime = datetime.datetime.now()
#long running
# 字典拆分字符并记录频率
# load stopwords into appropriate data structure
stopwords = set()
with open('files\stopwords.txt', 'r',encoding='utf-8') as f:
    for line in f:
        stopwords.add(line.rstrip())
# load the porter stemmer
stemmer = porter.PorterStemmer()

# 处理词
def handle_words(query):
    terms = query.split(" ")
    new_term = []
    for term in terms:
        if term not in stopwords and term!='':
            term = stemmer.stem(term)
            if term not in new_term:
                new_term.append(term)
    return new_term

# 储存次数
dictionary = {}
# 储存长度的字典
dic_length = {}
# 单词
words = []

files = sorted(os.listdir('documents'))
# 打开文件并写入内容
# if not os.path.exists('test.json'):
for file in files[1:]:
    # 使用 readlines() 方法读取文件中的所有行
    with open(os.path.join('documents', file), "r", encoding="UTF-8") as t:
        text = re.sub('([^\2000-\206F])', ' ', ' '.join(t.read().splitlines()))
        # 2000-206F
        terms = text.split(' ')
        docdict = {}
        # 有标点的话会被划分到前面那个词，不会多占位置
        length = 0
        # 可以通过两步计算，就是先找到不同的词有什么，使用set，然后在遍历不同的词，找到次数，使用list.count()
        # 这个地方不对，无法计算次数
        for term in terms:
            if term not in stopwords:
                term = stemmer.stem(term)
                length += 1
                if term not in docdict:
                    docdict[term] = 1
                else:
                    docdict[term] += 1
                if term not in words:
                    words.append(term)
        dic_length[file] = length
        dictionary[file] = docdict

doc_average = sum(dic_length.values()) / len(dic_length)
endtime = datetime.datetime.now()
print ((endtime - starttime).seconds)

# open the document collection
# f = open('files/file_of_document.txt', 'r',encoding='utf-8')
#
# # 减少循环次数！！！
# docs = f.read().encode('gbk', 'ignore').decode('gbk').replace('|', '').split('\n')
#
# # close the file
# f.close()

# making dictionary
# for doc in docs:
#     terms = doc.split(" ")
#     docdict = {}
#     # 有标点的话会被划分到前面那个词，不会多占位置
#     length = 0
#     for term in terms[2:]:
#         if term not in stopwords:
#             term = stemmer.stem(term)
#             length += 1
#             if term not in docdict:
#                 docdict[term] = 1
#             else:
#                 docdict[term] += 1
#     dic_length[terms[1]] = length
#     dictionary[terms[1]] = docdict
# doc_average = sum(dic_length.values()) / len(dic_length)

# making dictionary
# for doc in docs:
#     terms = doc.split(" ")
#     docdict = {}
#     # 有标点的话会被划分到前面那个词，不会多占位置
#     length = 0
#     # 可以通过两步计算，就是先找到不同的词有什么，使用set，然后在遍历不同的词，找到次数，使用list.count()
#     # 这个地方不对，无法计算次数
#     for term in list(set(terms[1:])-set(stopwords)):
#         term = stemmer.stem(term)
#         length += 1
#         if term not in docdict:
#             docdict[term] = 1
#         else:
#             docdict[term] += 1
#     if terms[0] != '':
#         dic_length[terms[1]] = length
#         dictionary[terms[1]] = docdict
# doc_average = sum(dic_length.values()) / len(dic_length)


#
# 获取含有某词的文档数
def getNumber(term):
    times = 0
    for doc in dictionary:
        if term in doc:
            times+=1
    return times

# BM25: 对于文档和测试中都有的词，总文档数(1400)，需要某词出现的文档数，词在文档中出现的次数，该文档的长度和全部文档的平均长度
# 假设：k=1，b=0.75
def bm25(word):
    dic_bm25 = {}
    # 字典记录相似度
    # 遍历每一个文档信息
    similarity = 0
    for doc_key in dictionary.keys():
        # 每一个term的相似度加和，起始是0
        print('doc_key',doc_key)
        doc = dictionary[doc_key]
        print('doc:',doc)
        if word in doc:
            # 对每一个词
            number_word = getNumber(word)
            print(int(dic_length[doc_key])/doc_average)
            dic_bm25[doc_key] = ((int(doc[word])*2)/(int(doc[word])+0.25+(0.75*int(dic_length[doc_key])/doc_average)))*log((1400-number_word+0.5)/(number_word+0.5),2)
    return dic_bm25

# open the query
# q = open('files/queries.txt', 'r')
# queries = q.read().replace('/', '').split('\n')
# q.close()


# 打开文件并写入内容
# for query in queries:
#     # f.write("The result for query:" + query + '\n')
#     print(query[1:])
#     bm25(query[1:])
# # f.close()
if not os.path.exists('test.json'):
    dic_result={}
    result_all = ''
    for word in words:
        dic_result[word] = bm25(word)
    with open("test.json", "w") as f:
        f.write(json.dumps(dic_result,sort_keys=False, indent=4, separators=(',', ': ')))

with open("test.json") as f:
    dic_bm25 = json.loads(f.read())

q = open('files/queries.txt', 'r')
queries = q.read().replace('/', '').split('\n')
q.close()
for query in queries:
    print(handle_words(query))
print(dictionary)
print(bm25(queries[0]))

isKeeping = True
while isKeeping:
    print('Loading BM25 index from file, please wait.')
    query = input("Enter query:")
    print('Results for query:',query)
    if query=='EXIT':
        isKeeping = False
    else:
        query = handle_words(query)
        dic_bm = {}
        for term in query:
            if term in dic_bm25.keys():
                if len(dic_bm.keys())==0:
                    dic_bm = dic_bm25[term].copy()
                else:
                    for doc in dic_bm25[term].keys():
                        if doc not in dic_bm.keys():
                            dic_bm[doc] = dic_bm25[term][doc]
                        else:
                            dic_bm[doc] += dic_bm25[term][doc]
        rank_list = sorted(dic_bm.items(), key=lambda x: x[1], reverse=True)
        num = 0
        rank = 1
        while num < 15:
            result_all = str(rank_list[num][0]) + " " + str(
                rank_list[num][1])
            print(result_all)
            num += 1
            rank += 1



