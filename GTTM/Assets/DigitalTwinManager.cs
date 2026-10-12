using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
using TMPro;

/// <summary>
/// ===================================================================================
/// DỰ ÁN DIGITAL TWIN GA TÀU CAO TỐC - BỘ ĐIỀU KHIỂN ĐỒNG BỘ DỮ LIỆU THỜI GIAN THỰC
/// Tệp: DigitalTwinManager.cs
/// Chức năng:
///   1. Thu thập dữ liệu cảm biến thời tiết và mật độ hành khách từ Supabase REST API.
///   2. Gửi dữ liệu tới máy chủ AI FastAPI (localhost:8000) để suy luận công suất HVAC.
///   3. Trực quan hóa 3D: Đổi Material phát sáng (Emission) cho dàn lạnh điều hòa khi
///      quá tải (> 80%) và cập nhật độ trong suốt/màu sắc Heatmap sàn sảnh ga.
/// ===================================================================================
/// </summary>
public class DigitalTwinManager : MonoBehaviour
{
    [Header("1. CẤU HÌNH KẾT NỐI DỮ LIỆU CLOUD & AI")]
    [Tooltip("Đường dẫn Project URL của Supabase")]
    public string supabaseUrl = "https://dajourmarbthhfmkkjqs.supabase.co";

    [Tooltip("API Key (Anon hoặc Service Role Key) của Supabase")]
    public string supabaseApiKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRham91cm1hcmJ0aGhmbWtranFzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4ODIwMjgxMiwiZXhwIjoyMTAzNzc4ODEyfQ.C449gImZ3nRflRBoQ0PiPNdiXdQdzocOKG28Zn0gJho";

    [Tooltip("Đường dẫn API suy luận mô hình học máy cục bộ")]
    public string mlPredictEndpoint = "http://localhost:8000/predict";

    [Tooltip("Tần suất chu kỳ cập nhật dữ liệu tự động (giây)")]
    public float refreshInterval = 15.0f;

    [Header("2. ĐỐI TƯỢNG 3D VÀ VẬT LIỆU HIỂN THỊ (VISUAL MAPPING)")]
    [Tooltip("Danh sách các khối mô hình điều hòa HVAC trong nhà ga")]
    public GameObject[] hvacUnits;

    [Tooltip("Đối tượng mặt phẳng hiển thị bản đồ nhiệt (Heatmap Plane) sảnh ga")]
    public Renderer heatmapFloorRenderer;

    [Tooltip("Hệ thống hạt đốm nhiệt ngẫu nhiên (Tự động tạo nếu để trống)")]
    public ParticleSystem crowdHeatmapParticles;

    [Tooltip("Vật liệu mặc định của dàn lạnh HVAC khi hoạt động bình thường")]
    public Material defaultHvacMaterial;

    [Tooltip("Vật liệu phát sáng (Active Emission) cảnh báo khi HVAC tải cao > 80%")]
    public Material activeEmissionMaterial;

    [Header("3. GIAO DIỆN HIỂN THỊ TRỰC QUAN (UI TEXTMESHPRO)")]
    [Tooltip("Thành phần TextMeshPro hiển thị công suất dự báo HVAC trên màn hình")]
    public TextMeshProUGUI hvacPowerText;

    [Tooltip("Thành phần TextMeshPro hiển thị thông tin thời tiết & hành khách (Tùy chọn)")]
    public TextMeshProUGUI telemetryStatusText;

    [Header("4. MÔ PHỎNG ĐOÀN TÀU ĐẾN/ĐI (3D TRAIN SIMULATION)")]
    [Tooltip("Đoàn tàu 1 (Làn ray 1 - 'tau')")]
    public TrainAnimationController train1;

    [Tooltip("Đoàn tàu 2 (Làn ray 2 - 'tau2')")]
    public TrainAnimationController train2;

    [Header("4.1. CẤU HÌNH ĐỒNG BỘ CAMERA 3D & HEATMAP RADAR")]
    [Tooltip("Camera chính góc nhìn 3D ngang")]
    public Camera mainCamera;

    [Tooltip("Camera phụ góc nhìn Top-Down từ trần ga xuống sàn Heatmap")]
    public Camera topDownCamera;

