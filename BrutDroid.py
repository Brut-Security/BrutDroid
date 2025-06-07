import os
import sys
import time
import zipfile
import shutil
import requests
import subprocess
import platform
from OpenSSL import crypto
try:
    from termcolor import colored, cprint
    from termcolor import force_color
except ImportError:
    colored = None
    cprint = None
    force_color = None

def display_banner():
    if force_color:
        force_color()
    banner = """
█▄▄ █▀█ █░█ ▀█▀ █▀▄ █▀█ █▀█ █ █▀▄
█▄█ █▀▄ █▄█ ░█░ █▄▀ █▀▄ █▄█ █ █▄▀
"""
    tagline = "Built to Break. Powered by Brut."
    version = "BrutDroid | v1.0.1"
    if colored:
        cprint("[DEBUG] termcolor loaded", 'yellow', attrs=['bold'])
        print(colored(banner, 'red', attrs=['bold']))
        print(colored(tagline, 'cyan', attrs=['bold']))
        print(colored(version, 'green', attrs=['bold']))
    else:
        print("\033[1;31m" + banner + "\033[0m")
        print("\033[1;36m" + tagline + "\033[0m")
        print("\033[1;32m" + version + "\033[0m")
        print("\033[1;33m[DEBUG] Using ANSI colors (termcolor not installed)\033[0m")

