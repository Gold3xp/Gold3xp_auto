from instagrapi import Client
from utils.license_check import is_license_valid
import json, time, os

def input_with_confirm(prompt):
    while True:
        value = input(prompt)
        confirm = input(f"✅ Kamu yakin dengan: '{value}'? (y/n): ").lower()
        if confirm == 'y':
            return value

# Login
print("🔐 Login Instagram")
username = input_with_confirm("Masukkan username IG: ")
password = input_with_confirm("Masukkan password IG: ")

# Lisensi
print("\n🧾 Cek Lisensi")
license_key = input_with_confirm("Masukkan License Key: ")
if not is_license_valid(license_key):
    print("❌ Lisensi tidak valid. Hubungi pembuat script.")
    exit()

# Target
print("\n🎯 Target Komentar")
target_list = []
while True:
    target = input("➕ Tambah username target (tanpa @): ")
    if target: target_list.append(target)
    lanjut = input("Tambah lagi? (y/n): ").lower()
    if lanjut != 'y':
        break

# Komentar
print("\n💬 Isi Komentar")
comment_list = []
while True:
    comment = input("➕ Tambah komentar: ")
    if comment: comment_list.append(comment)
    lanjut = input("Tambah komentar lagi? (y/n): ").lower()
    if lanjut != 'y':
        break

# Jeda dan batas
print("\n⏱️ Pengaturan Waktu")
BATAS_DETIK = int(input("Batas detik postingan baru (misal 1): "))
JEDA_CEK = int(input("Jeda cek tiap berapa detik (misal 1): "))
JEDA_KOMEN = int(input("Tunggu berapa detik sebelum komentar (misal 30): "))

# Login ke Instagram
cl = Client()
cl.login(username, password)

# Simpan history media_id yang sudah dikomen
commented = set()

# Loop terus
while True:
    for target in target_list:
        try:
            user_id = cl.user_id_from_username(target)
            medias = cl.user_medias(user_id, 1)

            if medias:
                media = medias[0]
                age_seconds = (time.time() - media.taken_at.timestamp())
                if age_seconds <= BATAS_DETIK and media.id not in commented:
                    comment = comment_list[0]  # Ambil komentar pertama atau random
                    print(f"\n⏳ Menunggu {JEDA_KOMEN} detik sebelum komentar ke @{target}...")
                    time.sleep(JEDA_KOMEN)
                    cl.media_comment(media.id, comment)
                    commented.add(media.id)
                    print(f"✅ Komentar terkirim ke @{target}: {comment}")
                else:
                    print(f"⏭️ Postingan @{target} tidak baru ({int(age_seconds)}s lalu)")
            else:
                print(f"⚠️ Tidak ada postingan dari @{target}")

        except Exception as e:
            print(f"❌ Gagal komentar ke @{target}: {e}")

    print(f"🔁 Menunggu {JEDA_CEK} detik sebelum pengecekan berikutnya...\n")
    time.sleep(JEDA_CEK)
