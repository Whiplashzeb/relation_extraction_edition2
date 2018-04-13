# relation_extraction_edition2

## 船新版本

- deal_raw_data.py 
处理原始语料，包含实体识别及替换，text tokenization和sentence tokenization
- inner_sentence.py
主要句内特征抽取文件
目前包含特征为：CID,化学物质位置,疾病位置,距离,顺序,化学物质出现次数,疾病出现次数,关系出现次数,包含化学物质数量,包含疾病数量,包含化学物质种类,包含疾病种类,是否在标题中
- statistics.py 
统计每篇文章内化学物质和疾病的种类及出现次数，以及每种实体对的共现次数。
- keywords.py
利用卡方校验分析每个词和正例及负例的相关性，并按照从大到小排序及过滤。