    [Header("5. BẢNG THEO DÕI DỮ LIỆU THỜI GIAN THỰC (LIVE TELEMETRY)")]
    [SerializeField] private float currentTemp = 25.0f;
    [SerializeField] private float currentHumidity = 65.0f;
    [SerializeField] private int currentPassengerCount = 300;
    [SerializeField] private string currentTrainId = "NONE";
    [SerializeField] private float predictedHvacPower = 45.0f;
    [SerializeField] private float predictedVentPower = 20.0f;
    [SerializeField] private float predictedLightPower = 80.0f;
    [SerializeField] private bool isHighLoadAlarm = false;
    [SerializeField] private float sessionAiKwh = 0f;
    [SerializeField] private float sessionTraditionalKwh = 0f;
    [SerializeField] private float savingsPercent = 0f;

    private const float HvacMaxKw = 120f;
    private const float TraditionalHvacPct = 85f;
    private float lastEnergyStamp = -1f;

    private Material dynamicHeatmapMat;
    private Texture2D proceduralHeatmapTex;
    private Color32[] heatmapPixelBuffer;
    private const int HEATMAP_RES = 128; // Độ phân giải Texture bản đồ nhiệt (128x128 cho độ mịn tối đa và cực nhẹ WebGL)

    void Start()
    {
        // Tự động gán Main Camera nếu chưa gán
        if (mainCamera == null) mainCamera = Camera.main;
        if (topDownCamera == null)
        {
            GameObject cam2Obj = GameObject.Find("TopDownCamera") ?? GameObject.Find("Camera2");
            if (cam2Obj != null) topDownCamera = cam2Obj.GetComponent<Camera>();
        }

        // Khởi tạo Texture2D động cho bản đồ nhiệt dạng vết loan (Gaussian Blur Heatmap)
        if (heatmapFloorRenderer != null)
        {
            dynamicHeatmapMat = heatmapFloorRenderer.material;
            
            proceduralHeatmapTex = new Texture2D(HEATMAP_RES, HEATMAP_RES, TextureFormat.RGBA32, false);
            proceduralHeatmapTex.filterMode = FilterMode.Bilinear;
            proceduralHeatmapTex.wrapMode = TextureWrapMode.Clamp;
            heatmapPixelBuffer = new Color32[HEATMAP_RES * HEATMAP_RES];

            // Gán Texture vào Material sàn ga
            if (dynamicHeatmapMat.HasProperty("_BaseMap")) dynamicHeatmapMat.SetTexture("_BaseMap", proceduralHeatmapTex);
            if (dynamicHeatmapMat.HasProperty("_MainTex")) dynamicHeatmapMat.SetTexture("_MainTex", proceduralHeatmapTex);
            dynamicHeatmapMat.color = Color.white;
        }

        // Tự động tìm và cấu hình các đoàn tàu 'tau' và 'tau2' nếu chưa gán
        SetupTrainControllers();

        Debug.Log("<color=#00FF00><b>[DIGITAL TWIN MANAGER]</b> Đã khởi tạo thành công hệ thống đồng bộ dữ liệu thời gian thực!</color>");
        
        // Bắt đầu chu kỳ Coroutine lặp lại mỗi 15 giây
        StartCoroutine(DigitalTwinUpdateLoop());
    }

    void Update()
    {
        // Phím 'C' hoặc phím '1' / '2': Chuyển đổi linh hoạt giữa Camera 1 (3D Ngang) và Camera 2 (Top-Down Heatmap)
        if (Input.GetKeyDown(KeyCode.C))
        {
            ToggleCameraView();
        }
        else if (Input.GetKeyDown(KeyCode.Alpha1))
        {
            SwitchCameraMode(1);
        }
        else if (Input.GetKeyDown(KeyCode.Alpha2))
        {
            SwitchCameraMode(2);
        }

        // Phím tắt 'T' trên bàn phím: Kích hoạt tức thời kịch bản Tàu cập bến & Quá tải (Dành cho thuyết trình/Demo)
        if (Input.GetKeyDown(KeyCode.T))
        {
            Debug.Log("<color=#FF3D00><b>[DEMO MANUAL TRIGGER]</b> Kích hoạt mô phỏng Tàu cập bến & Lượng khách tăng đột biến!</color>");
            currentPassengerCount = 1450;
            currentTemp = 38.5f;
            currentHumidity = 85.0f;
            currentTrainId = "TRAIN_2";
            StartCoroutine(ManualTriggerDemoRoutine());
        }
    }

