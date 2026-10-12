# CẤU TRÚC VÀ QUY CHUẨN VIẾT CV KỸ THUẬT (CHUẨN ATS & THỰC CHIẾN)

> **Mục đích**: Tài liệu này phân tích cấu trúc, phong cách hành văn và công thức tạo ra các điểm nhấn kỹ thuật từ mẫu CV chuẩn của **Nguyễn Hiếu Nghĩa**, dùng làm khung tham chiếu (template & framework) để xây dựng CV cho các dự án sau này.

---

## 1. CẤU TRÚC TỔNG THỂ (1 TRANG - ATS FRIENDLY)

CV được thiết kế theo chuẩn **Single-Column (1 cột)** cổ điển của Harvard / Jake's Resume, không dùng bảng biểu phức tạp, không icon đồ họa hay ảnh chân dung để tối ưu 100% cho hệ thống lọc hồ sơ tự động (ATS) và mắt nhìn của Tech Lead / Tuyển dụng.

Thứ tự các phần:
1. **Header (Thông tin liên hệ)**
2. **Summary (Tóm tắt nghề nghiệp - Định vị bản thân)**
3. **Skills (Kỹ năng kỹ thuật theo nhóm)**
4. **Education (Học vấn)**
5. **Projects (Dự án thực tế / Cá nhân / Đồ án)**

*(Lưu ý: Với sinh viên / fresher, mục Projects chiếm trọng số lớn nhất: 50% - 60% diện tích trang).*

---

## 2. CHI TIẾT TỪNG PHẦN VÀ CÔNG THỨC VIẾT

### PHẦN 1: HEADER (THÔNG TIN LIÊN HỆ)
* **Quy tắc**: Ngắn gọn, đặt ở giữa trang (center align), font chữ tên lớn và in hoa/đậm.
* **Các thành phần bắt buộc**:
  - **Họ và tên**: To nhất, nổi bật nhất (ví dụ: `NGUYEN HIEU NGHIA`)
  - **Dòng liên kết**: `github.com/...` | `linkedin.com/in/...` | `email@domain.com`
  - **Dòng thông tin cơ bản**: `Thành phố, Quốc gia` | `(+84) Số điện thoại`
* **Những thứ NÊN TRÁNH**: Không ảnh thẻ, không ngày tháng năm sinh, không tình trạng hôn nhân, không địa chỉ nhà cụ thể (chỉ cần Tỉnh/Thành phố).

---

### PHẦN 2: SUMMARY (TÓM TẮT BẢN THÂN - 3 ĐẾN 4 DÒNG)
* **Mục tiêu**: Trả lời ngay cho NTD: *Bạn là ai? Chuyên về mảng nào? Đã làm được gì thực tế? Bạn mong muốn đóng góp điều gì cho team?*
* **Công thức 4 bước**:
  1. **Định danh & Trọng tâm**: Sinh viên/Kỹ sư ngành gì, tập trung vào công nghệ cốt lõi nào (ví dụ: *Software Engineering student with hands-on full-stack experience, focused on Laravel backend development*).
  2. **Bằng chứng năng lực (Proof of Work)**: Đã độc lập thiết kế và triển khai bao nhiêu sản phẩm quy mô production, bao quát các vấn đề kỹ thuật nào (RESTful API, kiến trúc phân tầng, transaction locking, RBAC,...).
  3. **Tư duy kiến trúc/hệ thống**: Đề cập đến tư duy giải quyết vấn đề (Clean Code, Design Patterns, Data integrity).
  4. **Thái độ & Khả năng hội nhập**: Dù làm solo tốt nhưng sẵn sàng thích nghi với môi trường làm việc nhóm chuyên nghiệp (Agile/Scrum, Git workflow, Code review).

---

### PHẦN 3: SKILLS (KỸ NĂNG CHUYÊN MÔN)
* **Quy tắc**: Phân loại theo danh mục rõ ràng, không dùng thanh đo % hay chấm điểm sao (5/5 sao rất phản cảm đối với tuyển dụng kỹ thuật).
* **Các nhóm kỹ năng mẫu**:
  - **Languages**: PHP, JavaScript, TypeScript, HTML, CSS, SQL...
  - **Frameworks & Libraries**: Laravel (Blade), Vue 3, React, Tailwind CSS, ExpressJS...
  - **Databases**: MySQL, PostgreSQL, MongoDB, Redis...
  - **Architecture & Concepts**: RESTful API, OOP, SOLID, Repository & Service Pattern, MVC...
  - **Tools & Environment**: Git, Docker, Docker Compose, GitHub Actions (CI/CD), Postman, Linux/Laragon...
  - **Soft Skills / Others**: Technical English (Đọc hiểu tài liệu), Viết clean code & document code...

---

