#!/usr/bin/python
import argparse
import datetime
import fnmatch
import multiprocessing
import os
import sys
import time
from functools import partial
from shutil import copyfile
from subprocess import call

import colorama as cr


def main():
    cr.init()
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to mod root directory (not addons)")
    parser.add_argument("-k", "--public-key-path", help="path to directory for storing generated public key (default <base path>/keys)")
    parser.add_argument("-p", "--private-key-path", help="path to directory for storing generated private key")
    parser.add_argument("-a", "--authority", help="basically the name of the key")
    parser.add_argument("-t", "--timestamp", help="adds a timestamp to the authority name", action="store_true")
    parser.add_argument("-c", "--clean", help="if old bisign and key files should be deleted", action="store_true")
    parser.add_argument("-o", "--old", help="do not create new key because old one exists (if there is no old one things will break)", action="store_true")
    parser.add_argument("-u", "--unsafe", help="do not check if created signatures are valid", action="store_true")
    parser.add_argument("-d", "--delete", help="delete bikey and private key when finished", action="store_true")
    parser.add_argument("-e", "--export", help="export public key to defined directory", action="store_true")
    parser.add_argument("-v", "--verbose", help="verbose console output when signing", action="store_true")
    args = parser.parse_args()

    mod_path = str(args.path).replace("\\", "/")

    if not mod_path.endswith("/"):
        mod_path += "/"

    mod_addon_path = mod_path + "addons/"

    mod_public_key_path = mod_path + "/keys/"
    if args.public_key_path:
        mod_public_key_path = str(args.keypath).replace("\\", "/")
        if not mod_public_key_path.endswith("/"):
            mod_public_key_path += "/"

    key_authority = "RL_RPG"
    if args.authority:
        key_authority = args.authority

    key_name = key_authority
    if args.timestamp:
        key_name = key_authority + "_" + datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    print(cr.Fore.GREEN + "== RealLifeRPG Sign Tool ==")
    print("PBO Path: " + mod_addon_path + cr.Style.RESET_ALL)

    if args.clean:
        delete_bisign(mod_addon_path)
        clean_public_keys(mod_public_key_path)

    if not args.old:
        create_key(key_name)

    sign_files(mod_addon_path, key_name, args.verbose)

    if not args.unsafe:
        check_signatures(mod_addon_path)

    if args.export:
        safe_public_key(key_name, mod_public_key_path)

    if args.private_key_path:
        mod_private_key_path = str(args.private_key_path).replace("\\", "/");
        if not mod_private_key_path.endswith("/"):
            mod_private_key_path += "/"
        safe_private_key(key_name, mod_private_key_path)

    if args.delete:
        delete_key(key_name)


def sign_files(path, key_name, verbose):
    files = fnmatch.filter(os.listdir(path), '*.pbo')
    print(cr.Fore.GREEN + "Starting to sign " + str(len(files)) + " files" + cr.Fore.YELLOW)
    start = time.time()
    func = partial(sign_file, path, key_name, verbose)
    with multiprocessing.Pool() as pool:
        pool.map(func, files)
        pool.close()
        pool.join()

    end = time.time()
    print(cr.Style.RESET_ALL + "Signing completed in " + str(round(end - start, 4)) + "s")


def sign_file(path, key_name, verbose, file):
    if file.endswith(".pbo"):
        if verbose:
            print(cr.Style.RESET_ALL + "signing " + file + cr.Fore.YELLOW)

        result = call(["DSSignFile.exe", key_name + ".biprivatekey", path + file])
        if not result == 0:
            print("Error signing file " + file + " retrying")
            sign_file(path, key_name, verbose, file)


def check_signatures(mod_addon_path):
    print("Verifying signatures")
    print(cr.Fore.RED)
    call(["DSCheckSignatures.exe", mod_addon_path, "."])
    print(cr.Style.RESET_ALL)


def delete_bisign(path):
    print("Deleting old .bisign's")
    files = os.listdir(path)
    for file in files:
        if file.endswith(".bisign"):
            os.remove(path + file)


def create_key(key_name):
    print("Creating key with name: " + key_name)
    call(["DSCreateKey.exe", key_name])


def clean_public_keys(path):
    if os.path.exists(path):
        files = os.listdir(path)
        for file in files:
            os.remove(path + file)


def safe_public_key(key_name, path):
    print("Exporting public key")
    if not os.path.exists(path):
        print("Creating public key directory")
        os.makedirs(path)

    copyfile(key_name + ".bikey", path + key_name + ".bikey")


def safe_private_key(key_name, path):
    print("Exporting private key")
    if not os.path.exists(path):
        print("Creating private key directory")
        os.makedirs(path)

    copyfile(key_name + ".biprivatekey", path + key_name + ".biprivatekey")


def delete_key(key_name):
    print("Removing key with name: " + key_name)
    os.remove(key_name + ".bikey")
    os.remove(key_name + ".biprivatekey")


def color(code):
    if code == "info":
        sys.stdout.write('\033[92m')
    elif code == "error":
        sys.stdout.write('\033[91m')
    elif code == "warning":
        sys.stdout.write('\033[93m')
    elif code == "default":
        sys.stdout.write('\033[0m')


if __name__ == "__main__":
    main()
