import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "daphne", "-p", "8000", "victorAi.asgi:application"])
    
    # python run_dev.py