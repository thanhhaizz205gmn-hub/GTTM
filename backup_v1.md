# 📌 HƯỚNG DẪN CẤU HÌNH & LƯU TRỮ DỰ ÁN — BACKUP V1
**Ngày khởi tạo:** 29/09/2026 | **Tên phiên bản:** `backup_v1`  
**Dự án:** Digital Twin Ga Đường Sắt Cao Tốc Hà Nội (Tối ưu năng lượng HVAC bằng AI)

---

## 🗂️ 1. MÔ TẢ TỔNG QUAN PHIÊN BẢN BACKUP V1
Phiên bản `backup_v1` đã hoàn thiện 100% các tính năng theo yêu cầu đồ án:
1. **Mô hình AI ML:** Pipeline học máy LightGBM/StandardScaler (`digital_twin_hvac_model.pkl`) dự báo công suất HVAC tối ưu.
2. **FastAPI Backend (v2.0):** Hỗ trợ đầy đủ các endpoint dự báo tức thời, dự báo chuỗi 30-60 phút, thông gió, chiếu sáng, và quy đổi kWh tích lũy. Hỗ trợ song song cả route gốc và route alias `/api/...` cho WebGL.
3. **Màn hình Tích hợp Dual Split-Screen Dashboard (`templates/dashboard.html`):** Cho phép xem mượt mà mô hình 3D Unity WebGL trực tiếp song song với các biểu đồ Chart.js và bộ giả lập kịch bản IoT.
4. **Unity 6 WebGL Build:** Đã xuất bản và chạy mượt trên trình duyệt web tại đường dẫn `Build_Web/`.
5. **n8n & Supabase Real-Time Sync:** n8n pipeline tự động kéo thời tiết Hanoi mỗi 15 phút, `mock_iot_sensor.py` cập nhật mật độ khách mỗi 3 giây.

---

## ⚙️ 2. CẤU HÌNH BUILD CẦN THIẾT TRONG UNITY 6 (UNITY SETTINGS)

### 📌 A. Cấu hình Build Profile (Build Settings)
* **Platform:** `Web` (WebGL).
* **Target Folder xuất file:** `d:\Đồ Án GTTM\Build_Web`
* **Scene List:** `GTTM` (Scene chính).

### 📌 B. Cấu hình Player Settings (Publishing Settings)
* **Compression Format:** `Gzip` (Phương thức nén chuẩn cho WebGL nhẹ và tải nhanh).
* **Decompression Fallback:** `Enabled` (Tích chọn để trình duyệt tự giải nén nếu máy chủ không hỗ trợ header).
* **Code Optimization:** `Runtime Speed`.

---

## 🚀 3. LỆNH KHỞI CHẠY HỆ THỐNG (COMMAND LINE RUNNERS)

### 1️⃣ Khởi chạy bằng Docker Compose (Đóng gói 4 Containers tự động kết nối Cloudflare Tunnel cho Domain `gamification.ink`):
```bash
docker-compose up -d --build
```
* **Container 1 (`digital_twin_app`):** FastAPI AI Backend (`port 8000`).
* **Container 2 (`digital_twin_mock_sensor`):** Chạy ngầm `mock_iot_sensor.py` đẩy dữ liệu giả lập vào Supabase.
* **Container 3 (`digital_twin_nginx`):** Nginx Reverse Proxy (`port 80`), phục vụ tên miền **`gamification.ink`** & Unity WebGL gzip assets.
* **Container 4 (`digital_twin_cloudflared`):** Chạy Cloudflare Tunnel tự động nối ống hầm về `gamification.ink` mà không cần cài đặt `.exe` thủ công trên Windows!


### 2️⃣ Khởi chạy thủ công (Dev mode):
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
* **Trang Dashboard Tích Hợp (3D + Biểu đồ):** `http://gamification.ink` hoặc `http://localhost:8000/dashboard`
* **API Documentation (Swagger UI):** `http://localhost:8000/docs`




### 2️⃣ Khởi chạy Bộ Mô Phỏng IoT Cảm Biến Real-Time:
Mở một cửa sổ Terminal mới:
```bash
python mock_iot_sensor.py
```
*(Cập nhật dữ liệu thời tiết & hành khách theo 12 bước kịch bản vào Supabase mỗi 3 giây)*

### 3️⃣ Chạy Kiểm Thử Tải Cao (Stress-Test Benchmark):
```bash
python stress_test.py
```
*(Giả lập 20 luồng đồng thời, 200 requests quá tải và xuất báo cáo ra `stress_test_report.md`)*

---

## 🔗 4. DANH SÁCH ENDPOINTS API CHÍNH (`app.py`)

| Endpoint | Method | Mô tả | Đường dẫn Alias cho WebGL |
|----------|--------|-------|--------------------------|
| `/predict` | POST | Dự báo công suất HVAC tức thời từ AI Model | `/api/predict` |
| `/predict/forecast` | POST | Dự báo chuỗi 30-60 phút tới (5 min/step) | `/api/predict/forecast` |
| `/predict/ventilation` | POST | Dự báo công suất quạt thông gió & CO₂ risk | `/api/predict/ventilation` |
| `/predict/lighting` | POST | Dự báo công suất chiếu sáng thông minh | `/api/predict/lighting` |
| `/energy/stats` | GET | Thống kê kWh tích lũy AI vs Truyền thống | `/api/energy/stats` |
| `/energy/history` | GET | Chuỗi lịch sử tải để vẽ biểu đồ Chart.js | `/api/energy/history` |
| `/dashboard` | GET | Giao diện Web Analytics & 3D WebGL Dashboard | N/A |
| `/unity_build/{path}` | GET | Phục vụ file tĩnh Unity WebGL (`.gz` headers) | N/A |

---

## 🔑 5. THÔNG TIN CẤU HÌNH SUPABASE DATABASE

* **Supabase Project URL:** `https://dajourmarbthhfmkkjqs.supabase.co`
* **Các bảng dữ liệu:**
  * `weather_logs`: Lưu vết nhiệt độ `temp` (°C) và độ ẩm `humidity` (%).
  * `passenger_density_logs`: Lưu vết `passenger_count` (người) và `train_id`.
  * `train_schedules`: Lưu lịch trình tàu cao tốc vào/ra ga.

---

## 🛠️ 6. HƯỚNG DẪN XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

1. **Màn hình 3D trên Dashboard bị đứng yên / không đổi thông số:**
   * **Nguyên nhân:** Trình duyệt lưu cache file `.wasm.gz` cũ.
   * **Khắc phục:** Mở `http://localhost:8000/dashboard` và nhấn **`Ctrl + F5`** (hoặc `Ctrl + Shift + R`).
2. **Không thấy nút Build Web trong Unity 6:**
   * **Khắc phục:** Vào `Build Profiles` ➔ Chọn `Web` ➔ Bấm `Install with Unity Hub` để cài module WebGL Support.
3. **Cửa sổ Unity cảnh báo "Missing Project ID":**
   * **Khắc phục:** Bấm `Yes` để tiếp tục, không ảnh hưởng đến build.
