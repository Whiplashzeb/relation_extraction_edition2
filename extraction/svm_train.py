from extraction.libsvm.python.svmutil import *


def extraction(file_label, file_entity):
    fp1 = open(file_label).readlines()
    fp2 = open(file_entity).readlines()

    res = set()
    for i in range(len(fp1)):
        r = fp1[i].split()[0][0]
        if r == '1':
            entity = fp2[i].split()
            res.add((entity[0], entity[1]))
    return res


def extraction_2(file_label, file_entity):
    fp1 = open(file_label).readlines()
    fp2 = open(file_entity).readlines()

    entities = dict()
    for i in range(len(fp1)):
        r = int(fp1[i].split()[0][0])
        if r == 0:
            r = -1
        entity = fp2[i].split()
        cd = (entity[0], entity[1])
        if cd not in entities.keys():
            entities[cd] = r
        else:
            entities[cd] += r

    res = set()
    for cd, i in entities.items():
        if i > -2:
            res.add(cd)

    return res

def standard(file_standard):
    result = set()
    with open(file_standard) as fp:
        line = fp.readline()
        while len(line) > 0:
            entity = line.split()
            result.add((entity[0], entity[1]))
            line = fp.readline()
    return result


if __name__ == "__main__":
    parameter = "-c 64.0 -g 0.0078125"
    y_train, x_train = svm_read_problem("scale/train_in.scale")
    y_develop, x_develop = svm_read_problem("scale/develop_in.scale")
    model = svm_train(y_train, x_train, parameter)
    svm_save_model("model/develop_in.model", model)

    model = svm_load_model("model/develop_in.model")
    p_label, p_acc, p_val = svm_predict(y_develop, x_develop, model)

    with open("result/develop_in.txt", 'w') as fp:
        for label, val in zip(p_label, p_val):
            fp.write(str(label) + '\t' + str(val[0]) + '\n')

    cid_r = extraction("result/develop_in.txt", "CID_extract/develop_in.txt")
    cid_s = standard("CID_standard_in/develop.txt")

    count = 0
    for cid in cid_r:
        if cid in cid_s:
            count += 1

    extract_total = len(cid_r)
    standard_total = len(cid_s)

    F = 2 * count / (extract_total + standard_total)

    print("%d\t%d\t%d\t%.4f%%\t%.4f%%\t%.4f%%\n" % (
        count, extract_total, standard_total, count / extract_total * 100, count / standard_total * 100, F * 100))