    /// <summary>
    /// Hàm nhận tín hiệu từ WebGL hoặc Bàn phím để chuyển đổi góc nhìn Camera (1: 3D Ngang | 2: Top-Down Heatmap)
    /// </summary>
    public void SwitchCameraMode(int camIndex)
    {
        if (mainCamera == null) mainCamera = Camera.main;
        if (topDownCamera == null)
        {
            GameObject cam2Obj = GameObject.Find("TopDownCamera") ?? GameObject.Find("Camera2");
            if (cam2Obj != null) topDownCamera = cam2Obj.GetComponent<Camera>();
        }

        if (camIndex == 1)
        {
            if (mainCamera != null) mainCamera.gameObject.SetActive(true);
            if (topDownCamera != null) topDownCamera.gameObject.SetActive(false);
            Debug.Log("[CAMERA] Đã chuyển sang Camera 1: Góc nhìn 3D Ngang");
        }
        else if (camIndex == 2)
        {
            if (mainCamera != null) mainCamera.gameObject.SetActive(false);
            if (topDownCamera != null) topDownCamera.gameObject.SetActive(true);
            Debug.Log("[CAMERA] Đã chuyển sang Camera 2: Góc nhìn Top-Down Radar Heatmap");
        }
    }

    public void ToggleCameraView()
    {
        if (mainCamera != null && topDownCamera != null)
        {
            bool mainActive = mainCamera.gameObject.activeSelf;
            SwitchCameraMode(mainActive ? 2 : 1);
        }
    }


    private IEnumerator ManualTriggerDemoRoutine()
    {
        yield return StartCoroutine(RequestHvacPrediction());
        Apply3DVisualUpdates();
    }

    /// <summary>
    /// Tự động tìm kiếm các đối tượng tàu 'tau' và 'tau2' và cấu hình hướng chạy
    /// </summary>
    private void SetupTrainControllers()
    {
        if (train1 == null)
        {
            GameObject t1 = GameObject.Find("tau");
            if (t1 != null)
            {
                train1 = t1.GetComponent<TrainAnimationController>() ?? t1.AddComponent<TrainAnimationController>();
                train1.invertDirection = false;
            }
        }

        if (train2 == null)
        {
            GameObject t2 = GameObject.Find("tau2");
            if (t2 != null)
            {
                train2 = t2.GetComponent<TrainAnimationController>() ?? t2.AddComponent<TrainAnimationController>();
                train2.invertDirection = true; // Tàu 2 chạy ngược hướng với Tàu 1
            }
        }
    }

    /// <summary>
    /// Tự động tạo hệ thống hạt phát sáng (Particles) phân bố ngẫu nhiên trên toàn bộ mặt sàn ga
    /// </summary>
    private void SetupCrowdParticleSystem()
    {
        if (crowdHeatmapParticles != null || heatmapFloorRenderer == null) return;

        GameObject psObj = new GameObject("Crowd_Heatmap_Dots");
        psObj.transform.SetParent(heatmapFloorRenderer.transform, false);
        psObj.transform.localPosition = new Vector3(0, 0.05f, 0); // Đặt cao hơn mặt sàn 5cm

        crowdHeatmapParticles = psObj.AddComponent<ParticleSystem>();
        ParticleSystem.MainModule main = crowdHeatmapParticles.main;
        main.loop = true;
        main.startLifetime = 3.0f; // Thời gian sống cố định 3 giây
        main.startSpeed = new ParticleSystem.MinMaxCurve(0.05f, 0.25f);
        main.startSize = new ParticleSystem.MinMaxCurve(0.35f, 0.60f);
        main.maxParticles = 3000;
        main.simulationSpace = ParticleSystemSimulationSpace.Local;

        // Định hình vùng phát hạt khớp với kích thước mặt sàn
        ParticleSystem.ShapeModule shape = crowdHeatmapParticles.shape;
        shape.shapeType = ParticleSystemShapeType.Box;
        Bounds bounds = heatmapFloorRenderer.bounds;
        shape.scale = new Vector3(bounds.size.x, bounds.size.z, 0.1f);
        shape.rotation = new Vector3(90, 0, 0); // Hướng hạt nổi lên mặt sàn

        // Tốc độ phát hạt khởi tạo
        ParticleSystem.EmissionModule emission = crowdHeatmapParticles.emission;
        emission.rateOverTime = 50f;

        // Hiệu ứng mờ dần lúc sinh ra và biến mất (Fade in/out)
        ParticleSystem.ColorOverLifetimeModule colorMod = crowdHeatmapParticles.colorOverLifetime;
        colorMod.enabled = true;
        Gradient grad = new Gradient();
        grad.SetKeys(
            new GradientColorKey[] { new GradientColorKey(Color.white, 0.0f), new GradientColorKey(Color.white, 1.0f) },
            new GradientAlphaKey[] { new GradientAlphaKey(0.0f, 0.0f), new GradientAlphaKey(0.85f, 0.3f), new GradientAlphaKey(0.85f, 0.7f), new GradientAlphaKey(0.0f, 1.0f) }
        );
        colorMod.color = grad;

        // Render billboard mềm mại
        ParticleSystemRenderer psRenderer = psObj.GetComponent<ParticleSystemRenderer>();
        if (activeEmissionMaterial != null)
        {
            psRenderer.material = activeEmissionMaterial;
        }

        crowdHeatmapParticles.Play();
    }

