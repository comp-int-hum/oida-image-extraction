import re
import os
from SCons.Subst import scons_subst
import steamroller
from glob import glob

vars = Variables("custom.py")
vars.AddVariables(
    (
        "OUTPUT_WIDTH",
        "Truncate the display length of commands after this number of characters",
        400
    ),
    (
        "DATA_PATH",
        "The location where OIDA zip/tar files can be found",
        "data"
    ),
    (
        "FILES_PER_BATCH",
        "",
        500
    ),
    (
        "GPU_BUILDERS",
        "",
        []
    )
)

env = Environment(
    ENV=os.environ,
    variables=vars,
    tools=[steamroller.generate],
    BUILDERS={
        "ProcessFiles" : Builder(
            action="python scripts/process_files.py ${SOURCES[0]} --output ${TARGETS[0]} --archive_mode --start ${START} --count ${COUNT}",
        ),
    }
)

env.Decider("timestamp-newer")

def print_cmd_line(s, target, source, env):
    if len(s) > int(env["OUTPUT_WIDTH"]):
        print(s[:int(float(env["OUTPUT_WIDTH"]) / 2) - 2] + "..." + s[-int(float(env["OUTPUT_WIDTH"]) / 2) + 1:])
    else:
        print(s)
env['PRINT_CMD_LINE_FUNC'] = print_cmd_line

for cfname in glob(os.path.join(env["DATA_PATH"], "*.txt")):
    fname = re.match(r"^(.*)\.txt$", cfname).group(1)
    _, ext = os.path.splitext(fname)
    eexts = {}
    with open(cfname, "rt") as ifd:
        num_files = len([x for x in ifd if x.strip().endswith("zip")])
        num_batches = num_files / env["FILES_PER_BATCH"]
        num_batches = int(num_batches) if num_batches == int(num_batches) else int(num_batches) + 1
        prefix = os.path.splitext(os.path.basename(fname))[0]
        for batch in range(num_batches):
            env.ProcessFiles(
                "work/${PREFIX}_${BATCH}.zip",
                fname,
                BATCH=batch,
                PREFIX=prefix,
                START=batch * env["FILES_PER_BATCH"],
                COUNT=min(num_files, (batch + 1) * env["FILES_PER_BATCH"]) - (batch * env["FILES_PER_BATCH"])
            )
