import os
import requests
import time
try:
    from pystyle import Colors, Colorate, Write, Center, Add, Box
except:
    os.system("pip install pystyle")
    from pystyle import Colors, Colorate, Write, Center, Add, Box

CONFIG_FILE = 'ttc_config.txt'
FACEBOOK_IDS_FILE = 'facebook_ids.txt'

def save_config(token):
    with open(CONFIG_FILE, 'w') as f:
        f.write(f'{token}\n')

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            lines = f.read().splitlines()
            if len(lines) >= 1:
                return lines[0]
    return None

def get_user_config():
    token = load_config()
    while True:
        if token:
            print(Colors.yellow + 'Đã tìm thấy access_token cũ:')
            print(Colors.green + '1. Dùng lại access_token cũ')
            print(Colors.red + '2. Nhập access_token mới')
            chon = input('Chọn (1/2): ').strip()
            if chon == '1':
                break
            elif chon == '2':
                token = input('Nhập TTC_TOKEN: ').strip()
                save_config(token)
                break
            else:
                print(Colors.red + 'Chỉ nhập 1 hoặc 2!')
        else:
            token = input('Nhập TTC_TOKEN: ').strip()
            save_config(token)
            break
    return token

def select_facebook_id():
    ids = []
    if os.path.exists(FACEBOOK_IDS_FILE):
        with open(FACEBOOK_IDS_FILE, 'r') as f:
            for line in f:
                if '|' in line:
                    parts = line.strip().split('|')
                    ids.append((parts[0], parts[1]))
                elif line.strip():
                    ids.append((line.strip(), ''))
    if ids:
        print(Colors.yellow + 'Danh sách nick Facebook đã lưu:')
        for idx, (fb_id, fb_name) in enumerate(ids, 1):
            print(f'{Colors.green}{idx}. {Colors.cyan}{fb_name} {Colors.light_gray}(ID: {fb_id})')
        print(f'{Colors.green}{len(ids)+1}. {Colors.red}Nhập nick mới')
        while True:
            try:
                chon = int(Write.Input('Chọn số thứ tự nick Facebook hoặc nhập số mới:', Colors.green_to_yellow, interval=0.0025))
                if 1 <= chon <= len(ids):
                    return ids[chon-1][0]
                elif chon == len(ids)+1:
                    break
                else:
                    print(Colors.red + 'Chỉ chọn số trong danh sách!')
            except:
                print(Colors.red + 'Chỉ chọn số trong danh sách!')
    # Nhập nick mới
    while True:
        fb_id = Write.Input('Nhập ID Facebook:', Colors.green_to_yellow, interval=0.0025)
        if fb_id:
            break
    fb_name = Write.Input('Nhập tên nick Facebook:', Colors.green_to_yellow, interval=0.0025)
    with open(FACEBOOK_IDS_FILE, 'a') as f:
        f.write(f'{fb_id}|{fb_name}\n')
    return fb_id

def get_delay_and_maxjob():
    while True:
        try:
            delay = int(Write.Input('Nhập thời gian delay giữa các job (giây, >=2):', Colors.green_to_yellow, interval=0.0025))
            if delay >= 2:
                break
            else:
                print(Colors.red + 'Delay tối thiểu là 2 giây!')
        except:
            print(Colors.red + 'Vui lòng nhập số nguyên!')
    while True:
        try:
            max_job = int(Write.Input('Dừng lại khi làm được số nhiệm vụ là (>=5):', Colors.green_to_yellow, interval=0.0025))
            if max_job >= 5:
                break
            else:
                print(Colors.red + 'Tối thiểu là 5!')
        except:
            print(Colors.red + 'Vui lòng nhập số nguyên!')
    while True:
        try:
            batch = int(Write.Input('Nhận xu sau bao nhiêu nhiệm vụ? (mặc định 10):', Colors.green_to_yellow, interval=0.0025) or 10)
            if batch >= 1:
                break
            else:
                print(Colors.red + 'Tối thiểu là 1!')
        except:
            print(Colors.red + 'Vui lòng nhập số nguyên!')
    return delay, max_job, batch

LOGIN_URL = 'https://tuongtaccheo.com/logintoken.php'
GET_JOB_URL = "https://tuongtaccheo.com/kiemtien/likepostvipcheo/getpost.php"
RECEIVE_XU_URL = "https://tuongtaccheo.com/kiemtien/likepostvipcheo/nhantien.php"

headers = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest"
}

