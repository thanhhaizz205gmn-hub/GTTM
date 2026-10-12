"""
===================================================================================
DỰ ÁN DIGITAL TWIN GA TÀU CAO TỐC HÀ NỘI - TỔNG HỢP DỮ LIỆU MÔ PHỎNG (BIG DATA)
Tệp: generate_hanoi_station_raw.py
Mô tả: Sinh tập dữ liệu thô 2.000.000 dòng (hệ thống khí hậu 4 mùa Hà Nội + vận hành)
Đầu ra: hanoi_station_raw.csv (Dùng cho huấn luyện mô hình XGBoost & Tiền xử lý Big Data)
===================================================================================
"""

import sys
import time
import numpy as np
import pandas as pd

# Đảm bảo in tiếng Việt có dấu mượt mà trên Windows Console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def generate_hanoi_station_raw(
    output_filepath: str = "hanoi_station_raw.csv",
    num_rows: int = 2_000_000,
    random_seed: int = 42
):
    print("=======================================================================")
    print("  BẮT ĐẦU TỔNG HỢP DỮ LIỆU THÔ DIGITAL TWIN (2.000.000 DÒNG)")
    print("=======================================================================")
    start_total_time = time.time()
    
    # Thiết lập Random Seed để tái lập kết quả
    np.random.seed(random_seed)
    
    # -------------------------------------------------------------------------
    # 1. TẠO CHUỖI THỜI GIAN (TIMESTAMP THEO TỪNG PHÚT ~ 3.8 NĂM)
    # -------------------------------------------------------------------------
    print(f"\n[BƯỚC 1/6] Khởi tạo chuỗi thời gian ({num_rows:,} phút từ 2022-01-01)...")
    t0 = time.time()
    dt_index = pd.date_range(start="2022-01-01 00:00:00", periods=num_rows, freq="1min")
    
    # Trích xuất các biến số thời gian dưới dạng mảng NumPy (Vectorized)
    day_of_year = dt_index.dayofyear.values          # Ngày trong năm (1 - 366)
    hour_float = dt_index.hour.values + dt_index.minute.values / 60.0  # Giờ thực (0.0 - 23.98)
    month = dt_index.month.values                    # Tháng trong năm (1 - 12)
    hour = dt_index.hour.values                      # Giờ nguyên (0 - 23)
    minute = dt_index.minute.values                  # Phút (0 - 59)
    print(f" -> Hoàn thành chuỗi thời gian trong {time.time() - t0:.2f} giây.")

    # -------------------------------------------------------------------------
    # 2. MÔ HÌNH HÓA NHIỆT ĐỘ HÀ NỘI (4 MÙA RÕ RỆT + CHU KỲ NGÀY ĐÊM)
    # -------------------------------------------------------------------------
    print("\n[BƯỚC 2/6] Mô phỏng nhiệt độ (°C) theo đặc trưng 4 mùa Hà Nội...")
    t0 = time.time()
    
    # Chu kỳ mùa trong năm: Đỉnh tháng 6-7 (~33°C), Đáy tháng 1-2 (~16°C)
    annual_temp_cycle = 24.5 + 8.5 * np.sin(2 * np.pi * (day_of_year - 110) / 365.25)
    
    # Biên độ dao động ngày đêm (Mùa hè/thu chênh lệch lớn hơn mùa đông/xuân)
    diurnal_amp = 3.5 + 1.5 * np.sin(2 * np.pi * (day_of_year - 60) / 365.25)
    
    # Chu kỳ nhiệt ngày đêm: Đỉnh nhiệt độ ~14:00, đáy nhiệt độ ~05:30 sáng
    daily_temp_cycle = -diurnal_amp * np.cos(2 * np.pi * (hour_float - 5.5) / 24.0)
    
    # Sóng áp khí quyển (Gió mùa đông bắc / Đợt nắng nóng kéo dài 4-7 ngày) + Nhiễu ngẫu nhiên
    synoptic_weather_wave = 2.2 * np.sin(2 * np.pi * np.arange(num_rows) / (1440 * 6.0))
    temp_noise = np.random.normal(0, 1.2, num_rows)
    
    temp_clean = np.round(annual_temp_cycle + daily_temp_cycle + synoptic_weather_wave + temp_noise, 2)
    print(f" -> Nhiệt độ trung bình: {np.mean(temp_clean):.2f}°C (Min: {np.min(temp_clean):.2f}°C, Max: {np.max(temp_clean):.2f}°C) [{time.time() - t0:.2f}s]")

    # -------------------------------------------------------------------------
    # 3. MÔ HÌNH HÓA ĐỘ ẨM KHÔNG KHÍ (MÙA NỒM ẨM XUÂN & HANH KHÔ ĐÔNG)
    # -------------------------------------------------------------------------
    print("\n[BƯỚC 3/6] Mô phỏng độ ẩm (%) tương quan khí hậu Hà Nội...")
    t0 = time.time()
    
    # Nền độ ẩm theo mùa: Mùa xuân (Tháng 2,3,4 - Nồm ẩm cực đại), Mùa đông (Hanh khô)
    seasonal_humidity_base = 77.0 + 13.0 * np.cos(2 * np.pi * (month - 3) / 12.0)
    
    # Tương quan nghịch với nhiệt độ trong ngày (Nhiệt độ buổi trưa tăng -> độ ẩm tương đối giảm)
    temp_anomaly = temp_clean - annual_temp_cycle
    humidity_noise = np.random.normal(0, 3.2, num_rows)
    
    humidity_raw = seasonal_humidity_base - 1.15 * temp_anomaly + humidity_noise
    humidity_clean = np.round(np.clip(humidity_raw, 38.0, 99.0), 2)
    print(f" -> Độ ẩm trung bình: {np.mean(humidity_clean):.2f}% (Min: {np.min(humidity_clean):.2f}%, Max: {np.max(humidity_clean):.2f}%) [{time.time() - t0:.2f}s]")

    # -------------------------------------------------------------------------
    # 4. MÔ HÌNH HÓA LƯU LƯỢNG HÀNH KHÁCH & XUNG TÀU ĐẾN/ĐI (PASSENGER DENSITY)
    # -------------------------------------------------------------------------
    print("\n[BƯỚC 4/6] Mô phỏng mật độ hành khách với xung tàu giờ cao điểm & thấp điểm...")
    t0 = time.time()
    
    # Khung giờ hoạt động của ga (05:00 - 23:00)
    is_operating_hours = (hour >= 5) & (hour < 23)
    # Giờ cao điểm (07:00 - 09:00 và 16:00 - 18:00)
    is_peak_hours = ((hour >= 7) & (hour < 9)) | ((hour >= 16) & (hour < 18))
    
    # Lưu lượng khách nền trong sảnh ga
    base_crowd = np.where(
        is_operating_hours,
        np.where(
            is_peak_hours,
            650 + 350 * np.sin(np.pi * (hour_float % 9) / 2.0),
            280 + 140 * np.sin(np.pi * (hour_float - 5) / 18.0)
        ),
        np.random.randint(0, 8, num_rows) # Ban đêm: chỉ có vài nhân viên kỹ thuật/bảo trì
    )
    
    # Xung tăng đột biến khi tàu đến/đi (Spike curve: Cao điểm 30 phút/chuyến, Thấp điểm 60 phút/chuyến)
    cycle_minutes = np.where(is_peak_hours, minute % 30, minute % 60)
    # Hành khách dồn ứ cao nhất tại phút thứ 25 (trước giờ tàu khởi hành)
    dist_to_peak_arrival = np.abs(cycle_minutes - 25)
    gaussian_spike = np.exp(-0.5 * (dist_to_peak_arrival / 4.2) ** 2)
    spike_amplitude = np.where(is_peak_hours, 900, 480)
    train_arrival_surge = np.where(is_operating_hours, gaussian_spike * spike_amplitude, 0)
    
    crowd_noise = np.random.normal(0, 25, num_rows)
    passenger_count_clean = np.clip(
        np.round(base_crowd + train_arrival_surge + crowd_noise).astype(int),
        0, 4000
    )
    print(f" -> Khách trung bình: {np.mean(passenger_count_clean):.0f} người (Max peak: {np.max(passenger_count_clean):,} người) [{time.time() - t0:.2f}s]")

    # -------------------------------------------------------------------------
    # 5. TÍNH TOÁN CÔNG SUẤT ĐIỀU HÒA HVAC (TARGET: HVAC_POWER 0 - 100%)
    # -------------------------------------------------------------------------
    print("\n[BƯỚC 5/6] Tính toán tải nhiệt phi tuyến và công suất HVAC (0 - 100%)...")
    t0 = time.time()
    
    # Điểm chuẩn tiện nghi nhiệt độ: 24.0°C, Độ ẩm chuẩn: 55.0%
    q_sensible = np.maximum(0, temp_clean - 24.0) * 2.85         # Tải nhiệt cảm (Sensible heat load)
    q_latent = np.maximum(0, humidity_clean - 55.0) * 0.42       # Tải ẩm (Latent dehumidification load)
    q_occupancy = (passenger_count_clean / 1000.0) * 18.5        # Tải nhiệt từ thân nhiệt hành khách (~120W/người)
    q_base = 8.0                                                 # Tải thông gió cơ sở & chiếu sáng thiết bị
    
    # Tổng tải làm mát yêu cầu
    total_thermal_load = q_sensible + q_latent + q_occupancy + q_base
    
    # Đường cong đáp ứng công suất máy nén phi tuyến (Sigmoid saturation curve)
    hvac_power_ideal = 100.0 / (1.0 + np.exp(-(total_thermal_load - 36.0) / 13.0))
    
    # Bổ sung nhiễu Gauss để mô hình ML không học công thức xác định hoàn hảo
    hvac_noise = np.random.normal(0, 2.5, num_rows)
    hvac_power_final = np.round(np.clip(hvac_power_ideal + hvac_noise, 0.0, 100.0), 2)
    print(f" -> Công suất HVAC trung bình: {np.mean(hvac_power_final):.2f}% (Min: {np.min(hvac_power_final):.2f}%, Max: {np.max(hvac_power_final):.2f}%) [{time.time() - t0:.2f}s]")

    # -------------------------------------------------------------------------
    # 6. TIÊM DỮ LIỆU BẤT THƯỜNG: 1% GIÁ TRỊ THIẾU (NAN) & 1% OUTLIERS DỊ THƯỜNG
    # -------------------------------------------------------------------------
    print("\n[BƯỚC 6/6] Tiêm 1% giá trị khuyết (NaN) và 1% dị thường ngoại lai (Outliers)...")
    t0 = time.time()
    
    num_nans = int(0.01 * num_rows)       # ~20,000 dòng khuyết
    num_outliers = int(0.01 * num_rows)   # ~20,000 dòng dị biệt
    
    # Chuyển đổi sang float để chứa NaN
    temp_corrupted = temp_clean.astype(float)
    humidity_corrupted = humidity_clean.astype(float)
    passenger_corrupted = passenger_count_clean.astype(float)
    
    # 6.1. Tiêm giá trị NaN (Missing Values)
    nan_idx_temp = np.random.choice(num_rows, size=num_nans, replace=False)
    temp_corrupted[nan_idx_temp] = np.nan
    
    nan_idx_hum = np.random.choice(num_rows, size=num_nans, replace=False)
    humidity_corrupted[nan_idx_hum] = np.nan
    
    nan_idx_pass = np.random.choice(num_rows, size=num_nans, replace=False)
    passenger_corrupted[nan_idx_pass] = np.nan
    
    # 6.2. Tiêm giá trị ngoại lai (Extreme Outliers)
    out_idx_temp = np.random.choice(num_rows, size=num_outliers, replace=False)
    temp_corrupted[out_idx_temp] = np.random.choice([150.0, -50.0, 999.0, -99.0, 125.5], size=num_outliers)
    
    out_idx_hum = np.random.choice(num_rows, size=num_outliers, replace=False)
    humidity_corrupted[out_idx_hum] = np.random.choice([200.0, -15.0, 150.0, 300.0, -5.0], size=num_outliers)
    
    out_idx_pass = np.random.choice(num_rows, size=num_outliers, replace=False)
    passenger_corrupted[out_idx_pass] = np.random.choice([-15.0, -999.0, 99999.0, -50.0, 88888.0], size=num_outliers)
    
    print(f" -> Đã tiêm {num_nans:,} NaNs và {num_outliers:,} Outliers trên từng thuộc tính [{time.time() - t0:.2f}s]")

    # -------------------------------------------------------------------------
    # 7. ĐÓNG GÓI VÀ XUẤT TẬP DỮ LIỆU RA FILE CSV (CHUNK STREAMING)
    # -------------------------------------------------------------------------
    print(f"\n[XUẤT DỮ LIỆU] Đang ghi tập dữ liệu ra tệp '{output_filepath}'...")
    t0 = time.time()
    
    df_raw = pd.DataFrame({
        "timestamp": dt_index.strftime("%Y-%m-%d %H:%M:%S"),
        "temp": temp_corrupted,
        "humidity": humidity_corrupted,
        "passenger_count": passenger_corrupted,
        "hvac_power": hvac_power_final
    })
    
    # Xuất file CSV phân khối (chunking) để tối ưu hóa bộ nhớ I/O
    chunk_size = 200_000
    df_raw.to_csv(output_filepath, index=False, chunksize=chunk_size)
    
    total_duration = time.time() - start_total_time
    print(f" -> Xuất file CSV thành công ({df_raw.shape[0]:,} dòng, {df_raw.shape[1]} cột) trong {time.time() - t0:.2f}s.")
    print("=======================================================================")
    print(f"  HOÀN THÀNH TOÀN BỘ TIẾN TRÌNH TRONG: {total_duration:.2f} GIÂY!")
    print("=======================================================================")
    
    # Hiển thị mẫu 10 dòng đầu tiên
    print("\n--- MẪU DỮ LIỆU XUẤT RA (10 DÒNG ĐẦU TIÊN) ---")
    print(df_raw.head(10).to_string(index=False))
    
    # Thống kê tình trạng giá trị thiếu (Missing values summary)
    print("\n--- THỐNG KÊ GIÁ TRỊ KHUYẾT THIẾU (NULL / NAN) ---")
    print(df_raw.isnull().sum())
    
    return df_raw


if __name__ == "__main__":
    generate_hanoi_station_raw(
        output_filepath="hanoi_station_raw.csv",
        num_rows=2_000_000,
        random_seed=42
    )
