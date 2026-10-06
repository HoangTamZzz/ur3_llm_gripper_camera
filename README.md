# UR3 LLM Gripper — Điều khiển robot bằng ngôn ngữ tự nhiên

Dự án tích hợp mô hình ngôn ngữ lớn (LLM) với robot **UR3e** trong môi trường mô phỏng **Gazebo + MoveIt 2** (ROS 2 Humble). Người dùng nhập lệnh bằng tiếng Việt hoặc tiếng Anh; hệ thống tự động sinh kế hoạch JSON, kiểm duyệt an toàn, rồi thực thi từng kỹ năng trên robot thật hoặc mô phỏng.

## Luồng hoạt động

```
Câu lệnh tự nhiên
  → LLM Planner (Gemini / OpenAI / Mock)
  → JSON Plan (Structured Outputs)
  → Task Validator
  → Skill Executor
  → /execute_skill (ROS 2 Action)
  → MoveIt 2
  → joint_trajectory_controller
  → Robot UR3e
```

---

## Tính năng chính

| Tính năng | Mô tả |
|---|---|
| **Nhập lệnh tự nhiên** | Tiếng Việt & tiếng Anh, hỗ trợ dấu tiếng Việt |
| **3 chế độ LLM** | Gemini API, OpenAI API, Mock (offline) |
| **Kiểm duyệt plan** | Validator từ chối lệnh nguy hiểm trước khi gửi robot |
| **Camera overhead** | Phát hiện vật bằng màu sắc qua OpenCV (HSV) |
| **Scene state-aware** | Planner nhận trạng thái scene thực từ camera |
| **Tái lập kế hoạch** | Tự động replan khi môi trường thay đổi giữa chừng |
| **Cá nhân hóa MSSV** | Ánh xạ vật–zone tính từ 2 chữ số cuối mã sinh viên |

---

## Cấu trúc thư mục

```
UR3_LLM_GRIPPER/
│
├── ur3_workcell_description/       # Mô tả robot và workcell
│   ├── urdf/
│   │   └── ur3e_robotiq.urdf.xacro     # URDF robot UR3e + gripper Robotiq
│   ├── worlds/
│   │   └── camera_empty.sdf            # Thế giới Gazebo với camera trên cao
│   ├── config/
│   │   ├── ur_controllers.yaml         # Cấu hình controller ROS 2 Control
│   │   ├── kinematics.yaml             # Kinematics solver (KDL)
│   │   └── joint_limits.yaml           # Giới hạn khớp
│   └── srdf/
│       └── ur_robotiq.srdf.xacro       # Nhóm khớp và trạng thái named
│
├── ur_simulation_gz/               # Tích hợp Gazebo Ignition Fortress
│   ├── launch/
│   │   ├── ur_sim_control.launch.py    # Khởi động robot + controllers
│   │   └── ur_sim_moveit.launch.py     # Khởi động MoveIt 2
│   └── config/
│       └── ur_controllers.yaml
│
├── ur3_perception/                 # Nhận diện vật qua camera
│   ├── ur3_perception/
│   │   ├── perception_core.py          # Phát hiện màu bằng HSV (OpenCV)
│   │   └── block_detector_node.py      # ROS 2 node publish SceneState
│   ├── launch/
│   │   └── perception.launch.py
│   └── config/
│       └── perception.yaml             # Ngưỡng HSV và tham số detector
│
├── ur3_llm_control/                # Tầng điều phối & LLM
│   ├── ur3_llm_control/
│   │   ├── llm_planner.py              # MockLLMPlanner (offline, xác định)
│   │   ├── gemini_planner.py           # Planner dùng Gemini API
│   │   ├── openai_planner.py           # Planner dùng OpenAI API
│   │   ├── planner_contract.py         # JSON schema & prompt chuẩn
│   │   ├── task_validator.py           # Kiểm duyệt plan trước khi thực thi
│   │   ├── state_aware_planning.py     # Plan tích hợp trạng thái scene
│   │   ├── skill_executor.py           # Thực thi từng PlanStep qua action
│   │   ├── robot_skills.py             # Chuyển PlanStep → ExecuteSkill goal
│   │   ├── scene_config.py             # Đọc & validate scene.yaml
│   │   ├── scene_manager.py            # ROS 2 node quản lý SceneState
│   │   ├── scene_guard.py              # Kiểm tra điều kiện tiên quyết
│   │   ├── student_config.py           # Ánh xạ vật–zone từ MSSV
│   │   ├── camera_geometry.py          # Đổi pixel → tọa độ bàn
│   │   └── spawn_scene.py              # Spawn vật thể vào Gazebo
│   ├── config/
│   │   ├── scene.yaml                  # Tọa độ bàn, cube và zone
│   │   ├── scene_clear.yaml            # Scene không có vật chặn
│   │   ├── scene_blocked.yaml          # Scene có vật chặn zone
│   │   ├── student_config.yaml         # Tên & MSSV sinh viên  ← CẦN CHỈNH
│   │   └── mssv_<ID>_plan.json         # Plan cá nhân theo MSSV
│   └── launch/
│       └── llm_robot.launch.py
│
└── ur3_robot_skills/               # Kỹ năng robot (C++ + Python)
    ├── src/
    │   ├── robot_skill_server.cpp      # Action server thực thi kỹ năng MoveIt
    │   └── robot_skill_demo.cpp        # Node demo tự động pick → place
    ├── scripts/
    │   └── execute_plan                # CLI: nhận lệnh → plan → thực thi
    ├── action/
    │   └── ExecuteSkill.action         # Định nghĩa ROS 2 Action
    ├── config/
    │   └── robot_skills.yaml           # Tham số kỹ năng (chiều cao, tốc độ...)
    └── launch/
        ├── robot_skills.launch.py      # Launch đầy đủ: Gazebo+MoveIt+server
        ├── validated_plan.launch.py    # Launch với plan JSON có sẵn
        └── end_to_end.launch.py        # Launch toàn bộ + LLM command
```