def login_ttc(token):
    data = {'access_token': token}
    try:
        resp = requests.post(LOGIN_URL, data=data)
        res = resp.json()
        if res.get('status') == 'success':
            print(Colors.green + f"Đăng nhập thành công! User: {res['data']['user']} | Số dư: {res['data']['sodu']}")
            return True
        else:
            print(Colors.red + 'Access token không hợp lệ!')
            return False
    except Exception as e:
        print(Colors.red + 'Lỗi khi đăng nhập:', e)
        return False

def get_job(token):
    data = {"access_token": token}
    resp = requests.post(GET_JOB_URL, headers=headers, data=data)
    try:
        job = resp.json()
        if "id" in job:
            print(Colors.cyan + f"Nhận nhiệm vụ: {job['id']}")
            return job['id'], job.get('link', '')
        else:
            print(Colors.yellow + "Không có nhiệm vụ mới!")
            return None, None
    except Exception as e:
        print(Colors.red + "Lỗi khi lấy nhiệm vụ:", e)
        return None, None

def fake_like_facebook(link):
    print(Colors.purple + f"(Giả lập) Like bài viết: {link}")
    time.sleep(2)
    return True

def receive_xu(job_id, token):
    data = {"id": job_id, "access_token": token}
    resp = requests.post(RECEIVE_XU_URL, headers=headers, data=data)
    try:
        result = resp.json()
        mess = result.get("mess", str(result))
        print(Colors.green + "Kết quả nhận xu:", mess)
        return mess
    except Exception as e:
        print(Colors.red + "Lỗi khi nhận xu:", e)
        return None

def main():
    banner = r'''
████████╗██████╗ ███████╗
╚══██╔══╝██╔══██╗██╔════╝
   ██║   ██║  ██║███████╗
   ██║   ██║  ██║╚════██║
   ██║   ██████╔╝███████║
   ╚═╝   ╚═════╝ ╚══════╝
'''
    print(Colorate.Horizontal(Colors.yellow_to_red, Center.XCenter(banner)))
    print(Colors.red + Center.XCenter(Box.DoubleCube("Tool TTC Facebook auto nhiệm vụ")))
    while True:
        token = get_user_config()
        if not login_ttc(token):
            continue
        fb_id = select_facebook_id()
        delay, max_job, batch = get_delay_and_maxjob()
        dem_tong = 0
        jobs_buffer = []
        while True:
            job_id, link = get_job(token)
            if not job_id:
                print(Colors.yellow + "Hết nhiệm vụ, thử lại sau 30 giây...")
                time.sleep(30)
                continue
            if fake_like_facebook(link):
                jobs_buffer.append(job_id)
                dem_tong += 1
                print(Colors.cyan + f"Đã làm {dem_tong}/{max_job} nhiệm vụ! (Chưa nhận xu: {len(jobs_buffer)})")
            if len(jobs_buffer) >= batch or dem_tong >= max_job:
                for jid in jobs_buffer:
                    mess = receive_xu(jid, token)
                    if mess and "+0 Xu" in mess:
                        print(Colors.red + "Nick Facebook bị lỗi hoặc bị chặn! Hãy chọn nick khác.")
                        print(Colors.yellow + "1. Đổi nick Facebook và chạy tiếp")
                        print(Colors.red + "2. Kết thúc chương trình")
                        while True:
                            chon = input('Chọn (1/2): ').strip()
                            if chon == '1':
                                break  # Quay lại đầu vòng while True ngoài cùng
                            elif chon == '2':
                                print(Colors.red + 'Kết thúc!')
                                return
                            else:
                                print(Colors.red + 'Chỉ nhập 1 hoặc 2!')
                        break
                jobs_buffer = []
                if mess and "+0 Xu" in mess:
                    break  # Quay lại đầu vòng while True ngoài cùng để chọn nick khác
            if dem_tong >= max_job:
                print(Colors.green + f"Hoàn thành {max_job} nhiệm vụ!")
                print(Colors.yellow + "1. Chạy tiếp với cấu hình hiện tại")
                print(Colors.cyan + "2. Đổi cấu hình (token/delay/số job)")
                print(Colors.red + "3. Kết thúc chương trình")
                while True:
                    chon = input('Chọn (1/2/3): ').strip()
                    if chon == '1':
                        dem_tong = 0
                        break
                    elif chon == '2':
                        break  # Quay lại đầu vòng while True ngoài cùng
                    elif chon == '3':
                        print(Colors.red + 'Kết thúc!')
                        return
                    else:
                        print(Colors.red + 'Chỉ nhập 1, 2 hoặc 3!')
                if chon == '2':
                    break  # Quay lại đầu vòng while True ngoài cùng
            time.sleep(delay)

if __name__ == "__main__":
    main() 
