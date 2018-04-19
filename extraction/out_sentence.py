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


# 专注于2个句子本身的特征，不考虑中间跨越的整句
def read_sentence(raw_file, statistics_file, feature_file, CID_file, key_num):
    fw = open(feature_file, 'w')
    fCID = open(CID_file, 'w')

    with open(raw_file) as fp:
        # 标记文章
        passage = fp.readline()

        while len(passage) > 0:
            title = ""
            all_chemical, all_disease, all_cid, all_chemical_num, all_disease_num, all_cid_num = get_number(passage,
                                                                                                            statistics_file)
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
                        if abs(i - j) <= 3 and contain_entities(sentences[i], sentences[j]):
                            all_entities = extract_all_entities(sentences[i], sentences[j])
                            for key, value in all_entities.items():
                                # 计算句子的长度
                                l1 = len(sentences[i].split())
                                l2 = len(sentences[j].split())
                                l_two = l1 + l2
                                # 实体对的信息
                                chemical = key[0][0]
                                chemical_pos = key[0][1]  # 化学物质位置
                                disease = key[1][0]
                                disease_pos = key[1][1]  # 疾病位置
                                is_cid = value[0]  # 是否为CID关系
                                order = value[1]  # 顺序
                                if order == 0:
                                    distance = float(l1 - chemical_pos + disease_pos) / l_two
                                    others = contain_others(
                                        sentences[i][chemical_pos + 1:] + sentences[j][:disease_pos])
                                else:
                                    distance = float(l1 - disease_pos + chemical_pos) / l_two
                                    others = contain_others(
                                        sentences[i][disease_pos + 1:] + sentences[j][:chemical_pos])
                                chemical_number = all_chemical[chemical]  # 化学物质出现次数
                                disease_number = all_disease[disease]  # 疾病出现次数
                                if (chemical, disease) in all_cid.keys():
                                    cid_number = all_cid[(chemical, disease)]  # 共现次数
                                else:
                                    cid_number = 0
                                chemical_freq = float(chemical_number) / all_chemical_num  # 化学物质出现频率
                                disease_freq = float(disease_number) / all_disease_num  # 疾病出现频率
                                if all_cid_num == 0:
                                    cid_freq = 0
                                else:
                                    cid_freq = float(cid_number) / all_cid_num  # 共现频率
                                other_chemical_number = others[0]  # 包含其他化学物质数量
                                other_disease_number = others[1]  # 包含其他疾病数量
                                other_chemical_kind = others[2]  # 包含其他化学物质种类
                                other_disease_kind = others[3]  # 包含其他疾病种类
                                chemical_in, disease_in, entities_in = in_title(chemical, disease, title)  # 是否出现在标题中
                                kwords = contain_keywords(sentences[i] + sentences[j], key_num)
                                fw.write(
                                    "%d 1:%d 2:%d 3:%f 4:%d 5:%d 6:%d 7:%d 8:%f 9:%f 10:%f 11:%d 12:%d 13:%d 14:%d 15:%d 16:%d 17:%d 18:%d 19:%d" % (
                                        is_cid, chemical_pos, disease_pos, distance, order, chemical_number,
                                        disease_number,
                                        cid_number, chemical_freq, disease_freq, cid_freq, other_chemical_number,
                                        other_disease_number, other_chemical_kind, other_disease_kind, 1,
                                        chemical_in, disease_in, entities_in, abs(i - j)))
                                for position, value in enumerate(kwords):
                                    fw.write(" %d:%d" % (position + 20, value))
                                fw.write('\n')
                                fCID.write("%s\t%s\n" % (chemical, disease))
            passage = line
    fw.close()
    fCID.close()


# 判断两个句子是否包含实体对
def contain_entities(sentence1, sentence2):
    sentence1 = sentence1.split()
    sentence2 = sentence2.split()

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

    if (chemical1 is True and disease2 is True) or (chemical2 is True and disease1 is True):
        return True
    else:
        return False


# 从两个句子中抽取全部的跨句实体对
# 返回格式：((pos,chemical),(pos,disease)):(CID,order)
def extract_all_entities(sentence1, sentence2):
    result = {}
    chemical1, disease1 = get_all_entities(sentence1)
    chemical2, disease2 = get_all_entities(sentence2)

    for c in chemical1:
        for d in disease2:
            if c[0] in CID and d[0] in CID[c[0]]:
                result[(c, d)] = (1, 0)
            else:
                result[(c, d)] = (0, 0)
    for c in chemical2:
        for d in disease1:
            if c[0] in CID and d[0] in CID[c[0]]:
                result[(c, d)] = (1, 1)
            else:
                result[(c, d)] = (0, 1)
    return result


# 获取一个句子中的全部实体
def get_all_entities(sentence):
    chemical = []
    disease = []

    sentence = sentence.split()
    for i, word in enumerate(sentence):
        if "C_D" in word or "C_C" in word:
            pattern = re.compile(r'C_D[-]*\d+|C_C[-]*\d+')
            match = pattern.search(word)
            if match:
                chemical.append((match.group(), i))
        if "D_D" in word or "D_C" in word:
            pattern = re.compile(r'D_D[-]*\d+|D_C[-]*\d+')
            match = pattern.search(word)
            if match:
                disease.append((match.group(), i))

    return chemical, disease


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
        if "D_D" in word or "D_C" in word:
            pattern = re.compile(r'D_D[-]*\d+|D_C[-]*\d+')
            match = pattern.search(word)
            if match:
                disease.add(word)
                disease_number += 1
    res = (chemical_number, disease_number, len(chemical), len(disease))
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