---

## Yêu cầu hệ thống

### Phần mềm bắt buộc

| Thành phần | Phiên bản |
|---|---|
| Ubuntu | 22.04 LTS (hoặc WSL 2) |
| ROS 2 | Humble Hawksbill |
| Gazebo | Ignition Fortress |
| MoveIt 2 | humble |
| Python | 3.10+ |

### Cài đặt ROS 2 dependencies

```bash
sudo apt update && sudo apt install -y \
  ros-humble-ur \
  ros-humble-moveit \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-gz-ros2-control \
  ros-humble-joint-state-publisher \
  ros-humble-robot-state-publisher \
  ros-humble-rviz2 \
  python3-colcon-common-extensions \
  python3-pip
```

### Cài đặt Python dependencies

```bash
pip3 install "google-genai>=1.0.0" "openai>=1.0.0" opencv-python pyyaml
```

---

## Cấu hình sinh viên (bắt buộc trước khi build)

Mở và sửa file `ur3_llm_control/config/student_config.yaml`:

```yaml
student:
  name: "Họ và Tên"
  id: "MSSV_CỦA_BẠN"   # Ví dụ: "23020765"
```

> **Lưu ý:** 2 chữ số cuối của MSSV xác định ánh xạ vật–zone theo công thức `P = MSSV[-2:] mod 6`.
>
> | P | zone\_a | zone\_b | zone\_c |
> |---|---|---|---|
> | 0 | red\_cube | yellow\_cube | blue\_cube |
> | 1 | red\_cube | blue\_cube | yellow\_cube |
> | 2 | yellow\_cube | red\_cube | blue\_cube |
> | 3 | yellow\_cube | blue\_cube | red\_cube |
> | 4 | blue\_cube | red\_cube | yellow\_cube |
> | 5 | blue\_cube | yellow\_cube | red\_cube |

---

## Cách build workspace

```bash
# 1. Vào workspace
cd ~/ros2_ws

# 2. Source ROS 2
source /opt/ros/humble/setup.bash

# 3. Build toàn bộ UR3_LLM_GRIPPER
colcon build --base-paths src/UR3_LLM_GRIPPER --symlink-install

# 4. Source workspace sau khi build
source install/setup.bash
```

> **Lưu ý WSL:** Nếu dùng Windows Subsystem for Linux và gặp lỗi `python3\r: No such file or directory`,
> hãy sửa line endings trước khi build:
> ```bash
> find ~/ros2_ws/src/UR3_LLM_GRIPPER -name "*.py" -exec sed -i 's/\r//' {} +
> ```

---

## Cách chạy

### Chế độ 1 — Interactive (nhập lệnh tùy ý từ bàn phím)

**Terminal 1** — Khởi động Gazebo + MoveIt 2 + Robot Skill Server:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

ros2 launch ur3_robot_skills robot_skills.launch.py
```

**Terminal 2** — Nhập lệnh tự nhiên:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

ros2 run ur3_robot_skills execute_plan --interactive --planner mock
```

Ví dụ lệnh có thể nhập:

```
Robot Command > Đưa khối đỏ sang vùng A.
Robot Command > Move blue cube to zone C.
Robot Command > Put the yellow cube in zone B.
Robot Command > Arrange all objects according to my student ID.
Robot Command > exit
```

---

### Chế độ 2 — Một lệnh duy nhất (command line)

```bash
ros2 run ur3_robot_skills execute_plan \
  --command "Đưa vật màu vàng sang vùng B." \
  --planner mock
```

---

### Chế độ 3 — LLM Gemini API (cần API key)

```bash
# Lấy API key tại: https://aistudio.google.com/app/apikey
export GEMINI_API_KEY="your_api_key_here"

ros2 run ur3_robot_skills execute_plan \
  --command "Đưa khối đỏ sang vùng A." \
  --planner gemini
```

---

### Chế độ 4 — Launch end-to-end (Gazebo + LLM + thực thi tự động)

