import os
import sys
import threading

class ExpHelper:
    #NOTE: use relative path

    def __init__(self, basedir=".", verbose=True):
        self.verbose = verbose
        self.basedir = basedir

    def set_basedir(self, basedir):
        self.basedir = basedir

    # printout: Print message only self.verbose is set
    #           Only used by (internal) methods
    # @msg: message to print
    #       single line string is recommended
    def printout(self, msg):
        if not self.verbose:
            return
        else:
            print("[ExpHelper] " + str(msg))


    # read_value_from_file: Get a single line from the given file using @key
    #                       and then parse the line to get value
    #                       This only uses first line of grep output
    #
    # @fname:       file to use
    # @key:         grep search key
    # @parse_style: style to parse the given input
    #   SINGLE_VALUE:         The file only contains single value
    #                         e.g., 123
    #   WHITESPACE_SEPARATED: key and value are separated by one or more whitespaces
    #                         e.g., SOME_KEY 123
    #                         e.g., SOME_KEY          123
    #   COLON_SEPARATED:      key and value are sepataed by one colon, and possibly whitespace
    #                         e.g., SOME_KEY:123
    #                         e.g., SOME_KEY: 123
    #                         e.g., SOME_KEY:         123
    #   
    # @return: returns read value (string form), None if reading was failed
    def read_value_from_file(self, fname, key, parse_style="WHITESPACE_SEPARATED"):
        result = os.popen("grep \"{}\" {}".format(key, os.path.join(self.basedir, fname))).read().strip().split("\n")[0]
        
        if result == "":
            self.printout("No search result was found.")
            return None
        
        if parse_style == "SINGLE_VALUE":
            return result
        
        elif parse_style == "WHITESPACE_SEPARATED":
            return list(filter(None, result.split(" ")))[1]

        elif parse_style == "COLON_SEPARATED":
            return list(filter(None, result.split(":")))[1]
        
        else:
            self.printout("Invalid parse style")
            return None
    
    # TODO
    def read_line_from_file(self, fname, key):
        return os.popen("grep \"{}\" {}".format(key, os.path.join(self.basedir, fname))).read().strip().split("\n")[0]
    

    # get_delta_from_files: Get values from the given two files using @key
    #                       and then get the difference between two values
    #
    # @fname_start:             file to use, start
    # @fname_end:               file to use, end
    # @key:                     grep search key
    # @parse_style:             style to parse the given input
    #                           (refer read_value_from_file)
    # @dtype:                   data type for these values
    # @fname_start_basedir:     @fname_start's basedir
    # @fname_end_basedir:       @fname_end's basedir
    #
    # @return: returns delta value, None if reading was failed
    def get_delta_from_files(self, fname_start, fname_end, key, parse_style="WHITESPACE_SEPARATED", dtype="INT", fname_start_basedir=None, fname_end_basedir=None):
        if fname_start_basedir != None:
            fname_start_ = os.path.join(str(fname_start_basedir), str(fname_start))
        else:
            fname_start_ = str(fname_start)
        
        if fname_end_basedir != None:
            fname_end_ = os.path.join(str(fname_end_basedir), str(fname_end))
        else:
            fname_end_ = str(fname_end)


        val_start = self.read_value_from_file(fname_start_, key, parse_style)
        val_end = self.read_value_from_file(fname_end_, key, parse_style)

        if val_start == None or val_end == None:
            self.printout("No search result was found")
            return None

        if dtype == "INT":
            return int(val_end) - int(val_start)
        elif dtype == "FLOAT":
            return float(val_end) - float(val_end)
        else:
            self.printout("Invalid dtype")
            return None
    
    # read_value_from_cmd: get value from a command line output
    #
    # @cmd:         command to use
    # @parse_style: style to parse the given input
    #   SINGLE_VALUE:         The file only contains single value
    #                         e.g., 123
    #   
    # @return: returns read value (string form), None if reading was failed
    def read_value_from_cmd(self, cmd, parse_style="SINGLE_VALUE"):
        result = os.popen(str(cmd)).read().strip().split("\n")[0]
        
        if result == "":
            self.printout("No search result was found.")
            return None
        
        if parse_style == "SINGLE_VALUE":
            return result

        else:
            self.printout("Invalid parse style")
            return None


    # check_value_from_file: get the value from the file and check if the value is equal to @ref
    #
    # @fname:  filename to get value
    # @ref:    value to compare
    # @sudo:   get value using sudo
    #
    # @return: returns 0 if equal, otherwise 1 (including read failure)
    def check_value_from_file(self, fname, ref, sudo=False):
        sudocmd = "sudo" if sudo else ""
        
        val = os.popen("{} cat {}".format(sudocmd, fname)).read().strip()
        return 0 if val == ref else 1


    # set_value_to_file: set the given value to the file
    #
    # @cmd:    value to set
    # @fname:  filename to set
    # @append: append or overwrite
    # @sudo:   write value using sudo
    #
    # @return: always returns 0 (it does not check if the operation was successful)
    def set_value_to_file(self, val, fname, append=False, sudo=False):
        append_option = "-a" if append else ""
        sudocmd = "sudo" if sudo else ""

        os.system("echo \"{}\" | {} tee {} {} >> /dev/null".format(val, sudocmd, append_option, fname))
