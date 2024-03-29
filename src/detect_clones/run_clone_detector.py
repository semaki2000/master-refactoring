import sys
import os
import subprocess
import datetime

import shutil

from pathlib import Path

#remove files which aren't test_*py or *_test.py 
# run nicad on remaining files to see if code clones in tests of repo
# TODO: also check potential pytest.ini file(or hidden .pytest.ini) 
#   for filepaths that could include tests other than tests/)

class RunCloneDetector:
    fileglob = {}

    consistent_cross_file = False
    log_clone_detector_run = False
    def run(path, tmp_dir_path, config):
        orig_path = path

        orig_dir_name = str(path.name)

        path = RunCloneDetector.create_tmp_filestructure(path, tmp_dir_path)
        
        if 'fileglob' in config.keys():
            RunCloneDetector.fileglob = config['fileglob']

        cwd = os.getcwd()
        #run nicad clone detector on tmp filestructure to find clones in test files
        #UNSAFE: os.system("nicad6 functions py " + str(path) + "/ type2_abstracted")
        #TODO: use config in this repo, instead of at nicad install location
        if RunCloneDetector.consistent_cross_file:
            command = ["nicad6", "functions", "py", str(path) + "/", "type2_consistent_abstracted"]
            cp_from_path = Path(str(path) + "_functions-consistent-abstract-clones/tmp_subfolder_functions-consistent-abstract-clones-0.00-classes.xml")

        else:
            command = ["nicad6", "functions", "py", str(path) + "/", "type2_abstracted"]
            cp_from_path = Path(str(path) + "_functions-blind-abstract-clones/tmp_subfolder_functions-blind-abstract-clones-0.00-classes.xml")


        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


        error = "*** ERROR" in result.stdout.decode()
        if RunCloneDetector.log_clone_detector_run or error:
            filename = "nicad" + str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log")
            with open(filename, "a+") as f:
                f.write(result.stdout.decode())
                f.write(result.stderr.decode())
            print(f"Clone detection logged in {filename}")

        if error:
            print("Error running clone detector. Check log file.")
            sys.exit()


        target_xml_path = ""
        clones_xml_file = "clone_classes.xml"
        if not cp_from_path.exists():
            raise FileNotFoundError("Path does not exist: " + str(cp_from_path))
        command = ["cp", str(cp_from_path), str(clones_xml_file)]
        subprocess.run(command, check=True)

        return (clones_xml_file, orig_path, path)



    def create_tmp_filestructure(path, tmp_dir_path):
        """Copies the directory structure at the given path into the current working directory,
        Also copies over all files which adhere to pytests test discovery rules
        TODO: include specific rules for this repo, set up in pytest.ini, or similar file (.toml, etc.)"""
        
        #problems with these two options: first creates regular directory. Second creates directory in tmp/, but has to be deleted by user
        #tmp_dir_path = Path(os.getcwd() + "/"+ str(path.name) + "_temp_filestructure").mkdtemp
        #tmp_dir_path = tempfile.mkdtemp()
        
        #therefore we use tmp_dir_path supplied from caller on run function. Should be created in context manager ("with ... as ...:")
        tmp_dir_path = tmp_dir_path / Path("tmp_subfolder")
        try:
            shutil.copytree(str(path), str(tmp_dir_path), ignore=RunCloneDetector.ignore_non_test_py_files)
        except FileExistsError:
            print("This error should not occur... remove tmp directory?")
            sys.exit()
        except shutil.Error: #permissions thing
            pass
        return tmp_dir_path


    #copytree will only copy test files and directories
    def ignore_non_test_py_files(direc, files):
        pdir = Path(direc)
        ignore_files = []
        for file in files:
            
            filepath = Path(direc + "/" + file)
            if filepath.match("*/test_*.py") or filepath.match("*_test.py") or filepath.is_dir():
                pass
            elif any(filepath.match("*/" + glob) for glob in RunCloneDetector.fileglob):
                pass
            else:             
                ignore_files.append(file)
        return ignore_files
