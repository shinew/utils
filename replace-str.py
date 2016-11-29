import argparse
import os
import os.path
import re
import shutil

DOC = '''Replaces all instances of old string with new string in the given directory.
Replaces in directory/file names as well as their contents.

Example:
python replace-str.py . --old=bar --new=foo
'''

def memo1(f):
    cache = []
    def _f(*args, **kwargs):
        if cache:
            return cache[0]
        cache.append(f(*args, **kwargs))
        return cache[0]
    return _f

@memo1
def get_regex(old):
    return re.compile(old)

def replace(old, new, data):
    return get_regex(old).sub(new, data)

def replace_file_contents(file_name, old, new):
    contents = ''
    new_contents = ''
    with open(file_name, 'r') as f:
        contents = f.read()
        new_contents = replace(old, new, contents)
    if contents == new_contents:
        return
    with open(file_name, 'w') as f:
        f.write(new_contents)

def rename(path, old, new):
    new_path = replace(old, new, path)
    if new_path != path:
        if os.path.exists(new_path):
            raise Exception('{} already exists'.format(new_path))
        shutil.move(path, new_path)
    return new_path

def get_appended_children(path):
    return map(lambda c: os.path.join(path, c), os.listdir(path))

def replace_in_dir_shallow(path, old, new):
    if not os.path.isdir(path):
        raise Exception('{} is not a directory'.format(path))

    children = get_appended_children(path)

    map(lambda c: replace_file_contents(c, old, new),
        filter(lambda c: os.path.isfile(c), children))

    renamed_children = map(lambda c: rename(c, old, new), children)

    return filter(lambda c: os.path.isdir(c), renamed_children)

def replace_in_dir(path, old, new):
    if not os.path.isdir(path):
        raise Exception('starting is not a directory'.format(path))

    abspath = os.path.abspath(path)
    head, tail = os.path.split(abspath)
    os.chdir(head)
    path = rename(tail, old, new)

    stack = [path]
    while stack:
        path = stack.pop()
        new_dirs = replace_in_dir_shallow(path, old, new)
        stack.extend(new_dirs)

if '__main__' == __name__:
    parser = argparse.ArgumentParser(description=DOC)
    parser.add_argument('starting', type=str, help='root directory of the replacement')
    parser.add_argument('--old', type=str, help='the string to be replaced')
    parser.add_argument('--new', type=str, help='the replacement string')
    args = parser.parse_args()
    replace_in_dir(args.starting, args.old, args.new)
