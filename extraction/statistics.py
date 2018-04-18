# -*- coding: utf-8 -*-

import re
from inner_sentence import contain_entities


def count(raw_file, statistics_file):
    fw = open(statistics_file, 'w')

    with open(raw_file) as fp:
        passage = fp.readline()
        fw.write(passage)
        while len(passage) > 0:
            # 保存
            chemical = {}
            disease = {}
            entities = {}
            line = fp.readline()
            while not line.startswith("passage") and len(line) > 0:
                if line == 'title:\n' or line == 'abstract:\n' or line.startswith("CID"):
                    pass
                else:
                    if contain_entities(line):
                        all_entities = extract_all_entities(line)
                        for c, d in all_entities:
                            if c not in chemical.keys():
                                chemical[c] = 1
                            else:
                                chemical[c] += 1
                            if d not in disease.keys():
                                disease[d] = 1
                            else:
                                disease[d] += 1
                            if (c, d) not in entities.keys():
                                entities[(c, d)] = 1
                            else:
                                entities[(c, d)] += 1
                    elif contain_entity(line):
                        entity = extract_entity(line)
                        for en in entity:
                            if en.startswith("C_"):
                                if en not in chemical.keys():
                                    chemical[en] = 1
                                else:
                                    chemical[en] += 1
                            else:
                                if en not in disease.keys():
                                    disease[en] = 1
                                else:
                                    disease[en] += 1
                line = fp.readline()
            for c, i in chemical.items():
                fw.write("%s\t%d\n" % (c, i))
            for d, i in disease.items():
                fw.write("%s\t%d\n" % (d, i))
            for (c, d), i in entities.items():
                fw.write("%s\t%s\t%d\n" % (c, d, i))
            passage = line
            fw.write(passage)
    fw.close()


# 查找只包含一种实体的句子
def contain_entity(sentence):
    sentence = sentence.split()

    contain_chemical = False
    contain_disease = False

    for word in sentence:
        if "C_D" in word or "C_C" in word:
            contain_chemical = True
        if "D_D" in word or "D_C" in word:
            contain_disease = True

    if (contain_chemical and (not contain_disease)) or ((not contain_chemical) and contain_disease):
        return True
    else:
        return False


def extract_entity(sentence):
    entity = []

    sentence = sentence.split()
    for word in sentence:
        if "C_D" in word or "C_C" in word:
            pattern = re.compile(r'C_D[-]*\d+|C_C[-]*\d+')
            match = pattern.search(word)
            if match:
                entity.append(match.group())
        if "D_D" in word or "D_D" in word:
            pattern = re.compile(r'D_D[-]*\d+|D_C[-]*\d+')
            match = pattern.search(word)
            if match:
                entity.append(match.group())
    return entity


def extract_all_entities(sentence):
    # 存储化学物质实体，疾病实体，结果集合
    chemical_entities = []
    disease_entities = []
    result = []

    sentence = sentence.split()
    for word in sentence:
        if "C_D" in word or "C_C" in word:
            pattern = re.compile(r'C_D[-]*\d+|C_C[-]*\d+')
            match = pattern.search(word)
            if match:
                chemical_entities.append(match.group())
        if "D_D" in word or "D_C" in word:
            pattern = re.compile(r'D_D[-]*\d+|D_C[-]*\d+')
            match = pattern.search(word)
            if match:
                disease_entities.append(match.group())

    for c in chemical_entities:
        for d in disease_entities:
            result.append((c, d))

    return result


if __name__ == "__main__":
    raw_file_list = ["replace/train.txt", "replace/develop.txt", "replace/test.txt"]
    statistics_file_list = ["statistics/train.txt", "statistics/develop.txt", "statistics/test.txt"]

    for raw_file, statistics_file in zip(raw_file_list, statistics_file_list):
        count(raw_file, statistics_file)
