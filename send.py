#!/usr/bin/env python3
import subprocess
import os
import shutil

def run_cmd(cmd, check=False):
    print(f"[RUN] {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[WARN] Command failed (code {result.returncode}): {result.stderr.strip()}")
        if check:
            raise Exception(f"Command failed: {cmd}")
    else:
        if result.stdout.strip():
            print(result.stdout.strip())
    return result

def main():
    print("=== Skirk Cleanup Script ===\n")

    # 1. Stop and disable systemd service
    run_cmd("sudo systemctl stop skirk-exit.service 2>/dev/null")
    run_cmd("sudo systemctl disable skirk-exit.service 2>/dev/null")

    # 2. Remove service file
    run_cmd("sudo rm -f /etc/systemd/system/skirk-exit.service")
    run_cmd("sudo systemctl daemon-reload")

    # 3. Remove skirk binary
    which_skirk = subprocess.run("which skirk", shell=True, capture_output=True, text=True).stdout.strip()
    if which_skirk:
        run_cmd(f"sudo rm -f {which_skirk}")
    else:
        # try common paths
        for path in ["/usr/local/bin/skirk", os.path.expanduser("~/.local/bin/skirk")]:
            if os.path.exists(path):
                run_cmd(f"rm -f {path}")

    # 4. Remove kit folders
    for folder in ["skirk-kit", "skirk-kit-new"]:
        if os.path.exists(folder):
            run_cmd(f"rm -rf {folder}")

    # 5. Remove google login credentials
    a0c_path = os.path.expanduser("~/.skirk_a0c")
    if os.path.exists(a0c_path):
        run_cmd(f"rm -rf {a0c_path}")

    # 6. Remove install script if exists
    if os.path.exists("install_skirk.sh"):
        run_cmd("rm -f install_skirk.sh")

    # 7. Remove PATH line from .bashrc (optional)
    bashrc = os.path.expanduser("~/.bashrc")
    if os.path.exists(bashrc):
        with open(bashrc, "r") as f:
            lines = f.readlines()
        new_lines = [l for l in lines if 'export PATH="$HOME/.local/bin:$PATH"' not in l]
        with open(bashrc, "w") as f:
            f.writelines(new_lines)
        print(f"[INFO] Removed Skirk PATH from {bashrc}")

    # 8. Remove empty .local/bin
    local_bin = os.path.expanduser("~/.local/bin")
    if os.path.exists(local_bin) and not os.listdir(local_bin):
        os.rmdir(local_bin)
        print(f"[INFO] Removed empty {local_bin}")

    # 9. Remove /tmp/skirk* files
    run_cmd("rm -rf /tmp/skirk* 2>/dev/null")

    print("\n=== Skirk полностью удалён ===")
    print("Рекомендуется перезагрузить сервер: sudo reboot")

if __name__ == "__main__":
    main()
