import os
import hashlib
import json
import urllib.error
import urllib.request
import sys
import shutil
import subprocess

def downloadPackage(packageEntry: dict) -> bool:
    try:
        urllib.request.urlretrieve(packageEntry['dl-link'], f"packages/{packageEntry['name']}")
    except urllib.error.URLError:
        print("ERROR: You don't have internet access!")
        return False
    
    subprocess.run(["chmod", "+x", f"{os.getcwd()}/packages/{packageEntry['name']}"])

    if(loadConfig()["check-hashes"] == False):
        return True
    
    if(str(packageEntry["hash-sha256"]).strip() != hashlib.sha256(open(f"packages/{packageEntry['name']}", "rb").read()).hexdigest()):
        print("ERROR: Hashes do not match.")
        os.remove(f"packages/{packageEntry['name']}")
        return False
    
    return True

def updateLocalPackageList(packageEntry: dict):
    if(not os.path.isfile("packages/packages_local.json")):
        open("packages/packages_local.json", "w").write("{\"packages\":[]}")
    localjson = json.loads(open("packages/packages_local.json", "r").read())

    packageIndex = 0
    for localjsonentry in localjson['packages']:
        if(localjsonentry['name'] == packageEntry['name']):
            if(not checkIfInstalled(packageEntry["name"])):
                localjson['packages'].pop(packageIndex)
                break
            
            localjsonentry = packageEntry
            break
        packageIndex += 1

    localjson['packages'].append(packageEntry)
    open("packages/packages_local.json", "w").write(json.dumps(localjson))

def checkPackageLists(package: str) -> list:
    matched = []
    for packagelistfile in os.listdir("packages/packagelists"):
        packagelist = json.loads(open(f"packages/packagelists/{packagelistfile}", "r").read())
        for pkg in packagelist["packages"]:
            if(pkg['name'] == f"{package}.py" or pkg['name'] == package or f"{pkg['name']}.py" == package):
                matched.append(pkg)
            
    return matched

def checkLocalPackageLists(package: str) -> list:
    matched = []
    packagelist = json.loads(open("packages/packages_local.json", "r").read())
    for pkg in packagelist["packages"]:
        if(pkg['name'] == f"{package}.py" or pkg['name'] == package or f"{pkg['name']}.py" == package):
            matched.append(pkg)

    return matched

def downloadPackageLists() -> bool:
    config = loadConfig()

    if(not os.path.isdir("packages/packagelists")):
        os.mkdir("packages/packagelists")

    i = 0
        
    for server in config["remote-servers"]:
        i += 1
        try:
            urllib.request.urlretrieve(server, f"packages/packagelists/packages_remote{i}.json")
        except urllib.error.URLError:
            print("ERROR: You don't have internet access!")
            return False
    return True

def loadConfig():
    if(checkConfig()):
        return json.loads(open("packages/ap-config/config.json").read())
    print("WARNING: Config is invalid, using the default one!")
    return defaultConfig()

def defaultConfig():
    config = {"check-hashes": True, "canInstallAgain": False, "remote-servers": ["https://raw.githubusercontent.com/m3z0id/AP-packages/main/packages-remote.json"]}
    if(not os.path.isdir("packages/ap-config")):
        os.mkdir("packages/ap-config")
    open("packages/ap-config/config.json", "w").write(json.dumps(config))
    return config

def checkConfig() -> bool:
    if(not os.path.isfile("packages/ap-config/config.json")):
        return False
    if(os.stat("packages/ap-config/config.json").st_size == 0):
        return False
    try:
        json.loads(open("packages/ap-config/config.json").read())
    except json.decoder.JSONDecodeError:
        return False
    return True

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

def install(package: str):
    if(not checkIfInstalled(package) and loadConfig()['canInstallAgain'] == False):
        print(f"ERROR: Package {package} is already installed!")
        return
    
    if(not downloadPackageLists()):
        return

    packageEntries = checkPackageLists(package)

    if(packageEntries == []):
        print(f"ERROR: Package {package} was not found.")
        shutil.rmtree("packages/packagelists")
        return False
    
    choiceinput = "0"
    if(len(packageEntries) > 1):
        for entry in packageEntries:
            print(f"{packageEntries.index(entry)}. {entry['name']} ({entry['dl-link']})")
        choiceinput = input("Which package(s) do you want? <index(es)>/<all>: ")
    if(choiceinput != "all"):
        choice = choiceinput.split(" ")
        try:
            for i in choice:
                i = int(i)
                if(not i in range(len(choice))):
                    print("ERROR: Invalid input.")
                    continue
                
                if(not os.path.isdir("packages")):
                    os.mkdir("packages")
                print(f"INFO: Installing {package}...")
    
                if(not downloadPackage(packageEntries[i])):
                    shutil.rmtree("packages/packagelists")
                    return

                updateLocalPackageList(packageEntries[i])

                print(f"Package {package} was installed successfully!")
                if(packageEntries[i]['name'] == "base.py" or packageEntries[i]['name'] == "shell.py" or packageEntries[i]['name'] == "spm.py"):
                    os.replace(f"packages/{packageEntries[i]['name']}", packageEntries[i]['name'])
                
        except TypeError:
            shutil.rmtree("packages/packagelists")
            print("ERROR: Invalid input. Aborting instalation.")
            return False
    
    else:
        for i in range(len(packageEntries)):          
            if(not os.path.isdir("packages")):
                os.mkdir("packages")
            print(f"INFO: Installing {package}...")
    
            if(not downloadPackage(packageEntries[i])):
                shutil.rmtree("packages/packagelists")
                return

            updateLocalPackageList(packageEntries[i])

            print(f"Package {package} was installed successfully!")
            if(packageEntries[i]['name'] == "base.py" or packageEntries[i]['name'] == "shell.py" or packageEntries[i]['name'] == "spm.py"):
                os.replace(f"packages/{packageEntries[i]['name']}", packageEntries[i]['name'])

    shutil.rmtree("packages/packagelists")

