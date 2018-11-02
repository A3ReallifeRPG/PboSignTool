#!/usr/bin/python
import datetime
import multiprocessing
import os, re
import time
from shutil import copyfile
from functools import partial
from subprocess import call


def main():
    mod_path = "C:/Users/vabene1111/Desktop/@Mod"
    mod_addon_path = mod_path + "/addons/"
    mod_public_key_path = mod_path + "/keys/"

    key_name = "RL_RPG_" + datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    print("== RealLifeRPG Sign Tool ==")
    print("PBO Path: " + mod_addon_path)

    delete_bisign(mod_addon_path)
    clean_public_keys(mod_public_key_path)

    create_key(key_name)
    sign_files(mod_addon_path, key_name)

    safe_public_key(key_name, mod_public_key_path)

    delete_key(key_name)


def delete_bisign(path):
    print("Deleting old .bisign's")
    pattern = re.compile("^([a-zA-Z0-9\s_.\-:])+\.bisign$")
    files = os.listdir(path)
    for file in files:
        if pattern.match(file):
            os.remove(path + file)


def sign_files(path, key_name):
    files = os.listdir(path)
    print("Starting to sign " + str(len(files)) + " files")
    start = time.time()
    func = partial(sign_file, path, key_name)
    with multiprocessing.Pool() as pool:
        pool.map(func, files)
        pool.close()
        pool.join()

    end = time.time()
    print("Signing completed in " + str(round(end - start, 4)) + "s")


def sign_file(path, key_name, file):
    pattern = re.compile("^([a-zA-Z0-9\s_.\-:])+\.pbo")
    if pattern.match(file):
        call(["DSSignFile.exe", key_name + ".biprivatekey", path + file])


def create_key(key_name):
    print("Creating key with name: " + key_name)
    call(["DSCreateKey.exe", key_name])


def clean_public_keys(mod_public_key_path):
    if os.path.exists(mod_public_key_path):
        files = os.listdir(mod_public_key_path)
        for file in files:
            os.remove(mod_public_key_path + file)


def safe_public_key(key_name, mod_public_key_path):
    print("Storing public key")
    if not os.path.exists(mod_public_key_path):
        print("Creating public key directory")
        os.makedirs(mod_public_key_path)

    copyfile(key_name + ".bikey", mod_public_key_path + key_name + ".bikey")


def delete_key(key_name):
    print("Removing key with name: " + key_name)
    os.remove(key_name + ".bikey")
    os.remove(key_name + ".biprivatekey")


if __name__ == "__main__":
    main()
