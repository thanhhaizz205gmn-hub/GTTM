"""
===================================================================================
DỰ ÁN DIGITAL TWIN GA TÀU CAO TỐC - BỘ MÔ PHỎNG CẢM BIẾN IOT KỊCH BẢN THỰC TẾ
Tệp: mock_iot_sensor.py
Mô tả: Mô phỏng chu kỳ lịch trình 12 bước tách biệt Tàu 1 và Tàu 2:
   - Giai đoạn A (Bước 1): Ga vắng (Màu Xanh, ~80 khách)
   - Giai đoạn B (Bước 2-4): TÀU 1 CẬP BẾN -> Dừng đón khách -> Tàu 1 rời đi (Tăng lên ~850 khách, Vàng/Cam)
   - Giai đoạn C (Bước 5-7): Khoảng nghỉ giữa 2 chuyến (Ga hạ nhiệt về Xanh)
   - Giai đoạn D (Bước 8-10): TÀU 2 CẬP BẾN (Làn đối diện) -> Dừng đón khách -> Quá tải đỉnh điểm (~1.450 khách, Đỏ rực)
   - Giai đoạn E (Bước 11-12): Tàu 2 rời đi -> Khách tỏa ra sảnh -> Hạ nhiệt dần
Khởi chạy: python mock_iot_sensor.py
===================================================================================
"""

import os
import random
import sys
import time
from datetime import datetime, timezone, timedelta

# Định nghĩa múi giờ Việt Nam (GMT+7)
VN_TZ = timezone(timedelta(hours=7))

# Cấu hình mã hóa UTF-8 cho console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import requests
except ImportError:
    print("[LỖI] Thiếu thư viện 'requests'. Vui lòng cài đặt: pip install requests")
    sys.exit(1)

# =================================================================================
# 1. CẤU HÌNH KẾT NỐI SUPABASE REST API
# =================================================================================
SUPABASE_URL = "https://dajourmarbthhfmkkjqs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRham91cm1hcmJ0aGhmbWtranFzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4ODIwMjgxMiwiZXhwIjoyMTAzNzc4ODEyfQ.C449gImZ3nRflRBoQ0PiPNdiXdQdzocOKG28Zn0gJho"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# =================================================================================
# 2. ĐỊNH NGHĨA KỊCH BẢN 12 BƯỚC THỜI GIAN THỰC (REALISTIC TIMELINE)
# =================================================================================
TIMELINE_STEPS = [
    # GIAI ĐOẠN 1: Ga yên tĩnh ban đầu
    {"step": 1, "train_id": "NONE", "pax_min": 60, "pax_max": 100, "temp_min": 24.5, "temp_max": 26.0, "hum_min": 52, "hum_max": 58, "desc": "🟢 [1/12] Ga yên tĩnh | Không có tàu | Khách thưa thớt"},
    
    # GIAI ĐOẠN 2: TÀU 1 VÀO GA & ĐÓN KHÁCH (Làn 1)
    {"step": 2, "train_id": "TRAIN_1", "pax_min": 450, "pax_max": 600, "temp_min": 27.0, "temp_max": 28.5, "hum_min": 58, "hum_max": 65, "desc": "🟡 [2/12] TÀU 1 CẬP BẾN | Đang tiến vào ke ga số 1 | Khách bắt đầu tăng"},
    {"step": 3, "train_id": "TRAIN_1", "pax_min": 800, "pax_max": 950, "temp_min": 30.0, "temp_max": 32.5, "hum_min": 65, "hum_max": 72, "desc": "🟡 [3/12] TÀU 1 DỪNG Ở GA | Khách ùa xuống ke ga 1 đông đúc | Tải nhiệt tăng"},
    {"step": 4, "train_id": "TRAIN_1_LEAVING", "pax_min": 650, "pax_max": 750, "temp_min": 29.0, "temp_max": 30.5, "hum_min": 62, "hum_max": 68, "desc": "🟡 [4/12] TÀU 1 RỜI GA | Khách tỏa vào sảnh trung tâm ga | Tải bắt đầu giảm"},
    
    # GIAI ĐOẠN 3: KHOẢNG NGHỈ GIỮA 2 CHUYẾN TÀU (Để quan sát rõ sự thay đổi)
    {"step": 5, "train_id": "NONE", "pax_min": 250, "pax_max": 350, "temp_min": 26.5, "temp_max": 28.0, "hum_min": 55, "hum_max": 60, "desc": "🟢 [5/12] Khách tỏa đi dần | Ga bắt đầu vắng lại"},
    {"step": 6, "train_id": "NONE", "pax_min": 80, "pax_max": 120, "temp_min": 25.0, "temp_max": 26.0, "hum_min": 50, "hum_max": 56, "desc": "🟢 [6/12] Khoảng nghỉ yên tĩnh | Cả 2 ke ga đều vắng"},
    {"step": 7, "train_id": "NONE", "pax_min": 70, "pax_max": 110, "temp_min": 24.8, "temp_max": 25.8, "hum_min": 50, "hum_max": 55, "desc": "🟢 [7/12] Chuẩn bị đón tàu 2 vào làn đối diện..."},

    # GIAI ĐOẠN 4: TÀU 2 VÀO GA & QUÁ TẢI ĐỈNH ĐIỂM (Làn 2 - Cao điểm)
    {"step": 8, "train_id": "TRAIN_2", "pax_min": 700, "pax_max": 900, "temp_min": 33.0, "temp_max": 35.5, "hum_min": 70, "hum_max": 78, "desc": "🟠 [8/12] TÀU 2 CẬP BẾN | Tiến vào ke ga đối diện (Làn 2) | Khách tăng vọt"},
    {"step": 9, "train_id": "TRAIN_2", "pax_min": 1350, "pax_max": 1550, "temp_min": 38.5, "temp_max": 42.0, "hum_min": 85, "hum_max": 95, "desc": "🔥 [9/12] TÀU 2 DỪNG Ở GA | CAO ĐIỂM QUÁ TẢI (ĐỎ RỰC) | CẢNH BÁO HVAC > 80%"},
    {"step": 10, "train_id": "TRAIN_2_LEAVING", "pax_min": 1050, "pax_max": 1200, "temp_min": 36.0, "temp_max": 38.0, "hum_min": 78, "hum_max": 85, "desc": "🔥 [10/12] TÀU 2 RỜI GA | Khách chật kín sảnh đón | Duy trì cảnh báo"},

    # GIAI ĐOẠN 5: TÀU 2 ĐI XA & HẠ NHIỆT VỀ BÌNH THƯỜNG
    {"step": 11, "train_id": "NONE", "pax_min": 400, "pax_max": 550, "temp_min": 28.0, "temp_max": 30.0, "hum_min": 60, "hum_max": 65, "desc": "🟡 [11/12] Khách tỏa ra các cửa thoát hiểm | Tải hạ nhiệt dần"},
    {"step": 12, "train_id": "NONE", "pax_min": 90, "pax_max": 140, "temp_min": 25.0, "temp_max": 26.5, "hum_min": 52, "hum_max": 58, "desc": "🟢 [12/12] Ga trở lại bình thường | Kết thúc chu kỳ"}
]

