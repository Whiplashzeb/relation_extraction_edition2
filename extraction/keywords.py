from inner_sentence import contain_entities
import re
import string

# 保存全部的CID关系
CID = {}

unigram = set()
bigram = set()

sentences = []


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


def read_sentence(file):
    with open(file) as fp:
        passage = fp.readline()
        while len(passage) > 0:
            line = fp.readline()
            while "passage" not in line and len(line) > 0:
                if line == 'title:\n' or line == 'abstract:\n' or line.startswith("CID"):
                    pass
                else:
                    if line.startswith("title"):
                        line = line[8:]
                    if line.startswith("abstract"):
                        line = line[11:]
                    if contain_entities(line):
                        get_word(line)
                        all_entities = extract_all_entities(line)
                        for key, value in all_entities.items():
                            sentences.append((value, line))
                line = fp.readline()
            passage = line


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


def get_word(sentence):
    sentence = sentence.split()

    for word in sentence:
        unigram.add(word)
    for i in range(len(sentence) - 1):
        word = sentence[i] + ' ' + sentence[i + 1]
        bigram.add(word)


def chi(gram):
    res = []
    for word in gram:
        A, B, C, D = 0, 0, 0, 0
        for value, sentence in sentences:
            if word in sentence and value == 1:
                A += 1
            elif word in sentence and value == 0:
                B += 1
            elif word not in sentence and value == 1:
                C += 1
            elif word not in sentence and value == 0:
                D += 1
        if (A + B) == 0 or (C + D) == 0:
            result = 0
        else:
            result = (A * D - B * C) * (A * D - B * C) / ((A + B) * (C + D))
        res.append((word, result))
    return res


def extract_keywords():
    chi_one = chi(unigram)
    chi_two = chi(bigram)

    return chi_one, chi_two


def contain_number_or_punctuation(words):
    words = words.split()
    for word in words:
        if word.isdigit() or word in string.punctuation:
            return True
    return False


if __name__ == "__main__":
    extract_file_list = ["replace/train.txt"]

    raw_file_list = ["replace/train.txt", "replace/develop.txt", "replace/test.txt"]
    for raw_file in raw_file_list:
        read_CID(raw_file)

    for file in extract_file_list:
        read_sentence(file)

    chi_one, chi_two = extract_keywords()
    chi_one = sorted(chi_one, key=lambda x: -x[1])
    chi_two = sorted(chi_two, key=lambda x: -x[1])

    with open("keywords/unigram.txt", 'w') as fp:
        for word, value in chi_one:
            if word.find("C_") != -1 or word.find("D_") != -1:
                continue
            if word.isdigit() or word in string.punctuation:
                continue
            fp.write(word + ' ' + str(value) + '\n')

    with open("keywords/bigram.txt", 'w') as fp:
        for word, value in chi_two:
            if word.find("C_") != -1 or word.find("D_") != -1:
                continue
            if contain_number_or_punctuation(word):
                continue
            fp.write(word + ' ' + str(value) + '\n')
