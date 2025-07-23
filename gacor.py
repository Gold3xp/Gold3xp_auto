from instagrapi import Client
from colorama import Fore, init
import time, random
from utils.license_check import is_license_valid

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
    pending_comments = {}
    print("\n🚀 AUTO KOMEN BERJALAN TIAP DETIK — hanya jika postingan baru (≤1 detik)\n")
    try:
        while True:
            now = time.time()
            # Proses komentar
            to_remove = []
            for media_id, (username, komentar, found_time) in pending_comments.items():
                if now - found_time >= 30:
                    try:
                        cl.media_comment(media_id, komentar)
                        print(f"✅ KOMENTAR ke @{username}: {komentar}")
                        to_remove.append(media_id)
                    except Exception as e:
                        print(f"❌ Gagal komentar ke @{username}: {e}")
                        to_remove.append(media_id)
            for media_id in to_remove:
                pending_comments.pop(media_id, None)

            # Cek postingan baru
            for username in targets:
                try:
                    user_id = cl.user_id_from_username(username)
                    medias = cl.user_medias(user_id, 1)
                    if medias:
                        media = medias[0]
                        media_id = media.id
                        umur_post = now - media.taken_at.timestamp()

                        if media_id in pending_comments:
                            continue

                        if umur_post <= 1:
                            komentar = random.choice(comments)
                            print(f"🕐 @{username}: Postingan baru ({umur_post:.2f}s), komentar akan dikirim dalam 30 detik...")
                            pending_comments[media_id] = (username, komentar, now)
                        else:
                            print(f"⏭️ @{username}: Postingan terlalu lama ({int(umur_post)} detik)")
                    else:
                        print(f"⚠️ @{username}: Tidak ada postingan.")
                except Exception as e:
                    print(f"❌ Error @{username}: {e}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Dihentikan oleh pengguna.")
        try:
            cl.logout()
            print("🔒 Berhasil logout dari Instagram.")
        except:
            print("⚠️ Gagal logout.")

def menu():
    print(Fore.CYAN + "\n==== MENU ====")
    print("1. Jalankan auto-comment")
    print("2. Logout Instagram")
    print("3. Keluar")
    return input("Pilih menu: ")

def main():
    print(Fore.CYAN + "===== AUTO KOMEN INSTAGRAM v2.0 =====")
    cek_lisensi()
    cl = login_instagram()

    while True:
        pilihan = menu()

        if pilihan == "1":
            # Input target
            while True:
                targets = input_list("Masukkan daftar target username (tanpa @, pisahkan dengan koma)", ",")
                confirmed = konfirmasi(targets, "target")
                if confirmed:
                    break

            # Input komentar
            while True:
                comments = input_list("Masukkan daftar komentar (pisahkan dengan '|')", "|")
                confirmed = konfirmasi(comments, "komentar")
                if confirmed:
                    break

            print(Fore.GREEN + "\n▶️ Menjalankan auto-comment...\n")
            auto_comment_loop(cl, targets, comments)

        elif pilihan == "2":
            try:
                cl.logout()
                print(Fore.GREEN + "✅ Berhasil logout.\n")
            except:
                print(Fore.RED + "❌ Logout gagal.\n")

        elif pilihan == "3":
            print(Fore.CYAN + "\n👋 Keluar...")
            break

        else:
            print(Fore.RED + "\n❌ Pilihan tidak valid!")

if __name__ == "__main__":
    main()
