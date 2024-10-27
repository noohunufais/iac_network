import subprocess

def ping_check(host:str) -> bool:
    try:
        subprocess.run(["ping", "-c", "1", host], stdout=subprocess.DEVNULL, timeout=1)
        return True
    except Exception as e:
        return False
