"""
===================================================================================
DỰ ÁN DIGITAL TWIN GA TÀU CAO TỐC - FASTAPI BACKEND INFERENCE SERVICE
Tệp: app.py
Phiên bản: 2.0.0
Mô tả: Máy chủ API phục vụ suy luận mô hình học máy HVAC trong thời gian thực
Endpoints:
  GET  /                        → Health check + trạng thái model
  POST /predict                 → Dự báo HVAC tức thời
  POST /predict/forecast        → Dự báo chuỗi 30-60 phút tới
  POST /predict/ventilation     → Dự báo công suất thông gió
  POST /predict/lighting        → Dự báo công suất chiếu sáng
  GET  /energy/stats            → Thống kê kWh + so sánh AI vs Truyền thống
Khởi chạy: uvicorn app:app --host 0.0.0.0 --port 8000 --reload
===================================================================================
"""

import os
import sys
import math
from datetime import datetime, timedelta, timezone
from typing import Optional, List

# Định nghĩa múi giờ Việt Nam (GMT+7)
VN_TZ = timezone(timedelta(hours=7))

# Cấu hình mã hóa UTF-8 cho console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import joblib
import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Digital Twin HVAC AI Service",
    description=(
        "Dịch vụ suy luận AI đa năng cho Ga đường sắt cao tốc Hà Nội.\n\n"
        "Bao gồm: Dự báo HVAC tức thời, Chuỗi dự báo 30-60 phút, "
        "Thông gió, Chiếu sáng và Thống kê tiết kiệm điện năng."
    ),
    version="2.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================================================================================
# NẠP MÔ HÌNH
# =================================================================================
_candidates = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "digital_twin_hvac_model.pkl"),
    os.path.join(os.getcwd(), "digital_twin_hvac_model.pkl"),
    r"d:\Đồ Án GTTM\digital_twin_hvac_model.pkl",
]
MODEL_PATH = next((p for p in _candidates if os.path.exists(p)), _candidates[0])
print(f"[INFO] Đường dẫn model: {MODEL_PATH} | Tồn tại: {os.path.exists(MODEL_PATH)}", file=sys.stderr)

try:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Không tìm thấy tệp mô hình tại: {MODEL_PATH}")
    model_pipeline = joblib.load(MODEL_PATH)
    print(f"[KHỞI TẠO THÀNH CÔNG] Đã tải mô hình Machine Learning: {MODEL_PATH}", file=sys.stderr)
except Exception as e:
    print(f"[LỖI TẢI MÔ HÌNH] {e}", file=sys.stderr)
    model_pipeline = None

# Bộ tích lũy năng lượng phiên làm việc (in-memory)
_energy_log: List[dict] = []
HVAC_MAX_KW = 120.0        # Công suất điều hòa tối đa của ga (kW)
VENT_MAX_KW  = 45.0         # Công suất thông gió tối đa (kW)
LIGHT_MAX_KW = 30.0         # Công suất chiếu sáng tối đa (kW)
TRADITIONAL_HVAC_PCT = 85.0 # Giả định kịch bản truyền thống luôn chạy cố định 85%


# =================================================================================
# SCHEMAS PYDANTIC
# =================================================================================
class SensorDataInput(BaseModel):
    """Dữ liệu đầu vào từ cảm biến trạm hoặc Unity."""
    temp: float = Field(..., description="Nhiệt độ môi trường (°C)", ge=-20.0, le=60.0, example=34.5)
    humidity: float = Field(..., description="Độ ẩm tương đối (%)", ge=0.0, le=100.0, example=78.0)
    passenger_count: int = Field(..., description="Mật độ hành khách tại ga (người)", ge=0, le=10000, example=1200)
    hour: Optional[int] = Field(None, description="Giờ quan sát (0-23)", ge=0, le=23)
    month: Optional[int] = Field(None, description="Tháng quan sát (1-12)", ge=1, le=12)
    is_peak_hour: Optional[int] = Field(None, description="Giờ cao điểm (1/0)", ge=0, le=1)

    @field_validator("temp", "humidity", mode="before")
    @classmethod
    def parse_float_lenient(cls, v):
        if isinstance(v, str):
            v = v.replace(",", ".").strip()
        return float(v)

    @field_validator("passenger_count", mode="before")
    @classmethod
    def parse_int_lenient(cls, v):
        if isinstance(v, str):
            v = v.replace(",", "").strip()
        return int(float(v))


