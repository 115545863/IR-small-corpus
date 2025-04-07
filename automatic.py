# result format: rankID, documentID, similarity

# BM25: 对于文档和测试中都有的词，总文档数(1400)，需要某词出现的文档数，词在文档中出现的次数，该文档的长度和全部文档的平均长度
# 假设：k=1，b=0.75

# read files and write to a new file
import os,re
from files import porter
from math import log

files = sorted(os.listdir('documents'))
# 打开文件并写入内容
if not os.path.exists('files/file_of_document.txt'):
    with open('files/file_of_document.txt', "w") as f:
        for file in files:
            with open(os.path.join('documents', file), "r", encoding="UTF-8") as t:
                text = re.sub('([^\u0030-\u0039\u0041-\u007a])', ' ', ' '.join(t.read().splitlines()))
                f.write(file + " " + text + "\n")

# 字典拆分字符并记录频率
# load stopwords into appropriate data structure
stopwords = set()
with open('files\stopwords.txt', 'r') as f:
    for line in f:
        stopwords.add(line.rstrip())
# load the porter stemmer
stemmer = porter.PorterStemmer()

# open the document collection
f = open('files/file_of_document.txt', 'r')

docs = f.read().replace('/', '').split('\n')

# close the file
f.close()
dictionary = {}

# 储存长度的字典
dic_length = {}

# making dictionary
for doc in docs:
    terms = doc.split(" ")
    docdict = {}
    # 有标点的话会被划分到前面那个词，不会多占位置
    length = 0
    for term in terms[1:]:
        if term not in stopwords and term!='':
            term = stemmer.stem(term)
            length+=1
            if term not in docdict:
                docdict[term] = 1
            else:
                docdict[term] += 1
    dic_length[terms[0]] = length
    dictionary[terms[0]] = docdict
doc_average = sum(dic_length.values())/len(dic_length)

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

# 获取含有某词的文档数
def getNumber(term):
    times = 0
    for key in dictionary.keys():
        doc = dictionary[key]
        if term in doc:
            times+=1
    return times

# BM25: 对于文档和测试中都有的词，总文档数(1400)，需要某词出现的文档数，词在文档中出现的次数，该文档的长度和全部文档的平均长度
# 假设：k=1，b=0.75
def bm25(query,result_all,num_q):
    # 处理query
    terms = handle_words(query[1:])
    # 字典记录相似度
    dic_similar = {}
    # 遍历每一个文档信息
    for doc_key in dictionary.keys():
        # 每一个term的相似度加和，起始是0
        similarity_all = 0
        doc = dictionary[doc_key]
        for term in terms:
            # 对每一个词
            if term in doc:
                # 如果在文档里
                number_word = getNumber(term)
                similarity = ((int(doc[term])*2)/(int(doc[term])+0.25+(0.75*int(dic_length[doc_key])/doc_average)))*log((1400-number_word+0.5)/(number_word+0.5),2)
                similarity_all += similarity
        dic_similar[doc_key] = similarity_all
    rank_list = sorted(dic_similar.items(),key=lambda x : x[1], reverse=True)
    num = 0
    rank = 1
    while num <15:
        result_all = result_all+str(num_q)+' '+str(rank)+" "+str(rank_list[num][0])+" "+str(rank_list[num][1])+'\n'
        num+=1
        rank+=1
    return result_all

# open the query
q = open('files/queries.txt', 'r')
queries = q.read().replace('/', '').split('\n')
q.close()


# 打开文件并写入内容
# for query in queries:
#     # f.write("The result for query:" + query + '\n')
#     print(query[1:])
#     bm25(query[1:])
# # f.close()

if not os.path.exists('files/result.txt'):
    with open('files/result.txt', "w") as f:
        result_all = ''
        for query in queries:
            # result_all = result_all + "The result for query:"+query+'\n'
            # print(query[1:])
            num = query.split(' ')[0]
            result_all =  bm25(query,result_all,num)
        f.write(result_all)

