import re

CID = {}
keywords = []


# 读取全部的CID关系
def read_CID(file):
    with open(file) as fp:
        line = fp.readline()
        while len(line) > 0:
            if line.startswith("CID"):
                line = line.split()
                if line[1] in CID:
                    CID[line[1]].append(line[2])
                else:
                    CID[line[1]] = [line[2]]
            line = fp.readline()


# 读取关键词unigram和bigram
def read_keywords(file, num):
    count = 0
    with open(file) as fp:
        while count < num:
            line = fp.readline()[:-1]
            keywords.append(line)
            count += 1


def read_sentence(raw_file, statistics_file, feature_file, CID_file, key_num):
    fw = open(feature_file, 'w')
    fCID = open(CID_file, 'w')

    with open(raw_file) as fp:
        # 标记文章
        passage = fp.readline()

        while len(passage) > 0:
            title = ""
            # 保存每篇文章中的句子
            sentences = []

            line = fp.readline()
            while not line.startswith("passage") and len(line) > 0:
                if line == 'title:\n' or line == 'abstract:\n' or line.startswith("CID"):
                    pass
                else:
                    if line.startswith("title"):
                        line = line[8:]
                        title = line
                    elif line.startswith("abstract"):
                        line = line[11:]
                    sentences.append(line)
                line = fp.readline()

            l = len(sentences)
            if l >= 2:
                for i in range(l - 1):
                    for j in range(i + 1, l):
                        if contain_entities(sentences[i], sentences[j]):
                            all_entities = extract_all_entities(sentences[i], sentences[j])

# 判断两个句子是否
def contain_entities(sentence1, sentence2):
    sentence1 = sentence1.split()
    sentence2 = sentence2.split()

    chemical1 = False
    disease1 = False

    chemical1 = False
    disease1 = False
    for word in sentence1:
        if "C_D" in word or "C_C" in word:
            chemical1 = True
        if "D_D" in word or "D_C" in word:
            disease1 = True

    chemical2 = False
    disease2 = False
    for word in sentence2:
        if "C_D" in word or "C_C" in word:
            chemical2 = True
        if "D_D" in word or "D_C" in word:
            disease2 = True

    if (chemical1 == True and disease2 == True) or (chemical2 == True and disease1 == True):
        return True
    else:
        return False

if __name__ == "__main__":
    raw_file_list = ["replace/train.txt", "replace/develop.txt", "replace/test.txt"]
    feature_file_list = ["feature/train_out.txt", "feature/develop_out.txt", "feature/test_out.txt"]
    CID_file_list = ["CID_extract/train_out.txt", "CID_extract/develop_out.txt", "CID_extract/test_out.txt"]
    statistics_file_list = ["statistics/train.txt", "statistics/develop.txt", "statistics/test.txt"]
    keywords_file_list = ["keywords/unigram.txt", "keywords/bigram.txt"]

    key_num = 50

    for keywords_file in keywords_file_list:
        read_keywords(keywords_file, key_num)

    for raw_file, statistics_file, feature_file, CID_file in zip(raw_file_list, statistics_file_list, feature_file_list,
                                                                 CID_file_list):
        read_CID(raw_file)
        read_sentence(raw_file, statistics_file, feature_file, CID_file, key_num)
