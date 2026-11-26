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

PINCH_DISTANCE = 40            # thumb-index distance in pixels that counts as a pinch
PINCH_GRACE_FRAMES = 5         # brief tracking dropouts shorter than this do not count as a new pinch
HAND_DETECT_SIZE = (640, 360)  # hand tracking runs on a smaller frame for speed
CREDIT_TEXT = "Made by Ali Khan"

EMOJIS = [
    "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇",
    "😍", "🥰", "😘", "😎", "🤩", "😏", "😜", "🤔", "😴", "😭",
    "😡", "👍", "👎", "👏", "🙏", "🔥", "❤️", "🎉", "💯", "✨",
]
SYMBOLS_ROW_A = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+"]
SYMBOLS_ROW_B = ["}", "{", ":", '"', "|", "?", ">", "<", "/", "`", "\\"]

# Common words, most frequent first. Used for word completion.
WORDS = list(dict.fromkeys([
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "it", "for", "not", "on",
    "with", "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we",
    "say", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their",
    "what", "so", "up", "out", "if", "about", "who", "get", "which", "go", "me", "when",
    "make", "can", "like", "time", "no", "just", "him", "know", "take", "people", "into",
    "year", "your", "good", "some", "could", "them", "see", "other", "than", "then", "now",
    "look", "only", "come", "its", "over", "think", "also", "back", "after", "use", "two",
    "how", "our", "work", "first", "well", "way", "even", "new", "want", "because", "any",
    "these", "give", "day", "most", "us", "hello", "thanks", "thank", "please", "love",
    "yes", "okay", "sorry", "today", "tomorrow", "home", "really", "right", "going",
    "morning", "night", "nice", "great", "where", "why", "hey", "happy", "birthday",
    "friend", "call", "text", "message", "meet", "later", "soon", "sure", "maybe",
    "understand", "question", "answer", "need", "should", "would", "could", "please",
]))

# Words that often follow a given word.
NEXT_WORDS = {
    "i": ["am", "have", "will"],
    "you": ["are", "can", "want"],
    "the": ["best", "first", "same"],
    "thank": ["you"],
    "how": ["are", "is", "do"],
    "is": ["the", "a", "it"],
    "are": ["you", "the", "we"],
    "see": ["you", "the", "it"],
    "good": ["morning", "night", "luck"],
    "love": ["you"],
    "going": ["to"],
    "want": ["to"],
    "to": ["be", "the", "do"],
}
DEFAULT_NEXT = ["the", "and", "to"]


def current_word(text):
    if not text or text[-1].isspace():
        return ""
    return text.split()[-1]


def apply_case(word, partial):
    if len(partial) > 1 and partial.isupper():
        return word.upper()
    if partial[:1].isupper():
        return word.capitalize()
    return word


def get_suggestions(text):
    partial = current_word(text).lower()
    if partial:
        return [w for w in WORDS if w.startswith(partial) and w != partial][:3]
    if not text.strip():
        return DEFAULT_NEXT[:3]
    last = text.split()[-1].lower()
    return NEXT_WORDS.get(last, DEFAULT_NEXT)[:3]


