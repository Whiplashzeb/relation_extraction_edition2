import os

if __name__ == "__main__":
    cmd4 = "/Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/svm-scale -s /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/rule_out.scale /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/feature/train_out.txt > /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/scale/train_out.scale"
    cmd5 = "/Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/svm-scale -r /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/rule_out.scale /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/feature/develop_out.txt > /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/scale/develop_out.scale"
    cmd6 = "/Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/svm-scale -r /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/libsvm/rule_out.scale /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/feature/test_out.txt > /Users/aurora/Desktop/work/relation_extraction_edition2/extraction/scale/test_out.scale"
    os.system(cmd4)
    os.system(cmd5)
    os.system(cmd6)