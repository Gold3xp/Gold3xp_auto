from instagrapi import Client
from colorama import Fore, init
import time, random
from utils.license_check import is_license_valid
from utils.tools import clear_terminal
from utils.banner import tampilkan_banner

init(autoreset=True)

def input_list(prompt, separator=","):
    print(f"{prompt} (pisahkan dengan '{separator}')")
    return [i.strip() for i in input(">> ").split(separator) if i.strip()]

def konfirmasi(data, nama_data):
    print(f"\n📌 Konfirmasi {nama_data}:")
    for i, d in enumerate(data, 1):
        print(f"{i}. {d}")
    while True:
        lanjut = input("✅ Lanjut? (y = ya, r = ubah, x = keluar): ").lower()
        if lanjut == "y":
            return data
        elif lanjut == "r":
            return None
        elif lanjut == "x":
            print("❌ Dibatalkan.")
            exit()
        else:
            print("⚠️ Pilih hanya: y / r / x")

def login_instagram():
    print("\n🔐 LOGIN INSTAGRAM")
    username = input("Username: ")
    password = input("Password: ")
    print("⏳ Login...")
    cl = Client()
    try:
        cl.login(username, password)
        print("✅ Login berhasil!\n")
        return cl
    except Exception as e:
        print(f"❌ Gagal login: {e}")
        exit()

def cek_lisensi():
    print("🔑 CEK LISENSI")
    lisensi = input("Masukkan kode lisensi: ")
    if not is_license_valid(lisensi):
        print("❌ Lisensi tidak valid.")
        exit()
    print("✅ Lisensi valid.\n")

def auto_comment_loop(cl, targets, comments):
    sudah_dikomentari = set()
    print("\n🚀 AUTO KOMEN BERJALAN — Deteksi cepat postingan baru\n")

    sudah_print_menunggu = False
    try:
        while True:
            now = time.time()
            ada_post_baru = False

            for username in targets:
                try:
                    user_id = cl.user_id_from_username(username)
                    medias = cl.user_medias(user_id, amount=1)
                    if not isinstance(medias, list) or not medias:
                        continue

                    media = medias[0]
                    media_id = media.id
                    umur_post = now - media.taken_at.timestamp()

                    if media_id in sudah_dikomentari:
                        continue

                    if umur_post <= 31:
                        print(Fore.GREEN + f"✅ Postingan baru ditemukan! Mengirim komentar.. (user: {username}, umur: {int(umur_post)} detik)")
                        komentar = random.choice(comments)
                        try:
                            cl.media_comment(media_id, komentar)
                            print(Fore.CYAN + "💬 Komentar terkirim")
                            sudah_dikomentari.add(media_id)
                            ada_post_baru = True
                        except:
                            print(Fore.RED + "❌ Gagal komentar")
                except:
                    continue

            if not ada_post_baru:
                if not sudah_print_menunggu:
                    print(Fore.YELLOW + "⏳ Menunggu postingan baru...")
                    sudah_print_menunggu = True
                time.sleep(0.8)
            else:
                sudah_print_menunggu = False
                jeda = random.randint(3, 6)
                print(Fore.YELLOW + f"🕒 Jeda {jeda} detik...\n")
                time.sleep(jeda)

    except KeyboardInterrupt:
        print(Fore.RED + "\n🛑 Dihentikan oleh pengguna.")
        try:
            cl.logout()
            print(Fore.GREEN + "🔒 Logout berhasil.")
        except:
            print(Fore.RED + "⚠️ Gagal logout.")

def menu():
    print(Fore.CYAN + "\n==== MENU ====")
    print("1. Jalankan auto-comment")
    print("2. Logout Instagram")
    print("3. Keluar")
    return input("Pilih menu: ")

def main():
    clear_terminal()
    tampilkan_banner()
    cek_lisensi()
    cl = login_instagram()

    while True:
        clear_terminal()
        tampilkan_banner()
        pilihan = menu()

        if pilihan == "1":
            clear_terminal()
            tampilkan_banner()
            while True:
                targets = input_list("Masukkan daftar target username (tanpa @, pisahkan dengan koma)", ",")
                confirmed = konfirmasi(targets, "target")
                if confirmed:
                    break

            while True:
                comments = input_list("Masukkan daftar komentar (pisahkan dengan '|')", "|")
                confirmed = konfirmasi(comments, "komentar")
                if confirmed:
                    break

            print(Fore.GREEN + "\n▶️ Menjalankan auto-comment...\n")
            auto_comment_loop(cl, targets, comments)

        elif pilihan == "2":
            clear_terminal()
            tampilkan_banner()
            try:
                cl.logout()
                print(Fore.GREEN + "✅ Berhasil logout.\n")
            except:
                print(Fore.RED + "❌ Logout gagal.\n")
            input("Tekan Enter untuk kembali...")

        elif pilihan == "3":
            print(Fore.CYAN + "\n👋 Keluar...")
            break

        else:
            print(Fore.RED + "\n❌ Pilihan tidak valid!")
            input("Tekan Enter untuk kembali...")

if __name__ == "__main__":
    main()
