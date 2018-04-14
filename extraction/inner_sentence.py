# -*- coding: utf-8 -*-
import re

# 保存全部的CID关系
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


# 抽取特征函数
def read_sentence(raw_file, statistics_file, feature_file, CID_file):
    fw = open(feature_file, 'w')
    fCID = open(CID_file, 'w')

    # 0 标记标题 1 标记摘要
    title_flag = 0

    with open(raw_file) as fp:
        # 标记文章
        passage = fp.readline()

        while len(passage) > 0:
            all_chemical, all_disease, all_cid = get_number(passage, statistics_file)
            line = fp.readline()
            while not line.startswith("passage") and len(line) > 0:
                if line == 'title:\n' or line == 'abstract:\n' or line.startswith("CID"):
                    pass
                else:
                    if line.startswith("title"):
                        title_flag = 0
                        line = line[8:]
                    elif line.startswith("abstract"):
                        title_flag = 1
                        line = line[11:]
                    # 识别出全部共现的实体对
                    if contain_entities(line):
                        all_entities = extract_all_entities(line)
                        kwords = contain_keywords(line, 50)
                        line = line.split()
                        l = len(line)
                        # 处理每一对实体
                        # 特征顺序：CID,化学物质位置,疾病位置,距离,顺序,化学物质出现次数,疾病出现次数,关系出现次数,包含化学物质数量,包含疾病数量,包含化学物质种类,包含疾病种类,是否在标题中,关键词特征
                        for key, value in all_entities.items():
                            chemical_pos = key[0][0]  # 化学物质位置
                            chemical = key[0][1]
                            disease_pos = key[1][0]  # 疾病位置
                            disease = key[1][1]
                            is_cid = value  # 是否为正例
                            distance = abs(chemical_pos - disease_pos) / l  # 距离
                            order = 0  # 化学物质在前
                            if chemical_pos > disease_pos:
                                order = 1
                            chemical_number = all_chemical[chemical]
                            disease_number = all_disease[disease]
                            cid_number = all_cid[(chemical, disease)]
                            if order == 0:
                                others = contain_others(line[chemical_pos + 1:disease_pos])
                            else:
                                others = contain_others(line[disease_pos + 1:chemical_pos])
                            other_chemical_number = others[0]
                            other_disease_number = others[1]
                            other_chemical_kind = others[2]
                            other_disease_kind = others[3]
                            fw.write("%d 1:%d 2:%d 3:%f 4:%d 5:%d 6:%d 7:%d 8:%d 9:%d 10:%d 11:%d 12:%d" % (
                                is_cid, chemical_pos, disease_pos, distance, order, chemical_number, disease_number,
                                cid_number, other_chemical_number, other_disease_number, other_chemical_kind,
                                other_disease_kind, title_flag))
                            for i, value in enumerate(kwords):
                                fw.write(" %d:%d" % (i + 13, value))
                            fw.write('\n')
                            fCID.write("%s\t%s\n" % (chemical, disease))
                line = fp.readline()
            passage = line
    fw.close()
    fCID.close()


# 判断句子内是否存在实体对
def contain_entities(sentence):
    sentence = sentence.split()

    contain_chemical = False
    contain_disease = False

    for word in sentence:
        if "C_D" in word or "C_C" in word:
            contain_chemical = True
        if "D_D" in word or "D_C" in word:
            contain_disease = True

    if contain_chemical == True and contain_disease == True:
        return True
    else:
        return False


# 从共现的句子内抽取全部的实体对:
# 返回格式：((pos,chemical),(pos,disease)):CID
def extract_all_entities(sentence):
    # 存储化学物质实体，疾病实体，结果集合
    chemical_entities = []
    disease_entities = []
    result = {}

    sentence = sentence.split()
    for i, word in enumerate(sentence):
        if "C_D" in word or "C_C" in word:
            pattern = re.compile(r'C_D[-]*\d+|C_C[-]*\d+')
            match = pattern.search(word)
            if match:
                chemical_entities.append((i, match.group()))
        if "D_D" in word or "D_D" in word:
            pattern = re.compile(r'D_D[-]*\d+|D_C[-]*\d+')
            match = pattern.search(word)
            if match:
                disease_entities.append((i, match.group()))

    for c in chemical_entities:
        for d in disease_entities:
            if c[1] in CID and d[1] in CID[c[1]]:
                result[(c, d)] = 1
            else:
                result[(c, d)] = 0

    return result


# 统计实体对间包含的其他化学物质，疾病数量及种类
def contain_others(sentence):
    chemical = set()
    disease = set()
    chemical_number = 0
    disease_number = 0

    for word in sentence:
        if "C_D" in word or "C_C" in word:
            pattern = re.compile(r'C_D[-]*\d+|C_C[-]*\d+')
            match = pattern.search(word)
            if match:
                chemical.add(word)
                chemical_number += 1
        if "D_D" in word or "D_D" in word:
            pattern = re.compile(r'D_D[-]*\d+|D_C[-]*\d+')
            match = pattern.search(word)
            if match:
                disease.add(word)
                disease_number += 1
    res = (chemical_number, disease_number, len(chemical), len(disease))
    return res


# 统计实体对中实体在文章中出现的次数和共现次数
def get_number(passage_get, statistics_file):
    chemical = {}
    disease = {}
    cid = {}
    with open(statistics_file) as fp:
        passage = fp.readline()
        while len(passage) > 0:
            if passage_get == passage:
                line = fp.readline()
                while (not line.startswith("passage")) and len(line) > 0:
                    line = line.split()
                    if len(line) == 2:
                        if line[0].startswith('C_'):
                            chemical[line[0]] = int(line[1])
                        else:
                            disease[line[0]] = int(line[1])
                    elif len(line) == 3:
                        cid[(line[0], line[1])] = int(line[2])
                    line = fp.readline()
                break
            else:
                passage = fp.readline()

    return (chemical, disease, cid)


# 统计句内是否出现了关键词
def contain_keywords(sentence, num):
    words = sentence.split()
    res = []
    for i in range(len(keywords)):
        if i < num:
            if keywords[i] in words:
                res.append(1)
                print(keywords[i])
            else:
                res.append(0)
        else:
            if keywords[i] in sentence:
                res.append(1)
                print(keywords[i])
            else:
                res.append(0)
    return res


if __name__ == "__main__":
    raw_file_list = ["replace/train.txt", "replace/develop.txt", "replace/test.txt"]
    feature_file_list = ["feature/train.txt", "feature/develop.txt", "feature/test.txt"]
    CID_file_list = ["CID_extract/train.txt", "CID_extract/develop.txt", "CID_extract/test.txt"]
    statistics_file_list = ["statistics/train.txt", "statistics/develop.txt", "statistics/test.txt"]
    keywords_file_list = ["keywords/unigram.txt", "keywords/bigram.txt"]

    # sentence = "In brain membranes from spontaneously D_D006973 rats C_D003000 , 10 ( -8 ) to 10 ( -5 ) M , did not influence stereoselective binding of [ 3H ] -C_D009270 ( 8 nM ) , and C_D009270 , 10 ( -8 ) to 10 ( -4 ) M , did not influence C_D003000-suppressible binding of C_-1 ( 1 nM ) ."
    for keywords_file in keywords_file_list:
        read_keywords(keywords_file, 50)
    for raw_file, statistics_file, feature_file, CID_file in zip(raw_file_list, statistics_file_list, feature_file_list,
                                                                 CID_file_list):
        read_CID(raw_file)
        read_sentence(raw_file, statistics_file, feature_file, CID_file)