    /// <summary>
    /// Coroutine chu kỳ chính: Chạy liên tục mỗi 15 giây để đồng bộ và cập nhật 3D.
    /// </summary>
    private IEnumerator DigitalTwinUpdateLoop()
    {
        while (true)
        {
            Debug.Log($"<color=#00E5FF><b>[BƯỚC 1/3]</b> Bắt đầu chu kỳ đồng bộ mới lúc: {DateTime.Now:HH:mm:ss}...</color>");

            // ---------------------------------------------------------------------------------
            // BƯỚC A: TRUY VẤN DỮ LIỆU MỚI NHẤT TỪ SUPABASE REST API
            // ---------------------------------------------------------------------------------
            yield return StartCoroutine(FetchLatestSupabaseData());

            // ---------------------------------------------------------------------------------
            // BƯỚC B: GỬI DỮ LIỆU SANG MÁY CHỦ FASTAPI ĐỂ SUY LUẬN CÔNG SUẤT HVAC
            // ---------------------------------------------------------------------------------
            yield return StartCoroutine(RequestHvacPrediction());

            // ---------------------------------------------------------------------------------
            // BƯỚC C: CẬP NHẬT TRẠNG THÁI HIỂN THỊ VẬT LÝ TRÊN MÔ HÌNH 3D (UNITY SCENE)
            // ---------------------------------------------------------------------------------
            Apply3DVisualUpdates();

            // Chờ hết khoảng thời gian refreshInterval (15 giây) trước khi lặp lại
            yield return new WaitForSeconds(refreshInterval);
        }
    }

    /// <summary>
    /// Bước A: Gọi GET request tới Supabase để lấy giá trị thời tiết và hành khách mới nhất.
    /// </summary>
    private IEnumerator FetchLatestSupabaseData()
    {
        // 1. Lấy dữ liệu thời tiết mới nhất từ bảng weather_logs
        string weatherUrl = $"{supabaseUrl.TrimEnd('/')}/rest/v1/weather_logs?select=temp,humidity&order=id.desc&limit=1";
        
        using (UnityWebRequest reqWeather = UnityWebRequest.Get(weatherUrl))
        {
            reqWeather.SetRequestHeader("apikey", supabaseApiKey);
            reqWeather.SetRequestHeader("Authorization", $"Bearer {supabaseApiKey}");
            reqWeather.timeout = 8;

            yield return reqWeather.SendWebRequest();

            if (reqWeather.result == UnityWebRequest.Result.Success)
            {
                string json = reqWeather.downloadHandler.text;
                // Parse mảng JSON trả về dạng [{"temp":35.0,"humidity":50.0}]
                WeatherLogItem item = ParseWeatherLogJson(json);
                if (item != null)
                {
                    currentTemp = item.temp;
                    currentHumidity = item.humidity;
                    Debug.Log($"<color=#76FF03> -> [SUPABASE WEATHER] Nhiệt độ: {currentTemp}°C | Độ ẩm: {currentHumidity}%</color>");
                }
            }
            else
            {
                Debug.LogWarning($"[SUPABASE ERROR] Lỗi lấy dữ liệu weather_logs: {reqWeather.error} ({reqWeather.responseCode})");
            }
        }

        // 2. Lấy dữ liệu mật độ hành khách và mã chuyến tàu mới nhất từ bảng passenger_density_logs
        string densityUrl = $"{supabaseUrl.TrimEnd('/')}/rest/v1/passenger_density_logs?select=passenger_count,train_id&order=id.desc&limit=1";
        
        using (UnityWebRequest reqDensity = UnityWebRequest.Get(densityUrl))
        {
            reqDensity.SetRequestHeader("apikey", supabaseApiKey);
            reqDensity.SetRequestHeader("Authorization", $"Bearer {supabaseApiKey}");
            reqDensity.timeout = 8;

            yield return reqDensity.SendWebRequest();

            if (reqDensity.result == UnityWebRequest.Result.Success)
            {
                string json = reqDensity.downloadHandler.text;
                PassengerDensityItem pItem = ParsePassengerDensityJson(json);
                if (pItem != null)
                {
                    currentPassengerCount = pItem.passenger_count;
                    if (!string.IsNullOrEmpty(pItem.train_id))
                    {
                        currentTrainId = pItem.train_id;
                    }
                    Debug.Log($"<color=#76FF03> -> [SUPABASE DENSITY] Mật độ: {currentPassengerCount} người | Chuyến tàu: {currentTrainId}</color>");
                }
            }
            else
            {
                Debug.LogWarning($"[SUPABASE ERROR] Lỗi lấy dữ liệu passenger_density_logs: {reqDensity.error}");
            }
        }
    }

