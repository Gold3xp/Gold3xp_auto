import os, sys, random, time, requests
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, FeedbackRequired, PleaseWaitFewMinutes
from colorama import Fore, init
from utils.license_check import is_license_valid
from utils.tools import clear_terminal
from utils.banner import tampilkan_banner

init(autoreset=True)

def load_file_lines(path):
    if not os.path.exists(path):
        return []
    return [line.strip() for line in open(path) if line.strip()]

def cek_proxy(proxy, ua):
    try:
        response = requests.get(
            "https://www.instagram.com/",
            proxies={"http": proxy, "https": proxy},
            headers={"User-Agent": ua},
            timeout=5
        )
        return response.status_code == 200
    except:
        return False

def pilih_kombinasi_valid(proxies, uas):
    random.shuffle(proxies)
    random.shuffle(uas)
    for proxy in proxies:
        for ua in uas:
            if cek_proxy(proxy, ua):
                return proxy, ua
    return None, None

def load_accounts(folder='Data'):
    if not os.path.exists(folder):
        return []
    return [(n, os.path.join(folder, n)) for n in os.listdir(folder)
            if os.path.isdir(os.path.join(folder, n))]

def login_dengan_cookie(account_path):
    cookie_path = os.path.join(account_path, 'cookie.txt')
    user_path = os.path.join(account_path, 'user.txt')

    if not os.path.exists(cookie_path) or not os.path.exists(user_path):
        print(Fore.RED + f"❌ cookie.txt / user.txt tidak ditemukan di {account_path}")
        return None

    sessionid = open(cookie_path).read().strip()
    username = open(user_path).read().strip()

    if not sessionid or not username:
        print(Fore.RED + f"❌ sessionid atau username kosong di {account_path}")
        return None

    # Load proxy & user-agent
    proxy_files = ['Proxy.txt', 'Proxy2.txt']
    ua_files = ['Ua.txt', 'User-agents.txt']
    proxies, uas = [], []

    for f in proxy_files:
        proxies += load_file_lines(os.path.join(account_path, f))
    for f in ua_files:
        uas += load_file_lines(os.path.join(account_path, f))

    proxy, ua = pilih_kombinasi_valid(proxies, uas)

    print(Fore.CYAN + f"🔐 Login: {username} | Proxy: {proxy or 'None'} | UA: {ua or 'Default'}")

    cl = Client()
    if proxy:
        cl.set_proxy(proxy)
    if ua:
        cl.headers.update({'User-Agent': ua})

    try:
        cl.login_by_sessionid(sessionid)
        cl.get_timeline_feed()
        cl.username_login = username
        print(Fore.GREEN + f"✅ Login berhasil: {username}\n")
        return cl
    except Exception as e:
        print(Fore.RED + f"❌ Gagal login: {username} — {e}")
        return None

def auto_comment_loop(cl, targets, comments, dummy_mode=False):
    posted = set()
    print(Fore.YELLOW + "\n⏳ Menunggu postingan baru...\n")
    while True:
        now = time.time()
        found = False

        for target in targets:
            try:
                uid = cl.user_id_from_username(target.strip())
                media = cl.user_medias(uid, 1)
                if not media:
                    continue

                m = media[0]
                umur = now - m.taken_at.timestamp()
                if m.id in posted or umur < 30 or umur >= 32:
                    continue

                print(Fore.GREEN + f"✅ Postingan baru dari @{target.strip()} — umur: {int(umur)} detik")
                msg = random.choice(comments).strip()
                if dummy_mode:
                    print(Fore.MAGENTA + f"💡 DUMMY: Komentar tidak dikirim → \"{msg}\"")
                else:
                    try:
                        cl.media_comment(m.id, msg)
                        print(Fore.CYAN + f"💬 @{cl.username_login}: Komentar dikirim ({int(umur)}s)")
                    except (FeedbackRequired, ChallengeRequired, PleaseWaitFewMinutes):
                        print(Fore.RED + "🚫 Akun dibatasi. Pindah akun.")
                        return False
                    except Exception as e:
                        print(Fore.RED + f"❌ Gagal komentar: {e}")
                posted.add(m.id)
                found = True
            except:
                continue

        if not found:
            time.sleep(0.6)
        else:
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
        targets = input("🎯 Target username (pisah dengan koma): ").split(',')

    comments = []
    while not comments:
        comments = input("💬 Komentar (pisah dengan |): ").split('|')

    for name, path in accounts:
        cl = login_dengan_cookie(path)
        if not cl:
            continue
        sukses = auto_comment_loop(cl, targets, comments, dummy_mode)
        try:
            cl.logout()
            print(Fore.GREEN + "🔒 Logout berhasil.\n")
        except:
            pass
        if sukses:
            print(Fore.GREEN + "✅ Semua komentar terkirim.")
            break
    else:
        print(Fore.RED + "❌ Semua akun gagal login atau dibatasi.")

if __name__ == '__main__':
    main()
