import argparse
import multiprocessing
import time
import requests
import json
import os
import urllib
import hashlib

from functools import partial

"""
Arma 3 Mod Download Script
by RealLifeRPG Team - www.realliferpg.de

More Info: https://github.com/A3ReallifeRPG/PboSignTool
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to mod root directory")
    parser.add_argument("api", help="api base url to download from")
    parser.add_argument("mod_id", help="mod_id")
    parser.add_argument("--secret", help="whitelist secret", type=str, default=1)

    args = parser.parse_args()

    mod_path = str(args.path).replace("\\", "/")
    api = str(args.api)
    mod_id = int(args.mod_id)
    if(args.secret is not None):
        secret = str(args.secret)

    headers = {
        'User-Agent': 'Build Server',
        'X-Requested-With': 'XMLHttpRequest'
    }

    if(args.secret is None):
        mod_info = json.loads(requests.get(api + "/v1/mods", headers=headers).content.decode('utf-8'))["data"]
    else:
        mod_info = json.loads(requests.get(api + "/v1/mods/" + secret, headers=headers).content.decode('utf-8'))["data"]

    for mod in mod_info:
        if(mod["Id"] == mod_id):
            mod_info = mod


    print("dwnloading/hashing mod: '" + str(mod_info["Name"]) + "' to path: '" + mod_path + "'")

    if os.path.isdir(os.path.join(mod_path, mod_info["Directories"])):
        hashlist = get_hash_list(api, mod_info)["data"]
        hash_mod(mod_path, mod_info, hashlist)
    else:
        hashlist = get_hash_list(api, mod_info)["data"]
        download_mod(mod_path, mod_info, hashlist)


def hash_mod(mod_path, mod_info, hashlist):
    print("Starting to hash/check " + str(len(hashlist)) + " files")
    start = time.time()

    func = partial(hash_file, mod_path)
    with multiprocessing.Pool(6) as pool:
        results = pool.map(func, hashlist)
        pool.close()
        pool.join()

    end = time.time()
    results = list(filter(None.__ne__, results))
    print("Hashing completed in " + str(round(end - start, 4)) + "s")
    print(str(len(results)) + " files missing or wrong")

    download_mod(mod_path, mod_info, results)


def hash_file(mod_path, hashfile):
    file = os.path.join(str(mod_path), str(hashfile["RelativPath"]).replace("\\", "/"))
    if not (os.path.isfile(file)):
        return hashfile
    else:
        file_hash = hashlib.md5(open(file, 'rb').read()).hexdigest()
        if (file_hash.lower() != hashfile["Hash"]):
            return hashfile


def download_mod(mod_path, mod_info, hashlist):
    print("Starting to download " + str(len(hashlist)) + " files")

    start = time.time()
    func = partial(download_file, mod_path, mod_info)
    with multiprocessing.Pool(10) as pool:
        pool.map(func, hashlist)
        pool.close()
        pool.join()

    end = time.time()

    print("Downloaded " + str(len(hashlist)) + " files in " + str(round(end - start, 4)) + "s")


def download_file(mod_path, mod_info, file):
    path = os.path.join(str(mod_path), str(file["RelativPath"]).replace("\\", "/"))
    url = str(mod_info["DownloadUrl"]).replace("\\", "/") + "/" + str(file["RelativPath"]).replace("\\", "/")
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    urllib.request.urlretrieve(url, path)
    print(url)


def get_hash_list(api, mod_info):
    headers = {
        'User-Agent': 'Build Server',
        'X-Requested-With': 'XMLHttpRequest'
    }

    return json.loads(
        requests.get(api + "/v1/mod/hashlist/" + str(mod_info["Id"]), headers=headers).content.decode('utf-8'))


if __name__ == "__main__":
    main()