    /// <summary>
    /// Bước B: Gửi POST request tới máy chủ FastAPI Backend để chạy trực tiếp mô hình 'digital_twin_hvac_model.pkl'.
    /// Kết quả công suất HVAC và cảnh báo tải cao được tính toán 100% từ mô hình Machine Learning thực tế.
    /// </summary>
    private IEnumerator RequestHvacPrediction()
    {
        string endpoint = mlPredictEndpoint;

        // Khi chạy trên WebGL (Online), luôn gọi qua Reverse Proxy /api/predict
        if (Application.platform == RuntimePlatform.WebGLPlayer)
        {
            endpoint = "/api/predict";
        }

        // Đóng gói JSON gửi sang FastAPI Backend chuẩn hóa dấu chấm thập phân (Invariant Culture)
        string tempStr = currentTemp.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture);
        string humStr = currentHumidity.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture);
        string jsonPayload = $"{{\"temp\":{tempStr},\"humidity\":{humStr},\"passenger_count\":{currentPassengerCount}}}";
        byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonPayload);

        using (UnityWebRequest req = new UnityWebRequest(endpoint, "POST"))
        {
            req.uploadHandler = new UploadHandlerRaw(bodyRaw);
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");
            req.timeout = 5;

            yield return req.SendWebRequest();

            if (req.result == UnityWebRequest.Result.Success)
            {
                string responseJson = req.downloadHandler.text;
                FastApiPredictionResponse result = JsonUtility.FromJson<FastApiPredictionResponse>(responseJson);
                
                if (result != null)
                {
                    // Lấy chính xác giá trị công suất tối ưu được dự báo từ file .pkl
                    predictedHvacPower = result.predicted_hvac_power;
                    isHighLoadAlarm = result.is_high_load;
                    if (result.predicted_ventilation_power > 0f) predictedVentPower = result.predicted_ventilation_power;
                    if (result.predicted_lighting_power > 0f) predictedLightPower = result.predicted_lighting_power;
                    if (result.session_ai_kwh > 0f)
                    {
                        sessionAiKwh = result.session_ai_kwh;
                        sessionTraditionalKwh = result.session_traditional_kwh;
                        savingsPercent = result.savings_percent;
                    }
                    else
                    {
                        AccumulateLocalEnergy();
                    }
                    
                    if (isHighLoadAlarm)
                    {
                        Debug.Log($"<color=#FF3D00><b>[MÔ HÌNH PKL -> FASTAPI]</b> Công suất HVAC tối ưu: <b>{predictedHvacPower:F2}%</b> - <color=red><b>CẢNH BÁO TẢI CAO</b></color></color>");
                    }
                    else
                    {
                        Debug.Log($"<color=#00E676><b>[MÔ HÌNH PKL -> FASTAPI]</b> Công suất HVAC tối ưu: <b>{predictedHvacPower:F2}%</b></color>");
                    }
                }
            }
            else
            {
                Debug.LogError($"<color=#FF1744><b>[LỖI GỌI MÔ HÌNH PKL]</b> Không thể kết nối tới FastAPI Backend ({endpoint}): {req.error}. Hãy kiểm tra uvicorn app:app.</color>");
            }
        }
    }

    /// <summary>
    /// Bước C: Cập nhật vật liệu và hiệu ứng hình ảnh 3D trong Scene.
    /// </summary>
    private void Apply3DVisualUpdates()
    {
        // 1. Cập nhật trạng thái phát sáng cho các khối điều hòa HVAC
        Material targetHvacMat = (predictedHvacPower > 80.0f && activeEmissionMaterial != null) 
            ? activeEmissionMaterial 
            : defaultHvacMaterial;

        if (hvacUnits != null && hvacUnits.Length > 0 && targetHvacMat != null)
        {
            foreach (GameObject hvac in hvacUnits)
            {
                if (hvac == null) continue;
                
                Renderer rend = hvac.GetComponent<Renderer>();
                if (rend != null)
                {
                    rend.material = targetHvacMat;
                }
                else
                {
                    // Trường hợp mô hình gồm nhiều Mesh con bên trong (LOD/Children)
                    Renderer[] childRends = hvac.GetComponentsInChildren<Renderer>();
                    foreach (Renderer cr in childRends)
                    {
                        cr.material = targetHvacMat;
                    }
                }
            }
        }

        // 2. Cập nhật Heatmap dạng vết loan nhiệt Gaussian (Sports/Crowd Heatmap)
        UpdateGaussianHeatmapTexture();

        // 3. Cập nhật giao diện TextMeshPro hiển thị trực tiếp trên màn hình (WebGL Responsive UI)
        if (hvacPowerText != null)
        {
            string powerFormatted = predictedHvacPower.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture);
            string displayText;

            // Nếu công suất > 80%: Con số màu Đỏ + CẢNH BÁO TẢI CAO màu Đỏ
            if (predictedHvacPower > 80.0f)
            {
                displayText = $"Công suất HVAC tối ưu: <color=#FF3333><b>{powerFormatted}%</b></color>\n<color=#FF3333><b>CẢNH BÁO TẢI CAO</b></color>";
            }
            else
            {
                displayText = $"Công suất HVAC tối ưu: <color=#00FF66><b>{powerFormatted}%</b></color>";
            }

            displayText += $"\nThông gió: {predictedVentPower:0.0}% | Chiếu sáng: {predictedLightPower:0.0}%";
            displayText += $"\nĐiện năng AI: {sessionAiKwh:0.000} kWh | Truyền thống: {sessionTraditionalKwh:0.000} kWh";
            displayText += $"\n<color=#4FC3F7>Tiết kiệm: {savingsPercent:0.0}%</color>";

            // Gán chuỗi kết quả vào TextMeshPro
            hvacPowerText.text = displayText;
        }

        if (telemetryStatusText != null)
        {
            string tStr = currentTemp.ToString("0.0", System.Globalization.CultureInfo.InvariantCulture);
            string hStr = currentHumidity.ToString("0.0", System.Globalization.CultureInfo.InvariantCulture);
            telemetryStatusText.text = $"Nhiệt độ: {tStr}°C | Độ ẩm: {hStr}%\nHành khách: {currentPassengerCount} người";
        }

        // 4. Điều khiển lịch trình Tàu 1 và Tàu 2 độc lập theo dữ liệu thời gian thực
        if (currentTrainId.StartsWith("TRAIN_1"))
        {
            if (train1 != null)
            {
                if (currentTrainId == "TRAIN_1") train1.CallTrainArrival();
                else if (currentTrainId == "TRAIN_1_LEAVING") train1.CallTrainDeparture();
            }
            if (train2 != null) train2.CallTrainDeparture();
        }
        else if (currentTrainId.StartsWith("TRAIN_2"))
        {
            if (train2 != null)
            {
                if (currentTrainId == "TRAIN_2") train2.CallTrainArrival();
                else if (currentTrainId == "TRAIN_2_LEAVING") train2.CallTrainDeparture();
            }
            if (train1 != null) train1.CallTrainDeparture();
        }
        else
        {
            // Ga vắng / Khoảng nghỉ yên tĩnh giữa 2 chuyến
            if (train1 != null) train1.CallTrainDeparture();
            if (train2 != null) train2.CallTrainDeparture();
        }
    }

    /// <summary>
    /// Tạo và cập nhật bản đồ nhiệt vết loan Gaussian phân bổ chính xác theo vị trí ke ga và sảnh
    /// </summary>
    private void UpdateGaussianHeatmapTexture()
    {
        if (proceduralHeatmapTex == null) return;

        float[,] intensityGrid = new float[HEATMAP_RES, HEATMAP_RES];
        int count = Mathf.Clamp(currentPassengerCount, 0, 2000);

        // Phân bổ tâm nhiệt theo từng chuyến tàu và giai đoạn
        Vector2[] hotCenters;
        if (currentTrainId.StartsWith("TRAIN_1"))
        {
            // Tàu 1 cập bến: Nhiệt tập trung dọc Ke ga 1
            hotCenters = new Vector2[] {
                new Vector2(0.25f, 0.30f),
                new Vector2(0.50f, 0.35f),
                new Vector2(0.75f, 0.30f)
            };
        }
        else if (currentTrainId.StartsWith("TRAIN_2"))
        {
            // Tàu 2 cập bến: Nhiệt bùng nổ tập trung dọc Ke ga 2 và lan sang toàn sảnh
            hotCenters = new Vector2[] {
                new Vector2(0.25f, 0.70f),
                new Vector2(0.50f, 0.65f),
                new Vector2(0.75f, 0.70f),
                new Vector2(0.50f, 0.50f)
            };
        }
        else
        {
            // Ga vắng / Khách di chuyển rải rác quanh sảnh trung tâm
            hotCenters = new Vector2[] {
                new Vector2(0.35f, 0.50f),
                new Vector2(0.50f, 0.50f),
                new Vector2(0.65f, 0.50f)
            };
        }

        // Seed giả lập sự di chuyển tự nhiên của hành khách theo thời gian
        int seed = (int)(Time.time * 0.3f);
        System.Random rnd = new System.Random(seed);

        int radius = 9;
        float sigma = 4.2f;
        float twoSigmaSq = 2f * sigma * sigma;

        for (int i = 0; i < count; i++)
        {
            Vector2 center = hotCenters[i % hotCenters.Length];
            
            float u1 = (float)rnd.NextDouble();
            float u2 = (float)rnd.NextDouble();
            float rNorm1 = Mathf.Sqrt(-2.0f * Mathf.Log(Mathf.Max(0.0001f, u1))) * Mathf.Sin(2.0f * Mathf.PI * u2);
            float rNorm2 = Mathf.Sqrt(-2.0f * Mathf.Log(Mathf.Max(0.0001f, u1))) * Mathf.Cos(2.0f * Mathf.PI * u2);

            int cx = Mathf.Clamp((int)((center.x + rNorm1 * 0.12f) * HEATMAP_RES), 0, HEATMAP_RES - 1);
            int cy = Mathf.Clamp((int)((center.y + rNorm2 * 0.22f) * HEATMAP_RES), 0, HEATMAP_RES - 1);

            for (int dx = -radius; dx <= radius; dx++)
            {
                int x = cx + dx;
                if (x < 0 || x >= HEATMAP_RES) continue;

                for (int dy = -radius; dy <= radius; dy++)
                {
                    int y = cy + dy;
                    if (y < 0 || y >= HEATMAP_RES) continue;

                    float distSq = dx * dx + dy * dy;
                    if (distSq <= radius * radius)
                    {
                        intensityGrid[x, y] += Mathf.Exp(-distSq / twoSigmaSq);
                    }
                }
            }
        }

        // Xác định tỷ lệ tải hành khách từ 0.0 (vắng) đến 1.0 (quá tải)
        float crowdRatio = Mathf.Clamp01(currentPassengerCount / 1300.0f);

        // Chuẩn hóa mức độ nhạy nhiệt để luôn hiển thị rõ cả 3 dải màu Xanh -> Vàng -> Đỏ
        float sensitivity = Mathf.Lerp(10.0f, 35.0f, crowdRatio);

        for (int y = 0; y < HEATMAP_RES; y++)
        {
            for (int x = 0; x < HEATMAP_RES; x++)
            {
                // Cường độ điểm nhiệt từ 0.0 đến 1.0
                float val = Mathf.Clamp01(intensityGrid[x, y] / sensitivity);
                Color32 pixelColor;

                if (val <= 0.03f)
                {
                    // Vùng không có người: Trong suốt hoàn toàn
                    pixelColor = new Color32(0, 0, 0, 0);
                }
                else
                {
                    // Kết hợp cường độ cục bộ (val) và mật độ tổng (crowdRatio) để ra màu chính xác
                    float heatScore = Mathf.Clamp01(val * 0.4f + crowdRatio * 0.6f);

                    if (heatScore < 0.35f)
                    {
                        // 🟢 DẢI 1: XANH LÁ CÂY (Vắng khách < 400 người)
                        float t = heatScore / 0.35f;
                        Color c = Color.Lerp(new Color(0.0f, 0.9f, 0.3f, 0.35f), new Color(0.3f, 1.0f, 0.1f, 0.75f), t);
                        pixelColor = (Color32)c;
                    }
                    else if (heatScore < 0.70f)
                    {
                        // 🟡 DẢI 2: VÀNG TƯƠI ➔ CAM ĐẬM (Lượng khách vừa 400 - 900 người)
                        float t = (heatScore - 0.35f) / 0.35f;
                        Color c = Color.Lerp(new Color(1.0f, 0.95f, 0.0f, 0.85f), new Color(1.0f, 0.50f, 0.0f, 0.92f), t);
                        pixelColor = (Color32)c;
                    }
                    else
                    {
                        // 🔴 DẢI 3: ĐỎ RỰC PHÁT QUANG (Đông đúc / Quá tải > 900 người)
                        float t = (heatScore - 0.70f) / 0.30f;
                        Color c = Color.Lerp(new Color(1.0f, 0.35f, 0.0f, 0.95f), new Color(1.0f, 0.0f, 0.0f, 1.0f), t);
                        pixelColor = (Color32)c;
                    }
                }

                heatmapPixelBuffer[y * HEATMAP_RES + x] = pixelColor;
            }
        }

        proceduralHeatmapTex.SetPixels32(heatmapPixelBuffer);
        proceduralHeatmapTex.Apply(false);

        // Cập nhật màu phát quang (Emission) tổng thể cho sàn ga theo đúng 3 mức màu
        if (dynamicHeatmapMat != null)
        {
            Color overallColor;
            if (crowdRatio < 0.35f) overallColor = new Color(0.1f, 0.9f, 0.2f, 0.6f);      // Xanh
            else if (crowdRatio < 0.70f) overallColor = new Color(1.0f, 0.85f, 0.0f, 0.75f); // Vàng
            else overallColor = new Color(1.0f, 0.05f, 0.05f, 0.9f);                        // Đỏ

            if (dynamicHeatmapMat.HasProperty("_Color")) dynamicHeatmapMat.SetColor("_Color", Color.white);
            if (dynamicHeatmapMat.HasProperty("_EmissionColor")) dynamicHeatmapMat.SetColor("_EmissionColor", overallColor * (crowdRatio * 0.8f));
        }
    }

    // =================================================================================
    // CÁC LỚP TRỢ GIÚP GIẢI MÃ JSON (JSON SERIALIZATION HELPERS)
    // =================================================================================
    [System.Serializable]
    private class FastApiPredictionResponse
    {
        public string status;
        public float predicted_hvac_power;
        public float predicted_ventilation_power;
        public float predicted_lighting_power;
        public bool is_high_load;
        public float session_ai_kwh;
        public float session_traditional_kwh;
        public float savings_percent;
        public string timestamp;
    }

    [System.Serializable]
    private class WeatherLogItem
    {
        public float temp;
        public float humidity;
    }

    [System.Serializable]
    private class PassengerDensityItem
    {
        public int passenger_count;
        public string train_id;
    }

    /// <summary>
    /// Tích lũy kWh cục bộ khi API chưa trả session (Editor / lần gọi đầu).
    /// Công thức: kWh = (công suất % / 100) × 120 kW × Δt (giờ). Truyền thống cố định 85%.
    /// </summary>
    private void AccumulateLocalEnergy()
    {
        float now = Time.unscaledTime;
        float dtHours = (lastEnergyStamp < 0f) ? (refreshInterval / 3600f) : Mathf.Max(1f / 3600f, (now - lastEnergyStamp) / 3600f);
        lastEnergyStamp = now;

        sessionAiKwh += (predictedHvacPower / 100f) * HvacMaxKw * dtHours;
        sessionTraditionalKwh += (TraditionalHvacPct / 100f) * HvacMaxKw * dtHours;
        if (sessionTraditionalKwh > 0.0001f)
        {
            savingsPercent = Mathf.Max(0f, (sessionTraditionalKwh - sessionAiKwh) / sessionTraditionalKwh * 100f);
        }
    }

    /// <summary>
    /// Phân tích chuỗi mảng JSON dạng [{"temp":34.5,"humidity":70.0}] từ PostgREST.
    /// </summary>
    private WeatherLogItem ParseWeatherLogJson(string jsonArray)
    {
        try
        {
            string clean = jsonArray.Trim();
            if (clean.StartsWith("[") && clean.EndsWith("]"))
            {
                clean = clean.Substring(1, clean.Length - 2).Trim();
            }
            if (string.IsNullOrEmpty(clean)) return null;
            return JsonUtility.FromJson<WeatherLogItem>(clean);
        }
        catch
        {
            return null;
        }
    }

    /// <summary>
    /// Phân tích chuỗi mảng JSON dạng [{"passenger_count":850}] từ PostgREST.
    /// </summary>
    private PassengerDensityItem ParsePassengerDensityJson(string jsonArray)
    {
        try
        {
            string clean = jsonArray.Trim();
            if (clean.StartsWith("[") && clean.EndsWith("]"))
            {
                clean = clean.Substring(1, clean.Length - 2).Trim();
            }
            if (string.IsNullOrEmpty(clean)) return null;
            return JsonUtility.FromJson<PassengerDensityItem>(clean);
        }
        catch
        {
            return null;
        }
    }
}
