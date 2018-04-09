import nltk.data
from nltk.tokenize import word_tokenize

# 替换文章中的化学物质和疾病为MeSH@ID
def replace_entity(raw_file, replace_file):
    # 写入文件
    fw = open(replace_file, 'w')

    # 处理原始文件
    with open(raw_file) as fp:
        title = fp.readline()
        while len(title) > 0:
            # 获得文章的编号及标题
            title1 = title.partition("|t|")[0]
            title = title.partition("|t|")[2]
            fw.write("passage:" + title1 + '\n')

            # 获得文章摘要
            abstract = fp.readline().partition("|a|")[2]

            # 待匹配文章
            raw_passage = title + abstract
            # 匹配后文章
            passage = 'title:\n' + title + 'abstract:\n' + abstract

            # 存储致病关系
            CID = {}
            # 获取实体
            entity = fp.readline()
            while len(entity) > 1:
                entity = entity.split()
                l = len(entity)
                # 替换实体
                if l >= 6:
                    start, end = int(entity[1]), int(entity[2])
                    if entity[l - 2] == 'Chemical':
                        passage = passage.replace(raw_passage[start:end], 'C_' + entity[l - 1])
                    elif entity[l - 2] == 'Disease':
                        passage = passage.replace(raw_passage[start:end], 'D_' + entity[l - 1])
                # 存储CID关系
                if l == 4:
                    if 'C_' + entity[2] in CID:
                        CID['C_' + entity[2]].add('D_' + entity[3])
                    else:
                        CID['C_' + entity[2]] = set(['D_' + entity[3]])

                entity = fp.readline()

            # 存储文章，包含text tokenization 和 sentence tokenization
            tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
            result = tokenizer.tokenize(passage)
            for sentence in result:
                r = word_tokenize(sentence)
                for word in r:
                    fw.write(word + ' ')
                fw.write('\n')

            # 存储致病关系
            for c, d in CID.items():
                for item in d:
                    fw.write("CID:\t%s\t%s\n" % (c, item))

            title = fp.readline()
    fw.close()


if __name__ == "__main__":
    raw_file_list = ["raw_data/train.txt", "raw_data/develop.txt", "raw_data/test.txt"]
    replace_file_list = ["replace/train.txt", "replace/develop.txt", "replace/test.txt"]
    for file1, file2 in zip(raw_file_list, replace_file_list):
        replace_entity(file1, file2)
