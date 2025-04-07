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
    query = query.casefold()
    query = re.sub('([^\u0030-\u0039\u0041-\u007a])', ' ', ''.join(query.replace('/', '')))
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
# 每个单词出现的文档
dic_occur = {}
# 单词
words = {}
whole_num = 1400
files = sorted(os.listdir('documents'))
# for file in files[1:]:
#     whole_num+=len(os.listdir('documents/'+file))
# 打开文件并写入内容

# 10-100
# 如果没有test文件(bm25_of_words)
if not os.path.exists('bm25_of_words.json'):
    for file in files[1:]:
        with open(os.path.join("documents/"+file), "r",encoding='utf-8') as t:
            # 使用 readlines() 方法读取文件中的所有行
            lines = t.readlines()
            text = ''
            for line in lines:
                # print(line.strip().replace('/','').replace('_',''))
                line =re.sub('([^\u0030-\u0039\u0041-\u007a])', ' ', ''.join(line.strip().replace('/','')))
                # print('lines'+line)
                text= text +' '+line
            # 2000-206F
            terms = text.split(' ')
            # print("terms:",terms)
            # 储存每个文档中每个词出现的次数
            docdict = {}

            # 有标点的话会被划分到前面那个词，不会多占位置
            length = 0
            # 可以通过两步计算，就是先找到不同的词有什么，使用set，然后在遍历不同的词，找到次数，使用list.count()
            # 这个地方不对，无法计算次数
            for term in terms:
                if term not in stopwords and term!= '' and len(term)!=1 and (term.find('__')!=False):
                    term = stemmer.stem(term)
                    term = term.casefold()
                    # print('term:',term)
                    length += 1
                    if term not in docdict:
                        docdict[term] = 1
                    else:
                        docdict[term] += 1
                    if term not in words:
                        words[term] = 1
                    if term not in dic_occur:
                        dic_occur[term] = [file]
                    else:
                        if file not in dic_occur[term]:
                            dic_occur[term].append(file)
            dic_length[file] = length
            dictionary[file] = docdict
                    # print('dictionary,',dictionary)
    # 额外的stopwords
    extend_stopwords={}
    # 实际应用过程中的单词及其出现文档
    actural_fre = {}
    # 计算stopwords，频率超过0.9就当做stopwords
    for key in dic_occur.keys():
        value_list = dic_occur[key]
        if len(value_list)/whole_num >=0.9:
            extend_stopwords[key] = len(value_list)/whole_num
            words.pop(key)
        else:
            actural_fre[key] = value_list
    # 将有用的数据写入文档
    with open("extend_stopwords.json", "w") as f:
        f.write(json.dumps(extend_stopwords,sort_keys=False, indent=4, separators=(',', ': ')))
    with open("actural_fre.json", "w") as f:
        f.write(json.dumps(actural_fre,sort_keys=False, indent=4, separators=(',', ': ')))
    with open("dictionary.json", "w") as f:
        f.write(json.dumps(dictionary,sort_keys=False, indent=4, separators=(',', ': ')))
    with open("dic_length.json", "w") as f:
        f.write(json.dumps(dic_length,sort_keys=False, indent=4, separators=(',', ': ')))
    with open("words.json", "w") as f:
        f.write(json.dumps(words,sort_keys=False, indent=4, separators=(',', ': ')))
    with open("fre_word.json", "w") as f:
        f.write(json.dumps(dic_occur,sort_keys=False, indent=4, separators=(',', ': ')))
    with open("whole.txt", "w") as f:
        f.write(str(whole_num))

else:
    extend_stopwords={}
    actural_fre = {}

    with open("dic_length.json") as d_length:
        length = json.loads(d_length.read())
        dic_length = length
    with open("dictionary.json") as dices:
        docs = json.loads(dices.read())
        dictionary = docs
    with open("whole.txt") as dices:
        whole_num = int(dices.readline())
    with open("words.json") as d_words:
        wordes = json.loads(d_words.read())
        words = wordes
    with open("actural_fre.json") as fre:
        fre_w = json.loads(fre.read())
        actural_fre = fre_w
# 平均长度
doc_average = sum(dic_length.values()) / len(dic_length)

# BM25: 对于文档和测试中都有的词，总文档数(1400)，需要某词出现的文档数，词在文档中出现的次数，该文档的长度和全部文档的平均长度
# 假设：k=1，b=0.75
def bm25(word):
    dic_bm25 = {}
    # 字典记录相似度
    # 遍历每一个文档信息
    similarity = 0
    for doc_key in actural_fre[word]:
        # 每一个term的相似度加和，起始是0
        doc = dictionary[doc_key]
        # if word in doc:
            # 对每一个词

        number_word = len(actural_fre[word])
        print(number_word)
        dic_bm25[doc_key] = ((int(doc[word])*2)/(int(doc[word])+0.25+(0.75*int(dic_length[doc_key])/doc_average)))*log((whole_num-number_word+0.5)/(number_word+0.5),2)

    return dic_bm25

dic_result={}
result_all = ''
# 如果无，则生成
if not os.path.exists('bm25_of_words.json'):
    for word in words:
        print('word',word)
        dic_result[word] = bm25(word)
    with open("bm25_of_words.json", "w") as f:
        f.write(json.dumps(dic_result,sort_keys=False, indent=4, separators=(',', ': ')))
# 获取bm25
dic_bm25 = {}
with open("bm25_of_words.json") as f:
    dic_bm25 = json.loads(f.read())

# 执行项目
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
            # 遍历查询里面的每个词
            if term in dic_bm25.keys():
                # 如果这个词的bm25已知
                if len(dic_bm.keys())==0:
                    # 如果此时还没有词在dic_bm中
                    # 则此时字典是dic_bm = {'documentID': bmOfTerm, ...}
                    # copy表示当一个改变，另一个不变
                    dic_bm = dic_bm25[term].copy()
                else:
                    for doc in dic_bm25[term].keys():
                        if doc not in dic_bm.keys():
                            # 如果还没有这个文档，就以他为开头
                            dic_bm[doc] = dic_bm25[term][doc]
                        else:
                            # 如果有了，就在原基础上加上
                            dic_bm[doc] += dic_bm25[term][doc]
        rank_list = sorted(dic_bm.items(), key=lambda x: x[1], reverse=True)
        num = 0
        rank = 1
        while len(rank_list) >num and num<15:
            result_all = str(rank_list[num][0]) + " " + str(
                rank_list[num][1])
            print(rank,result_all)
            num += 1
            rank += 1

