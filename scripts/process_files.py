import subprocess
import os.path
import argparse
import shlex
from glob import glob
import logging
import zipfile


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(dest="inputs", nargs="+", help="Any number and mixture of Powerpoint and Excel files to process")
    parser.add_argument("--output", dest="output", help="Path under which to save extracted images")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    
    for fname in args.inputs:
        base = os.path.basename(fname)
        ext = os.path.splitext(base.lower())[-1]
        dest = os.path.join(args.output, base)
        if os.path.exists(dest):
            logging.info("Not processing file '%s' because the directory '%s' already exists!", fname, dest)
        else:
            os.makedirs(dest)
            if ext in [".xls", ".ppt"]:
                pid = subprocess.Popen(
                    shlex.split("python -m hachoir.subfile --category image {} {}".format(fname, dest)),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                pid.communicate()
            elif ext in [".pptx", ".xlsx"]:
                with zipfile.ZipFile(fname, "r") as zfd:
                    for member in zfd.namelist():
                        mext = os.path.splitext(member)[1].lower()
                        if mext in [".gif", ".jpeg", ".jpg", ".png", ".wmf"]:
                            subdest = os.path.join(dest, os.path.dirname(member))                            
                            if not os.path.exists(subdest):
                                os.makedirs(subdest)                                
                            with open(os.path.join(dest, member), "wb") as ofd:
                                ofd.write(zfd.read(member))
            else:
                raise Exception("Unknown file extension: {}".format(ext))