class PredictionResponse(BaseModel):
    """Kết quả dự báo HVAC tức thời — kèm thông gió, chiếu sáng và kWh phiên."""
    status: str
    predicted_hvac_power: float = Field(..., description="Công suất HVAC dự báo (%)")
    predicted_ventilation_power: float = Field(0.0, description="Công suất thông gió (%)")
    predicted_lighting_power: float = Field(0.0, description="Công suất chiếu sáng (%)")
    is_high_load: bool = Field(..., description="Cảnh báo tải cao (> 80%)")
    session_ai_kwh: float = Field(0.0, description="Điện năng AI tích lũy phiên (kWh)")
    session_traditional_kwh: float = Field(0.0, description="Điện năng kịch bản truyền thống (kWh)")
    savings_percent: float = Field(0.0, description="Mức tiết kiệm so với truyền thống (%)")
    input_received: dict
    timestamp: str


class ForecastPoint(BaseModel):
    """Một điểm dự báo trong chuỗi tương lai."""
    offset_minutes: int
    target_time: str
    predicted_hvac_power: float
    predicted_ventilation_power: float
    predicted_lighting_power: float
    estimated_passenger_count: int
    is_high_load: bool
    alert_level: str   # "NORMAL" | "WARNING" | "CRITICAL"


class ForecastResponse(BaseModel):
    """Chuỗi dự báo 30-60 phút tới."""
    status: str
    forecast_window_minutes: int
    data_points: List[ForecastPoint]
    peak_hvac_power: float
    avg_hvac_power: float
    timestamp: str


class VentilationResponse(BaseModel):
    """Kết quả dự báo công suất thông gió."""
    status: str
    predicted_ventilation_power: float = Field(..., description="Công suất thông gió (%)")
    ventilation_mode: str
    co2_risk_level: str
    input_received: dict
    timestamp: str


class LightingResponse(BaseModel):
    """Kết quả dự báo công suất chiếu sáng."""
    status: str
    predicted_lighting_power: float = Field(..., description="Công suất chiếu sáng (%)")
    lighting_zone: str
    daylight_saving: float = Field(..., description="Tiết kiệm so với 100% (%)")
    input_received: dict
    timestamp: str


class EnergyStatsResponse(BaseModel):
    """Thống kê điện năng và so sánh AI vs Truyền thống."""
    status: str
    session_duration_minutes: float
    ai_total_kwh: float
    traditional_total_kwh: float
    savings_kwh: float
    savings_percent: float
    avg_ai_hvac_power: float
    avg_traditional_hvac_power: float
    total_predictions: int
    high_load_events: int
    timestamp: str


# =================================================================================
# HÀM TIỆN ÍCH DÙNG CHUNG
# =================================================================================
def _resolve_time_features(hour: Optional[int], month: Optional[int], is_peak_hour: Optional[int], now: datetime):
    """Tự động điền giờ/tháng/cao điểm nếu client không truyền vào."""
    curr_hour = hour if hour is not None else now.hour
    curr_month = month if month is not None else now.month
    if is_peak_hour is not None:
        is_peak = is_peak_hour
    else:
        is_peak = 1 if curr_hour in [7, 8, 16, 17] else 0
    return curr_hour, curr_month, is_peak


def _predict_hvac(temp: float, humidity: float, passenger_count: int,
                  hour: int, month: int, is_peak: int) -> float:
    """Gọi model pipeline và trả về giá trị HVAC đã clamp [0, 100]."""
    feature_df = pd.DataFrame([{
        "temp": float(temp),
        "humidity": float(humidity),
        "passenger_count": int(passenger_count),
        "hour": int(hour),
        "month": int(month),
        "is_peak_hour": int(is_peak)
    }])
    raw = model_pipeline.predict(feature_df)[0]
    return float(max(0.0, min(100.0, round(float(raw), 2))))