### PHẦN 4: EDUCATION (HỌC VẤN)
* **Quy tắc**: Để 2 dòng gọn gàng.
  - **Tên trường đại học** | **Năm nhập học - Năm tốt nghiệp dự kiến**
  - **GPA** (Nếu >= 3.0/4.0 thì nên đưa vào) — **Chuyên ngành / Bậc học**

---

### PHẦN 5: PROJECTS (TRỌNG TÂM - CÔNG THỨC VIẾT DỰ ÁN)

#### 1. Cấu trúc tiêu đề mỗi dự án:
```text
[TÊN DỰ ÁN] - [Phân loại / Lĩnh vực ngắn]                    [Thời gian: MM/YYYY - MM/YYYY]
[Vai trò: Full-stack Developer / Backend Developer / Lead]
Stack: [Liệt kê các công nghệ chính: Backend, Frontend, DB, DevOps/API]
GitHub: [Link repo]
Live Demo: [Link chạy thực tế trên Render/Vercel/Cloud]
```

#### 2. Công thức viết Bullet Point (Google X-Y-Z & STAR Formula):
> **"Accomplished [X], as measured by [Y], by doing [Z]"**
> *(Đạt được kết quả X, đo lường bằng con số Y, thông qua giải pháp kỹ thuật Z)*

Mỗi dự án nên có từ **4 - 5 bullet points**, mỗi gạch đầu dòng giải quyết một bài toán kỹ thuật khác nhau:

1. **Bullet 1: Quy mô & Kiến trúc hệ thống (Architecture & Scope)**
   - Nêu số lượng endpoints, kiến trúc áp dụng (Repository & Service, layered architecture) để code tách bạch nghiệp vụ.
   - *Ví dụ mẫu*: *Designed ~122 RESTful API endpoints with a layered architecture (Repository & Service pattern).*
2. **Bullet 2: Tối ưu hiệu năng & Tính toàn vẹn dữ liệu (Performance & Database Concurrency)**
   - Nêu rõ vấn đề: Giải quyết N+1 query, Race condition / Overselling khi đặt hàng đồng thời.
   - Nêu giải pháp: Eager loading, Database transactions, Pessimistic locking (`lockForUpdate`).
   - Có chỉ số cụ thể: *Giảm truy vấn từ 22 xuống 6 (-73%)*.
3. **Bullet 3: Nghiệp vụ phức tạp / Bảo mật phân quyền (Business Logic & Security/RBAC)**
   - Nêu giải pháp phân quyền chuyên sâu: Custom RBAC engine cho nhiều module, per-staff direct permission overrides, quản lý qua Admin UI.
4. **Bullet 4: Tích hợp bên thứ 3 & Quy trình xử lý lỗi (Integrations & State Machine/Workflow)**
   - Cổng thanh toán (VNPay, SePay, Stripe) kèm IPN/Webhook verification, cơ chế idempotency.
   - Workflow trạng thái đơn hàng / hoàn trả (finite-state machine: 5-state return workflow).
   - Tích hợp AI (Gemini API / OpenAI) kèm Prompt caching và Rate limiting/Throttling middleware.
5. **Bullet 5: DevOps, Testing & Triển khai (DevOps, Testing & Deployment)**
   - Xác thực: Laravel Sanctum, JWT, OAuth2.
   - Containerization: Docker Compose (số lượng services: app, db, mailpit,...).
   - Quality & Deployment: Unit test (PHPUnit), CI/CD pipeline (GitHub Actions), triển khai live demo (Render, VPS).

---

## 3. BẢNG TỪ KHÓA ĐẮT GIÁ (POWER ACTION VERBS & TECH TERMS)

| Nhóm | Từ khóa hành động | Thuật ngữ kỹ thuật nên có |
| :--- | :--- | :--- |
| **Kiến trúc & Thiết kế** | *Designed, Architected, Implemented, Structured* | Layered Architecture, Repository & Service Pattern, RESTful API, Decoupling, Modular |
| **Hiệu năng & Tối ưu** | *Optimized, Benchmarked, Mitigated, Scaled* | N+1 Queries, Eager Loading, Caching, Query Execution Time, Throughput, Scalability |
| **Dữ liệu & Đồng thời** | *Enforced, Secured, Handled, Guarded* | Database Transactions, Pessimistic Locking (`lockForUpdate`), Race Condition, ACID |
| **Phân quyền & Bảo mật** | *Engineered, Granularized, Restricted, Overrode* | RBAC (Role-Based Access Control), Per-staff Permission Overrides, Token Auth, Sanitization |
| **Tích hợp & Dịch vụ** | *Integrated, Automated, Orchestrated, Hooked* | Webhook/IPN verification, State Workflow, Rate Limiting / Middleware, Third-party SDK |
| **DevOps & Kiểm thử** | *Containerized, Deployed, Covered, Streamlined* | Docker Compose, CI/CD Pipeline, Automated Tests (PHPUnit), Server-Side Rendering (SSR) |

---

