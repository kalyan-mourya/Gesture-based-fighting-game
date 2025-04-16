# Step 1: Import Libraries
import cv2
import mediapipe as mp

# Step 2: Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Step 3: Initialize Video Capture
cap = cv2.VideoCapture(0)

# Step 4: Capture and Process Each Frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break

    # Flip the frame horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Check if hand landmarks are detected
    if results.multi_hand_landmarks:
        print("Hand landmarks detected")
        # Loop through all detected hands
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            handedness = results.multi_handedness[idx].classification[0].label
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Initialize list to store landmark coordinates
            landmark_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                # Get the coordinates
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmark_list.append([cx, cy])

            # Gesture recognition logic
            gesture = None  # Default gesture is None
            if len(landmark_list) != 0:
                # Closed Fist (Punch): All fingers bent
                if (
                    landmark_list[8][1] > landmark_list[6][1]
                    and landmark_list[12][1] > landmark_list[10][1]
                ):
                    gesture = "Punch"

                # Open Hand (Block): All fingers extended
                elif (
                    landmark_list[8][1] < landmark_list[6][1]
                    and landmark_list[12][1] < landmark_list[10][1]
                    and landmark_list[16][1] < landmark_list[14][1]
                    and landmark_list[20][1] < landmark_list[18][1]
                ):
                    gesture = "Jump"

                # Move Right (Right Hand with Index Finger Extended)
                elif (
                    handedness == "Right"
                    and landmark_list[8][1] < landmark_list[6][1]
                    and landmark_list[12][1] > landmark_list[10][1]
                    and landmark_list[16][1] > landmark_list[14][1]
                    and landmark_list[20][1] > landmark_list[18][1]
                ):
                    gesture = "Move Right"

                # Move Left (Left Hand with Index Finger Extended)
                elif (
                    handedness == "Left"
                    and landmark_list[8][1] < landmark_list[6][1]
                    and landmark_list[12][1] > landmark_list[10][1]
                    and landmark_list[16][1] > landmark_list[14][1]
                    and landmark_list[20][1] > landmark_list[18][1]
                ):
                    gesture = "Move Left"

            # Display the corresponding text, but at different locations for multiple hands
            if gesture:
                print(f"Gesture detected: {gesture}")
                if handedness == "Right":
                    # Display gesture for right hand slightly on the right of the hand
                    cv2.putText(
                        frame,
                        gesture,
                        (landmark_list[8][0] + 50, landmark_list[8][1] - 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.5,  # Adjusted font scale
                        (0, 255, 0),
                        3,
                        cv2.LINE_AA,
                    )
                elif handedness == "Left":
                    # Display gesture for left hand slightly on the left of the hand
                    cv2.putText(
                        frame,
                        gesture,
                        (landmark_list[8][0] - 200, landmark_list[8][1] - 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.5,  # Adjusted font scale
                        (0, 255, 0),
                        3,
                        cv2.LINE_AA,
                    )

    # Step 5: Display the Frame
    cv2.imshow('Hand Gesture Recognition', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Step 6: Release Resources
cap.release()
cv2.destroyAllWindows()

