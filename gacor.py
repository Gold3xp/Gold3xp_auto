from utils.auth_handler import login_instagram
from utils.comment_manager import load_comments, choose_comment
from utils.license_check import is_license_valid
import json, time, os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")
LICENSE_KEY = os.getenv("LICENSE_KEY")

# Cek lisensi
if not is_license_valid(LICENSE_KEY):
    print("❌ Lisensi tidak valid. Hubungi pembuat script.")
    exit()

# Load daftar komentar
comments = load_comments("comments.json")

# Load daftar target username
with open("targets.json", "r") as f:
    targets = json.load(f)

# Login ke Instagram
from instagrapi import Client
cl = login_instagram(IG_USERNAME, IG_PASSWORD)

# Durasi maksimal postingan dianggap "baru" (dalam detik)
BATAS_DETIK = 1  # ganti sesuai kebutuhanmu

# Loop ke semua target
for username in targets:
    try:
        user_id = cl.user_id_from_username(username)
        medias = cl.user_medias(user_id, 1)  # Ambil 1 postingan terbaru

        if medias:
            media = medias[0]
            timestamp = media.taken_at
            sekarang = datetime.now()

            if timestamp >= sekarang - timedelta(seconds=BATAS_DETIK):
                media_id = media.id
                comment = choose_comment(comments)

                print(f"⏳ Menunggu 30 detik sebelum komentar ke @{username}...")
                time.sleep(30)

                cl.media_comment(media_id, comment)
                print(f"✅ Komentar terkirim ke @{username}: {comment}")
            else:
                print(f"⏭️ Postingan @{username} terlalu lama (upload: {timestamp}) — dilewati.")

        else:
            print(f"⚠️ Tidak ada postingan dari @{username}")

    except Exception as e:
        print(f"❌ Gagal komentar ke @{username}: {e}")
