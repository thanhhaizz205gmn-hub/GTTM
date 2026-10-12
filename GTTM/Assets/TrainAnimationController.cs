using UnityEngine;

/// <summary>
/// ===================================================================================
/// DỰ ÁN DIGITAL TWIN GA TÀU CAO TỐC - BỘ ĐIỀU KHIỂN CHUYỂN ĐỘNG TÀU CHUẨN ĐƯỜNG RAY
/// Tệp: TrainAnimationController.cs
/// Chức năng:
///   1. Đường ray ga tàu chạy theo trục X (Station Track X-Axis).
///   2. Khóa cứng trục Y (độ cao) và trục Z (vị trí làn ray) để tàu không bao giờ trượt ngang.
///   3. Cho phép tàu lướt êm ái 100% từ ngoài xa vào ke ga đón khách và rời ga ra xa.
/// ===================================================================================
/// </summary>
public class TrainAnimationController : MonoBehaviour
{
    public enum TrackAxisMode { Truc_X_Chuan_GaTau, Truc_Z_TheGioi, Theo_Huong_DauTau }

    [Header("1. THIẾT LẬP TRỤC ĐƯỜNG RAY")]
    [Tooltip("Trục đường ray chính của nhà ga (Mặc định: Trục X Chuan GaTau)")]
    public TrackAxisMode trackAxis = TrackAxisMode.Truc_X_Chuan_GaTau;

    [Tooltip("Vị trí dừng đón khách tại ke ga (Tự động lấy vị trí ban đầu trong Scene)")]
    public Vector3 stationStopPosition;

    [Tooltip("Khoảng cách tàu chạy ra ngoài ga (mét)")]
    public float travelDistance = 120.0f;

    [Tooltip("Đảo ngược hướng vào/ra của tàu")]
    public bool invertDirection = false;

    [Header("2. THÔNG SỐ VẬN HÀNH")]
    [Tooltip("Tốc độ chạy của tàu trên ray (m/s)")]
    public float trainSpeed = 16.0f;

    public enum TrainState { Outside, EnteringStation, AtStation, LeavingStation }
    [Header("3. TRẠNG THÁI HIỆN TẠI")]
    public TrainState currentState = TrainState.AtStation;

    private Vector3 approachPosition;
    private Vector3 departPosition;
    private Vector3 targetPosition;
    private Vector3 moveDirection;

    void Start()
    {
        // 1. Ghi nhận vị trí chuẩn ban đầu khi tàu đang nằm trên ke ga
        stationStopPosition = transform.position;

        // 2. Xác định vector đường ray chính xác
        switch (trackAxis)
        {
            case TrackAxisMode.Truc_X_Chuan_GaTau:
                moveDirection = Vector3.right;
                break;
            case TrackAxisMode.Truc_Z_TheGioi:
                moveDirection = Vector3.forward;
                break;
            case TrackAxisMode.Theo_Huong_DauTau:
                moveDirection = transform.forward;
                break;
        }

        if (invertDirection)
        {
            moveDirection = -moveDirection;
        }

        // 3. Khóa cứng quỹ đạo 2 điểm ngoài ga trên cùng 1 đường thẳng ray sắt
        approachPosition = stationStopPosition - moveDirection * travelDistance;
        departPosition = stationStopPosition + moveDirection * travelDistance;

        targetPosition = stationStopPosition;
    }

    void Update()
    {
        // Tịnh tiến mượt mà chính xác 100% dọc theo đường ray
        if (Vector3.Distance(transform.position, targetPosition) > 0.05f)
        {
            transform.position = Vector3.MoveTowards(transform.position, targetPosition, trainSpeed * Time.deltaTime);
        }
        else
        {
            if (currentState == TrainState.EnteringStation) currentState = TrainState.AtStation;
            else if (currentState == TrainState.LeavingStation) currentState = TrainState.Outside;
        }
    }

    /// <summary>
    /// Kích hoạt tàu chạy từ ngoài xa vào ga dừng đón khách (khi sảnh ga đông đúc)
    /// </summary>
    public void CallTrainArrival()
    {
        if (currentState == TrainState.Outside || currentState == TrainState.LeavingStation)
        {
            transform.position = approachPosition;
            targetPosition = stationStopPosition;
            currentState = TrainState.EnteringStation;
            Debug.Log($"<color=#00E5FF><b>[TRAIN CONTROLLER]</b> Đoàn tàu '{name}' đang tiến vào ke ga đón khách...</color>");
        }
    }

    /// <summary>
    /// Kích hoạt tàu rời ke ga chạy ra xa (khi đã hoàn tất đón khách)
    /// </summary>
    public void CallTrainDeparture()
    {
        if (currentState == TrainState.AtStation)
        {
            targetPosition = departPosition;
            currentState = TrainState.LeavingStation;
            Debug.Log($"<color=#FFD600><b>[TRAIN CONTROLLER]</b> Đoàn tàu '{name}' bắt đầu rời ga ra xa...</color>");
        }
    }

    // Vẽ tia gizmo màu vàng trong Unity Scene để bạn quan sát rõ đường ray của tàu
    private void OnDrawGizmosSelected()
    {
        Vector3 center = (stationStopPosition != Vector3.zero) ? stationStopPosition : transform.position;
        Vector3 dir = Vector3.right;
        if (trackAxis == TrackAxisMode.Truc_Z_TheGioi) dir = Vector3.forward;
        else if (trackAxis == TrackAxisMode.Theo_Huong_DauTau) dir = transform.forward;

        if (invertDirection) dir = -dir;

        Gizmos.color = Color.yellow;
        Gizmos.DrawLine(center - dir * travelDistance, center + dir * travelDistance);
        Gizmos.color = Color.green;
        Gizmos.DrawWireSphere(center, 1.0f);
    }
}
