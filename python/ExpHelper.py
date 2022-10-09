import os
import sys
import threading
import subprocess

class ExpHelper:
    ##################
    ### PARSE TYPE ###
    ##################
    # PARSE_NO_PARSE: Does not need to parse, the search key maybe None
    PARSE_NO_PARSE         = 0

    # PARSE_WHITESPACE: Key-value is separated by one or more whitespaces
    #                       e.g., KEY VAL
    #                             KEY          VAL
    PARSE_WHITESPACE = 1
    
    # PARSE_COLON: Key-value is separated by a single colon, 
    #              and possibly with one or more whitespace
    #                  e.g., KEY:VAL
    #                        KEY: VAL
    PARSE_COLON      = 2
    
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
        #   - If relative path is given, it is converted into the abspath with
        #     this basedir
        self.basedir = os.path.abspath(basedir)   
        
    # set_basedir: Set new basedir, converting it into absolute path
    #
    #   @basedir: Basedir to set 
    def set_basedir(self, basedir):
        self.basedir = os.path.abspath(basedir)

    # get_basedir: Get current basedir as a string
    #
    #   @return: current basedir
    def get_basedir(self):
        return str(self.basedir)

    # set_value_to_file: set value to a file
    #
    #   @fname:  filename to set
    #   @val:    value to set, @val is converted into str type
    #   @prefix: prefix before the command (e.g., sudo)
    #
    #   @return: 0 if success, non-zero otherwise
    def set_value_to_file(self, fname, val, prefix=""):
        path = self.__process_path(fname)
        if not path:
            self.__log_error("set_value_to_file: Invalid filename")
            return -1

        cmd = "echo {} | {} dd status=none of={}".format(val, prefix, path)

        self.__log_debug("set_value_to_file: command: {}".format(cmd))
    
        ret = os.system(cmd)
        return ret


    # read_value_from_file: Get a single line from the given file using @key
    #                       and then parse the line to get value.
    #                       This only uses first line of cat/grep output.
    #                       If multiple separators exist, uses the last one.
    #
    # @fname:      file to use
    # @key:        grep search key
    # @parse_type: style to parse the given input
    #   
    # @return: returns read value (string form), None if reading was failed
    def read_value_from_file(self, fname, key, parse_type):
        ret = None

        path = self.__process_path(fname)
        if not path:
            self.__log_error("read_value_from_file: Invalid filename")
            return None

        if parse_type == ExpHelper.PARSE_NO_PARSE:
            cmd_to_read =  "cat \"{}\"".format(path)
        else:
            cmd_to_read = "grep \"{}\" {}".format(key, path)

        # Only uses first line of output
        result = os.popen(cmd_to_read).read().strip().split("\n")[0]
        
        if result == "":
            self.__log_error("read_value_from_file: No value was found")
            return None
        
        if parse_type == ExpHelper.PARSE_NO_PARSE:
            ret = result
        
        elif parse_type == ExpHelper.PARSE_WHITESPACE:
            ret = list(filter(None, result.split(" ")))[-1]

        elif parse_type == ExpHelper.PARSE_COLON:
            ret = list(filter(None, result.split(":")))[-1]
            ret = ret.strip()
        
        else:
            self.__log_error("read_value_from_file: Invalid parse type")
            return None

        self.__log_debug("read_value_from_file: read value: \"{}\"".format(ret))
        return ret


    # __process_path: When a path is given, perform a simple sanity check
    #                 and convert it into absolute path
    #
    #   @path: Path to process
    #   
    #   @return: Absolute path converted from the given path
    #            None in the case of any failure
    def __process_path(self, path):
        # TODO: check existance
        ret = ""
        try:
            if path[0] == "/":
                ret = path 
            else:
                ret = os.path.abspath(os.path.join(self.basedir, path))

            self.__log_debug("__process_path: actual path: \"{}\"".format(ret))
            return ret

        except:
            self.__log_error("__process_path({}): failed, returning None".format(path))
            return None


    # __log_error: Print error message. It wraps __log() function
    #
    #   @msg: Error message to print
    def __log_error(self, msg):
        self.__log(ExpHelper.LEVEL_ERROR, msg)
    
    # __log_debug: Print debug message. It wraps __log() function
    #
    #   @msg: Debug message to print
    def __log_debug(self, msg):
        self.__log(ExpHelper.LEVEL_DEBUG, msg)

    # __log: Print log message
    #
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

