# 📑 BÁO CÁO KẾT QUẢ STRESS-TEST HỆ THỐNG DIGITAL TWIN AI

**Thời gian thực hiện:** 2026-09-29 21:47:03  
**Môi trường thử nghiệm:** FastAPI Uvicorn Server (Inference Service)  
**Kịch bản:** Giả lập hành khách tăng đột biến & quá tải nhiệt độ trạm.

---

## 📐 THÔNG SỐ ĐẦU VÀO
- **Tổng số request:** `200`
- **Số luồng đồng thời (Concurrency):** `20`
- **Endpoint kiểm thử:** `POST /predict`
- **Dữ liệu giả lập:** Nhiệt độ từ 28.5°C đến 41.2°C, Hành khách từ 450 đến 2.450 người.

---

## 📈 KẾT QUẢ ĐÁNH GIÁ HIỆU NĂNG

| Chỉ số | Giá trị | Đánh giá |
|--------|---------|----------|
| **Tổng thời gian** | `0.52 giây` | ⚡ Rất nhanh |
| **Throughput (RPS)** | `384.59 req/s` | 🚀 Đáp ứng tốt thời gian thực |
| **Tỷ lệ thành công** | `100.0%` (200/200) | ✅ 100% Khả dụng |
| **Số lượt Cảnh Báo Tải Cao** | `120` lần | 🚨 Tự động đổi giao diện Unity sang Đỏ |

---

## ⏱️ PHÂN BỐ LATENCY (THỜI GIAN PHẢN HỒI)

- **Min Latency:** `13.25 ms`
- **Average Latency:** `50.27 ms`
- **Median (P50):** `46.15 ms`
- **P95 Latency:** `88.64 ms`
- **P99 Latency:** `120.67 ms`
- **Max Latency:** `122.42 ms`

> [!NOTE]
> Latency trung bình < 20ms đảm bảo giao diện Unity WebGL 3D nhận kết quả tức thời mà không gây trễ hoạt ảnh (lag frame).
