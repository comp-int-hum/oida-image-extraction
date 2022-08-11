import os.path
import argparse
import logging
import zipfile
from PIL.ImageStat import Stat
from PIL.Image import open as im_open

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", dest="output", help="Zip archive of unfiltered files")
    parser.add_argument("--input", dest="input", help="Zip archive under which to store filtered files")
    parser.add_argument("--minimum_entropy", dest="minimum_entropy", default=6.0, type=float)
    parser.add_argument("--minimum_width", dest="minimum_width", default=200, type=int)
    parser.add_argument("--minimum_height", dest="minimum_height", default=200, type=int)
    parser.add_argument("--include_pdfs", dest="include_pdfs", default=False, action="store_true")
    parser.add_argument("--include_thumbnails", dest="include_thumbnails", default=False, action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    ofd_zip = zipfile.ZipFile(args.output, "w")
    with zipfile.ZipFile(args.input, "r") as ifd:
        for i, item in enumerate(ifd.infolist()):
            if ("thumb" not in item.filename or args.include_thumbnails) and not item.is_dir():
                fname = item.filename.replace("/", "_")
                if item.filename.endswith("pdf"):
                    if args.include_pdfs:
                        with ofd_zip.open(fname, "w") as ofd:
                            ofd.write(ifd.read(item))
                else:
                    try:
                        im = im_open(ifd.open(item))
                        entropy = im.entropy()
                        if entropy >= args.minimum_entropy and (im.width >= args.minimum_width and im.height >= args.minimum_height):
                            with ofd_zip.open(fname, "w") as ofd:
                                ofd.write(ifd.read(item))
                    except:
                        logging.info("Couldn't read image file '%s'", item.filename)


            
