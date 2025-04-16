import cv2
import mediapipe as mp
import pygame
import threading
from queue import Queue
import time

class GestureController:
    def __init__(self, player_num=1):
        self.player_num = player_num
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = None
        self.is_running = False
        self.current_gesture = None
        self.gesture_queue = Queue()
        self.last_attack_time = 0
        self.attack_cooldown = 1.0  

    def start(self):
        """Start the gesture detection in a separate thread"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Error: Could not open camera")
                return
            self.is_running = True
            threading.Thread(target=self._process_gestures, daemon=True).start()
        except Exception as e:
            print(f"Error starting gesture detection: {e}")
            self.stop()

    def stop(self):
        """Stop the gesture detection"""
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        time.sleep(0.5)  # Give time for windows to close

    def get_current_keys(self):
        """Convert gestures to Pygame key states"""
        try:
            # Get the latest gesture without blocking
            if not self.gesture_queue.empty():
                self.current_gesture = self.gesture_queue.get_nowait()
                print(f"Current gesture: {self.current_gesture}")  # Debug output
        except:
            pass

        # Initialize an empty list for pressed keys
        pressed_keys = []
        
        if self.current_gesture:
            current_time = time.time()
            if self.player_num == 1:
                # Player 1 controls
                if self.current_gesture == "Move Left":
                    pressed_keys.append(pygame.K_a)
                    print("Moving Left")  # Debug output
                elif self.current_gesture == "Move Right":
                    pressed_keys.append(pygame.K_d)
                    print("Moving Right")  # Debug output
                elif self.current_gesture == "Jump":
                    pressed_keys.append(pygame.K_w)
                    print("Jumping")  # Debug output
                elif self.current_gesture == "Punch" and (current_time - self.last_attack_time) >= self.attack_cooldown:
                    pressed_keys.append(pygame.K_r)
                    self.last_attack_time = current_time
                    print("Punching")  # Debug output
            else:
                # Player 2 controls
                if self.current_gesture == "Move Left":
                    pressed_keys.append(pygame.K_LEFT)
                elif self.current_gesture == "Move Right":
                    pressed_keys.append(pygame.K_RIGHT)
                elif self.current_gesture == "Jump":
                    pressed_keys.append(pygame.K_UP)
                elif self.current_gesture == "Punch" and (current_time - self.last_attack_time) >= self.attack_cooldown:
                    pressed_keys.append(pygame.K_KP1)
                    self.last_attack_time = current_time
        
        return pressed_keys

    def _process_gestures(self):
        """Process video feed and detect gestures"""
        print("Starting gesture detection...")
        last_gesture_time = time.time()
        gesture_cooldown = 0.2  # 200ms cooldown between gestures
        
        while self.is_running:
            try:
                if not self.cap or not self.cap.isOpened():
                    print("Error: Camera not available")
                    break

                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to get frame from camera")
                    continue

                # Flip the frame horizontally for a later selfie-view display
                frame = cv2.flip(frame, 1)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(frame_rgb)

                current_time = time.time()
                if results.multi_hand_landmarks and (current_time - last_gesture_time) >= gesture_cooldown:
                    for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        try:
                            self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                            
                            # Get handedness
                            handedness = results.multi_handedness[idx].classification[0].label
                            
                            # Get landmark coordinates
                            landmark_list = []
                            h, w, c = frame.shape
                            for lm in hand_landmarks.landmark:
                                cx, cy = int(lm.x * w), int(lm.y * h)
                                landmark_list.append([cx, cy])

                            # Detect gestures
                            gesture = None
                            if len(landmark_list) >= 21:  # Ensure we have all landmarks
                                # Check for fist first (most important)
                                # A fist is when all fingers are curled down
                                fingers_down = True
                                # Check each finger (index, middle, ring, pinky)
                                for tip, pip in [(8,6), (12,10), (16,14), (20,18)]:
                                    if landmark_list[tip][1] <= landmark_list[pip][1]:  # If tip is above or at PIP
                                        fingers_down = False
                                        break

                                if fingers_down:
                                    gesture = "Punch"
                                    print("Fist detected - PUNCH!")
                                # Only check other gestures if it's not a fist
                                else:
                                    # Open Hand (Jump)
                                    if (all(landmark_list[tip][1] < landmark_list[pip][1] - 20
                                           for tip, pip in [(8,6), (12,10), (16,14), (20,18)])):
                                        gesture = "Jump"
                                    
                                    # Point Right (Move Right)
                                    elif (landmark_list[8][0] > landmark_list[5][0] + 15 and  # Index finger extended right
                                          landmark_list[8][1] > landmark_list[5][1] - 20 and  # Index finger roughly horizontal
                                          all(landmark_list[tip][1] > landmark_list[pip][1]  # Other fingers down
                                              for tip, pip in [(12,10), (16,14), (20,18)])):
                                        gesture = "Move Right"
                                    
                                    # Point Left (Move Left)
                                    elif (landmark_list[8][0] < landmark_list[5][0] - 15 and  # Index finger extended left
                                          landmark_list[8][1] > landmark_list[5][1] - 20 and  # Index finger roughly horizontal
                                          all(landmark_list[tip][1] > landmark_list[pip][1]  # Other fingers down
                                              for tip, pip in [(12,10), (16,14), (20,18)])):
                                        gesture = "Move Left"

                                if gesture:
                                    last_gesture_time = current_time
                                    try:
                                        # Clear old gesture and put new one
                                        while not self.gesture_queue.empty():
                                            self.gesture_queue.get_nowait()
                                        self.gesture_queue.put_nowait(gesture)
                                    except:
                                        pass
                        except Exception as e:
                            print(f"Error processing hand landmarks: {e}")
                            continue

                # Display the frame with larger window size
                try:
                    frame = cv2.resize(frame, (800, 600))
                    cv2.imshow(f'Hand Gesture Controls - Player {self.player_num}', frame)
                except Exception as e:
                    print(f"Error displaying frame: {e}")

                # Break the loop when 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Quitting gesture detection...")
                    break

            except Exception as e:
                print(f"Error in gesture processing loop: {e}")
                time.sleep(0.1)  # Prevent tight error loop

        self.stop()
