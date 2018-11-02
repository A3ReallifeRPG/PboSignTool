![Banner](https://raw.githubusercontent.com/A3ReallifeRPG/RealLifeRPGLauncher/master/resources/img/banner.png)

# PBO SignTool
Simple PBO sign tool using python multiprocessing. 

##Features
- Uses all available CPU power to make signing fast
- Can creates new unique keypair each time you sign
- can move public/private key to configured dir (for easier deployment)
- verify signatures after signing
- heavily customizable with command line arguments (see usage)

## Usage
Since colors are nice (and show errors better) and manually doing colors in python is annoying you have to
install `colorama` either in a virtual env or globally.

```
pip install colorama
```

Simply drop the `DSSignFiles.exe`,`DSCreateKey.exe` and `DSCheckSignatures.exe` in a directory of your choice 
together with the `sign.py` script.

The simplest option is to run `ptyhon sign.py /path/to/your/@Mod`. 
For more advanced usage and documentation run `python sign.py --help`.

```
usage: sign.py [-h] [-k PUBLIC_KEY_PATH] [-p PRIVATE_KEY_PATH] [-a AUTHORITY]
               [-t] [-c] [-o] [-u] [-d] [-e]
               path

positional arguments:
  path                  path to mod root directory (not addons)

optional arguments:
  -h, --help            show this help message and exit
  -k PUBLIC_KEY_PATH, --public-key-path PUBLIC_KEY_PATH
                        path to directory for storing generated public key
                        (default <base path>/keys)
  -p PRIVATE_KEY_PATH, --private-key-path PRIVATE_KEY_PATH
                        path to directory for storing generated private key
  -a AUTHORITY, --authority AUTHORITY
                        basically the name of the key
  -t, --timestamp       adds a timestamp to the authority name
  -c, --clean           if old bisign and key files should be deleted
  -o, --old             do not create new key because old one exists (if there
                        is no old one things will break)
  -u, --unsafe          do not check if created signatures are valid
  -d, --delete          delete bikey and private key when finished
  -e, --export          export public key to defined directory
```