print("=" * 85)
print("  🚄 BỘ MÔ PHỎNG LỊCH TRÌNH DIGITAL TWIN GA TÀU CAO TỐC (CHU KỲ 12 BƯỚC CÁCH QUÃNG)")
print("  Quy trình: Tàu 1 đến -> Dừng -> Rời đi -> Nghỉ yên tĩnh -> Tàu 2 đến -> Quá tải Đỏ -> Tàu 2 đi")
print(f"  Mục tiêu REST API: {SUPABASE_URL}")
print("  Nhấn Ctrl + C để dừng.")
print("=" * 85)

step_idx = 0

try:
    while True:
        current_cfg = TIMELINE_STEPS[step_idx]
        now_str = datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S")
        timestamp_iso = datetime.now(VN_TZ).isoformat()

        temp = round(random.uniform(current_cfg["temp_min"], current_cfg["temp_max"]), 2)
        humidity = round(random.uniform(current_cfg["hum_min"], current_cfg["hum_max"]), 2)
        passenger_count = random.randint(current_cfg["pax_min"], current_cfg["pax_max"])
        train_id = current_cfg["train_id"]

        weather_payload = {"temp": temp, "humidity": humidity}
        density_payload = {
            "timestamp": timestamp_iso,
            "train_id": train_id,
            "passenger_count": passenger_count
        }

        try:
            res_w = requests.post(f"{SUPABASE_URL}/rest/v1/weather_logs", headers=HEADERS, json=weather_payload, timeout=3)
            res_d = requests.post(f"{SUPABASE_URL}/rest/v1/passenger_density_logs", headers=HEADERS, json=density_payload, timeout=3)

            if res_w.status_code in [200, 201] and res_d.status_code in [200, 201]:
                print(f"[{now_str}] {current_cfg['desc']} ➔ Nhiệt: {temp:4.1f}°C | Độ ẩm: {humidity:4.1f}% | Khách: {passenger_count:4d} ng | TrainID: {train_id}")
            else:
                print(f"[{now_str}] [LỖI HTTP] Weather: {res_w.status_code}, Density: {res_d.status_code}")

        except Exception as err:
            print(f"[{now_str}] [LỖI KẾT NỐI] {err}")

        # Tăng bước kịch bản tiếp theo
        step_idx = (step_idx + 1) % len(TIMELINE_STEPS)

        # Nghỉ 3 giây mỗi bước để người xem trên Web kịp quan sát tàu chuyển động và Heatmap đổi màu
        time.sleep(3)

except KeyboardInterrupt:
    print("\n" + "=" * 85)
    print("  🛑 ĐÃ DỪNG BỘ MÔ PHỎNG IOT AN TOÀN.")
    print("=" * 85)