```bash
# Mock planner — offline, không cần API key:
ros2 launch ur3_robot_skills end_to_end.launch.py \
  command:="Đưa vật màu đỏ sang vùng A." \
  planner:=mock

# Gemini — cần GEMINI_API_KEY đã export:
ros2 launch ur3_robot_skills end_to_end.launch.py \
  command:="Move blue cube to zone C." \
  planner:=gemini
```

---

### Chế độ 5 — Thực thi plan JSON có sẵn

```bash
ros2 run ur3_robot_skills execute_plan \
  --file ~/ros2_ws/src/UR3_LLM_GRIPPER/ur3_llm_control/config/milestone5_plan.json
```

Hoặc qua launch file:

```bash
ros2 launch ur3_robot_skills validated_plan.launch.py
```

---

## Các tham số launch quan trọng

| Tham số | Mặc định | Giá trị hợp lệ | Mô tả |
|---|---|---|---|
| `ur_type` | `ur3e` | `ur3`, `ur3e` | Loại robot |
| `gazebo_gui` | `true` | `true`, `false` | Hiển thị giao diện Gazebo |
| `launch_rviz` | `true` | `true`, `false` | Khởi động RViz2 |
| `run_demo` | `true` | `true`, `false` | Tự động chạy demo khi khởi động |
| `demo_object` | `red_cube` | `red_cube`, `yellow_cube`, `blue_cube`, `green_cube`, `purple_cube` | Cube để demo |
| `demo_zone` | `zone_a` | `zone_a`, `zone_b`, `zone_c` | Zone đích demo |
| `planner` | `mock` | `mock`, `gemini`, `openai` | Chế độ LLM planner |

Ví dụ tùy chỉnh:

```bash
ros2 launch ur3_robot_skills robot_skills.launch.py \
  demo_object:=yellow_cube \
  demo_zone:=zone_b \
  gazebo_gui:=true \
  launch_rviz:=true \
  run_demo:=true
```

---

## Kỹ năng robot (Skills)

| Skill | Tham số bắt buộc | Mô tả |
|---|---|---|
| `home` | — | Đưa robot về tư thế an toàn |
| `pick` | `object` | Nhặt cube từ vị trí camera phát hiện |
| `place` | `object`, `zone` | Đặt cube vào zone đích |
| `check_zone` | `zone` | Kiểm tra zone có trống không |
| `place_temp` | `object`, `slot` | Dọn vật sang vị trí tạm `temp_1` |
| `observe_scene` | — | Chụp snapshot trạng thái scene từ camera |

Ví dụ JSON plan hợp lệ:

```json
{
  "scene_version": 1,
  "goal": {"object": "red_cube", "destination": "zone_a"},
  "plan": [
    {"skill": "check_zone", "zone": "zone_a"},
    {"skill": "pick", "object": "red_cube"},
    {"skill": "place", "object": "red_cube", "zone": "zone_a"},
    {"skill": "home"}
  ]
}
```

---

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| `python3\r: No such file or directory` | File Python có CRLF (Windows line ending) | `find ~/ros2_ws/src -name "*.py" -exec sed -i 's/\r//' {} +` |
| `can't copy 'mssv_xxx_plan.json': doesn't exist` | Build cache cũ chứa file không tồn tại | `rm -rf ~/ros2_ws/build/ur3_llm_control && colcon build ...` |
| `ModuleNotFoundError: No module named 'ament_index_python'` | Chưa source ROS 2 | `source /opt/ros/humble/setup.bash` |
| `SERVER_UNAVAILABLE` | Chưa khởi động robot skill server | Chạy `robot_skills.launch.py` ở terminal khác trước |
| `SCENE_CHANGED` | Camera phát hiện môi trường thay đổi | Hệ thống tự động replan tối đa 2 lần |
| Gazebo màn hình trắng | Thiếu model hoặc lỗi render | Đợi thêm 30–60 giây để Gazebo load xong |

---

## ROS 2 Topics & Actions

| Topic / Action | Kiểu | Mô tả |
|---|---|---|
| `/execute_skill` | Action `ExecuteSkill` | Gọi một kỹ năng đơn lẻ |
| `/get_scene_state` | Service | Lấy trạng thái scene từ camera |
| `/scene_state` | Topic | Publish liên tục trạng thái scene |
| `/joint_states` | Topic | Trạng thái khớp hiện tại |
| `/camera/image_raw` | Topic | Ảnh từ camera overhead |

---

## Cấu hình sinh viên hiện tại

File `student_config.yaml` đang cấu hình:

```
Tên  : Alex
MSSV : 23020765
P    = 65 mod 6 = 5  →  blue_cube→zone_a | yellow_cube→zone_b | red_cube→zone_c
```

Để đổi sang MSSV của bạn:

```bash
nano ~/ros2_ws/src/UR3_LLM_GRIPPER/ur3_llm_control/config/student_config.yaml
colcon build --base-paths src/UR3_LLM_GRIPPER --symlink-install
source ~/ros2_ws/install/setup.bash
```