## 4. TEMPLATE SẴN DÀNG ĐỂ ĐIỀN (MARKDOWN TEMPLATE)

```markdown
# [HỌ VÀ TÊN VIẾT HOA]
github.com/[username] | linkedin.com/in/[profile] | [email]@gmail.com
[Thành phố, Quốc gia] | (+84) [Số điện thoại]

## SUMMARY
[Chuyên ngành/Vị trí] với kinh nghiệm thực chiến tập trung vào [Core Tech]. Đã độc lập thiết kế và triển khai [số lượng] ứng dụng tiêu chuẩn production — [kể tên các hệ thống] — bao quát [các vấn đề cốt lõi: RESTful API, kiến trúc phân tầng, toàn vẹn dữ liệu, RBAC]. Có năng lực giải quyết bài toán solo end-to-end, đồng thời sẵn sàng thích ứng với quy trình làm việc nhóm chuyên nghiệp (Agile/Scrum, Git, Code Review).

## SKILLS
- **Languages**: [Ngôn ngữ 1, Ngôn ngữ 2...]
- **Frameworks & Libraries**: [Framework backend, frontend...]
- **Databases**: [MySQL, PostgreSQL, Redis...]
- **Architecture & Concepts**: RESTful API, OOP, SOLID, Repository & Service Pattern
- **Tools & Environment**: Git, Docker, GitHub Actions (CI/CD), Postman, [Dev tool khác]
- **Soft Skills**: Technical English (Đọc hiểu tài liệu chuyên sâu), Viết tài liệu kỹ thuật

## EDUCATION
**[Tên Trường Đại Học]** | [Năm Bắt Đầu] - [Năm Tốt Nghiệp Dự Kiến]
GPA: [X.XX/4.0] — [Bậc học & Chuyên ngành]

## PROJECTS

### [TÊN DỰ ÁN 1] - [Mô tả ngắn gọn thể loại] | [MM/YYYY - MM/YYYY]
*[Vị trí/Vai trò (Full-stack / Backend / Frontend Developer)]*
- **Stack**: [Liệt kê công nghệ]
- **GitHub**: [Link GitHub]
- **Live Demo**: [Link Live Demo]
- [Action Verb] [Số lượng API/Chức năng] với kiến trúc [Repository & Service / Clean Architecture] nhằm [Mục tiêu tách biệt logic].
- [Action Verb] tối ưu hóa truy vấn cơ sở dữ liệu bằng [Eager Loading / Caching], giảm thiểu [N+1 query từ A -> B (-X%)], đồng thời áp dụng [Pessimistic locking / Transactions] để xử lý [Race condition / Overselling].
- [Action Verb] hệ thống phân quyền [RBAC / Permissions] với [tính năng nổi bật: UI cấu hình, dynamic roles, override permissions].
- [Action Verb] tích hợp bên thứ ba [Payment / Notification / AI] kèm cơ chế [Webhook verification / Idempotency / Rate Limiting], xây dựng quy trình [Workflow trạng thái].
- [Action Verb] kiểm thử tự động với [PHPUnit / Jest], đóng gói bằng [Docker Compose] và thiết lập [CI/CD / Triển khai live demo].

### [TÊN DỰ ÁN 2] - [Mô tả ngắn gọn thể loại] | [MM/YYYY - MM/YYYY]
*[Vị trí/Vai trò]*
- **Stack**: [Liệt kê công nghệ]
- **GitHub**: [Link GitHub]
- **Live Demo**: [Link Live Demo]
- [Action Verb] ...
- [Action Verb] ...
- [Action Verb] ...
- [Action Verb] ...
```

---

## 5. MÃ NGUỒN LATEX GỐC (OVERLEAF / PDFLATEX TEMPLATE)

File mã nguồn đã được tạo sẵn tại: [cv_template.tex](file:///d:/Đồ%20Án%20GTTM/cv_template.tex)

### Cách sử dụng trên Overleaf hoặc máy cá nhân:
1. **Trên Overleaf**: Tạo một New Project -> Blank Project -> dán toàn bộ nội dung của [cv_template.tex](file:///d:/Đồ%20Án%20GTTM/cv_template.tex) vào `main.tex` -> Nhấn **Recompile** (trình biên dịch mặc định `pdfLaTeX`).
2. **Căn chỉnh độ dài vừa khít 1 trang**:
   - Nếu bị tràn sang trang 2: Giảm margin ở dòng `\addtolength{\textheight}{1.2in}` hoặc điều chỉnh font size từ `[11pt]` thành `[10pt]`, hoặc giảm khoảng cách dòng `\vspace{-2pt}` trong macro `\resumeItem`.
   - Các gói LaTeX chính được sử dụng: `titlesec`, `enumitem`, `hyperref`, `tabularx`, `glyphtounicode` (đảm bảo máy quét ATS đọc được text mà không bị lỗi font).

