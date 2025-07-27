from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, FeedbackRequired, PleaseWaitFewMinutes
from colorama import Fore, init
import time, random, os, sys

from utils.tools import clear_terminal, load_file_lines
from utils.banner import tampilkan_banner
from utils.license_check import is_license_valid

init(autoreset=True)

def input_list(prompt, separator=","):
    print(f"{prompt} (pisahkan dengan '{separator}')")
    return [i.strip() for i in input(">> ").split(separator) if i.strip()]

def konfirmasi(data):
    print(f"{Fore.YELLOW}[?] Konfirmasi: {data}")
    return input(f"{Fore.YELLOW}Lanjut? (y/n): ").lower() == "y"

def ambil_data_postingan(cl, username):
    try:
        user_id = cl.user_id_from_username(username)
        post = cl.user_medias(user_id, 1)[0]
        return post
    except Exception as e:
        print(f"{Fore.RED}Gagal mengambil postingan: {e}")
        return None

def kirim_komentar(cl, media_id, komentar):
    try:
        cl.media_comment(media_id, komentar)
        print(f"{Fore.CYAN}💬 Komentar terkirim")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Gagal komentar: {e}")
        return False

def mulai_mode_gacor(cl, target, komentar_list):
    sudah_diproses = set()
    print(f"{Fore.YELLOW}⏳ Menunggu postingan baru...")
    while True:
        post = ambil_data_postingan(cl, target)
        if post and post.pk not in sudah_diproses:
            usia_detik = time.time() - post.taken_at.timestamp()
            if 30 <= usia_detik <= 31:
                print(f"{Fore.GREEN}✅ Postingan baru ditemukan! ({target}) - Usia: {int(usia_detik)} detik")
                komentar = random.choice(komentar_list)
                if kirim_komentar(cl, post.pk, komentar):
                    sudah_diproses.add(post.pk)
            else:
                time.sleep(1)
        else:
            time.sleep(1)

def main():
    clear_terminal()
    tampilkan_banner()

    if not is_license_valid():
        print(f"{Fore.RED}Lisensi tidak valid.")
        sys.exit()

    akun_path = "Data"
    akun_folders = sorted([f for f in os.listdir(akun_path) if os.path.isdir(os.path.join(akun_path, f))])

    for folder in akun_folders:
        path = os.path.join(akun_path, folder)
        cookie_file = os.path.join(path, "cookie.txt")
        user_file = os.path.join(path, "user.txt")

        if not os.path.exists(cookie_file) or not os.path.exists(user_file):
            print(f"{Fore.RED}❌ Lewat akun {folder}, file tidak ditemukan.")
            continue

        cl = Client()
        try:
            with open(user_file) as f:
                username = f.read().strip()
            with open(cookie_file) as f:
                cookie = f.read().strip()
            cl.load_settings({})
            cl.sessionid = cookie
            cl.login_by_sessionid(cookie)
            me = cl.account_info()
            print(f"{Fore.GREEN}✅ Login sukses: {me.username}")
        except Exception as e:
            print(f"{Fore.RED}❌ Gagal login akun {folder}: {e}")
            continue

        target = input("Masukkan username target: ").strip()
        komentar_list = input_list("Masukkan komentar")
        if not konfirmasi(f"Target: {target} | Total komentar: {len(komentar_list)}"):
            print("Dibatalkan.")
            break

        mulai_mode_gacor(cl, target, komentar_list)

if __name__ == "__main__":
    main()
