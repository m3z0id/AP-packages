import os
import hashlib
import json
import urllib.request
import sys

def checkIfInstalled(package: str) -> bool:
    if(not os.path.isfile("packages/packages_local.json")):
        return True
    if(os.path.getsize("packages/packages_local.json") == 0):
        return True
    pkglist = json.loads(open("packages/packages_local.json", "r").read())
    for pkg in pkglist['packages']:
        if(pkg['name'] == package or pkg['name'] == f"{package}.py"):
            return False
    return True

def install(package: str) -> bool:
    if(not checkIfInstalled(package)):
        print(f"ERROR: Package {package} is already installed!")
        return False
    try:
        urllib.request.urlretrieve("https://raw.githubusercontent.com/m3z0id/AP-packages/main/packages-remote.json", "packages/packages_remote.json")
    except Exception:
        print("ERROR: You don't have internet access!")
        return False

    packages = json.loads(open("packages/packages_remote.json", "r").read())

    for currentPackageId in packages['packages']:
        if(currentPackageId['name'] == f"{package}.py" or currentPackageId['name'] == package or f"{currentPackageId['name']}.py" == package):
            packageId = currentPackageId
            break
    else:
        print(f"ERROR: Package {package} was not found.")
        os.remove("packages/packages_remote.json")
        return False
    
    if(not os.path.isdir("packages")):
        os.mkdir("packages")
    print(f"INFO: Installing {package}...")
    urllib.request.urlretrieve(packageId["dl-link"], f"packages/{packageId['name']}")
    if(str(packageId["hash-sha256"]).strip() != hashlib.sha256(str(open(f"packages/{packageId['name']}", "rb").read()).encode()).hexdigest()):
        print(packageId["hash-sha256"])
        print(hashlib.sha256(str(open(f"packages/{packageId['name']}", "rb").read()).encode()).hexdigest())
        print("ERROR: Hashes do not match.")
        os.remove(f"packages/{packageId['name']}")
        os.remove("packages/packages_remote.json")
        return False
    os.remove("packages/packages_remote.json")
    if(not os.path.isfile("packages/packages_local.json")):
        open("packages/packages_local.json", "w").write("{\"packages\":[]}")
    localjson = json.loads(open("packages/packages_local.json", "r").read())

    for localjsonentry in localjson['packages']:
        if(localjsonentry['name'] == packageId['name']):
            localjsonentry = packageId
            break
    else:
        localjson['packages'].append(packageId)
        open("packages/packages_local.json", "w").write(json.dumps(localjson))
    print(f"Package {package} was installed successfully!")
    if(currentPackageId['name'] == "base.py" or currentPackageId['name'] == "shell.py" or currentPackageId['name'] == "spm.py"):
        os.replace(f"packages/{currentPackageId['name']}", currentPackageId['name'])
    return True

def update(package: str) -> bool:
    localPackages = json.loads(open("packages/packages_local.json", "r").read())

    localPackageIndex: int = 0
    for currentPackageId in localPackages['packages']:
        if(currentPackageId['name'] == package):
            localPackageId = currentPackageId
            break
        localPackageIndex += 1
    else:
        print(f"ERROR: Package {package} is not installed.")
        return False
    try:
        urllib.request.urlretrieve("https://raw.githubusercontent.com/m3z0id/AP-packages/main/packages-remote.json", "packages/packages_remote.json")
    except Exception:
        print("ERROR: You don't have internet access!")
    remotePackages = json.loads(open("packages/packages_remote.json", "r").read())
    for currentRemotePackageId in remotePackages['packages']:
        if(currentRemotePackageId['name'] == package):
            remotePackageId = currentRemotePackageId
            break
    else:
        os.remove("packages/packages_remote.json")
        print(f"ERROR: Package {package} was not found.")
        return False
    if(remotePackageId['version'] == localPackageId['version']):
        print(f"ERROR: Package {package} is already at its latest version!")
        return False
    print(f"Updating {localPackageId['name']}...")
    os.remove(f"{localPackageId['name']}")
    urllib.request.urlretrieve(remotePackageId["dl-link"], f"{remotePackageId['name']}")
    if(str(remotePackageId["hash-sha256"]).strip() != hashlib.sha256(str(open(f"{remotePackageId['name']}", "rb").read()).encode()).hexdigest()):
        print("ERROR: Hashes do not match.")
        os.remove(f"{remotePackageId['name']}")
        os.remove("packages/packages_remote.json")
        return False
    
    localPackageId = remotePackageId
    localPackages['packages'].pop(localPackageIndex)
    localPackages['packages'].append(localPackageId)

    open("packages/packages_local.json", "w").write(json.dumps(localPackages))
    print(f"INFO: Package {remotePackageId['name']} updated successfully!")
    if(currentPackageId['name'] == "base.py" or currentPackageId['name'] == "shell.py" or currentPackageId['name'] == "spm.py"):
        os.replace(f"packages/{currentPackageId['name']}", currentPackageId['name'])
    return True

def listpkg(package: str = None) -> bool:
    localPackages = json.loads(open("packages/packages_local.json", "r").read())
    if(package == None):
        print("INSTALLED PACKAGES:\n")
        for currentPackageId in localPackages['packages']:
            print(f"Name: {currentPackageId['name']}")
            print(f"Description: {currentPackageId['desc']}")
            print(f"Version: {currentPackageId['version']}")
            print("\n")
        return True
    
    for currentPackageId in localPackages['packages']:
        if(currentPackageId['name'] == package or currentPackageId['name'] == f"{package}.py"):
            print(f"Name: {currentPackageId['name']}")
            print(f"Description: {currentPackageId['desc']}")
            print(f"Version: {currentPackageId['version']}")
            print("\n")
            return True
    else:
        print(f"ERROR: Package {package} wasn't found.")
        return False

def remove(package: str) -> bool:
    localPackages = json.loads(open("packages/packages_local.json", "r").read())

    localPackageIndex: int = -1
    for currentPackageId in localPackages['packages']:
        localPackageIndex += 1
        if(currentPackageId['name'] == package or currentPackageId['name'] == f"{package}.py"):
            localPackageId = currentPackageId
            break
    else:
        print(f"ERROR: Package {package} is not installed.")
        return False
    
    localPackages['packages'].pop(localPackageIndex)
    if(currentPackageId['name'] == "base.py" or currentPackageId['name'] == "shell.py" or currentPackageId['name'] == "spm.py"):
        os.remove(currentPackageId['name'])
    else:
        os.remove(f"packages/{localPackageId['name']}")

    open("packages/packages_local.json", "w").write(json.dumps(localPackages))
    print(f"INFO: Package {package} removed successfully!")
    return True

args: list = sys.argv
if(len(args) > 2):
    if(args[1] == "install"):
        install(args[2])
    elif(args[1] == "update"):
        update(args[2])
    elif(args[1] == "listpkg"):
        listpkg(args[2])
    elif(args[1] == "remove"):
        remove(args[2])
    else:
        print("ERROR: Invalid arguments.")
else:
    try:
        if(args[1] == "listpkg"):
            listpkg()
    except IndexError:
        print("ERROR: Not enough arguments were passed!")