def update(package: str):
    packagesToUpdate = checkLocalPackageLists(package)

    if(not downloadPackageLists()):
        return
    packageEntries = checkPackageLists(package)
    if(packageEntries == []):
        print(f"ERROR: Package {package} was not found.")
        shutil.rmtree("packages/packagelists")
        return False
    
    choiceinput = "0"
    if(len(packagesToUpdate) > 1):
        for entry in packagesToUpdate:
            print(f"{packagesToUpdate.index(entry)}. {entry['name']} ({entry['dl-link']})")
        choiceinput = input("Which package(s) do you want? <index(es)>/<all>: ")
    
    if(choiceinput != "all"):
        choice = choiceinput.split(" ")
        try:
            for i in choice:
                i = int(i)
                if(not i in range(len(choice))):
                    print("ERROR: Invalid input.")
                    continue

                if(not os.path.isdir("packages")):
                    os.mkdir("packages")
                print(f"INFO: Updating {package}...")
                if(not downloadPackage(packagesToUpdate[i])):
                    shutil.rmtree("packages/packagelists")
                    return

                updateLocalPackageList(packageEntries[i])

                print(f"Package {package} was installed successfully!")
                if(packagesToUpdate[i]['name'] == "base.py" or packagesToUpdate[i]['name'] == "shell.py" or packagesToUpdate[i]['name'] == "spm.py"):
                    os.replace(f"packages/{packagesToUpdate[i]['name']}", packagesToUpdate[i]['name'])
        
        except TypeError:
            shutil.rmtree("packages/packagelists")
            print("ERROR: Invalid input. Aborting instalation.")
            return False
    
    else:
        for i in range(len(packageEntries)):          
            if(not os.path.isdir("packages")):
                os.mkdir("packages")
            print(f"INFO: Updating {package}...")
    
            if(not downloadPackage(packageEntries[i])):
                shutil.rmtree("packages/packagelists")
                return

            updateLocalPackageList(packageEntries[i])

            print(f"Package {package} was installed successfully!")
            if(packageEntries[i]['name'] == "base.py" or packageEntries[i]['name'] == "shell.py" or packageEntries[i]['name'] == "spm.py"):
                os.replace(f"packages/{packageEntries[i]['name']}", packageEntries[i]['name'])
                
    

    
def listpkg(package: str = None):
    try:
        localPackages = json.loads(open("packages/packages_local.json", "r").read())
    except FileNotFoundError:
        print("ERROR: No packages installed.")
        return True
    
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

def remove(package: str):
    localPackages = json.loads(open("packages/packages_local.json", "r").read())

    localPackageIndex: int = -1
    for currentPackageId in localPackages['packages']:
        localPackageIndex += 1
        if(currentPackageId['name'] == package or currentPackageId['name'] == f"{package}.py" or f"{currentPackageId['name']}.py" == package):
            localPackageId = currentPackageId
            break
    else:
        print(f"ERROR: Package {package} is not installed.")
        return False
    
    localPackages['packages'].pop(localPackageIndex)
    open("packages/packages_local.json", "w").write(json.dumps(localPackages))
    if(currentPackageId['name'] == "base.py" or currentPackageId['name'] == "shell.py" or currentPackageId['name'] == "spm.py"):
        os.remove(currentPackageId['name'])
    else:
        os.remove(f"packages/{localPackageId['name']}")

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
        elif(args[1] == "init"):
            defaultConfig()
        else:
            print("ERROR: Wrong arguments!")
    except IndexError:
        print("Autistic packager by M3z0id")
        print("---------------------------")
        print("Help:")
        print("ap init - initializes AP config (not required)")
        print("ap install <package> - installs package")
        print("ap update <package> - updates package")
        print("ap remove <package> - uninstalls a package")
        print("ap listpkg <package (optional)> - shows you info about packages")