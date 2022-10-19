import os, sys


def test_misc():
    pass

def test_ExpHelper():
    from ExpHelper import ExpHelper
    INITIAL_BASEDIR = "."

    exp = ExpHelper(INITIAL_BASEDIR, verbosity=ExpHelper.LEVEL_DEBUG)

    # TEST: set/get_basedir
    assert(exp.get_basedir() == str(os.path.abspath(INITIAL_BASEDIR)))    

    exp.set_basedir("..")
    assert(exp.get_basedir() == str(os.path.abspath("..")))
    
    # roll-back
    exp.set_basedir(INITIAL_BASEDIR)

    # TEST: set_value_to_file
    os.system("echo 1 > tmp.txt")
    ret = exp.set_value_to_file("tmp.txt", 2)
    val = os.popen("cat tmp.txt").read().strip()
    assert(ret == 0)
    assert("2" == str(val))

    # TEST: get_value_to_file
    os.system("echo 1000 > tmp.txt")
    os.system("echo 1001 >> tmp.txt")
    ret = exp.read_value_from_file("tmp.txt", None, ExpHelper.PARSE_NO_PARSE)
    assert(ret == str(1000))

    os.system("echo \"key 100\" > tmp.txt")
    os.system("echo \"key 101\" >> tmp.txt")
    os.system("echo \"key_a 102\" >> tmp.txt")
    ret = exp.read_value_from_file("tmp.txt", "key", ExpHelper.PARSE_WHITESPACE)
    assert(ret == str(100))

    os.system("echo \"key     255\" > tmp.txt")
    ret = exp.read_value_from_file("tmp.txt", "key", ExpHelper.PARSE_WHITESPACE)
    assert(ret == str(255))

    os.system("echo \"key something 16384\" > tmp.txt")
    ret = exp.read_value_from_file("tmp.txt", "key", ExpHelper.PARSE_WHITESPACE)
    assert(ret == str(16384))

    os.system("echo \"key:1\" > tmp.txt")
    ret = exp.read_value_from_file("tmp.txt", "key", ExpHelper.PARSE_COLON)
    assert(ret == str(1))

    os.system("echo \"key::2\" > tmp.txt")
    ret = exp.read_value_from_file("tmp.txt", "key", ExpHelper.PARSE_COLON)
    assert(ret == str(2))

    os.system("echo \"key:0:3\" > tmp.txt")
    ret = exp.read_value_from_file("tmp.txt", "key", ExpHelper.PARSE_COLON)
    assert(ret == str(3))

    os.system("echo \"key:   4\" > tmp.txt")
    ret = exp.read_value_from_file("tmp.txt", "key", ExpHelper.PARSE_COLON)
    assert(ret == str(4))

    
    os.system("echo 100 > tmp1.txt")
    os.system("echo 200 > tmp2.txt")

    ret = exp.get_delta_from_files("tmp1.txt", "tmp2.txt", None, ExpHelper.PARSE_NO_PARSE, "INT")
    assert(str(ret) == str(100)) 

    print("All tests passed. Cleaning up...")

    # cleanup
    os.system("rm tmp.txt tmp1.txt tmp2.txt")




if __name__ == "__main__":
    test_misc()
    test_ExpHelper()
