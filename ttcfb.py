import os
import requests
import time
from bs4 import BeautifulSoup

# ====== Hàm lưu và đọc cấu hình ======
CONFIG_FILE = 'ttc_config.txt'
def save_config(token, phpsessid):
    with open(CONFIG_FILE, 'w') as f:
        f.write(f'{token}\n{phpsessid}')

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            lines = f.read().splitlines()
            if len(lines) >= 2:
                return lines[0], lines[1]
    return None, None

# ====== Đăng nhập bằng access_token ======
LOGIN_URL = 'https://tuongtaccheo.com/logintoken.php'
def login_ttc(token):
    data = {'access_token': token}
    try:
        resp = requests.post(LOGIN_URL, data=data)
        res = resp.json()
        if res.get('status') == 'success':
            print(f"Đăng nhập thành công! User: {res['data']['user']} | Số dư: {res['data']['sodu']}")
            return True
        else:
            print('Access token không hợp lệ!')
            return False
    except Exception as e:
        print('Lỗi khi đăng nhập:', e)
        return False

# ====== Hỏi thông tin cấu hình ======
def get_user_config():
    token, phpsessid = load_config()
    while True:
        if token and phpsessid:
            print('Đã tìm thấy cấu hình cũ:')
            print(f'1. Dùng lại token/PHPSESSID cũ')
            print(f'2. Nhập token/PHPSESSID mới')
            chon = input('Chọn (1/2): ').strip()
            if chon == '1':
                if login_ttc(token):
                    break
                else:
                    token = None
                    phpsessid = None
            elif chon == '2':
                token = input('Nhập TTC_TOKEN: ').strip()
                phpsessid = input('Nhập PHPSESSID: ').strip()
                if login_ttc(token):
                    save_config(token, phpsessid)
                    break
                else:
                    token = None
                    phpsessid = None
            else:
                print('Chỉ nhập 1 hoặc 2!')
        else:
            token = input('Nhập TTC_TOKEN: ').strip()
            phpsessid = input('Nhập PHPSESSID: ').strip()
            if login_ttc(token):
                save_config(token, phpsessid)
                break
            else:
                token = None
                phpsessid = None
    return token, phpsessid

# ====== Kiểm tra nick Facebook đã cấu hình và cho phép chọn ======
FACEBOOK_CONFIG_URL = 'https://tuongtaccheo.com/cauhinh/facebook.php'
def select_facebook_config(phpsessid):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"PHPSESSID={phpsessid}"
    }
    while True:
        try:
            resp = requests.get(FACEBOOK_CONFIG_URL, headers=headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            table = soup.find('table')
            if not table:
                print('Bạn chưa cấu hình nick Facebook nào!')
                print('Vui lòng vào https://tuongtaccheo.com/cauhinh/facebook.php để thêm nick Facebook trước khi chạy tool.')
                input('Nhấn Enter sau khi đã cấu hình nick Facebook để kiểm tra lại...')
                continue
            rows = table.find_all('tr')
            if len(rows) < 2:
                print('Bạn chưa cấu hình nick Facebook nào!')
                print('Vui lòng vào https://tuongtaccheo.com/cauhinh/facebook.php để thêm nick Facebook trước khi chạy tool.')
                input('Nhấn Enter sau khi đã cấu hình nick Facebook để kiểm tra lại...')
                continue
            fb_list = []
            for i, row in enumerate(rows[1:], 1):
                cols = row.find_all('td')
                if len(cols) >= 2:
                    fb_id = cols[0].text.strip()
                    fb_name = cols[1].text.strip()
                    fb_list.append((fb_id, fb_name))
            if not fb_list:
                print('Không lấy được nick Facebook nào!')
                continue
            if len(fb_list) == 1:
                print(f'Chỉ có 1 nick Facebook: {fb_list[0][1]} (ID: {fb_list[0][0]})')
                return fb_list[0][0]
            print('Danh sách nick Facebook đã cấu hình:')
            for idx, (fb_id, fb_name) in enumerate(fb_list, 1):
                print(f'{idx}. {fb_name} (ID: {fb_id})')
            while True:
                try:
                    chon = int(input(f'Chọn số thứ tự nick Facebook muốn chạy (1-{len(fb_list)}): '))
                    if 1 <= chon <= len(fb_list):
                        return fb_list[chon-1][0]
                    else:
                        print('Chỉ chọn số trong danh sách!')
                except:
                    print('Vui lòng nhập số!')
        except Exception as e:
            print('Lỗi khi kiểm tra nick Facebook:', e)
            input('Nhấn Enter để thử lại...')

# ====== Hàm hỏi delay và số job ======
def get_delay_and_maxjob():
    while True:
        try:
            delay = int(input('Nhập thời gian delay giữa các job (giây, >=2): '))
            if delay >= 2:
                break
            else:
                print('Delay tối thiểu là 2 giây!')
        except:
            print('Vui lòng nhập số nguyên!')
    while True:
        try:
            max_job = int(input('Dừng lại khi làm được số nhiệm vụ là (>=5): '))
            if max_job >= 5:
                break
            else:
                print('Tối thiểu là 5!')
        except:
            print('Vui lòng nhập số nguyên!')
    while True:
        try:
            batch = int(input('Nhận xu sau bao nhiêu nhiệm vụ? (mặc định 10): ') or 10)
            if batch >= 1:
                break
            else:
                print('Tối thiểu là 1!')
        except:
            print('Vui lòng nhập số nguyên!')
    return delay, max_job, batch

# ====== Các URL và hàm API ======
GET_JOB_URL = "https://tuongtaccheo.com/kiemtien/likepostvipcheo/getpost.php"
RECEIVE_XU_URL = "https://tuongtaccheo.com/kiemtien/likepostvipcheo/nhantien.php"

def get_headers(phpsessid):
    return {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": f"PHPSESSID={phpsessid}"
    }

def get_job(token, phpsessid):
    data = {"access_token": token}
    resp = requests.post(GET_JOB_URL, headers=get_headers(phpsessid), data=data)
    try:
        job = resp.json()
        if "id" in job:
            print(f"Nhận nhiệm vụ: {job['id']}")
            return job['id'], job.get('link', '')
        else:
            print("Không có nhiệm vụ mới!")
            return None, None
    except Exception as e:
        print("Lỗi khi lấy nhiệm vụ:", e)
        return None, None

def fake_like_facebook(link):
    print(f"(Giả lập) Like bài viết: {link}")
    time.sleep(2)
    return True

def receive_xu(job_id, phpsessid):
    data = {"id": job_id}
    resp = requests.post(RECEIVE_XU_URL, headers=get_headers(phpsessid), data=data)
    try:
        result = resp.json()
        print("Kết quả nhận xu:", result.get("mess", result))
    except Exception as e:
        print("Lỗi khi nhận xu:", e)

# ====== Đặt nick Facebook làm nick chạy ======
SET_FB_URL = 'https://tuongtaccheo.com/cauhinh/datnick.php'
def set_active_facebook(phpsessid, fb_id):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"PHPSESSID={phpsessid}"
    }
    data = {"id": fb_id}
    try:
        resp = requests.post(SET_FB_URL, headers=headers, data=data)
        res = resp.json()
        if res.get("status") == "success":
            print("Đặt nick Facebook thành công!")
            return True
        else:
            print("Lỗi khi đặt nick Facebook:", res)
            return False
    except Exception as e:
        print("Lỗi khi đặt nick Facebook:", e)
        return False

