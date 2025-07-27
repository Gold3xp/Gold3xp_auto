import os, sys, time, random, requests
from bs4 import BeautifulSoup
from colorama import Fore, init
from utils.license_check import is_license_valid
from utils.tools import clear_terminal
from utils.banner import tampilkan_banner

init(autoreset=True)

def load_file_lines(path):
    if not os.path.exists(path):
        return []
    return [line.strip() for line in open(path) if line.strip()]

def load_accounts(folder='Data'):
    if not os.path.exists(folder):
        return []
    return [(n, os.path.join(folder, n)) for n in os.listdir(folder)
            if os.path.isdir(os.path.join(folder, n))]

def baca_cookie_file(path):
    try:
        with open(os.path.join(path, "cookie.txt"), "r") as f:
            isi = f.read().strip()
        bagian = dict(item.strip().split("=") for item in isi.split("; ") if "=" in item)
        sessionid = bagian.get("sessionid")
        ds_user_id = bagian.get("ds_user_id")
        if sessionid and ds_user_id:
            return sessionid, ds_user_id
        else:
            print(Fore.RED + f"[!] Format cookie salah di {path}")
            return None, None
    except FileNotFoundError:
        print(Fore.RED + f"[!] cookie.txt tidak ditemukan di {path}")
        return None, None
    except Exception as e:
        print(Fore.RED + f"[!] Gagal baca cookie di {path}: {e}")
        return None, None

def login_dengan_cookie(path):
    sessionid, ds_user_id = baca_cookie_file(path)
    if not sessionid or not ds_user_id:
        return None, None

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36",
        "Referer": "https://www.instagram.com/",
        "X-Requested-With": "XMLHttpRequest"
    }

    cookies = {
        "sessionid": sessionid,
        "ds_user_id": ds_user_id
    }

    session = requests.Session()
    session.headers.update(headers)
    session.cookies.update(cookies)

    try:
        res = session.get("https://www.instagram.com/accounts/edit/")
        if res.status_code == 200 and '"username":"' in res.text:
            username = res.json().get("username", "unknown")
            print(Fore.GREEN + f"[✅] Login berhasil: {username}")
            return session, username
        else:
            print(Fore.RED + "[❌] Cookie invalid atau expired.")
            return None, None
    except Exception as e:
        print(Fore.RED + f"[!] Gagal akses Instagram: {e}")
        return None, None

def get_latest_post(session, target_username):
    try:
        res = session.get(f"https://www.instagram.com/{target_username}/")
        if res.status_code != 200:
            return None

        html = res.text
        soup = BeautifulSoup(html, "html.parser")
        for script in soup.find_all("script"):
            if 'window._sharedData =' in script.text:
                json_text = script.text.split(' = ', 1)[1].rstrip(';')
                import json
                data = json.loads(json_text)
                try:
                    media = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
                    if not media:
                        return None
                    return media[0]["node"]
                except:
                    return None
        return None
    except Exception as e:
        print(Fore.RED + f"⚠️ Gagal ambil postingan @{target_username}: {e}")
        return None

def auto_comment_loop(session, username, targets, comments, dummy_mode=False):
    posted = set()
    print(Fore.YELLOW + "\n⏳ Menunggu postingan baru...\n")
    printed = False

    while True:
        now = time.time()
        found = False

        for target in targets:
            media = get_latest_post(session, target.strip())
            if not media:
                continue

            media_id = media["id"]
            timestamp = media["taken_at_timestamp"]
            umur = now - timestamp

            if media_id in posted or umur < 30 or umur > 31:
                continue

            print(Fore.GREEN + f"✅ Postingan baru dari @{target} — umur: {int(umur)} detik")
            msg = random.choice(comments).strip()

            if dummy_mode:
                print(Fore.MAGENTA + f"💡 DUMMY: Tidak kirim → \"{msg}\"")
            else:
                try:
                    comment_url = f"https://www.instagram.com/web/comments/{media_id}/add/"
                    res = session.post(comment_url, data={"comment_text": msg})
                    if res.status_code == 200:
                        print(Fore.CYAN + f"💬 @{username}: Komentar terkirim ({int(umur)}s)")
                    elif res.status_code == 400:
                        print(Fore.RED + "🚫 Komentar ditolak (400) — Akun dibatasi?")
                        return False
                    else:
                        print(Fore.RED + f"❌ Gagal komentar: {res.status_code} — {res.text}")
                except Exception as e:
                    print(Fore.RED + f"❌ Gagal komentar: {e}")
            posted.add(media_id)
            found = True

        if not found:
            if not printed:
                print(Fore.YELLOW + "⏳ Menunggu postingan baru...", end='\r')
                printed = True
            time.sleep(0.6)
        else:
            printed = False
            time.sleep(random.randint(3, 6))
    return True

def main():
    clear_terminal()
    tampilkan_banner()

    lisensi = input("🔑 Masukkan kode lisensi: ")
    if not is_license_valid(lisensi):
        print(Fore.RED + "❌ Lisensi tidak valid.")
        sys.exit()

    dummy_mode = input("🔧 Aktifkan mode dummy (komentar tidak dikirim)? (y/n): ").lower() == 'y'

    accounts = load_accounts('Data')
    if not accounts:
        print(Fore.RED + "❌ Tidak ada akun di folder /Data.")
        return

    targets = []
    while not targets:
        targets = input("🎯 Username target (pisah dengan koma): ").split(',')

    comments = []
    while not comments:
        comments = input("💬 Komentar (pisah dengan |): ").split('|')

    for name, path in accounts:
        session, username = login_dengan_cookie(path)
        if not session:
            continue
        sukses = auto_comment_loop(session, username, targets, comments, dummy_mode)
        if sukses:
            print(Fore.GREEN + "✅ Semua komentar berhasil dikirim.")
            break
    else:
        print(Fore.RED + "❌ Semua akun gagal login atau dibatasi.")

if __name__ == '__main__':
    main()
