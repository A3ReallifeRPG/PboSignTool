import datetime
import hashlib, os, fnmatch
import argparse
import multiprocessing
import time
from functools import partial

"""
Arma 3 Hashlist Script
by RealLifeRPG Team - www.realliferpg.de

More Info: https://github.com/A3ReallifeRPG/PboSignTool
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to mod root directory")
    parser.add_argument("out", help="path to where hash list should be put")

    args = parser.parse_args()

    hash_path = str(args.path).replace("\\", "/")
    out_path = str(args.out).replace("\\", "/")
    if not hash_path.endswith("/"):
        hash_path += ""

    if not out_path.endswith("/"):
        out_path += "/"

    hash_files(hash_path, out_path)


def hash_files(hash_path, out_path):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(hash_path):
        for file in filenames:
            if not dirpath.endswith("/"):
                dirpath += "/"

            files.append(dirpath + file)

    print("Starting to sign " + str(len(files)) + " files")
    start = time.time()

    func = partial(hash_file)
    with multiprocessing.Pool() as pool:
        results = pool.map(func, files)
        pool.close()
        pool.join()

    end = time.time()
    print("Signing completed in " + str(round(end - start, 4)) + "s")

    i = 0
    while i < len(results):
        results[i] = results[i].replace("__ID__", str(i))
        i += 1

    out_name = hash_path[hash_path.find('@'):] + " - " + datetime.datetime.now().strftime('%d.%m.%Y %H-%M-%S') + ".json"

    f = open(out_path + out_name, 'w')
    f.write(str(results).replace("\'", ""))
    f.close()


def hash_file(file):
    file_hash = hashlib.md5(open(file, 'rb').read()).hexdigest()

    name = os.path.basename(file)
    size = os.path.getsize(file)
    relative_path = file[file.find('@'):]
    relative_path = relative_path.replace("/", "\\")

    return '{"Id":__ID__,"RelativPath":"' + relative_path + '","Hash":"' + file_hash + '","FileName":"' + name + '","Size":' + str(size) + '}'


if __name__ == "__main__":
    main()
