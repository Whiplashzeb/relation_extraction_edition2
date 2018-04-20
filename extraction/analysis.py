# 分析每对实体被标注的情况
def entities_label(entity_file, result_file):
    entity = open(entity_file).readlines()
    result = open(result_file).readlines()

    res = dict()
    for i in range(len(entity)):
        entities = entity[i].split()
        label = int(result[i].split()[0][0])
        if (entities[0], entities[1]) in res:
            res[(entities[0], entities[1])].append(label)
        else:
            res[(entities[0], entities[1])] = [label]

    return res


# 获取标准CID
def standard(standard_file):
    result = set()
    with open(standard_file) as fp:
        line = fp.readline()
        while len(line) > 0:
            entity = line.split()
            result.add((entity[0], entity[1]))
            line = fp.readline()
    return result

# 查询跨句的占比
def get_rate():
    pass


if __name__ == "__main__":
    entity_file = "CID_extract/develop.txt"
    result_file = "result/develop.txt"
    standard_file = "CID_standard_in/develop.txt"
    

    res = entities_label(entity_file, result_file)
    CID = standard(standard_file)
    
    

    with open("analysis/entities_label.txt", 'w') as fp:
        for entities, lables in res.items():
            if entities in CID:
                fp.write('1\t')
                fp.write(entities[0] + ' ' + entities[1] + ': ')
                for label in lables:
                    fp.write("%d " % (label))
                fp.write('\n')
