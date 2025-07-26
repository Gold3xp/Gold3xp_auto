from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, FeedbackRequired, PleaseWaitFewMinutes
from colorama import Fore, init
import time, random, os, sys
from utils.license_check import is_license_valid
from utils.tools import clear_terminal
from utils.banner import tampilkan_banner

init(autoreset=True)

def load_file_lines(path):
    if not os.path.exists(path):
        print(Fore.RED + f"❌ File tidak ditemukan: {path}")
        return []
    lines = [l.strip() for l in open(path) if l.strip()]
    if not lines:
        print(Fore.RED + f"❌ File kosong: {path}")
    return lines

def load_accounts(base='Data'):
    akuns = []
    for name in os.listdir(base):
        d = os.path.join(base, name)
        if os.path.isdir(d):
            akuns.append((name, d))
    return akuns

def login_dengan_cookie(account_path):
    ck = os.path.join(account_path, 'cookie.txt')
    usr = os.path.join(account_path, 'user.txt')
    sessionid = ''
    username = ''
    if os.path.exists(ck) and os.path.exists(usr):
        sessionid = open(ck).read().strip()
        username = open(usr).read().strip()
    if not sessionid or not username:
        print(Fore.RED + f"❌ sessionid/user kosong di {account_path}")
        return None

    proxies = load_file_lines(os.path.join(account_path, 'Proxy.txt')) \
            + load_file_lines(os.path.join(account_path, 'Proxy2.txt'))
    uas = load_file_lines(os.path.join(account_path, 'Ua.txt')) \
          + load_file_lines(os.path.join(account_path, 'User-agents.txt'))
    
    proxy = random.choice(proxies) if proxies else None
    ua = random.choice(uas) if uas else None

    if proxy and not proxy.startswith("http"):
        print(Fore.YELLOW + f"⚠️ Format proxy tidak valid, diabaikan: {proxy}")
        proxy = None

    print(Fore.CYAN + f"🔐 Login akun `{username}` — proxy: {proxy}, UA: {ua}")
    cl = Client()
    if proxy:
        cl.set_proxy(proxy)
    if ua:
        cl.headers.update({'User-Agent': ua})

    try:
        cl.login_by_sessionid(sessionid)
        cl.get_timeline_feed()
        print(Fore.GREEN + f"✅ Login sukses: {username}\n")
        cl.username_login = username  # Simpan nama untuk digunakan nanti
        return cl
    except Exception as e:
        print(Fore.RED + f"❌ Gagal login {username}: {e}")
        return None

def auto_comment_loop(cl, targets, comments):
    sudah = set()
    print("\n🚀 Auto-comment aktif. Menunggu postingan baru…\n")
    while True:
        now = time.time()
        ada = False
        for u in targets:
            try:
                uid = cl.user_id_from_username(u)
                medias = cl.user_medias(uid, amount=1)
                if not medias:
                    continue
                m = medias[0]
                umur = now - m.taken_at.timestamp()
                if m.id in sudah:
                    continue
                if 30 <= umur < 32:
                    print(Fore.GREEN + f"🆕 Postingan baru dari @{u} — umur {int(umur)} detik")
                    msg = random.choice(comments)
                    try:
                        cl.media_comment(m.id, msg)
                        print(Fore.CYAN + f"💬 @{cl.username_login}: Komentar dikirim pada detik ke-{int(umur)}")
                        sudah.add(m.id)
                        ada = True
                    except (FeedbackRequired, ChallengeRequired, PleaseWaitFewMinutes):
                        print(Fore.RED + "🚫 Akun dibatasi — pindah akun")
                        return False
                    except Exception as e:
                        print(Fore.RED + f"❌ Gagal komentar: {e}")
            except Exception:
                continue
        if not ada:
            print(Fore.YELLOW + "⏳ Menunggu postingan baru...")
            time.sleep(0.6)  # Lebih cepat agar tidak telat
        else:
            time.sleep(random.randint(3, 6))
    return True

def main():
    clear_terminal()
    tampilkan_banner()
    if not is_license_valid(input("🔑 Masukkan kode lisensi: ")):
        print(Fore.RED + "❌ Lisensi tidak valid")
        sys.exit()

    accounts = load_accounts('Data')
    if not accounts:
        print(Fore.RED + "❌ Tidak ditemukan folder akun dalam Data/")
        return

    while True:
        a = input("🎯 Masukkan target (username1,username2,…): ")
        targets = [i.strip() for i in a.split(',') if i.strip()]
        if targets:
            break
    while True:
        c = input("💬 Masukkan komentar (pisah dengan '|'): ")
        comments = [i.strip() for i in c.split('|') if i.strip()]
        if comments:
            break

    for name, path in accounts:
        cl = login_dengan_cookie(path)
        if not cl:
            continue
        sukses = auto_comment_loop(cl, targets, comments)
        try:
            cl.logout()
            print(Fore.GREEN + "🔒 Logout akun berhasil.\n")
        except:
            pass
        if sukses:
            print(Fore.GREEN + "✅ Semua komentar terkirim — selesai.")
            break
    else:
        print(Fore.RED + "❌ Semua akun dibatasi atau gagal login. Program berhenti.")

if __name__ == '__main__':
    main()