class Button:
    def __init__(self, pos, text, size=(85, 85), kind="key"):
        self.pos = pos
        self.size = size
        self.text = text
        self.kind = kind
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self._label = None
        self._label_key = None

    def draw(self, screen, font, base_color, hover_color, click_color, is_hovered, is_clicked):
        current_color = base_color
        if is_clicked:
            current_color = click_color
        elif is_hovered:
            current_color = hover_color

        pygame.draw.rect(screen, current_color + (180,), self.rect, border_radius=10)

        key = (id(font), self.text)
        if self._label_key != key:
            self._label = font.render(self.text, True, (255, 255, 255))
            self._label_key = key
        text_rect = self._label.get_rect(center=self.rect.center)
        screen.blit(self._label, text_rect)


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
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    caps_lock_on = False
    live_typing_on = False
    emoji_mode = False         # False = letters keyboard, True = emoji and symbols keyboard
    suggestions = []

    key_size, key_gap = 80, 10
    key_area_width = 10 * (key_size + key_gap) - key_gap          # 890
    start_x = (screen_width - key_area_width) // 2                 # 195
    start_y = 150
    window_name = "AI Dynamic Virtual Keyboard"

    # Layout (no overlaps):
    #   top-right    (x 1100-1250, y 50-130) : EMOJI / ABC switch
    #   typed text   (x 195-1085,  y 50-130) : typed message
    #   key area     (x 195-1085,  y 150-590): letters, or emoji and symbols
    #   suggestions  (x 195-1085,  y 600-650): word suggestions (letters only)
    #   action row   (y 510 letters, y 600 emoji): Caps/ABC, Space, Backspace, Enter, LIVE
    #   credit       (bottom-right corner)
    def add_action_row(buttons, y):
        buttons.append(Button((start_x, y), "ABC" if emoji_mode else "Caps", (125, key_size), kind="toggle"))
        buttons.append(Button((start_x + 135, y), "Space", (390, key_size)))
        buttons.append(Button((start_x + 535, y), "Backspace", (160, key_size)))
        buttons.append(Button((start_x + 705, y), "Enter", (130, key_size)))
        live_text = "LIVE: ON" if live_typing_on else "LIVE: OFF"
        buttons.append(Button((start_x + 845, y), live_text, (200, key_size), kind="toggle"))

    def generate_buttons():
        buttons = []
        buttons.append(Button((1100, 50), "ABC" if emoji_mode else "EMOJI", (150, 80), kind="toggle"))

        if emoji_mode:
            for i, emo in enumerate(EMOJIS):
                row, col = divmod(i, 10)
                x = start_x + col * (key_size + key_gap)
                y = start_y + row * (key_size + key_gap)
                buttons.append(Button((x, y), emo, (key_size, key_size), kind="emoji"))

            sym_size, sym_gap = 68, 6
            row_a_y = start_y + 3 * (key_size + key_gap)        # 420
            total_a = len(SYMBOLS_ROW_A) * sym_size + (len(SYMBOLS_ROW_A) - 1) * sym_gap
            x0 = start_x + (key_area_width - total_a) // 2
            for i, ch in enumerate(SYMBOLS_ROW_A):
                x = x0 + i * (sym_size + sym_gap)
                buttons.append(Button((x, row_a_y), ch, (sym_size, key_size), kind="symbol"))

            row_b_y = row_a_y + key_size + key_gap              # 510
            total_b = len(SYMBOLS_ROW_B) * sym_size + (len(SYMBOLS_ROW_B) - 1) * sym_gap
            x0 = start_x + (key_area_width - total_b) // 2
            for i, ch in enumerate(SYMBOLS_ROW_B):
                x = x0 + i * (sym_size + sym_gap)
                buttons.append(Button((x, row_b_y), ch, (sym_size, key_size), kind="symbol"))

            add_action_row(buttons, row_b_y + key_size + key_gap)   # 600
        else:
            key_layout = get_key_layout(caps_lock_on)
            for row_idx, row in enumerate(key_layout):
                for col_idx, key in enumerate(row):
                    x = start_x + col_idx * (key_size + key_gap)
                    y = start_y + row_idx * (key_size + key_gap)
                    buttons.append(Button((x, y), key, (key_size, key_size)))

            last_row_y = start_y + len(key_layout) * (key_size + key_gap)   # 510
            add_action_row(buttons, last_row_y)

            suggest_y = last_row_y + key_size + key_gap                     # 600
            for i, word in enumerate(suggestions):
                x = start_x + i * (290 + 10)
                buttons.append(Button((x, suggest_y), word, (290, 50), kind="suggest"))
        return buttons

    button_list = generate_buttons()
    layout_key = None          # rebuild buttons only when their look or content changes

    font = pygame.font.SysFont("Arial", 35)
    display_font = pygame.font.SysFont("Arial", 50)
    status_font = pygame.font.SysFont("Arial", 24)
    small_font = pygame.font.SysFont("Arial", 25)
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", 34)
    credit_font = pygame.font.SysFont("Arial", 22)
    click_sound = generate_click_sound()

    typed_text = ""
    click_delay = 0.5
    last_click_times = {}      # key position -> time of its last click
    pinch_last_seen = {}       # key position -> frame index when it was last pinched
    frame_idx = 0

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, screen_width, screen_height)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

    running = True
    try:
        while running:
            success, frame = cap.read()
            if not success:
                continue

            frame_idx += 1
            suggestions = get_suggestions(typed_text)
            new_layout_key = (caps_lock_on, live_typing_on, emoji_mode, tuple(suggestions))
            if new_layout_key != layout_key:
                button_list = generate_buttons()
                layout_key = new_layout_key

            frame = cv2.flip(frame, 1)
            small_rgb = cv2.cvtColor(cv2.resize(frame, HAND_DETECT_SIZE), cv2.COLOR_BGR2RGB)
            results = hands.process(small_rgb)

            hovered_positions = set()
            pinch_buttons = {}     # key position -> button, pinched by any hand this frame

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

                    hovered = None
                    for button in button_list:
                        if button.rect.collidepoint(index_tip):
                            hovered = button

                    if hovered is not None:
                        hovered_positions.add(hovered.pos)

                    dist = math.hypot(
                        index_tip[0] - thumb_tip[0],
                        index_tip[1] - thumb_tip[1],
                    )
                    if dist < PINCH_DISTANCE and hovered is not None:
                        pinch_buttons[hovered.pos] = hovered

            current_time = time.monotonic()
            # A key only clicks when it was not pinched recently, so short tracking dropouts do not double-tap.
            clicked_buttons = []
            for pos, button in pinch_buttons.items():
                last_seen = pinch_last_seen.get(pos)
                is_new_pinch = last_seen is None or frame_idx - last_seen > PINCH_GRACE_FRAMES
                if is_new_pinch and current_time - last_click_times.get(pos, 0.0) >= click_delay:
                    clicked_buttons.append(button)
                pinch_last_seen[pos] = frame_idx
            for pos in [p for p, f in pinch_last_seen.items() if frame_idx - f > PINCH_GRACE_FRAMES]:
                del pinch_last_seen[pos]

            clicked_positions = set()
            for clicked_button in clicked_buttons:
                clicked_positions.add(clicked_button.pos)
                click_sound.play()
                last_click_times[clicked_button.pos] = current_time

                if clicked_button.kind == "toggle":
                    if clicked_button.text == "Caps":
                        caps_lock_on = not caps_lock_on
                    elif clicked_button.text.startswith("LIVE:"):
                        live_typing_on = not live_typing_on
                    elif clicked_button.text in ("EMOJI", "ABC"):
                        emoji_mode = not emoji_mode

                elif clicked_button.kind == "suggest":
                    partial = current_word(typed_text)
                    word = apply_case(clicked_button.text, partial)
                    if live_typing_on:
                        for _ in partial:
                            send_key(keyboard, "Backspace")
                        keyboard.type(word + " ")
                    typed_text = typed_text[:len(typed_text) - len(partial)] + word + " "

                elif clicked_button.kind in ("emoji", "symbol"):
                    typed_text += clicked_button.text
                    if live_typing_on:
                        keyboard.type(clicked_button.text)

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

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pygame_frame = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            screen.blit(pygame_frame, (0, 0))

            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            for button in button_list:
                is_hovered = button.pos in hovered_positions
                is_clicked = button.pos in clicked_positions

                if button.kind == "emoji":
                    button_font = emoji_font
                elif button.kind == "suggest" or button.text == "Backspace":
                    button_font = small_font
                elif button.text == "EMOJI" or button.text == "ABC":
                    button_font = small_font
                else:
                    button_font = font

                base_color = (50, 50, 50)
                if button.text == "Caps" and caps_lock_on:
                    base_color = (0, 150, 0)
                elif button.text == "LIVE: ON":
                    base_color = (0, 120, 0)
                elif button.text == "EMOJI" and emoji_mode:
                    base_color = (0, 120, 0)
                elif button.kind == "suggest":
                    base_color = (30, 60, 110)
                elif button.kind in ("emoji", "symbol"):
                    base_color = (60, 60, 60)

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
                [start_x, 50, key_area_width, 80],
                border_radius=10,
            )
            text_surf = display_font.render(typed_text.split("\n")[-1], True, (0, 0, 0))
            overlay.blit(text_surf, (start_x + 10, 60))

            status_text = "LIVE TYPING: ON" if live_typing_on else "LIVE TYPING: OFF"
            status_color = (0, 180, 0) if live_typing_on else (220, 60, 60)
            status_surf = status_font.render(status_text, True, status_color)
            overlay.blit(status_surf, (20, 15))

            credit_surf = credit_font.render(CREDIT_TEXT, True, (235, 235, 235))
            credit_rect = credit_surf.get_rect(
                bottomright=(screen_width - 14, screen_height - 8)
            ).inflate(16, 8)
            pygame.draw.rect(overlay, (0, 0, 0, 110), credit_rect, border_radius=8)
            overlay.blit(credit_surf, credit_surf.get_rect(center=credit_rect.center))

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