def initial_environment_check():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[96m→ Initializing BrutDroid Environment...\033[0m")
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    checks = [
        ("Python Installation", check_python),
        ("Python PATH", check_python_path),
        ("ADB Availability", check_adb)
    ]
    results = []
    for i, (name, check_func) in enumerate(checks):
        print(f"\033[96m{name}...\033[0m ", end="", flush=True)
        for _ in range(8):
            sys.stdout.write(f"\r\033[96m{name}... {spinner[i % len(spinner)]}\033[0m")
            sys.stdout.flush()
            time.sleep(0.15)
        success, detail = check_func()
        results.append((name, success, detail))
        status = "\033[92m✔\033[0m" if success else "\033[91m✖\033[0m"
        print(f"\r\033[96m{name}: {status}")
        time.sleep(0.3)
    print("\n\033[96m→ Check Results:\033[0m")
    all_passed = True
    for name, success, detail in results:
        status = "\033[92m✔\033[0m" if success else "\033[91m✖\033[0m"
        print(f"  {status} {name}")
        if not success:
            all_passed = False
            print(f"    \033[93m→ {detail}\033[0m")
    result_message = "\033[92m✔ All systems ready!\033[0m" if all_passed else "\033[91m⚠ Fix issues to proceed.\033[0m"
    print(f"\n{result_message}")
    time.sleep(1.5)
    print("\033[96m→ Loading menu...\033[0m")
    time.sleep(1)

def check_python():
    if "Microsoft\\WindowsApps\\python.exe" in sys.executable:
        return False, "Install Python from python.org, not Microsoft Store."
    return True, "Python installed."

def check_python_path():
    if not shutil.which("python"):
        return False, "Add Python to system PATH."
    return True, "Python in PATH."

def check_adb():
    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        if os.path.exists(os.path.join(path_dir, "adb.exe" if os.name == 'nt' else "adb")):
            return True, "ADB found."
    return False, "Add ADB (platform-tools) to PATH."

ADB = "adb"

def is_tool_installed(tool):
    try:
        subprocess.run([tool], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception:
        return False

def install_tool(tool):
    subprocess.run(['pip', 'install', tool])

def install_frida_server():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[96m→ Installing Frida Server...\033[0m")
    try:
        result = subprocess.getoutput("adb devices")
        if "device" not in result.splitlines()[-1]:
            print("\033[91m✖ No emulator device detected. Start your emulator.\033[0m")
            input("\033[96m→ Press Enter to continue...\033[0m")
            return
        abi = subprocess.check_output(f"{ADB} shell getprop ro.product.cpu.abi", shell=True, text=True).strip()
        version = subprocess.check_output("frida --version", shell=True, text=True).strip()
        frida_url = f"https://github.com/frida/frida/releases/download/{version}/frida-server-{version}-android-{abi}.xz"
        print("\033[96m  Downloading...\033[0m")
        os.system(f"curl -L -o frida-server.xz {frida_url}")
        print("\033[96m  Extracting...\033[0m")
        import lzma
        with lzma.open("frida-server.xz") as f_in, open("frida-server", "wb") as f_out:
            f_out.write(f_in.read())
        print("\033[96m  Pushing to emulator...\033[0m")
        os.system(f"{ADB} push frida-server /data/local/tmp/")
        os.system(f"{ADB} shell chmod +x /data/local/tmp/frida-server")
        print("\033[92m✔ Frida server installed.\033[0m")
    except Exception as e:
        print(f"\033[91m✖ Failed: {e}\033[0m")
        print("\033[93m→ Ensure emulator is running and frida-tools is installed.\033[0m")
    input("\033[96m→ Press Enter to continue...\033[0m")
    os.system('cls' if os.name == 'nt' else 'clear')

def run_frida_server():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[96m→ Starting Frida Server...\033[0m")
    subprocess.call("adb start-server", shell=True)
    result = subprocess.getoutput("adb devices")
    if "device" not in result.splitlines()[-1]:
        print("\033[91m✖ No emulator device detected. Start your emulator.\033[0m")
    else:
        print("\033[96m  Launching in background...\033[0m")
        cmd = f'{ADB} shell su -c "nohup /data/local/tmp/frida-server > /dev/null 2>&1 &"'
        subprocess.Popen(cmd, shell=True)
        time.sleep(2)  # Wait for server to start
        print("\033[92m✔ Frida server running.\033[0m")
    input("\033[96m→ Press Enter to continue...\033[0m")
    os.system('cls' if os.name == 'nt' else 'clear')

def setup_cert_with_magisk():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[96m→ Setting Up Burp Certificate...\033[0m\n"
    "\033[96m  Before proceeding:\033[0m\n"
    "  - Ensure Burp Suite is running on port 8080.\n"
    "  - Set emulator proxy: Settings → Network → Proxy\n"
    "    → Host: 127.0.0.1, Port: 8080\n"
    "\033[96m  Waiting 20s for proxy setup...\033[0m\n")

    for i in range(20, 0, -1):
        print(f"\r\033[96m  {i}s left...\033[0m", end="", flush=True)
        time.sleep(1)
    print("\r\033[96m  Downloading certificate...\033[0m")
    try:
        response = requests.get("http://127.0.0.1:8080/cert")
        with open("cacert.der", "wb") as f:
            f.write(response.content)
        cert = crypto.load_certificate(crypto.FILETYPE_ASN1, open("cacert.der", "rb").read())
        pem = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
        with open("portswigger.crt", "wb") as f:
            f.write(pem)
        print("\033[96m  Pushing certificate...\033[0m")
        os.system(f"{ADB} push portswigger.crt /sdcard/portswigger.crt")
        print("\033[96m  Fetching latest AlwaysTrustUserCerts version...\033[0m")
        try:
            response = requests.get("https://api.github.com/repos/NVISOsecurity/AlwaysTrustUserCerts/releases/latest", timeout=5)
            response.raise_for_status()
            module_version = response.json()["tag_name"]
            filename = f"AlwaysTrustUserCerts_{module_version}.zip"
            module_url = f"https://github.com/NVISOsecurity/AlwaysTrustUserCerts/releases/download/{module_version}/{filename}"
        except (requests.RequestException, KeyError) as e:
            print(f"\033[93m→ Failed to fetch latest version: {e}\033[0m")
            print("\033[93m→ Falling back to v1.3\033[0m")
            module_version = "v1.3"
            filename = f"AlwaysTrustUserCerts_{module_version}.zip"
            module_url = f"https://github.com/NVISOsecurity/AlwaysTrustUserCerts/releases/download/{module_version}/{filename}"
        print(f"\033[96m  Downloading AlwaysTrustUserCerts {module_version}...\033[0m")
        r = requests.get(module_url)
        r.raise_for_status()
        with open(filename, "wb") as f:
            f.write(r.content)
        print("\033[96m  Installing Magisk module...\033[0m")
        os.system(f"{ADB} push {filename} /data/local/tmp/")
        os.system(f"{ADB} shell su -c 'magisk --install-module /data/local/tmp/{filename}'")
        print("\033[92m✔ Module installed.\033[0m\n"
        "\n\033[93m→ Action Required:\033[0m\n"
        "  1. Go to Settings → Security → Encryption & Credentials\n"
        "  2. Select 'Install from SD card'\n"
        "  3. Choose '/sdcard/portswigger.crt'\n"
        "  4. Name it 'portswigger'\n"
        "\033[96m  Waiting 60s for installation...\033[0m")
        for i in range(60, 0, -1):
            print(f"\r\033[96m  {i}s left...\033[0m", end="", flush=True)
            time.sleep(1)
        print("\r\033[96m  Rebooting emulator...\033[0m")
        os.system(f"{ADB} reboot")
        print("\033[92m✔ Setup complete. Emulator rebooting.\033[0m")
    except Exception as e:
        print(f"\033[91m✖ Failed: {e}\033[0m")
    input("\033[96m→ Press Enter to continue...\033[0m")
    os.system('cls' if os.name == 'nt' else 'clear')

def show_virtual_device_instructions():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[1;93m→ Creating a Virtual Device:\033[0m\n"
      "\033[1;36m  1. Open Android Studio → AVD Manager\033[0m\n"
      "\033[1;36m  2. Click 'Create Virtual Device'\033[0m\n"
      "\033[1;36m  3. Select a device (e.g., Pixel 6, Pixel 5, Pixel 4)\033[0m\n"
      "\033[1;36m  4. Choose system image:\033[0m\n"
      "\033[1;36m     - API Level: 31 (Android 12)\033[0m\n"
      "\033[1;36m     - Architecture: x86_64/arm64\033[0m\n"
      "\033[1;36m  5. Complete setup\033[0m\n"
      "\n\033[1;93m→ Note: Ensure API Level 31 and x86_64/arm64 architecture for compatibility.\033[0m\n"
      "\033[92m✔ Instructions displayed.\033[0m")
    input("\033[96m→ Press Enter to continue...\033[0m")
    os.system('cls' if os.name == 'nt' else 'clear')

def install_magisk_and_patch_rootavd():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[96m→ Rooting Emulator with Magisk...\033[0m")
    try:
        print("\033[96m  Fetching latest Magisk version...\033[0m")
        try:
            response = requests.get("https://api.github.com/repos/topjohnwu/Magisk/releases/latest", timeout=5)
            response.raise_for_status()
            magisk_version = response.json()["tag_name"]
            magisk_filename = f"Magisk-{magisk_version}.apk"
            magisk_url = f"https://github.com/topjohnwu/Magisk/releases/download/{magisk_version}/{magisk_filename}"
        except (requests.RequestException, KeyError) as e:
            print(f"\033[93m→ Failed to fetch latest Magisk version: {e}\033[0m")
            print("\033[93m→ Falling back to Magisk v29.0\033[0m")
            magisk_version = "v29.0"
            magisk_filename = "Magisk-v29.0.apk"
            magisk_url = f"https://github.com/topjohnwu/Magisk/releases/download/{magisk_version}/{magisk_filename}"

        print(f"\033[96m  Downloading Magisk {magisk_version}...\033[0m")
        r = requests.get(magisk_url)
        r.raise_for_status()
        with open(magisk_filename, "wb") as f:
            f.write(r.content)
        print("\033[96m  Installing Magisk...\033[0m")
        os.system(f"{ADB} install {magisk_filename}")

        zip_url = "https://gitlab.com/newbit/rootAVD/-/archive/master/rootAVD-master.zip"
        zip_file = "rootAVD.zip"
        extract_dir = "rootAVD"
        print("\033[96m  Downloading rootAVD...\033[0m")
        r = requests.get(zip_url)
        r.raise_for_status()
        with open(zip_file, "wb") as f:
            f.write(r.content)

        print("\033[96m  Extracting rootAVD...\033[0m")
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        bat_path = os.path.join(extract_dir, "rootAVD-master", "rootAVD.bat")
        bat_dir = os.path.dirname(bat_path)
        cwd = os.getcwd()

        print("\033[96m  Listing system images...\033[0m")
        os.chdir(bat_dir)
        os.system('cmd /c "rootAVD.bat ListAllAVDs"')

        print("\n\033[1;93m→ Verify Emulator Details:\033[0m\n"
        "\033[1;36m  1. Open Android Studio → Virtual Device Manager\033[0m\n"
        "\033[1;36m  2. Select your emulator and check:\033[0m\n"
        "\033[1;36m     - API Level: 31 (Android 12)\033[0m\n"
        "\033[1;36m     - Architecture: x86_64/arm64\033[0m\n"
        "\033[1;36m  3. Note the system image path from the AVD details\033[0m\n"
        "\033[1;93m→ Enter the system image path (e.g., system-images\\android-31\\google_apis\\x86_64\\ramdisk.img):\033[0m")
        img_path = input("\033[1;36mPath: \033[0m")

        print("\033[96m  Patching image...\033[0m")
        os.system(f'cmd /c "rootAVD.bat {img_path}"')
        os.chdir(cwd)

        print("\033[96m  Shutting down emulator...\033[0m")
        time.sleep(5)

        print("\n\033[1;93m→ Action Required:\033[0m")
        print("\033[1;36m  1. Cold boot the emulator manually in Android Studio\033[0m")
        print("\033[96m  Waiting 60s for boot...\033[0m")
        for i in range(60, 0, -1):
            print(f"\r\033[96m  {i}s left...\033[0m", end="", flush=True)
            time.sleep(1)

        print("\r\033[96m  Verifying connection...\033[0m")
        os.system("adb devices")
        os.system("adb shell echo Emulator Connected")

        print("\033[96m  Requesting root...\033[0m")
        os.system("adb shell su -c 'echo Root granted'")

        print("\n\033[1;93m→ Action Required:\033[0m\n"
        "\033[1;36m  1. Open the Magisk app on the emulator\033[0m\n"
        "\033[1;36m  2. Click 'OK' on the popup to complete setup\033[0m\n"
        "\033[1;36m  3. The emulator will reboot automatically\033[0m\n"
        "\033[96m  Waiting 10s for you to complete this step...\033[0m\n")
        time.sleep(10)
        print("\033[92m✔ Root setup complete.\033[0m")
    except Exception as e:
        print(f"\033[91m✖ Failed: {e}\033[0m")
    input("\033[96m→ Press Enter to continue...\033[0m")
    os.system('cls' if os.name == 'nt' else 'clear')

def frida_tool_options():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        display_banner()
        print("\n\033[96mFrida Tools:\033[0m\n"
        "  1. List Apps\n"
        "  2. Bypass SSL Pinning\n"
        "  3. Bypass Root Check\n"
        "  4. Bypass SSL + Root\n"
        "  5. Run Frida Server\n"
        "  6. Back\n")
        choice = input("\033[92m→ Choose: \033[0m")
        if choice == "1":
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\033[96m→ Listing Applications...\033[0m")
            result = subprocess.getoutput("adb devices")
            if "device" not in result.splitlines()[-1]:
                print("\033[91m✖ No emulator device detected. Start your emulator.\033[0m")
                input("\033[96m→ Press Enter to continue...\033[0m")
                continue
            os.system("frida-ps -Uai")
            print("\033[92m✔ Apps listed.\033[0m")
            input("\033[96m→ Press Enter to continue...\033[0m")
        elif choice in ["2", "3", "4"]:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\033[96m→ Running Frida Bypass...\033[0m")
            result = subprocess.getoutput("adb devices")
            if "device" not in result.splitlines()[-1]:
                print("\033[91m✖ No emulator device detected. Start your emulator.\033[0m")
                input("\033[96m→ Press Enter to continue...\033[0m")
                continue
            print("\033[96m  Requesting root...\033[0m")
            os.system("adb shell su -c 'echo Root granted'")
            print("\033[92m✔ Root requested. Grant popup if prompted.\033[0m")
            time.sleep(3)
            package = input("\033[96m→ Enter package name: \033[0m")
            scripts = {"2": "SSL-BYE.js", "3": "ROOTER.js", "4": "PintooR.js"}
            script_path = f"./Fripts/{scripts[choice]}"
            if not os.path.exists(script_path):
                print(f"\033[91m✖ Script {script_path} not found.\033[0m")
                print("\033[93m→ Ensure Fripts directory contains {scripts[choice]}.\033[0m")
                input("\033[96m→ Press Enter to continue...\033[0m")
                continue
            print("\033[96m  Executing bypass...\033[0m")
            os.system(f"frida -U -f {package} -l {script_path}")
            print("\033[92m✔ Bypass executed.\033[0m")
            input("\033[96m→ Press Enter to continue...\033[0m")
        elif choice == "5":
            run_frida_server()
        elif choice == "6":
            break
        os.system('cls' if os.name == 'nt' else 'clear')

def display_main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        display_banner()
        print("\n\033[96mMain Menu:\033[0m\n"
        "  1. Create Virtual Device\n"
        "  2. Root Emulator\n"
        "  3. Install Tools\n"
        "  4. Configure Emulator\n"
        "  5. Frida Tools\n"
        "  6. Exit\n")
        choice = input("\033[92m→ Choose: \033[0m")
        if choice == "1":
            show_virtual_device_instructions()
        elif choice == "2":
            install_magisk_and_patch_rootavd()
        elif choice == "3":
            display_windows_tools_menu()
        elif choice == "4":
            display_emulator_options_menu()
        elif choice == "5":
            frida_tool_options()
        elif choice == "6":
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\033[92m✔ Exiting BrutDroid. Stay sharp!\033[0m")
            break

def display_windows_tools_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        display_banner()
        print("\n\033[96mInstall Tools:\033[0m\n"
        "  1. Frida\n"
        "  2. Frida-Tools\n"
        "  3. Objection\n"
        "  4. Reflutter\n"
        "  5. Back\n")
        choice = input("\033[92m→ Choose: \033[0m")
        tools = {"1": "frida", "2": "frida-tools", "3": "objection", "4": "reflutter"}
        if choice in tools:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\033[96m→ Installing {tools[choice]}...\033[0m")
            install_tool(tools[choice])
            print(f"\033[92m✔ {tools[choice]} installed.\033[0m")
            input("\033[96m→ Press Enter to continue...\033[0m")
        elif choice == "5":
            break
        os.system('cls' if os.name == 'nt' else 'clear')

def display_emulator_options_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        display_banner()
        print("\n\033[96mConfigure Emulator:\033[0m\n"
        "  1. Install Frida Server\n"
        "  2. Run Frida Server\n"
        "  3. Install Burp Certificate\n"
        "  4. Back\n")

        choice = input("\033[92m→ Choose: \033[0m")
        if choice == "1":
            install_frida_server()
        elif choice == "2":
            run_frida_server()
        elif choice == "3":
            setup_cert_with_magisk()
        elif choice == "4":
            break
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    initial_environment_check()
    os.system('cls' if os.name == 'nt' else 'clear')
    display_main_menu()
