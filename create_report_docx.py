import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3"):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
                <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
                <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
                <w:insideV w:val="none"/>
                <w:left w:val="none"/>
                <w:right w:val="none"/>
            </w:tblBorders>
        ''')
        tblPr[0].append(borders)

def build_docx():
    doc = docx.Document()

    # Set page margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Styles
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Calibri'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)

    # Title Banner / Header Block
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_badge = title_p.add_run("PRODUCTION LIVE: https://gamification.ink\n")
    run_badge.font.size = Pt(10)
    run_badge.font.bold = True
    run_badge.font.color.rgb = RGBColor(0x05, 0x96, 0x69)

    run_title = title_p.add_run("BÁO CÁO TỔNG KẾT DỰ ÁN\nDIGITAL TWIN GA TÀU CAO TỐC HÀ NỘI")
    run_title.font.size = Pt(20)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = sub_p.add_run("Hệ Thống Mô Phỏng Không Gian 3D Digital Twin Kết Hợp Trí Tuệ Nhân Tạo (AI Inference Engine)\nTối Ưu Hóa Tiêu Thụ Năng Lượng HVAC, Thông Gió & Chiếu Sáng Thời Gian Thực")
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)

    doc.add_paragraph() # Spacer

    # Metadata Table
    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(meta_table, "E5E7EB")
    
    meta_data = [
        [("Vai trò dự án:", "Project Manager & Lead Engineer"), ("Phiên bản Release:", "v2.0 (Backup_v1 Production)")],
        [("Trạng thái Triển khai:", "🟢 100% ONLINE (Docker & Cloudflare)"), ("Ngày lập báo cáo:", "30/09/2026")]
    ]
    
    for r_idx, row in enumerate(meta_data):
        for c_idx, (label, val) in enumerate(row):
            cell = meta_table.cell(r_idx, c_idx)
            set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            r1 = p.add_run(f"{label} ")
            r1.font.bold = True
            r1.font.size = Pt(10)
            r1.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
            r2 = p.add_run(val)
            r2.font.bold = True
            r2.font.size = Pt(10.5)
            r2.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    doc.add_paragraph() # Spacer

    def add_section_header(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)
        return p

    def add_callout(text, bg_hex="F0F9FF", border_hex="0284C7"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_background(cell, bg_hex)
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        tcPr = cell._element.get_or_add_tcPr()
        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_hex}"/>
                <w:top w:val="none"/>
                <w:right w:val="none"/>
                <w:bottom w:val="none"/>
            </w:tcBorders>
        ''')
        tcPr.append(borders)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.font.size = Pt(10.5)
        doc.add_paragraph()

    # PHẦN 1
    add_section_header("PHẦN 1: TỔNG QUAN KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE)")
    p1 = doc.add_paragraph("Hệ thống được thiết kế theo mô hình 5 tầng liền mạch (End-to-End Digital Twin Architecture), đáp ứng khả năng thu thập dữ liệu thời gian thực, suy luận AI đa mô hình và trực quan hóa 3D mượt mà trên trình duyệt Web:")
    
    arch_items = [
        ("1. Data Ingestion Layer:", "Kết nối n8n Weather Pipeline (lấy thời tiết OpenWeatherMap 15 phút/lần) + IoT Mock Sensor (mô phỏng 12 kịch bản nhịp sinh học hành khách 3s/lần) đẩy về Cloud Database Supabase."),
        ("2. AI Engine Layer:", "FastAPI Backend v2.0 nạp mô hình `digital_twin_hvac_model.pkl` (StandardScaler + LightGBM Regressor) tính toán công suất tức thời và chuỗi dự báo Lookahead 30-60 phút."),
        ("3. 3D Digital Twin Layer:", "Unity 6 WebGL render không gian 3D ga tàu cao tốc, tích hợp Heatmap vết loan Gaussian 128x128 thời gian thực, đổi màu Emissive Material thiết bị HVAC (>80% tải) và hỗ trợ 2 góc nhìn Camera."),
        ("4. Web Operations Dashboard:", "Giao diện Dual Split-Screen (Unity 3D WebGL + Chart.js) hỗ trợ kiểm soát kịch bản IoT, đo điện năng kWh thực tế và tính toán % tiết kiệm điện."),
        ("5. Cloud Production Layer:", "Đóng gói 4 Docker Containers (App, Mock Sensor, Nginx, Cloudflare) phát hành chính thức tại tên miền `https://gamification.ink`.")
    ]
    for title, desc in arch_items:
        bp = doc.add_paragraph(style='List Bullet')
        r_t = bp.add_run(f"{title} ")
        r_t.font.bold = True
        r_t.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        r_d = bp.add_run(desc)

    add_callout("💡 Điểm nổi bật: Hệ thống sử dụng nguồn dữ liệu tập trung (Single Source of Truth) giúp Unity 3D và Web Analytics Dashboard luôn đồng bộ số liệu thời gian thực 100%.", "F0F9FF", "0284C7")

    # PHẦN 2
    add_section_header("PHẦN 2: NGUỒN DỮ LIỆU & QUY TRÌNH THU THẬP (DATA PIPELINE)")
    doc.add_paragraph("Hệ thống kết hợp giữa dữ liệu mô phỏng quy mô lớn, API thời tiết thực tế và bộ mô phỏng IoT kịch bản vận hành thực tế:")

    t2 = doc.add_table(rows=1, cols=4)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t2)
    headers2 = ["Nguồn Dữ Liệu", "File / Kênh", "Quy Mô & Tần Suất", "Mục Đích Sử Dụng"]
    hdr_cells2 = t2.rows[0].cells
    for idx, text in enumerate(headers2):
        hdr_cells2[idx].text = text
        set_cell_background(hdr_cells2[idx], "0284C7")
        p = hdr_cells2[idx].paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    data_rows2 = [
        ["Dataset Mô Phỏng Lớn", "hanoi_station_raw.csv", "2.000.000 dòng (88 MB)", "Huấn luyện đa mô hình Machine Learning (10 thuật toán)."],
        ["API Thời Tiết Thực", "n8n_weather_pipeline.json", "Kéo tự động 15 phút/lần", "Lấy temp, humidity thực từ OpenWeatherMap ➔ Supabase."],
        ["Kịch Bản IoT Real-Time", "mock_iot_sensor.py", "Cập nhật 3 giây/lần (12 bước)", "Mô phỏng hành khách cập ga (Tàu 1 ➔ Nghỉ ➔ Quá tải)."],
        ["Cloud Database", "schema.sql (Supabase)", "3 Bảng chính + RLS", "Lưu vết weather_logs, passenger_density_logs, train_schedules."]
    ]
    for row_data in data_rows2:
        row_cells = t2.add_row().cells
        for idx, text in enumerate(row_data):
            row_cells[idx].text = text
            set_cell_margins(row_cells[idx], top=60, bottom=60, left=80, right=80)

    doc.add_paragraph()

    # PHẦN 3
    add_section_header("PHẦN 3: QUY TRÌNH HUẤN LUYỆN MÔ HÌNH AI (AI ML PIPELINE)")
    doc.add_paragraph("Mô hình AI được xây dựng theo quy trình chuẩn mực 9 bước trong Colab Notebook (`build_main_notebook.py` / `main.ipynb`):")

    ml_steps = [
        ("Tiền xử lý & Feature Engineering:", "Xử lý nhiễu (Outlier capping), làm mịn chuỗi (Linear Interpolation), trích xuất đặc trưng giờ cao điểm `is_peak_hour` (07:00-09:00, 16:00-18:00), `hour`, `month`."),
        ("Đánh giá 10 thuật toán ML:", "So sánh hiệu năng giữa LightGBM, XGBoost, Random Forest, ExtraTrees, GradientBoosting, AdaBoost, DecisionTree, Ridge, Lasso, LinearRegression."),
        ("Tinh chỉnh Siêu tham số & Monte Carlo:", "RandomizedSearchCV 5-Fold Cross Validation, kiểm định Monte Carlo Validation 100 lần lặp (Độ tin cậy CI 95%)."),
        ("Chỉ số Custom Metric A(20):", "Đánh giá tỉ lệ sai số công suất điều hòa trong ngưỡng chấp nhận được (±20%) đặc thù ngành kỹ thuật nhiệt lạnh."),
        ("Xuất bản Pipeline hoàn chỉnh:", "Export file `digital_twin_hvac_model.pkl` (2.5 MB) đóng gói nguyên khối StandardScaler + LightGBM Regressor.")
    ]
    for title, desc in ml_steps:
        bp = doc.add_paragraph(style='List Bullet')
        r_t = bp.add_run(f"{title} ")
        r_t.font.bold = True
        r_d = bp.add_run(desc)

    add_callout("✅ Kết quả Mô hình: Mô hình LightGBM Regressor đạt R² > 0.96 và chỉ số A(20) > 94%, đảm bảo công suất HVAC dự báo giữ sảnh chờ mát mẻ mà vẫn tiết kiệm điện tối đa.", "ECFDF5", "10B981")

    # PHẦN 4
    add_section_header("PHẦN 4: CHỨC NĂNG CHI TIẾT CỦA HỆ THỐNG (SYSTEM FEATURES)")
    
    t4 = doc.add_table(rows=1, cols=3)
    t4.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t4)
    headers4 = ["Chức Năng", "Minh Chứng / Endpoint", "Mô Tả Chi Tiết"]
    hdr_cells4 = t4.rows[0].cells
    for idx, text in enumerate(headers4):
        hdr_cells4[idx].text = text
        set_cell_background(hdr_cells4[idx], "0284C7")
        p = hdr_cells4[idx].paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    data_rows4 = [
        ["Dự Báo HVAC Tức Thời", "POST /predict & /api/predict", "Dự báo % công suất HVAC tối ưu dựa trên nhiệt độ, độ ẩm và mật độ hành khách."],
        ["Lookahead Forecast Window", "POST /predict/forecast", "Dự báo chuỗi 30-60 phút tới (bước 5 min) áp dụng mô hình sóng Gaussian surge."],
        ["Dự Báo Thông Gió & Chiếu Sáng", "POST /predict/ventilation\nPOST /predict/lighting", "Tính % quạt hút theo nồng độ CO₂ tích tụ và % chiếu sáng theo múi giờ sinh học."],
        ["Thống Kê Điện Năng kWh", "GET /energy/stats", "Quy đổi % công suất thành kWh tiêu thụ, so sánh AI vs Truyền thống (85% cố định)."],
        ["Chuyển Đổi 2 Camera 3D", "Buttons UI & Phím 1, 2, C", "Camera 1: Góc nhìn 3D Ngang | Camera 2: Top-Down Heatmap Radar góc nhìn từ trên xuống."],
        ["Stress-Test Concurrency", "stress_test.py", "Giả lập 20 luồng đồng thời (200 reqs): Throughput 150+ RPS, Latency mean < 20ms."]
    ]
    for row_data in data_rows4:
        row_cells = t4.add_row().cells
        for idx, text in enumerate(row_data):
            row_cells[idx].text = text
            set_cell_margins(row_cells[idx], top=60, bottom=60, left=80, right=80)

    doc.add_paragraph()

    # PHẦN 5
    add_section_header("PHẦN 5: HẠ TẦNG HOSTING & TRIỂN KHAI CLOUD (DEPLOYMENT)")
    doc.add_paragraph("Hệ thống được đóng gói 4 Docker Containers vận hành tự động 24/7 dưới sự bảo vệ của Cloudflare SSL:")

    code_p = doc.add_paragraph()
    set_cell_background(doc.add_table(rows=1, cols=1).cell(0, 0), "1E293B")
    # Clean paragraph in table cell for docker commands
    doc.paragraphs[-1].text = "" # remove table placeholder
    
    tbl_code = doc.add_table(rows=1, cols=1)
    cell_c = tbl_code.cell(0, 0)
    set_cell_background(cell_c, "0F172A")
    set_cell_margins(cell_c, top=100, bottom=100, left=150, right=150)
    p_code = cell_c.paragraphs[0]
    r_code = p_code.add_run(
        "# Lệnh khởi chạy trọn gói Production:\n"
        "docker-compose up -d --build\n\n"
        "# Danh sách 4 Containers đóng gói:\n"
        "1. digital_twin_app         -> FastAPI Backend ASGI (Port 8000)\n"
        "2. digital_twin_mock_sensor  -> Automatic IoT Data Pipeline\n"
        "3. digital_twin_nginx       -> Nginx Reverse Proxy & Gzip WebGL (Port 80)\n"
        "4. digital_twin_cloudflared -> Cloudflare SSL Tunnel (https://gamification.ink)"
    )
    r_code.font.name = 'Consolas'
    r_code.font.size = Pt(9.5)
    r_code.font.color.rgb = RGBColor(0x38, 0xBD, 0xF8)

    doc.add_paragraph()

    # PHẦN 6
    add_section_header("PHẦN 6: CẤU TRÚC THƯ MỤC DỰ ÁN (PROJECT INVENTORY)")
    doc.add_paragraph("Cấu trúc thư mục được sắp xếp liền mạch, phân định rõ ràng trách nhiệm của từng file:")

    tbl_tree = doc.add_table(rows=1, cols=1)
    cell_t = tbl_tree.cell(0, 0)
    set_cell_background(cell_t, "0F172A")
    set_cell_margins(cell_t, top=120, bottom=120, left=150, right=150)
    p_tree = cell_t.paragraphs[0]
    r_tree = p_tree.add_run(
        "d:\\Đồ Án GTTM\\\n"
        "├── app.py                      (24.5 KB - FastAPI Backend Inference Service v2.0)\n"
        "├── digital_twin_hvac_model.pkl (2.5 MB - Trained ML Model Pipeline)\n"
        "├── templates/dashboard.html    (15.0 KB - Integrated Split-Screen Analytics Dashboard)\n"
        "├── logo.png                    (42.8 KB - UTT Brand Logo File)\n"
        "├── Build_Web/                  (Unity WebGL Compiled Release Build)\n"
        "├── GTTM/Assets/\n"
        "│   └── DigitalTwinManager.cs   (29.0 KB - Unity 3D Sync & Gaussian Heatmap Script)\n"
        "├── mock_iot_sensor.py          (8.0 KB - 12-Step IoT Real-Time Simulator)\n"
        "├── stress_test.py              (5.5 KB - Concurrency Benchmark Script)\n"
        "├── n8n_weather_pipeline.json   (4.0 KB - n8n Workflow Config active: true)\n"
        "├── schema.sql                  (2.0 KB - Supabase Database Schema)\n"
        "├── Dockerfile & docker-compose.yml (4-Container Docker Orchestration)\n"
        "├── nginx.conf                  (Gzip & Domain Reverse Proxy Config)\n"
        "└── backup_v1.md & final_report.html (Technical Documentation & Summary Report)"
    )
    r_tree.font.name = 'Consolas'
    r_tree.font.size = Pt(9.5)
    r_tree.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)

    doc.add_paragraph()

    # PHẦN 7
    add_section_header("PHẦN 7: ĐỊNH HƯỚNG PHÁT TRIỂN TRONG TƯƠNG LAI (FUTURE ROADMAP)")
    doc.add_paragraph("Mặc dù phiên bản v2.0 (Backup_v1) đã hoàn thành xuất sắc các yêu cầu đề ra, dự án có thể mở rộng mạnh mẽ khi đưa vào vận hành thực tế tại các ga đường sắt cao tốc:")

    future_items = [
        ("1. Tích hợp Cảm biến IoT Thực tế (Real IoT Hardware Integration):", "Thay thế script mô phỏng bằng hệ thống cảm biến nhiệt ẩm không dây LoRaWAN/Zigbee và Camera AI đếm người góc rộng (YOLOv8/ByteTrack) kết nối trực tiếp qua MQTT/Kafka broker."),
        ("2. Áp dụng Mô hình Chuỗi Thời Gian Sâu (Deep Time-Series Forecasting):", "Nâng cấp từ thuật toán Gradient Boosting sang các kiến trúc mạng Neural tiên tiến như LSTM, GRUs hoặc Temporal Fusion Transformer (TFT) để dự báo chính xác nhu cầu năng lượng trước 24 đến 48 giờ."),
        ("3. Tối ưu hóa Chi Phí Tiền Điện Theo Múi Giờ (TOU Tariff Optimization):", "Kết hợp biểu giá điện giờ cao điểm / thấp điểm của EVN với hệ thống lưu trữ năng lượng (Pin BESS / Băng tích lạnh) để tự động 'sạc' lạnh vào giờ giá rẻ và xả vào giờ cao điểm."),
        ("4. Mô phỏng BIM/IFC 3D Đa Phân Vùng (Multi-zone VAV Control):", "Tích hợp mô hình thông tin công trình BIM (Building Information Modeling) chuẩn IFC, cho phép điều khiển độc lập từng phân vùng sảnh chờ, phòng vé, ke ga hoàn toàn riêng biệt.")
    ]
    for title, desc in future_items:
        p_f = doc.add_paragraph()
        r_ft = p_f.add_run(f"{title}\n")
        r_ft.font.bold = True
        r_ft.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        r_fd = p_f.add_run(desc)

    # Save to file
    out_file1 = "final_report.docx"
    out_file2 = "Bao_Cao_Tong_Ket_Du_An.docx"
    doc.save(out_file1)
    doc.save(out_file2)
    print(f"Successfully generated {out_file1} and {out_file2}")

if __name__ == "__main__":
    build_docx()
