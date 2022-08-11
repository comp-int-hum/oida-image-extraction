import subprocess
import os.path
import os
import argparse
import shlex
from glob import glob
import logging
import zipfile
import tarfile
import tempfile
import shutil


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(dest="inputs", nargs="+", help="Any number and mixture of Powerpoint and Excel files to process")
    parser.add_argument("--output", dest="output", help="Path under which to save extracted images")
    parser.add_argument("--archive_mode", dest="archive_mode", default=False, action="store_true", help="Inputs are archives (zip or tar)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARN)


    ofd_zip = zipfile.ZipFile(args.output, "a")
    all_names = set()
    for name in ofd_zip.namelist():
        all_names.add(name)


    def process_file(fname, fhandle, prefix="", temp_path=None):
        ext = os.path.splitext(fname.lower())[-1]
        name = os.path.join(prefix, fname.strip("/"))
        logging.info("Processing file '%s'", fname)
        if name in all_names:
            logging.info("Skipping item already in the output")
        elif ext in [".zip", ".pptx", ".xlsx"]:
            logging.debug("Recursively processing contents")
            with zipfile.ZipFile(fhandle, "r") as nested_ifd:
                for nested_fname in nested_ifd.namelist():
                    process_file(nested_fname, nested_ifd.open(nested_fname, "r"), prefix=name, temp_path=temp_path)
        
        elif ext in [".xls", ".ppt"]:
            logging.debug("Treating as old Microsoft format")
            all_names.add(fname)
            input_fname = os.path.join(temp_path, os.path.basename(fname))
            with open(input_fname, "wb") as ofd:
                ofd.write(fhandle.read())
            pid = subprocess.Popen(
                shlex.split("python -m hachoir.subfile --category image") + [input_fname, temp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            pid.communicate()
            for output_fname in glob(os.path.join(temp_path, "*")):
                if output_fname != input_fname:
                    with open(output_fname, "rb") as nested_ifd:
                        process_file(os.path.basename(output_fname), nested_ifd, prefix=name, temp_path=temp_path)
                os.remove(output_fname)
        elif ext in [".gif", ".jpeg", ".jpg", ".png", ".wmf", ".pdf"]:
            logging.info("Adding to archive at '%s'", name)
            with ofd_zip.open(name, "w") as image_ofd:
                image_ofd.write(fhandle.read())
            all_names.add(name)
            if len(all_names) % 1000 == 0:
                logging.warning("%d image files in archive", len(all_names))
        elif "." not in fname or ext in [".ocr"]:
            logging.info("Skipping directory or file with known-non-image extension")
        else:
            logging.info("Skipping file with unknown extension ('%s')", fname)

            
    if args.archive_mode:
        temp_path = tempfile.mkdtemp()

        try:
            for fname in args.inputs:
                logging.info("Processing archive '%s'", fname)
                if tarfile.is_tarfile(fname):
                    with tarfile.open(fname, "r") as ifd:
                        for member in ifd:
                            process_file(member.name, ifd.extractfile(member), temp_path=temp_path)
                elif zipfile.is_zipfile(fname):
                    with zipfile.ZipFile(fname, "r") as ifd:
                        for item in ifd.getitems():
                            process_file(item.filename, ifd.open(item), temp_path=temp_path)
        except Exception as e:
            raise e
        finally:
            shutil.rmtree(temp_path)
    else:
        
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
