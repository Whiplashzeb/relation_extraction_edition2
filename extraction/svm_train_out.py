from libsvm.python.svmutil import *
from svm_train import extraction, standard

if __name__ == "__main__":
    parameter = "-c 1024.0 -g 0.03125"
    y_train, x_train = svm_read_problem("scale/train_out.scale")
    y_develop, x_develop = svm_read_problem("scale/develop_out.scale")
    model = svm_train(y_train, x_train, parameter)
    svm_save_model("model/develop_out.model", model)

    model = svm_load_model("model/develop_out.model")
    p_label, p_acc, p_val = svm_predict(y_develop, x_develop, model)

    with open("result/develop_out.txt", 'w') as fp:
        for label, val in zip(p_label, p_val):
            fp.write(str(label) + '\t' + str(val[0]) + '\n')

    cid_r = extraction("result/develop_out.txt", "CID_extract/develop_out.txt")
    cid_s = standard("CID_standard/develop.txt")

    count = 0
    for cid in cid_r:
        if cid in cid_s:
            count += 1

    extract_total = len(cid_r)
    standard_total = len(cid_s)

    F = 2 * count / (extract_total + standard_total)

    print("%d\t%d\t%d\t%.4f%%\t%.4f%%\t%.4f%%\n" % (
        count, extract_total, standard_total, count / extract_total * 100, count / standard_total * 100, F * 100))
