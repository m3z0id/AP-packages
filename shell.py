import base
import subprocess
import spm
import os
from rich import print
from rich.console import Console
base.clear_screen()
console = Console()
print("reverse [bold magenta]Reborn[/bold magenta]! [bold yellow]version 1.0[/bold yellow]", ":thumbsup:")
def popFirstArg(argsList: list) -> list:
    argsList.pop(0)
    return argsList

try:
    while True:
        line = input(" :house: home > ")
        lineList = line.split()
        if line == "spm -update base":
            print(" :file_folder: updating...")
            spm.update_base()
            spm.cleanup()
            
        elif line == "-fs setup":
            print(" :card_box: setting up filesystem...")
            base.setup_userfolders()
            
        elif line == "-fs go graveyard":
            print(" :warning: goodbye files!")
            
            base.remove_userfolders()
        elif line == "clear":
            base.clear_screen()
            
        elif line.startswith("makefile "):
            filename = line.split(" ", 1)[1]
            base.makefile(filename)
            
        elif line.startswith("makedir "):
            dirname = line.split(" ", 1)[1]
            base.makedir(dirname)
            
        elif line.startswith("delfile "):
            filename = line.split(" ", 1)[1]
            base.delfile(filename)
            
        elif line.startswith("deldir "):
            dirname = line.split(" ", 1)[1]
            base.deldir(dirname)
            
        elif line == "pwd":
            working_directory = os.getcwd()
            print(" " + working_directory)
            
        elif line == "clock":
            base.clock()
            
        elif line == "ls":
            try:
                files = os.listdir()
                for file in files:
                    if os.path.isdir(file):
                        console.print(file, style="bold blue")
                    else:
                        console.print(file, style="white")
            except Exception as e:
                print(f"Error listing directory: {e}")
            
        elif line == "exit":
            base.clear_screen()
            print("exited with no errors. I HOPE.")
            
        elif line == "spm -update core":
            spm.update_spm_core()
            
        elif line.startswith("spm -install "):
            package = line.split(" ", 2)[2]
            spm.spm_installpkg(package)
            

        elif(lineList[0].split(".")[-1] == "py" and os.path.isfile(f"packages/{lineList[0]}")):
            subprocess.run(["python", f"packages/{lineList[0]}", *popFirstArg(lineList)])
            

        elif(os.path.isfile(f"packages/{lineList[0]}.py")):
            subprocess.run(["python", f"packages/{lineList[0]}.py", *popFirstArg(lineList)])
            

        elif(os.path.isfile(f"packages/{lineList[0]}")):
            subprocess.run([f"{os.getcwd()}/packages/{lineList[0]}", *popFirstArg(lineList)])

        else:    
            print("ERROR: Command doesn't exist!")

except KeyboardInterrupt:
    base.clear_screen()
    print("exited with no errors. I HOPE.")