import argparse
import multiprocessing
import time
import requests
import json
import os
import urllib

"""
Arma 3 Download Script
by RealLifeRPG Team - www.realliferpg.de

More Info: https://github.com/A3ReallifeRPG/PboSignTool
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to mod root directory")
    parser.add_argument("api", help="api base url to download from")
    parser.add_argument("mod_id", help="mod_id")

    args = parser.parse_args()

    mod_path = str(args.path).replace("\\", "/")
    api = str(args.api)
    mod_id = int(args.mod_id)

    headers = {
        'User-Agent': 'Build Server',
        'X-Requested-With': 'XMLHttpRequest'
    }

    mod_info = json.loads(requests.get(api + "/v1/mods", headers=headers).content)["data"][mod_id]

    print("dwnloading/hashing mod: '" + str(mod_info["Name"]) + "' to path: '" + mod_path + "'")

    if os.path.isdir(os.path.join(mod_path, mod_info["Directories"])):
        hash_mod(mod_path, api, mod_info, mod_id)
    else:
        download_mod(mod_path, api, mod_info, mod_id)


def download_mod(mod_path, api, mod_info, mod_id):
    hashlist = get_hash_list(api, mod_info)

    download_mod_multithreaded(mod_path, mod_info, hashlist)


def hash_mod(mod_path, api, mod_info, mod_id):
    return ""

def download_mod_multithreaded(mod_path, mod_info, list):
    headers = {
        'User-Agent': 'Build Server',
        'X-Requested-With': 'XMLHttpRequest'
    }

    for file in list:
        urllib.request.urlretrieve(str(mod_path["DownloadUrl"]) + "/" + str(file["RelativPath"]), os.path.join(mod_path, file["RelativPath"]))
        print(str(mod_path["DownloadUrl"]) + "/" + str(file["RelativPath"]))

def get_hash_list(api, mod_info):
    headers = {
        'User-Agent': 'Build Server',
        'X-Requested-With': 'XMLHttpRequest'
    }

    return json.loads(requests.get(api + "/v1/mod/hashlist/" + str(mod_info["Id"]), headers=headers).content)


if __name__ == "__main__":
    main()
