from instagrapi import Client
from instagrapi.exceptions import (
    ChallengeRequired, FeedbackRequired, PleaseWaitFewMinutes, LoginRequired
)
from colorama import Fore, init
from utils.license_check import is_license_valid
from utils.tools import clear_terminal, load_file_lines, tampilkan_banner
import os, time, random, json

init(autoreset=True)

def parse_cookie_string(cookie_str):
    cookies = {}
    for item in cookie_str.split(";"):
        if "=" in item:
            key, value = item.strip().split("=", 1)
            cookies[key] = value
    return cookies

def login_dengan_cookie(folder):
    cl = Client()
    try:
        cookie_path = os.path.join(folder, "cookie.txt")
        user_path = os.path.join(folder, "user.txt")
        ua_path = os.path.join(folder, "Ua.txt")
        proxy_path = os.path.join(folder, "Proxy.txt")

        cookie_str = open(cookie_path, "r").read().strip()
        username = open(user_path, "r").read().strip()
        ua_list = load_file_lines(ua_path)
        proxy_list = load_file_lines(proxy_path)

        cookies = parse_cookie_string(cookie_str)
        cl.set_user_agent(random.choice(ua_list) if ua_list else None)
        if proxy_list:
            proxy = random.choice(proxy_list)
            cl.set_proxy(proxy)

        cl.set_cookie(cookies)
        cl.user_id = int(cookies["ds_user_id"])
        cl.account_id = cl.user_id
        cl.logged_in = True
        cl.get_timeline_feed()  # validasi login
        print(Fore.GREEN + f"✅ Login berhasil: {username}")
        return cl, username
    except Exception as e:
        print(Fore.RED + f"❌ Login gagal: {e}")
        return None, None

def mode_gacor(cl, username, targets, komentar_list, dummy):
    print(Fore.YELLOW + "⏳ Menunggu postingan baru...")

    terbaru = {}
    while True:
        for target in targets:
            try:
                user_id = cl.user_id_from_username(target)
                feed = cl.user_medias(user_id, 1)
                if not feed:
                    continue

                post = feed[0]
                post_id = post.pk
                timestamp = post.taken_at.timestamp()
                now = time.time()
                age = int(now - timestamp)

                if post_id != terbaru.get(target) and 30 <= age <= 31:
                    terbaru[target] = post_id
                    print(Fore.GREEN + f"✅ Postingan baru oleh @{target} (umur: {age}s)")

                    komentar = random.choice(komentar_list)
                    if dummy:
                        print(Fore.CYAN + f"💬 Dummy komentar: {komentar}")
                    else:
                        cl.media_comment(post_id, komentar)
                        print(Fore.CYAN + f"💬 Komentar terkirim: {komentar}")

                    print(Fore.YELLOW + "🕒 Jeda 5 detik...\n")
                    time.sleep(5)

            except Exception as e:
                print(Fore.RED + f"❌ Error @{target}: {e}")
                if "Please wait" in str(e) or isinstance(e, FeedbackRequired):
                    raise Exception("Akun limit")

        time.sleep(1)

def rotasi_multi_akun():
    akun_dirs = sorted([d for d in os.listdir("Data") if os.path.isdir(os.path.join("Data", d))])
    if not akun_dirs:
        print(Fore.RED + "❌ Tidak ada folder akun di /Data/")
        return

    komentar_list = input("💬 Masukkan komentar (pisahkan dengan |):\n>> ").split("|")
    targets = input("🎯 Masukkan target username (pisahkan dengan koma):\n>> ").split(",")
    dummy = input("🤖 Mode dummy? (y/n): ").lower() == "y"

    for akun in akun_dirs:
        clear_terminal()
        tampilkan_banner()
        print(Fore.BLUE + f"🔁 Menggunakan akun: {akun}")
        folder = os.path.join("Data", akun)

        cl, username = login_dengan_cookie(folder)
        if not cl:
            continue

        try:
            mode_gacor(cl, username, [t.strip() for t in targets], komentar_list, dummy)
        except Exception as e:
            print(Fore.RED + f"⚠️ Akun {akun} berhenti: {e}")
            print(Fore.YELLOW + "🔄 Beralih ke akun berikutnya...\n")
            time.sleep(3)
            continue

if __name__ == "__main__":
    clear_terminal()
    tampilkan_banner()
    if not is_license_valid():
        print(Fore.RED + "❌ Lisensi tidak valid!")
        exit()
    rotasi_multi_akun()
