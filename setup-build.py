#!/usr/bin/python3
import configparser
from os import walk

class Setup_preparer:
    translate_dict = {}

    def __init__(self, translate_dict_filepath):
        config = configparser.ConfigParser()
        config.read(translate_dict_filepath)
        for key in config["build_config"]:
            self.translate_dict[key] = config["build_config"][key] 

    def setup_file(self, file_path):
        read_file = ''
        with open(file_path) as file:
            read_file = file.read()
        for key in self.translate_dict:
            read_file = read_file.replace(key, self.translate_dict[key])
        with open(file_path, 'w') as file:
            file.write(read_file)


setup_preparer = Setup_preparer("./setup_vars.ini")
folders = ['api', 'client', 'config', 'mobile', 'overlay']
for folder in folders:
    for (dirpath, dirnames, filenames) in walk("./{}".format(folder)):
        if "node_modules" not in dirpath and "dist" not in dirpath:
            for filename in filenames:
                if '.js' in filename or '.vue' in filename:
                    setup_preparer.setup_file(dirpath + "/{}".format(filename))
