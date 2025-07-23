from instagrapi import Client
from colorama import Fore, init
import time, random, json
from utils.license_check import is_license_valid
from utils.tools import clear_terminal
from utils.banner import tampilkan_banner

init(autoreset=True)

def input_list(prompt, separator="|"):
    print(f"{prompt} (pisahkan dengan '{separator}')")
    return [i.strip() for i in input(">> ").split(separator) if i.strip()]

def konfirmasi(data, nama_data):
    print(f"\n📌 Konfirmasi {nama_data}:")
    for i, d in enumerate(data, 1):
        print(f"{i}. {d}")
    while True:
        konfirmasi = input(f"✅ Lanjut? (y = ya, r = ubah, x = keluar): ").lower()
        if konfirmasi == "y":
            return data
        elif konfirmasi == "r":
            return input_list(f"Masukkan ulang {nama_data}")
        elif konfirmasi == "x":
            exit()

def cek_season():
    try:
        with open("season.json") as f:
            data = json.load(f)
        if data.get("status", "").lower() != "active":
            print(Fore.RED + "🔒 Season tidak aktif.")
            exit()
    except FileNotFoundError:
        print(Fore.RED + "❌ File season.json tidak ditemukan.")
        exit()

def login_instagram():
    try:
        with open("session.json") as f:
            session = json.load(f)
    except FileNotFoundError:
        print(Fore.RED + "❌ File session.json tidak ditemukan.")
        exit()

    cl = Client()
    cl.login(session['username'], session['password'])
    return cl

# === START ===
clear_terminal()
tampilkan_banner()
cek_season()

key = input("🔑 Masukkan lisensi key Anda: ")
if not is_license_valid(key):
    print(Fore.RED + "❌ Lisensi tidak valid!")
    exit()

cl = login_instagram()
targets = konfirmasi(input_list("Masukkan username target"), "target")
comments = konfirmasi(input_list("Masukkan komentar"), "komentar")

print(Fore.GREEN + "✅ Menjalankan auto-comment...")
print(Fore.MAGENTA + "🚀 AUTO KOMEN BERJALAN – Deteksi semua postingan baru tanpa batas")

last_commented_media = {}

print(Fore.YELLOW + "⏳ Menunggu postingan baru...")

while True:
    for username in targets:
        try:
            user_id = cl.user_id_from_username(username)
            media = cl.user_medias(user_id, amount=1)[0]
            media_id = media.id
            age = time.time() - media.taken_at.timestamp()

            # Postingan baru dan belum dikomentari
            if media_id != last_commented_media.get(username) and age <= 31:
                print(Fore.GREEN + f"\n✅ Postingan baru ditemukan dari @{username} (umur: {int(age)} detik)")
                try:
                    komentar = random.choice(comments)
                    cl.media_comment(media_id, komentar)
                    last_commented_media[username] = media_id
                    print(Fore.CYAN + "💬 Komentar terkirim")
                except Exception as e:
                    print(Fore.RED + f"❌ Gagal komentar: {e}")
        except Exception as e:
            print(Fore.RED + f"⚠️  Gagal memeriksa @{username}: {e}")

    jeda = random.randint(4, 6)
    print(Fore.YELLOW + f"\n🕒 Jeda {jeda} detik...")
    time.sleep(jeda)
