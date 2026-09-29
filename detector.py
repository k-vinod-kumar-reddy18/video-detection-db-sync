import cv2
from datetime import datetime, timedelta
from ultralytics import YOLO


# ============================================
# LOAD ADVANCED YOLO MODELS
# ============================================

model = YOLO("yolo11x.pt")

pose_model = YOLO("yolo11x-pose.pt")


# ============================================
# POSE ACTIVITY DETECTION
# ============================================

def detect_pose_activity(keypoints):

    if keypoints is None:
        return "unknown"

    try:

        points = keypoints.xy[0].cpu().numpy()

        # COCO keypoints
        left_shoulder = points[5]
        right_shoulder = points[6]

        left_hip = points[11]
        right_hip = points[12]

        left_knee = points[13]
        right_knee = points[14]

        left_ankle = points[15]
        right_ankle = points[16]

        # Average coordinates

        shoulder_x = (
            left_shoulder[0] +
            right_shoulder[0]
        ) / 2

        shoulder_y = (
            left_shoulder[1] +
            right_shoulder[1]
        ) / 2

        hip_x = (
            left_hip[0] +
            right_hip[0]
        ) / 2

        hip_y = (
            left_hip[1] +
            right_hip[1]
        ) / 2

        knee_y = (
            left_knee[1] +
            right_knee[1]
        ) / 2

        ankle_y = (
            left_ankle[1] +
            right_ankle[1]
        ) / 2

        # Body measurements

        torso_length = abs(
            hip_y - shoulder_y
        )

        leg_length = abs(
            ankle_y - hip_y
        )

        if torso_length == 0:
            return "unknown"

        leg_ratio = (
            leg_length /
            torso_length
        )

        # ========================================
        # BENDING
        # ========================================

        body_lean = abs(
            hip_x - shoulder_x
        )

        if body_lean > torso_length * 0.5:

            return "bending"

        # ========================================
        # STANDING
        # ========================================

        if leg_ratio > 1.5:

            return "standing"

        # ========================================
        # SITTING
        # ========================================

        if leg_ratio < 1.2:

            return "sitting"

        return "unknown"

    except Exception:

        return "unknown"


# ============================================
# IOU
# ============================================

def calculate_iou(box1, box2):

    x1 = max(
        box1[0],
        box2[0]
    )

    y1 = max(
        box1[1],
        box2[1]
    )

    x2 = min(
        box1[2],
        box2[2]
    )

    y2 = min(
        box1[3],
        box2[3]
    )

    intersection_width = max(
        0,
        x2 - x1
    )

    intersection_height = max(
        0,
        y2 - y1
    )

    intersection_area = (
        intersection_width *
        intersection_height
    )

    box1_area = (
        (box1[2] - box1[0]) *
        (box1[3] - box1[1])
    )

    box2_area = (
        (box2[2] - box2[0]) *
        (box2[3] - box2[1])
    )

    union_area = (
        box1_area +
        box2_area -
        intersection_area
    )

    if union_area == 0:

        return 0

    return (
        intersection_area /
        union_area
    )


# ============================================
# GET CENTER
# ============================================

def get_center(bbox):

    x1, y1, x2, y2 = bbox

    center_x = (
        x1 + x2
    ) / 2

    center_y = (
        y1 + y2
    ) / 2

    return center_x, center_y


# ============================================
# CALCULATE MOVEMENT
# ============================================

def calculate_movement(
    previous_center,
    current_center
):

    if previous_center is None:

        return 0

    previous_x, previous_y = (
        previous_center
    )

    current_x, current_y = (
        current_center
    )

    movement = (
        (current_x - previous_x) ** 2
        +
        (current_y - previous_y) ** 2
    ) ** 0.5

    return movement


# ============================================
# VIDEO DETECTION
# ============================================

