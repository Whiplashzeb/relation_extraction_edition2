import os

if __name__ == "__main__":
    cmd1 = "/Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/svm-scale -s /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/rule.scale /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/feature/train.txt > /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/scale/train.scale"
    cmd2 = "/Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/svm-scale -r /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/rule.scale /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/feature/develop.txt > /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/scale/develop.scale"
    cmd3 = "/Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/svm-scale -r /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/rule.scale /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/feature/test.txt > /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/scale/test.scale"
    os.system(cmd1)
    os.system(cmd2)
    os.system(cmd3)
