using UnityEngine;

/// <summary>
/// ===================================================================================
/// DỰ ÁN DIGITAL TWIN GA TÀU CAO TỐC - BỘ ĐIỀU KHIỂN CAMERA 3D TƯƠNG TÁC (CHUYÊN BIỆT WEBGL)
/// Tệp: CameraController.cs
/// Chức năng:
///   1. Giữ chuột phải hoặc chuột trái kéo để xoay 360 độ ngắm toàn cảnh ga tàu.
///   2. Lăn chuột giữa để Zoom In / Zoom Out.
///   3. Phím WASD hoặc phím Mũi tên để di chuyển góc nhìn.
///   4. Phím R để khôi phục góc nhìn ban đầu.
/// ===================================================================================
/// </summary>
public class CameraController : MonoBehaviour
{
    [Header("1. ĐIỀU CHỈNH ĐỘ NHẠY (SENSITIVITY)")]
    [Tooltip("Tốc độ xoay camera khi rê chuột")]
    public float rotateSpeed = 0.25f;

    [Tooltip("Tốc độ phóng to / thu nhỏ khi cuộn chuột")]
    public float zoomSpeed = 20.0f;

    [Tooltip("Tốc độ di chuyển camera bằng phím WASD")]
    public float moveSpeed = 15.0f;

    [Header("2. GIỚI HẠN GÓC NHÌN (PITCH BOUNDS)")]
    public float minPitch = 5.0f;
    public float maxPitch = 88.0f;

    private Vector3 initialPosition;
    private Quaternion initialRotation;
    private Vector3 lastMousePosition;
    private float currentYaw;
    private float currentPitch;

    void Start()
    {
        // Lưu vị trí và góc nhìn mặc định ban đầu
        initialPosition = transform.position;
        initialRotation = transform.rotation;

        Vector3 euler = transform.eulerAngles;
        currentPitch = euler.x;
        currentYaw = euler.y;
    }

    void Update()
    {
        // =========================================================================
        // A. XOAY GÓC NHÌN (ROTATE CAMERA) - TƯƠNG THÍCH TUYỆT ĐỐI WEBGL
        // =========================================================================
        if (Input.GetMouseButtonDown(0) || Input.GetMouseButtonDown(1))
        {
            lastMousePosition = Input.mousePosition;
        }

        if (Input.GetMouseButton(0) || Input.GetMouseButton(1))
        {
            Vector3 delta = Input.mousePosition - lastMousePosition;
            lastMousePosition = Input.mousePosition;

            // Tính toán góc quay mới mượt mà
            currentYaw += delta.x * rotateSpeed;
            currentPitch -= delta.y * rotateSpeed;
            currentPitch = Mathf.Clamp(currentPitch, minPitch, maxPitch);

            transform.rotation = Quaternion.Euler(currentPitch, currentYaw, 0.0f);
        }

        // =========================================================================
        // B. PHÓNG TO / THU NHỎ (ZOOM IN / OUT)
        // =========================================================================
        float scroll = Input.GetAxis("Mouse ScrollWheel");
        if (Mathf.Abs(scroll) > 0.0001f)
        {
            transform.position += transform.forward * scroll * zoomSpeed;
        }

        // Hỗ trợ phím Q / E để Zoom lên xuống nếu máy không có chuột lăn
        if (Input.GetKey(KeyCode.E)) transform.position += transform.forward * moveSpeed * Time.deltaTime;
        if (Input.GetKey(KeyCode.Q)) transform.position -= transform.forward * moveSpeed * Time.deltaTime;

        // =========================================================================
        // C. DI CHUYỂN CAMERA (PAN / FLY) BẰNG PHÍM W, A, S, D
        // =========================================================================
        float h = 0f;
        float v = 0f;

        if (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow)) v += 1f;
        if (Input.GetKey(KeyCode.S) || Input.GetKey(KeyCode.DownArrow)) v -= 1f;
        if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) h += 1f;
        if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) h -= 1f;

        if (h != 0f || v != 0f)
        {
            Vector3 fwd = transform.forward;
            Vector3 rgt = transform.right;

            fwd.y = 0f;
            rgt.y = 0f;
            fwd.Normalize();
            rgt.Normalize();

            Vector3 moveDir = (fwd * v + rgt * h).normalized;
            transform.position += moveDir * moveSpeed * Time.deltaTime;
        }

        // =========================================================================
        // D. PHÍM 'R' ĐỂ RESET VỀ GÓC NHÌN BAN ĐẦU
        // =========================================================================
        if (Input.GetKeyDown(KeyCode.R))
        {
            transform.position = initialPosition;
            transform.rotation = initialRotation;
            Vector3 euler = initialRotation.eulerAngles;
            currentPitch = euler.x;
            currentYaw = euler.y;
        }
    }
}