def detect_video(video_path):

    cap = cv2.VideoCapture(
        video_path
    )

    if not cap.isOpened():

        print(
            "Unable to open video"
        )

        return []

    # ========================================
    # VIDEO FPS
    # ========================================

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    if fps <= 0:

        fps = 30

    detections = []

    frame_number = 0

    # ========================================
    # UNIQUE OBJECTS
    # ========================================

    unique_objects = {}

    # ========================================
    # ACTIVITY STATES
    # ========================================

    activity_states = {}

    # ========================================
    # VIDEO START TIME
    # ========================================

    video_start_time = datetime.now()

    # ========================================
    # DISPLAY WINDOW
    # ========================================

    cv2.namedWindow(
        "YOLO Video Detection",
        cv2.WINDOW_NORMAL
    )

    cv2.resizeWindow(
        "YOLO Video Detection",
        800,
        600
    )

    # ========================================
    # PROCESS VIDEO
    # ========================================

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        frame_number += 1

        # ====================================
        # VIDEO TIME
        # ====================================

        video_seconds = (
            frame_number /
            fps
        )

        current_time = (
            video_start_time +
            timedelta(
                seconds=video_seconds
            )
        )

        # ====================================
        # YOLO + BYTETRACK TRACKING
        # ====================================

        results = model.track(
            frame,
            conf=0.5,
            persist=True,
            tracker="bytetrack.yaml"
        )

        # ====================================
        # YOLO POSE
        # ====================================

        pose_results = pose_model(
            frame,
            conf=0.5,
            verbose=False
        )

        pose_result = pose_results[0]

        # ====================================
        # POSE PERSONS
        # ====================================

        pose_people = []

        if (
            pose_result.boxes is not None
            and
            pose_result.keypoints is not None
        ):

            for index, pose_box in enumerate(
                pose_result.boxes.xyxy
            ):

                pose_bbox = list(
                    map(
                        int,
                        pose_box.tolist()
                    )
                )

                pose_keypoints = (
                    pose_result.keypoints[
                        index
                    ]
                )

                pose_people.append({

                    "bbox":
                        pose_bbox,

                    "keypoints":
                        pose_keypoints

                })

        # ====================================
        # TRACKED OBJECTS
        # ====================================

        for result in results:

            for box in result.boxes:

                # ==============================
                # CLASS
                # ==============================

                class_id = int(
                    box.cls[0]
                )

                confidence = float(
                    box.conf[0]
                )

                object_class = (
                    model.names[
                        class_id
                    ]
                )

                # ==============================
                # OBJECT ID
                # ==============================

                if box.id is None:

                    continue

                object_id = int(
                    box.id[0]
                )

                # ==============================
                # BOUNDING BOX
                # ==============================

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist()
                )

                object_bbox = [
                    x1,
                    y1,
                    x2,
                    y2
                ]

                # ==============================
                # UNIQUE OBJECT
                # ==============================

                unique_objects[
                    (
                        object_class,
                        object_id
                    )
                ] = True

                # ==============================
                # ACTIVITY
                # ==============================

                activity = "unknown"

                if object_class == "person":

                    # ==========================
                    # FIND POSE
                    # ==========================

                    best_pose = None

                    best_iou = 0

                    for pose_person in pose_people:

                        iou = calculate_iou(
                            object_bbox,
                            pose_person[
                                "bbox"
                            ]
                        )

                        if iou > best_iou:

                            best_iou = iou

                            best_pose = (
                                pose_person
                            )

                    # ==========================
                    # POSE ACTIVITY
                    # ==========================

                    pose_activity = "unknown"

                    if (
                        best_pose is not None
                        and
                        best_iou > 0.2
                    ):

                        pose_activity = (
                            detect_pose_activity(
                                best_pose[
                                    "keypoints"
                                ]
                            )
                        )

                    # ==========================
                    # PERSON CENTER
                    # ==========================

                    current_center = (
                        get_center(
                            object_bbox
                        )
                    )

                    # ==========================
                    # PREVIOUS STATE
                    # ==========================

                    previous_state = (
                        activity_states.get(
                            object_id
                        )
                    )

                    previous_center = None

                    if previous_state:

                        previous_center = (
                            previous_state.get(
                                "center"
                            )
                        )

                    # ==========================
                    # MOVEMENT
                    # ==========================

                    movement = (
                        calculate_movement(
                            previous_center,
                            current_center
                        )
                    )

                    # ==========================
                    # ACTIVITY DECISION
                    # ==========================

                    if movement > 8:

                        activity = "walking"

                    elif movement > 3:

                        activity = "moving"

                    elif pose_activity != "unknown":

                        activity = (
                            pose_activity
                        )

                    else:

                        activity = "unknown"

                    # ==========================
                    # FIRST ACTIVITY
                    # ==========================

                    if object_id not in activity_states:

                        activity_states[
                            object_id
                        ] = {

                            "activity":
                                activity,

                            "start_time":
                                current_time,

                            "center":
                                current_center

                        }

                    else:

                        previous_activity = (
                            activity_states[
                                object_id
                            ]["activity"]
                        )

                        # ======================
                        # ACTIVITY CHANGED
                        # ======================

                        if (
                            activity != "unknown"
                            and
                            previous_activity != activity
                        ):

                            start_time = (
                                activity_states[
                                    object_id
                                ]["start_time"]
                            )

                            end_time = (
                                current_time
                            )

                            duration = (
                                end_time -
                                start_time
                            ).total_seconds()

                            # ==================
                            # SAVE ACTIVITY
                            # ==================

                            detections.append({

                                "object_id":
                                    object_id,

                                "object_class":
                                    "person",

                                "confidence":
                                    confidence,

                                "activity":
                                    previous_activity,

                                "activity_start_time":
                                    start_time.isoformat(),

                                "activity_end_time":
                                    end_time.isoformat(),

                                "activity_duration_seconds":
                                    duration,

                                "timestamp":
                                    end_time.isoformat(),

                                "bbox":
                                    object_bbox,

                                "frame_number":
                                    frame_number

                            })

                            # ==================
                            # START NEW ACTIVITY
                            # ==================

                            activity_states[
                                object_id
                            ] = {

                                "activity":
                                    activity,

                                "start_time":
                                    current_time,

                                "center":
                                    current_center

                            }

                        else:

                            activity_states[
                                object_id
                            ]["center"] = (
                                current_center
                            )

                # =================================
                # CURRENT DETECTION
                # =================================

                state = (
                    activity_states.get(
                        object_id
                    )
                )

                activity_start_time = None

                if (
                    object_class == "person"
                    and
                    state is not None
                ):

                    activity_start_time = (
                        state[
                            "start_time"
                        ].isoformat()
                    )

                detections.append({

                    "object_id":
                        object_id,

                    "object_class":
                        object_class,

                    "confidence":
                        confidence,

                    "activity":
                        activity,

                    "activity_start_time":
                        activity_start_time,

                    "activity_end_time":
                        None,

                    "activity_duration_seconds":
                        None,

                    "timestamp":
                        current_time.isoformat(),

                    "bbox":
                        object_bbox,

                    "frame_number":
                        frame_number

                })

        # ====================================
        # DISPLAY
        # ====================================

        annotated_frame = (
            results[0].plot()
        )

        cv2.imshow(
            "YOLO Video Detection",
            annotated_frame
        )

        # ====================================
        # STOP WITH Q
        # ====================================

        if (
            cv2.waitKey(1) & 0xFF
            == ord("q")
        ):

            break

    # ========================================
    # FINISH LAST ACTIVITIES
    # ========================================

    final_time = (
        video_start_time +
        timedelta(
            seconds=
            frame_number / fps
        )
    )

    for object_id, state in (
        activity_states.items()
    ):

        activity = (
            state["activity"]
        )

        if activity == "unknown":

            continue

        start_time = (
            state["start_time"]
        )

        duration = (
            final_time -
            start_time
        ).total_seconds()

        detections.append({

            "object_id":
                object_id,

            "object_class":
                "person",

            "confidence":
                0,

            "activity":
                activity,

            "activity_start_time":
                start_time.isoformat(),

            "activity_end_time":
                final_time.isoformat(),

            "activity_duration_seconds":
                duration,

            "timestamp":
                final_time.isoformat(),

            "bbox":
                [],

            "frame_number":
                frame_number

        })

    # ========================================
    # RELEASE
    # ========================================

    cap.release()

    cv2.destroyAllWindows()

    # ========================================
    # UNIQUE OBJECT COUNTS
    # ========================================

    object_counts = {}

    for object_class, object_id in (
        unique_objects.keys()
    ):

        if object_class not in object_counts:

            object_counts[
                object_class
            ] = 0

        object_counts[
            object_class
        ] += 1

    # ========================================
    # PRINT OBJECT COUNTS
    # ========================================

    print()

    print(
        "==================================="
    )

    print(
        "UNIQUE OBJECT COUNTS"
    )

    print(
        "==================================="
    )

    for object_class, count in (
        object_counts.items()
    ):

        print(
            f"{object_class}: {count}"
        )

    print(
        "==================================="
    )

    # ========================================
    # ACTIVITY COUNTS
    # ========================================

    activity_counts = {}

    for detection in detections:

        activity = detection.get(
            "activity"
        )

        if (
            activity is not None
            and
            activity != "unknown"
        ):

            if activity not in activity_counts:

                activity_counts[
                    activity
                ] = 0

            activity_counts[
                activity
            ] += 1

    print()

    print(
        "==================================="
    )

    print(
        "ACTIVITIES DETECTED"
    )

    print(
        "==================================="
    )

    for activity, count in (
        activity_counts.items()
    ):

        print(
            f"{activity}: {count}"
        )

    print(
        "==================================="
    )

    return detections