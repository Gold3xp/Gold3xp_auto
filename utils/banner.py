import os
from colorama import Fore, Style

def tampilkan_banner():
    os.system("clear")  # Untuk membersihkan terminal
    print(
        Fore.GREEN + Style.BRIGHT + " ██████╗ " +
        Fore.BLUE + Style.BRIGHT + "███████╗" +
        Fore.YELLOW + Style.BRIGHT + "███╗   ███╗" +
        Fore.RED + Style.BRIGHT + "███████╗"
    )
    print(
        Fore.GREEN + Style.BRIGHT + "██╔══██╗" +
        Fore.BLUE + Style.BRIGHT + "██╔════╝" +
        Fore.YELLOW + Style.BRIGHT + "████╗ ████║" +
        Fore.RED + Style.BRIGHT + "██╔════╝"
    )
    print(
        Fore.GREEN + Style.BRIGHT + "██████╔╝" +
        Fore.BLUE + Style.BRIGHT + "█████╗  " +
        Fore.YELLOW + Style.BRIGHT + "██╔████╔██║" +
        Fore.RED + Style.BRIGHT + "█████╗  "
    )
    print(
        Fore.GREEN + Style.BRIGHT + "██╔═══╝ " +
        Fore.BLUE + Style.BRIGHT + "██╔══╝  " +
        Fore.YELLOW + Style.BRIGHT + "██║╚██╔╝██║" +
        Fore.RED + Style.BRIGHT + "██╔══╝  "
    )
    print(
        Fore.GREEN + Style.BRIGHT + "██║     " +
        Fore.BLUE + Style.BRIGHT + "███████╗" +
        Fore.YELLOW + Style.BRIGHT + "██║ ╚═╝ ██║" +
        Fore.RED + Style.BRIGHT + "███████╗"
    )
    print(
        Fore.GREEN + Style.BRIGHT + "╚═╝     " +
        Fore.BLUE + Style.BRIGHT + "╚══════╝" +
        Fore.YELLOW + Style.BRIGHT + "╚═╝     ╚═╝" +
        Fore.RED + Style.BRIGHT + "╚══════╝"
    )
    print(Fore.CYAN + Style.BRIGHT + "\n🚀 CEFLON v2.0 - Auto Komen IG by GJP TEAM\n")
