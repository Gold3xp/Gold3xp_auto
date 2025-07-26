import os
from colorama import Fore, Style

def tampilkan_banner():
    os.system("clear")  # Bersihkan terminal

    print(Fore.YELLOW + r"""
   ____ ____ _      ____  ____ ___  ____  _  _ 
  / ___|  _ \ |    |  _ \|  _ \_ _| |  _ \| \| |
 | |  _| | | | |    | | | | | || |  | | | | .` |
 | |_| | |_| | |___ | |_| |_| || |  | |_| | |\ |
  \____|____/|____(_)____|____|___| |____/|_| \_|
    """)

    print(Fore.GREEN + Style.BRIGHT + "\n💎 G  O  L  D  3  X  P 💎")
    print(Fore.CYAN + Style.BRIGHT + "🚀 CEFLON v2.0 - Auto Komen IG by GJP TEAM\n" + Style.RESET_ALL)
