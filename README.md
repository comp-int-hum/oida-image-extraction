# Extracting images from Powerpoint and Excel files

The single script in this repository can be used to extract images from Powerpoint and Excel files in both the older "CFB" Microsoft format, and the newer XML-based format (typically distinguished by an additional "x", e.g. "file.ppt" versus "file.pptx").  For the approximately 900 example files from the OIDA corpus, the script runs in under two minutes on a typical laptop, and extracts approximately 4000 images.

## Running the script

On any computer with a recent version of Python (e.g. >3.6) and Git, first clone this repository and change directory into it:

```
git clone https://github.com/comp-int-hum/oida-image-extraction.git
cd oida-image-extraction
```

Then create and load a virtual environment, and install the requirements:

```
python3 -m venv local
source local/bin/activate
pip install -r requirements.txt
```

You can then invoke the script, which has a single named argument for the output directory, and any number of unnamed arguments corresponding to files to process:

```
python scripts/process_files.py --output some_output_directory/ file1.xlsx file2.pptx file3.ppt ...
```

In most cases you would likely run something like this, to process an entire directory:

```
python scripts/process_files.py --output some_output_directory some_input_directory/*
```

Alternatively, and perhaps more conveniently, the script can act on and write to archives:

```
python scripts/process_files.py --archive_mode --output some_output.zip some_input.zip some_other_input.zip ...
```

Finally, given a zip file of images such as produced by the above method, a filtered archive can be created with:

```
python scripts/filter_files.py --input some_output.zip --output filtered_output.zip
```

By default, the filter will exclude PDF files or files with "thumb" in the name, and images with width or height less than 200 pixels or entropy less than 6.0.  These defaults can be specified differently on the command line, see the script's help message for details (i.e. using the "-h" switch).

## Input, Processing, and Output

The script currently handles the old and new formats of Microsoft Powerpoint and Excel, which it distinguishes based on file extension.  The old formats are searched for known bit-patterns corresponding to file formats (using the Hachoir library), while the new formats are unpacked as zip archives and filtered for image extensions.  In all cases, each image found in a given input file `FILE_NAME` is extracted to `some_output_directory/FILE_NAME/IMAGE_NAME`, and so remains unambiguously associated with its source.

An input file is only processed if `some_output_directory/FILE_NAME` doesn't already exist, so to force re-evaluation one may delete one or more of the output sub-directories.

## Known Issues and Extending the Code

It might be worthwhile to be more sophisticated about determining input file format, e.g. using magic bytes, particularly if the data sources become less constrained or curated.  This could include the image-extraction stage for the newer formats, where each zip archive member could be tested, rather than also relying on file extensions.

The Hachoir approach used on the older formats is very general (searching for known patterns at the bit level), and so could prove useful for adding arbitrary additional input format handlers (i.e. branches to the main if-statement).  Care should be taken to ensure that Hachoir is being given uncompressed and/or unencrypted files, otherwise the bit-patterns won't be meaningful.

There are a handful of false positives, particularly ".wmf" files.
