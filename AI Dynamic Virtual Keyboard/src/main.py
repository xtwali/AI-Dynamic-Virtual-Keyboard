import cv2
import mediapipe as mp
import pygame
import numpy as np
import math
import time
import os
from pynput.keyboard import Controller, Key

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'

class Button:
    def __init__(self, pos, text, size=(85, 85)):
        self.pos = pos
        self.size = size
        self.text = text
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def draw(self, screen, font, base_color, hover_color, click_color, is_hovered, is_clicked):
        current_color = base_color
        if is_clicked:
            current_color = click_color
        elif is_hovered:
            current_color = hover_color
        
        pygame.draw.rect(screen, current_color + (180,), self.rect, border_radius=10)
        
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

def generate_click_sound():
    pygame.mixer.init()
    sample_rate = 44100
    frequency = 1500
    duration = 0.05
    t = np.linspace(0., duration, int(sample_rate * duration), endpoint=False)
    amplitude = np.iinfo(np.int16).max * 0.1
    data = amplitude * np.sin(2. * np.pi * frequency * t)
    fade_out = np.linspace(1., 0., len(data))
    data *= fade_out
    sound_data = np.asarray([data, data]).T.astype(np.int16).copy()
    sound = pygame.sndarray.make_sound(sound_data)
    return sound


def send_key(keyboard, key_text):
    special_keys = {
        "Space": Key.space,
        "Backspace": Key.backspace,
        "Enter": Key.enter,
    }
    key = special_keys.get(key_text, key_text)
    keyboard.press(key)
    keyboard.release(key)


def get_key_layout(caps_lock_on):
    if caps_lock_on:
        return [
            "1234567890",
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM"
        ]
    else:
        return [
            "1234567890",
            "qwertyuiop",
            "asdfghjkl",
            "zxcvbnm"
        ]

def main():
    pygame.init()
    
    screen_width, screen_height = 1280, 720
    screen = pygame.Surface((screen_width, screen_height))
    clock = pygame.time.Clock()
    keyboard = Controller()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        pygame.quit()
        raise RuntimeError(
            "Could not open webcam. Connect a camera and grant webcam access, then run the app again."
        )
    cap.set(3, screen_width)
    cap.set(4, screen_height)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    caps_lock_on = False
    live_typing_on = False
    
    key_size, key_gap = 80, 10
    start_x = (screen_width - (10 * (key_size + key_gap) - key_gap)) // 2
    start_y = 150
    window_name = "AI Dynamic Virtual Keyboard"

    def generate_buttons():
        button_list = []
        key_layout = get_key_layout(caps_lock_on)
        
        for row_idx, row in enumerate(key_layout):
            for col_idx, key in enumerate(row):
                x = start_x + col_idx * (key_size + key_gap)
                y = start_y + row_idx * (key_size + key_gap)
                button_list.append(Button((x, y), key, (key_size, key_size)))
        
        last_row_y = start_y + len(key_layout) * (key_size + key_gap)
        button_list.append(Button((start_x, last_row_y), "Caps", (125, key_size)))
        button_list.append(Button((start_x + 135, last_row_y), "Space", (390, key_size)))
        button_list.append(Button((start_x + 535, last_row_y), "Backspace", (160, key_size)))
        button_list.append(Button((start_x + 705, last_row_y), "Enter", (130, key_size)))
        live_text = "LIVE: ON" if live_typing_on else "LIVE: OFF"
        button_list.append(Button((start_x + 845, last_row_y), live_text, (200, key_size)))
        return button_list

    button_list = generate_buttons()
    font = pygame.font.SysFont("Arial", 35)
    display_font = pygame.font.SysFont("Arial", 50)
    status_font = pygame.font.SysFont("Arial", 24)
    small_font = pygame.font.SysFont("Arial", 25)
    click_sound = generate_click_sound()

    typed_text = ""
    last_click_time = 0.0
    click_delay = 0.4
    pinch_was_active = False

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, screen_width, screen_height)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

    running = True
    try:
        while running:
            success, frame = cap.read()
            if not success:
                continue

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            hovered_button = None
            clicked_button = None
            pinch_active = False

            if results.multi_hand_landmarks:
                for hand_lms in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)

                    h, w, _ = frame.shape
                    lm_list = [
                        (int(lm.x * w), int(lm.y * h))
                        for lm in hand_lms.landmark
                    ]
                    index_tip = lm_list[8]
                    thumb_tip = lm_list[4]

                    for button in button_list:
                        if button.rect.collidepoint(index_tip):
                            hovered_button = button

                    dist = math.hypot(
                        index_tip[0] - thumb_tip[0],
                        index_tip[1] - thumb_tip[1],
                    )
                    pinch_active = dist < 40 and hovered_button is not None

            current_time = time.monotonic()
            if (
                pinch_active
                and not pinch_was_active
                and current_time - last_click_time >= click_delay
            ):
                clicked_button = hovered_button
                click_sound.play()
                last_click_time = current_time

                if clicked_button.text == "Caps":
                    caps_lock_on = not caps_lock_on
                    button_list = generate_buttons()
                elif clicked_button.text.startswith("LIVE:"):
                    live_typing_on = not live_typing_on
                    button_list = generate_buttons()
                elif clicked_button.text == "Backspace":
                    typed_text = typed_text[:-1]
                    if live_typing_on:
                        send_key(keyboard, "Backspace")
                elif clicked_button.text == "Space":
                    typed_text += " "
                    if live_typing_on:
                        send_key(keyboard, "Space")
                elif clicked_button.text == "Enter":
                    typed_text += "\n"
                    if live_typing_on:
                        send_key(keyboard, "Enter")
                else:
                    typed_text += clicked_button.text
                    if live_typing_on:
                        send_key(keyboard, clicked_button.text)

            pinch_was_active = pinch_active

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pygame_frame = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            screen.blit(pygame_frame, (0, 0))

            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            for button in button_list:
                is_hovered = button == hovered_button
                is_clicked = button == clicked_button
                button_font = small_font if button.text == "Backspace" else font

                base_color = (50, 50, 50)
                if button.text == "Caps" and caps_lock_on:
                    base_color = (0, 150, 0)
                elif button.text == "LIVE: ON":
                    base_color = (0, 120, 0)

                button.draw(
                    overlay,
                    button_font,
                    base_color,
                    (100, 100, 100),
                    (0, 255, 0),
                    is_hovered,
                    is_clicked,
                )

            pygame.draw.rect(
                overlay,
                (200, 200, 200, 200),
                [start_x, 50, 10 * (key_size + key_gap) - key_gap, 80],
                border_radius=10,
            )
            text_surf = display_font.render(typed_text.split("\n")[-1], True, (0, 0, 0))
            overlay.blit(text_surf, (start_x + 10, 60))

            status_text = "LIVE TYPING: ON" if live_typing_on else "LIVE TYPING: OFF"
            status_color = (0, 180, 0) if live_typing_on else (220, 60, 60)
            status_surf = status_font.render(status_text, True, status_color)
            overlay.blit(status_surf, (20, 15))

            screen.blit(overlay, (0, 0))
            display_frame = pygame.surfarray.array3d(screen).swapaxes(0, 1)
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_RGB2BGR)
            cv2.imshow(window_name, display_frame)

            if cv2.waitKey(1) & 0xFF == 27:
                running = False
            elif cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                running = False

            clock.tick(30)
    finally:
        cap.release()
        hands.close()
        cv2.destroyAllWindows()
        pygame.quit()

    print(f"\n--- Final Typed Message ---\n{typed_text}\n---------------------------\n")

if __name__ == "__main__":
    main()