# -*- coding: utf-8 -*-
import re

# 保存全部的CID关系
CID = {}


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


# 抽取特征函数
def read_sentence(raw_file, feature_file):
    fw = open(feature_file, 'w')

    # 0 标记标题 1 标记摘要
    title_flag = 0

    with open(raw_file) as fp:
        # 标记文章
        passage = fp.readline()
        fw.write(passage)

        while len(passage) > 0:
            line = fp.readline()
            while "passage" not in line and len(line) > 0:
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
                    if contain_entity(line):
                        all_entities = extract_all_entities(line)
                        line = line.split()
                        l = len(line)
                        # 处理每一对实体
                        # 特征顺序：CID,化学物质位置,疾病位置,距离,顺序,包含化学物质数量,包含疾病数量,包含化学物质种类,包含疾病种类,是否在标题中
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
                            if order == 0:
                                others = contain_others(line[chemical_pos + 1:disease_pos])
                            else:
                                others = contain_others(line[disease_pos + 1:chemical_pos])
                            other_chemical_number = others[0]
                            other_disease_number = others[1]
                            other_chemical_kind = others[2]
                            other_disease_kind = others[3]
                            fw.write("%2d %2d %2d %10f %2d %2d %2d %2d %2d %2d\t%s\t%s\n" % (
                                is_cid, chemical_pos, disease_pos, distance, order, other_chemical_number,
                                other_disease_number, other_chemical_kind, other_disease_kind, title_flag, chemical,
                                disease))
                line = fp.readline()
            passage = line
            fw.write(passage)
    fw.close()


# 判断句子内是否存在实体对
def contain_entity(sentence):
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


if __name__ == "__main__":
    raw_file_list = ["replace/train.txt", "replace/develop.txt", "replace/test.txt"]
    feature_file_list = ["feature/train.txt", "feature/develop.txt", "feature/test.txt"]

    # sentence = "In brain membranes from spontaneously D_D006973 rats C_D003000 , 10 ( -8 ) to 10 ( -5 ) M , did not influence stereoselective binding of [ 3H ] -C_D009270 ( 8 nM ) , and C_D009270 , 10 ( -8 ) to 10 ( -4 ) M , did not influence C_D003000-suppressible binding of C_-1 ( 1 nM ) ."

    read_CID("replace/train.txt")
    for raw_file, feature_file in zip(raw_file_list, feature_file_list):
        read_sentence(raw_file, feature_file)