# ====== Main logic ======
def main():
    while True:
        token, phpsessid = get_user_config()
        # Hiển thị danh sách nick Facebook và cho chọn
        while True:
            fb_id = select_facebook_config(phpsessid)
            if set_active_facebook(phpsessid, fb_id):
                break
            else:
                print('Vui lòng chọn lại nick Facebook!')
        delay, max_job, batch = get_delay_and_maxjob()
        dem_tong = 0
        jobs_buffer = []
        while True:
            job_id, link = get_job(token, phpsessid)
            if not job_id:
                print("Hết nhiệm vụ, thử lại sau 30 giây...")
                time.sleep(30)
                continue
            if fake_like_facebook(link):
                jobs_buffer.append(job_id)
                dem_tong += 1
                print(f"Đã làm {dem_tong}/{max_job} nhiệm vụ! (Chưa nhận xu: {len(jobs_buffer)})")
            if len(jobs_buffer) >= batch or dem_tong >= max_job:
                for jid in jobs_buffer:
                    mess = None
                    try:
                        data = {"id": jid}
                        resp = requests.post(RECEIVE_XU_URL, headers=get_headers(phpsessid), data=data)
                        result = resp.json()
                        mess = result.get("mess", str(result))
                        print(f"Nhận xu cho job {jid}: {mess}")
                        if "+0 Xu" in mess:
                            print("Nick Facebook bị lỗi hoặc bị chặn! Hãy chọn nick khác.")
                            print("1. Đổi nick Facebook và chạy tiếp")
                            print("2. Kết thúc chương trình")
                            while True:
                                chon = input('Chọn (1/2): ').strip()
                                if chon == '1':
                                    break  # Quay lại đầu vòng while True ngoài cùng
                                elif chon == '2':
                                    print('Kết thúc!')
                                    return
                                else:
                                    print('Chỉ nhập 1 hoặc 2!')
                            break
                    except Exception as e:
                        print(f"Lỗi khi nhận xu cho job {jid}: {e}")
                jobs_buffer = []
                if "+0 Xu" in str(mess):
                    break  # Quay lại đầu vòng while True ngoài cùng để chọn nick khác
            if dem_tong >= max_job:
                print(f"Hoàn thành {max_job} nhiệm vụ!")
                print("1. Chạy tiếp với cấu hình hiện tại")
                print("2. Đổi cấu hình (token/PHPSESSID/delay/số job)")
                print("3. Kết thúc chương trình")
                while True:
                    chon = input('Chọn (1/2/3): ').strip()
                    if chon == '1':
                        dem_tong = 0
                        break
                    elif chon == '2':
                        break  # Quay lại đầu vòng while True ngoài cùng
                    elif chon == '3':
                        print('Kết thúc!')
                        return
                    else:
                        print('Chỉ nhập 1, 2 hoặc 3!')
                if chon == '2':
                    break  # Quay lại đầu vòng while True ngoài cùng
            time.sleep(delay)

if __name__ == "__main__":
    main() 