def _predict_ventilation_pct(temp: float, humidity: float, passenger_count: int) -> float:
    """
    Công thức dự báo thông gió dựa trên CO₂/nhiệt tích tụ từ hành khách.
    Mức nền: 20% (thông gió duy trì nền);
    Tăng theo mật độ và nhiệt độ vượt ngưỡng 26°C.
    """
    base = 20.0
    crowd_factor = (passenger_count / 2000.0) * 55.0   # 0% → 55% tùy mật độ
    heat_factor  = max(0.0, (temp - 26.0) * 1.2)        # Cộng thêm khi >26°C
    humid_factor = max(0.0, (humidity - 60.0) * 0.3)    # Cộng thêm khi >60%
    result = base + crowd_factor + heat_factor + humid_factor
    return round(min(100.0, result), 2)


def _predict_lighting_pct(hour: int, passenger_count: int) -> float:
    """
    Công thức chiếu sáng thông minh:
    - Ban đêm (22:00-05:00): 15% (đèn bảo vệ)
    - Sáng sớm/tối muộn: giảm 30-50% so với ban ngày
    - Điều chỉnh thêm theo mật độ hành khách (đông → sáng hơn)
    """
    if 5 <= hour < 7:
        base = 55.0
    elif 7 <= hour < 20:
        base = 80.0
    elif 20 <= hour < 22:
        base = 60.0
    else:
        base = 15.0

    crowd_bonus = (passenger_count / 2000.0) * 20.0  # Cộng tối đa 20% khi đông
    result = base + crowd_bonus
    return round(min(100.0, result), 2)


def _alert_level(hvac_pct: float, vent_pct: float) -> str:
    """Phân loại mức cảnh báo tổng hợp."""
    if hvac_pct > 85.0 or vent_pct > 85.0:
        return "CRITICAL"
    if hvac_pct > 70.0 or vent_pct > 70.0:
        return "WARNING"
    return "NORMAL"


def _log_energy(hvac_pct: float, vent_pct: float, light_pct: float):
    """Ghi nhận vào bộ tích lũy năng lượng phiên."""
    _energy_log.append({
        "ts": datetime.now(VN_TZ),
        "hvac": hvac_pct,
        "vent": vent_pct,
        "light": light_pct,
        "is_high": hvac_pct > 80.0
    })


def _compute_energy_totals():
    """Tính kWh AI vs truyền thống theo khoảng thời gian thực giữa các lần ghi."""
    if not _energy_log:
        return {
            "duration_minutes": 0.0,
            "ai_kwh": 0.0,
            "trad_kwh": 0.0,
            "savings_kwh": 0.0,
            "savings_percent": 0.0,
            "avg_hvac": 0.0,
            "high_load": 0,
            "count": 0,
        }

    first_ts = _energy_log[0]["ts"]
    last_ts = _energy_log[-1]["ts"]
    duration_minutes = max((last_ts - first_ts).total_seconds() / 60.0, 1.0 / 60.0)

    ai_kwh = 0.0
    trad_kwh = 0.0
    fallback_hours = 15.0 / 3600.0
    for i, log in enumerate(_energy_log):
        if i == 0:
            hours = fallback_hours
        else:
            hours = max((_energy_log[i]["ts"] - _energy_log[i - 1]["ts"]).total_seconds() / 3600.0, 1.0 / 3600.0)
        load = (log["hvac"] / 100.0) * HVAC_MAX_KW
        vent = (log["vent"] / 100.0) * VENT_MAX_KW
        light = (log["light"] / 100.0) * LIGHT_MAX_KW
        ai_kwh += (load + vent + light) * hours
        trad_load = (TRADITIONAL_HVAC_PCT / 100.0) * HVAC_MAX_KW
        trad_vent = 0.70 * VENT_MAX_KW
        trad_light = 1.00 * LIGHT_MAX_KW
        trad_kwh += (trad_load + trad_vent + trad_light) * hours

    savings_kwh = max(0.0, trad_kwh - ai_kwh)
    savings_pct = round((savings_kwh / trad_kwh * 100.0) if trad_kwh > 0 else 0.0, 2)
    avg_hvac = round(sum(log["hvac"] for log in _energy_log) / len(_energy_log), 2)
    high_load = sum(1 for log in _energy_log if log["is_high"])
    return {
        "duration_minutes": round(duration_minutes, 2),
        "ai_kwh": round(ai_kwh, 4),
        "trad_kwh": round(trad_kwh, 4),
        "savings_kwh": round(savings_kwh, 4),
        "savings_percent": savings_pct,
        "avg_hvac": avg_hvac,
        "high_load": high_load,
        "count": len(_energy_log),
    }


