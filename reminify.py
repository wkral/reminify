import os
import sys
from subprocess import Popen, PIPE
from monitor import monitor

def file_change_callback(filename, op):
    print "recompiling {0}".format(filename)
    with open(min_filename(filename), 'w') as f:
        f.write(_compile(filename))

def min_filename(filename):
    return filename.replace('.js', '.r0.min.js')

def _compile(js_file):
    """Compile the given file with a local closure compiler.
    """

    compiler = os.getenv('CLOSURE_COMPILER')
    command = ['java', '-jar', compiler, '--compilation_level',
               'SIMPLE_OPTIMIZATIONS', '--js', js_file]
    p = Popen(command, stdout=PIPE, stderr=PIPE)
    stderr = p.stderr.read()
    if stderr:
        sys.stderr.write(stderr)

    return p.stdout.read().rstrip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: python reminify.py <filename> [<filenames>]"
        sys.exit(1)

    monitor(sys.argv[1:], file_change_callback)
