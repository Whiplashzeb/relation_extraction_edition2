def extract_standard(raw_file, standard_file):
    fw = open(standard_file, 'w')

    with open(raw_file) as fp:
        line = fp.readline()
        while len(line) > 0:
            if line.startswith("CID"):
                line = line.split()
                fw.write(line[1] + ' ' + line[2] + '\n')
            line = fp.readline()


def get_entities_in_sentence(statistics_file):
    res = []
    with open(statistics_file) as fp:
        line = fp.readline()
        while len(line) > 0:
            line = line.split()
            if len(line) == 3:
                res.append([line[0], line[1]])
            line = fp.readline()
    return res


# 待完成
def extract_in_standard(raw_file, standard_file, statistic_file):
    fw = open(standard_file, 'w')
    in_sentence = get_entities_in_sentence(statistic_file)
    with open(raw_file) as fp:
        line = fp.readline()
        while len(line) > 0:
            if line.startswith("CID"):
                line = line.split()
                if [line[1], line[2]] in in_sentence:
                    fw.write(line[1] + ' ' + line[2] + '\n')
            line = fp.readline()


if __name__ == "__main__":
    raw_file_list = ["replace/train.txt", "replace/develop.txt", "replace/test.txt"]
    standard_file_list = ["CID_standard/train.txt", "CID_standard/develop.txt", "CID_standard/test.txt"]
    statistics_file_list = ["statistics/train.txt", "statistics/develop.txt", "statistics/test.txt"]
    standard_in_sentence_file_list = ["CID_standard_in/train.txt", "CID_standard_in/develop.txt",
                                      "CID_standard_in/test.txt"]
    for raw_file, standard_file in zip(raw_file_list, standard_file_list):
        extract_standard(raw_file, standard_file)

    for raw_file, standard_file, statistics_file in zip(raw_file_list, standard_in_sentence_file_list,
                                                        statistics_file_list):
        extract_in_standard(raw_file, standard_file, statistics_file)
