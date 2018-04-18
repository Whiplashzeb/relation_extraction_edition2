# -*- coding: utf-8 -*-
import re
from stanfordcorenlp import StanfordCoreNLP

# 保存全部的CID关系
CID = {}
# 保存全部的关键词
keywords = []
# 语法分析器
nlp = StanfordCoreNLP("/Users/aurora/stanford-corenlp")


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
def read_sentence(raw_file, statistics_file, feature_file, CID_file, key_num):
    fw = open(feature_file, 'w')
    fCID = open(CID_file, 'w')

    # 0 标记标题 1 标记摘要
    title_flag = 0

    with open(raw_file) as fp:
        # 标记文章
        passage = fp.readline()

        while len(passage) > 0:
            title = ""
            all_chemical, all_disease, all_cid, all_chemical_num, all_disease_num, all_cid_num = get_number(passage,
                                                                                                            statistics_file)
            line = fp.readline()
            while not line.startswith("passage") and len(line) > 0:
                if line == 'title:\n' or line == 'abstract:\n' or line.startswith("CID"):
                    pass
                else:
                    if line.startswith("title"):
                        title_flag = 0
                        line = line[8:]
                        title = line
                    elif line.startswith("abstract"):
                        title_flag = 1
                        line = line[11:]
                    # 识别出全部共现的实体对
                    if contain_entities(line):
                        all_entities = extract_all_entities(line)
                        kwords = contain_keywords(line, key_num)
                        pos = nlp.pos_tag(line)  # 词性标注
                        line = line.split()
                        l = len(line)
                        # 处理每一对实体
                        # 特征顺序：CID,化学物质位置,疾病位置,距离,顺序,化学物质出现次数,疾病出现次数,关系出现次数,化学物质频率，
                        # 疾病频率，共现频率，包含化学物质数量,包含疾病数量,包含化学物质种类,包含疾病种类,是否在标题中,
                        # 化学物质是否出现在标题，疾病是否出现在标题，实体对是否出现在标题，关键词特征
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
                            chemical_number = all_chemical[chemical]  # 化学物质出现次数
                            disease_number = all_disease[disease]  # 疾病出现次数
                            cid_number = all_cid[(chemical, disease)]  # 共现次数
                            chemical_freq = float(chemical_number) / all_chemical_num  # 化学物质出现频率
                            disease_freq = float(disease_number) / all_disease_num  # 疾病出现频率
                            cid_freq = float(cid_number) / all_cid_num
                            if order == 0:
                                others = contain_others(line[chemical_pos + 1:disease_pos])
                            else:
                                others = contain_others(line[disease_pos + 1:chemical_pos])
                            other_chemical_number = others[0]  # 包含其他化学物质数量
                            other_disease_number = others[1]  # 包含其他疾病数量
                            other_chemical_kind = others[2]  # 包含其他化学物质种类
                            other_disease_kind = others[3]  # 包含其他疾病种类
                            chemical_in, disease_in, entities_in = in_title(chemical, disease, title)  # 是否出现在标题中
                            verb_num = get_verb_num(chemical_pos, disease_pos, pos)
                            fw.write(
                                "%d 1:%d 2:%d 3:%f 4:%d 5:%d 6:%d 7:%d 8:%f 9:%f 10:%f 11:%d 12:%d 13:%d 14:%d 15:%d 16:%d 17:%d 18:%d 19:%d" % (
                                    is_cid, chemical_pos, disease_pos, distance, order, chemical_number, disease_number,
                                    cid_number, chemical_freq, disease_freq, cid_freq, other_chemical_number,
                                    other_disease_number, other_chemical_kind, other_disease_kind, title_flag,
                                    chemical_in, disease_in, entities_in, verb_num))
                            for i, value in enumerate(kwords):
                                fw.write(" %d:%d" % (i + 20, value))
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

    chemical_count = 0
    for _, value in chemical.items():
        chemical_count += value
    disease_count = 0
    for _, value in disease.items():
        disease_count += value
    cid_count = 0
    for _, value in cid.items():
        cid_count += value
    return (chemical, disease, cid, chemical_count, disease_count, cid_count)


# 统计句内是否出现了关键词
def contain_keywords(sentence, num):
    words = sentence.split()
    res = []
    for i in range(len(keywords)):
        if i < num:
            if keywords[i] in words:
                res.append(1)
            else:
                res.append(0)
        else:
            if keywords[i] in sentence:
                res.append(1)
            else:
                res.append(0)
    return res


# 判断化学物质，疾病，实体对是否在
def in_title(chemical, disease, title):
    chemical_in = 0
    disease_in = 0
    entities_in = 0
    if chemical in title:
        chemical_in = 1
    if disease in title:
        disease_in = 1
    if chemical_in == 1 and disease_in == 1:
        entities_in = 1

    return (chemical_in, disease_in, entities_in)


# 计算包含的动词数
def get_verb_num(chemical_pos, disease_pos, pos):
    count = 0
    for i in range(chemical_pos + 1, disease_pos):
        if pos[i][1].startswith("VB"):
            count += 1

    return count


if __name__ == "__main__":
    raw_file_list = ["replace/train.txt", "replace/develop.txt", "replace/test.txt"]
    feature_file_list = ["feature/train_in.txt", "feature/develop_in.txt", "feature/test_in.txt"]
    CID_file_list = ["CID_extract/train_in.txt", "CID_extract/develop_in.txt", "CID_extract/test_in.txt"]
    statistics_file_list = ["statistics/train.txt", "statistics/develop.txt", "statistics/test.txt"]
    keywords_file_list = ["keywords/unigram.txt", "keywords/bigram.txt"]

    key_num = 50

    # sentence = "In brain membranes from spontaneously D_D006973 rats C_D003000 , 10 ( -8 ) to 10 ( -5 ) M , did not influence stereoselective binding of [ 3H ] -C_D009270 ( 8 nM ) , and C_D009270 , 10 ( -8 ) to 10 ( -4 ) M , did not influence C_D003000-suppressible binding of C_-1 ( 1 nM ) ."
    for keywords_file in keywords_file_list:
        read_keywords(keywords_file, key_num)
    for raw_file, statistics_file, feature_file, CID_file in zip(raw_file_list, statistics_file_list, feature_file_list,
                                                                 CID_file_list):
        read_CID(raw_file)
        read_sentence(raw_file, statistics_file, feature_file, CID_file, key_num)