# =================================================================================
# ENDPOINT 1: HEALTH CHECK
# =================================================================================
@app.get("/", summary="Trang chủ Dashboard & Health check")
def root():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "dashboard.html")
    if os.path.exists(path):
        return FileResponse(path, media_type="text/html")
    return {
        "service": "Digital Twin HVAC AI Inference Engine v2.0",
        "status": "Online",
        "model_loaded": model_pipeline is not None,
        "timestamp": datetime.now(VN_TZ).isoformat()
    }

@app.get("/logo.png", summary="Logo hình ảnh ga tàu/UTT")
def get_logo():
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    if os.path.exists(logo_path):
        return FileResponse(logo_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Logo not found")




# =================================================================================
# ENDPOINT 2: DỰ BÁO HVAC TỨC THỜI (giữ nguyên tương thích Unity)
# =================================================================================
@app.post("/predict", response_model=PredictionResponse, summary="Dự báo HVAC tức thời")
@app.post("/api/predict", response_model=PredictionResponse, include_in_schema=False)
def predict_hvac_power(data: SensorDataInput):
    """
    Tiếp nhận dữ liệu cảm biến và dự báo công suất HVAC tối ưu tại thời điểm hiện tại.
    Endpoint này tương thích ngược với Unity DigitalTwinManager.cs.
    """
    if model_pipeline is None:
        raise HTTPException(status_code=500, detail="Mô hình ML chưa được nạp.")

    try:
        now = datetime.now(VN_TZ)
        curr_hour, curr_month, is_peak = _resolve_time_features(
            data.hour, data.month, data.is_peak_hour, now)
        hvac_pct = _predict_hvac(data.temp, data.humidity, data.passenger_count,
                                  curr_hour, curr_month, is_peak)
        vent_pct  = _predict_ventilation_pct(data.temp, data.humidity, data.passenger_count)
        light_pct = _predict_lighting_pct(curr_hour, data.passenger_count)
        _log_energy(hvac_pct, vent_pct, light_pct)
        energy = _compute_energy_totals()

        return PredictionResponse(
            status="success",
            predicted_hvac_power=hvac_pct,
            predicted_ventilation_power=vent_pct,
            predicted_lighting_power=light_pct,
            is_high_load=hvac_pct > 80.0,
            session_ai_kwh=energy["ai_kwh"],
            session_traditional_kwh=energy["trad_kwh"],
            savings_percent=energy["savings_percent"],
            input_received={
                "temp": data.temp, "humidity": data.humidity,
                "passenger_count": data.passenger_count,
                "hour": curr_hour, "month": curr_month, "is_peak_hour": is_peak
            },
            timestamp=now.strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Lỗi suy luận: {str(ex)}")



# =================================================================================
# ENDPOINT 3: DỰ BÁO CHUỖI 30-60 PHÚT TỚI
# =================================================================================
@app.post("/predict/forecast", response_model=ForecastResponse, summary="Dự báo chuỗi 30-60 phút tới")
@app.post("/api/predict/forecast", response_model=ForecastResponse, include_in_schema=False)
def predict_forecast(
    data: SensorDataInput,
    minutes: int = Query(default=60, ge=15, le=120, description="Số phút muốn dự báo (15-120)")
):
    """
    Dự báo chuỗi thời gian cho HVAC, thông gió và chiếu sáng trong N phút tới.
    Mỗi điểm dự báo cách nhau 5 phút. Mô hình giả lập xu hướng hành khách
    theo chu kỳ thực tế của ga (tăng dần → đỉnh → giảm dần).
    """
    if model_pipeline is None:
        raise HTTPException(status_code=500, detail="Mô hình ML chưa được nạp.")

    try:
        now = datetime.now(VN_TZ)
        curr_hour, curr_month, _ = _resolve_time_features(
            data.hour, data.month, data.is_peak_hour, now)

        forecast_points = []
        step = 5  # Bước dự báo mỗi 5 phút

        for offset in range(0, minutes + 1, step):
            future_dt = now + timedelta(minutes=offset)
            future_hour = future_dt.hour
            future_month = future_dt.month
            future_is_peak = 1 if future_hour in [7, 8, 16, 17] else 0

            # Mô hình hóa xu hướng nhiệt độ: tăng nhẹ ban ngày, giảm dần tối
            temp_trend = data.temp + math.sin(math.pi * offset / max(minutes, 1)) * 1.5
            temp_future = round(min(50.0, max(-10.0, temp_trend)), 1)

            # Mô hình hóa xu hướng hành khách: Gaussian peak sau 25 phút (tàu vào ga)
            pax_base = data.passenger_count
            gaussian_surge = pax_base * 0.6 * math.exp(-0.5 * ((offset - 25) / 15.0) ** 2)
            pax_future = int(min(3000, max(0, pax_base + gaussian_surge)))

            # Dự báo 3 hệ thống
            hvac_pct  = _predict_hvac(temp_future, data.humidity, pax_future,
                                       future_hour, future_month, future_is_peak)
            vent_pct  = _predict_ventilation_pct(temp_future, data.humidity, pax_future)
            light_pct = _predict_lighting_pct(future_hour, pax_future)

            forecast_points.append(ForecastPoint(
                offset_minutes=offset,
                target_time=future_dt.strftime("%H:%M"),
                predicted_hvac_power=hvac_pct,
                predicted_ventilation_power=vent_pct,
                predicted_lighting_power=light_pct,
                estimated_passenger_count=pax_future,
                is_high_load=hvac_pct > 80.0,
                alert_level=_alert_level(hvac_pct, vent_pct)
            ))

        hvac_values = [p.predicted_hvac_power for p in forecast_points]
        return ForecastResponse(
            status="success",
            forecast_window_minutes=minutes,
            data_points=forecast_points,
            peak_hvac_power=round(max(hvac_values), 2),
            avg_hvac_power=round(sum(hvac_values) / len(hvac_values), 2),
            timestamp=now.strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Lỗi forecast: {str(ex)}")


# =================================================================================
# ENDPOINT 4: DỰ BÁO CÔNG SUẤT THÔNG GIÓ
# =================================================================================
@app.post("/predict/ventilation", response_model=VentilationResponse, summary="Dự báo công suất thông gió")
def predict_ventilation(data: SensorDataInput):
    """
    Dự báo công suất hệ thống thông gió dựa trên mật độ hành khách,
    nhiệt độ và độ ẩm. Tính toán nguy cơ CO₂ và chế độ vận hành.
    """
    try:
        now = datetime.now(VN_TZ)
        curr_hour, _, _ = _resolve_time_features(data.hour, data.month, data.is_peak_hour, now)
        vent_pct = _predict_ventilation_pct(data.temp, data.humidity, data.passenger_count)

        # Phân loại chế độ vận hành thông gió
        if vent_pct < 30:
            mode = "STANDBY"
            co2_risk = "THẤP"
        elif vent_pct < 60:
            mode = "NORMAL"
            co2_risk = "TRUNG BÌNH"
        elif vent_pct < 80:
            mode = "BOOST"
            co2_risk = "CAO"
        else:
            mode = "EMERGENCY"
            co2_risk = "RẤT CAO - CẦN CAN THIỆP"

        return VentilationResponse(
            status="success",
            predicted_ventilation_power=vent_pct,
            ventilation_mode=mode,
            co2_risk_level=co2_risk,
            input_received={
                "temp": data.temp, "humidity": data.humidity,
                "passenger_count": data.passenger_count
            },
            timestamp=now.strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Lỗi dự báo thông gió: {str(ex)}")


# =================================================================================
# ENDPOINT 5: DỰ BÁO CÔNG SUẤT CHIẾU SÁNG
# =================================================================================
@app.post("/predict/lighting", response_model=LightingResponse, summary="Dự báo công suất chiếu sáng")
def predict_lighting(data: SensorDataInput):
    """
    Dự báo công suất chiếu sáng thông minh dựa trên giờ trong ngày
    và mật độ hành khách. Tính phần trăm tiết kiệm so với chạy 100%.
    """
    try:
        now = datetime.now(VN_TZ)
        curr_hour, _, _ = _resolve_time_features(data.hour, data.month, data.is_peak_hour, now)
        light_pct = _predict_lighting_pct(curr_hour, data.passenger_count)
        saving = round(100.0 - light_pct, 2)

        # Phân vùng chiếu sáng theo giờ
        if 7 <= curr_hour < 20:
            zone = "GIỜ BAN NGÀY - Kết hợp tự nhiên"
        elif 20 <= curr_hour < 22:
            zone = "BUỔI TỐI - Giảm tải thông minh"
        elif 22 <= curr_hour or curr_hour < 5:
            zone = "BAN ĐÊM - Chế độ bảo vệ"
        else:
            zone = "SÁNG SỚM - Khởi động dần"

        return LightingResponse(
            status="success",
            predicted_lighting_power=light_pct,
            lighting_zone=zone,
            daylight_saving=saving,
            input_received={
                "hour": curr_hour,
                "passenger_count": data.passenger_count
            },
            timestamp=now.strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Lỗi dự báo chiếu sáng: {str(ex)}")


# =================================================================================
# ENDPOINT 6: THỐNG KÊ ĐIỆN NĂNG & SO SÁNH AI vs TRUYỀN THỐNG
# =================================================================================
@app.get("/energy/stats", response_model=EnergyStatsResponse, summary="Thống kê kWh + so sánh AI vs Truyền thống")
@app.get("/api/energy/stats", response_model=EnergyStatsResponse, include_in_schema=False)
def get_energy_stats():
    """
    Trả về thống kê điện năng tích lũy phiên làm việc hiện tại.
    So sánh kWh tiêu thụ giữa kịch bản AI (thông minh) vs kịch bản truyền thống
    (chạy cố định 85% liên tục). Đây là cơ sở tính toán % tiết kiệm năng lượng.
    """
    energy = _compute_energy_totals()
    return EnergyStatsResponse(
        status="success" if energy["count"] else "no_data",
        session_duration_minutes=energy["duration_minutes"],
        ai_total_kwh=energy["ai_kwh"],
        traditional_total_kwh=energy["trad_kwh"],
        savings_kwh=energy["savings_kwh"],
        savings_percent=energy["savings_percent"],
        avg_ai_hvac_power=energy["avg_hvac"],
        avg_traditional_hvac_power=TRADITIONAL_HVAC_PCT,
        total_predictions=energy["count"],
        high_load_events=energy["high_load"],
        timestamp=datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S")
    )


@app.get("/energy/history", summary="Chuỗi công suất AI vs truyền thống (phục vụ dashboard)")
@app.get("/api/energy/history", include_in_schema=False)
def get_energy_history(limit: int = Query(default=80, ge=5, le=500)):
    rows = _energy_log[-limit:]
    return {
        "status": "success" if rows else "no_data",
        "points": [
            {
                "t": row["ts"].strftime("%H:%M:%S"),
                "hvac": row["hvac"],
                "vent": row["vent"],
                "light": row["light"],
                "traditional": TRADITIONAL_HVAC_PCT,
            }
            for row in rows
        ],
        "timestamp": datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S"),
    }



@app.get("/dashboard", summary="Analytics Dashboard (Chart.js)")
def analytics_dashboard():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "dashboard.html")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Chưa tìm thấy templates/dashboard.html")
    return FileResponse(path, media_type="text/html")


@app.get("/unity_build/{file_path:path}", summary="Phục vụ file tĩnh Unity WebGL Build (.gz headers)")
def serve_unity_build(file_path: str):
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Build_Web")
    full_path = os.path.normpath(os.path.join(base_dir, file_path))
    if not full_path.startswith(base_dir):
        raise HTTPException(status_code=403, detail="Access denied")
    if not os.path.exists(full_path) or os.path.isdir(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "no-cache, must-revalidate"
    }
    media_type = None

    if file_path.endswith(".data.gz"):
        media_type = "application/octet-stream"
        headers["Content-Encoding"] = "gzip"
    elif file_path.endswith(".wasm.gz"):
        media_type = "application/wasm"
        headers["Content-Encoding"] = "gzip"
    elif file_path.endswith(".js.gz"):
        media_type = "application/javascript"
        headers["Content-Encoding"] = "gzip"
    elif file_path.endswith(".html"):
        media_type = "text/html"
    elif file_path.endswith(".css"):
        media_type = "text/css"
    elif file_path.endswith(".js"):
        media_type = "application/javascript"

    return FileResponse(full_path, media_type=media_type, headers=headers)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

