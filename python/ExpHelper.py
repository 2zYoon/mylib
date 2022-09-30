import os
import sys
import threading
import subprocess

from enum import Enum

class ParseType(Enum):
    # SINGLE_VALUE: Only contains a single value, so does not need to parse
    #               The key maybe given as None
    SINGLE_VALUE         = 0

    # WHITESPACE_SEPARATED: Key-value is separated by one or more whitespaces
    #                       e.g., KEY VAL
    #                             KEY          VAL
    WHITESPACE_SEPARATED = 1
    
    # COLON_SEPARATED: Key-value is separated by a single colon, 
    #                  and possibly with whitespace
    #                  e.g., KEY:VAL
    #                        KEY: VAL
    COLON_SEPARATED      = 2

class ExpHelper:
    ##################
    ### PARSE TYPE ###
    ##################
    # SINGLE_VALUE: Only contains a single value, so does not need to parse
    #               The key maybe given as None
    SINGLE_VALUE         = 0

    # WHITESPACE_SEPARATED: Key-value is separated by one or more whitespaces
    #                       e.g., KEY VAL
    #                             KEY          VAL
    WHITESPACE_SEPARATED = 1
    
    # COLON_SEPARATED: Key-value is separated by a single colon, 
    #                  and possibly with whitespace
    #                  e.g., KEY:VAL
    #                        KEY: VAL
    COLON_SEPARATED      = 2
    
    ###########################
    ### LOG/VERBOSITY LEVEL ###
    ###########################
    LEVEL_SILENT    = 0 # Do not print anything
    LEVEL_ERROR     = 1 # Print in the case of failure or error
    LEVEL_DEBUG     = 2 # Very verbose (for debug)

    def __init__(self, basedir, verbosity=1):
        # Verbosity level
        self.verbosity = verbosity

        # Basedir
        #   - Basedir for reading/writing files
        #   - If relative path is given, it is converted into absolute path
        self.basedir = os.path.abspath(basedir)   
        
    # set_basedir: Set new basedir, converting it into absolute path
    #   @basedir: Basedir to set 
    def set_basedir(self, basedir):
        self.basedir = os.path.abspath(basedir)

    # set_value_to_file: set value to a file
    #   @fname: filename to set
    #   @val:   value to set, @val is converted into str type
    #   @sudo:  write value with sudo
    #
    #   @return: 0 if success, non-zero otherwise
    def set_value_to_file(self, fname, val, sudo=True):
        path = self.__process_path(fname)
        if not path:
            self.__log(ExpHelper.LEVEL_ERROR, "set_value_to_file: Invalid filename")
            return -1

        cmd = "echo {} | {} dd status=none of={}".format(
                val,
                "sudo" if sudo else "",
                path)

        self.__log(ExpHelper.LEVEL_DEBUG, "set_value_to_file: command: {}".format(cmd))
        
        # TODO: replace with subprocess
        # TODO: get result code
        os.system(cmd)

    
    # __process_path: When a path is given, perform a simple sanity check
    #                 and convert it into absolute path
    #   @path: Path to process
    #   
    #   @return: Absolute path converted from the given path
    #            None in the case of any failure
    def __process_path(self, path):
        try:
            if path[0] == "/":
                return path
            else:
                return os.path.abspath(path)

        except:
            self.__log(ExpHeler.LEVEL_ERROR, "__process_path: failed, returning None")
            return None

    # __log: Print log message
    #   @level: Log level. Log is printed only when verbosity >= level
    #   @msg:   Log message to print
    def __log(self, level, msg):
        if self.verbosity < level:
            return

        if level == ExpHelper.LEVEL_ERROR:
            print("[ERROR]", msg)
            return 

        elif level == ExpHelper.LEVEL_DEBUG:
            print("[DEBUG]", msg)
            return

        else:
            return

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
