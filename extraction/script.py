import os

if __name__ == "__main__":
    cmd1 = "/Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/svm-scale -s /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/rule.scale /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/feature/train_in.txt > /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/scale/train_in.scale"
    cmd2 = "/Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/svm-scale -r /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/rule.scale /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/feature/develop_in.txt > /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/scale/develop_in.scale"
    cmd3 = "/Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/svm-scale -r /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/rule.scale /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/feature/test_in.txt > /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/scale/test_in.scale"
    os.system(cmd1)
    os.system(cmd2)
    os.system(cmd3)

    cmd4 = "/Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/svm-scale -s /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/rule_out.scale /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/feature/train_out.txt > /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/scale/train_out.scale"
    cmd5 = "/Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/svm-scale -r /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/rule_out.scale /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/feature/develop_out.txt > /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/scale/develop_out.scale"
    cmd6 = "/Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/svm-scale -r /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/rule_out.scale /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/feature/test_out.txt > /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/scale/test_out.scale"
    os.system(cmd4)
    os.system(cmd5)
    os.system(cmd6)