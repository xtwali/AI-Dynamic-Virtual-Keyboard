# ⌨️ AI Dynamic Virtual Keyboard

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2B-0078D6.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-orange.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.11-green.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A webcam-based, **hands-free virtual keyboard** 🖐️. The app tracks **up to two hands** with MediaPipe, draws a keyboard over your camera feed, and detects a **pinch gesture** 🤏 to select keys. It also offers **word suggestions**, an **emoji and symbol keyboard** 😀, and **Live Typing**, which sends the selected keys to the currently active desktop application using `pynput`.

> ⚠️ **Safety:** Live Typing starts **OFF**. Turn it on only after focusing the intended text field. Keystrokes go to whichever application is active, so **do not use Live Typing in password fields** or other sensitive inputs.

---

## 📑 Table of Contents

- [Features](#-features)
- [How It Works](#-how-it-works)
- [Requirements](#-requirements)
- [Get the Source](#-get-the-source)
- [Installation](#️-installation)
- [Run the Application](#️-run-the-application)
- [How to Use](#-how-to-use)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Development](#-development)
- [Author](#-author)
- [License](#-license)

---

## ✨ Features

- 🖐️ Real-time tracking of **two hands** with MediaPipe and OpenCV.
- 🪞 Mirrored camera feed with the virtual keyboard drawn on top.
- 🤏 Pinch-to-press gesture using the index fingertip and thumb, with either hand.
- 🔤 Letter and number keys, with a **Caps** toggle for letter case.
- 💡 **Word suggestions** above the keyboard, like predictive text on a phone. Tap one to complete the word you're typing or to pick a likely next word.
- 😀 **Emoji keyboard** with 30 emojis, plus two rows of symbols (`!@#$%^&*()_+` and `}{:"|?></\`\`).
- ␣ Space, Backspace, and Enter keys.
- 💻 Optional OS-level typing in the active application, including browsers, text editors, and other standard apps.
- 🔒 Live Typing starts OFF and can be toggled from the virtual keyboard.
- ⏱️ One key press per pinch, with a 0.5-second cooldown per key. Holding a pinch does not repeat the key.
- 📌 OpenCV window configured to stay on top of other windows.
- 🔊 Click sound and an on-screen preview of the typed text.

---

## 🔬 How It Works

1. 📷 OpenCV reads and mirrors webcam frames.
2. 🖐️ MediaPipe Hands detects up to two hands. Hand tracking runs on a smaller copy of the frame to keep the app responsive.
3. 👆 Each index fingertip determines which virtual key is hovered.
4. 🤏 A pinch is detected when the index fingertip and thumb tip are close together while hovering over a key. Brief tracking dropouts do not count as a new pinch.
5. 🎨 Pygame draws the keyboard, suggestions, and preview onto the camera frame.
6. ⌨️ When Live Typing is ON, `pynput` sends the selected key, emoji, or symbol to the active application.

---

## 📋 Requirements

- 🪟 Windows 10 or later (the documented setup uses PowerShell and the Windows Python launcher).
- 🐍 Python 3.12.
- 📷 A webcam.
- 🔊 A working audio output device for the key-click sound.
- 🔐 Permission for Python to access the camera.

The project dependencies are listed in [`src/requirements.txt`](src/requirements.txt):

| Package | Used for |
|---|---|
| OpenCV | Camera capture and window |
| MediaPipe | Hand landmark detection |
| Pygame | Drawing the keyboard, suggestions, and preview |
| NumPy | Numeric processing |
| pynput | Sending keys to the active app |

---

## 📥 Get the Source

```powershell
git clone https://github.com/xtwali/AI-Dynamic-Virtual-Keyboard.git
cd AI-Dynamic-Virtual-Keyboard
```

---

## 🛠️ Installation

From the repository folder, open PowerShell and run:

```powershell
cd src
py -3.12 -m venv .venv-fixed
.\.venv-fixed\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The dependency file installs `pynput` along with the other packages. To install or update it separately in the active environment:

```powershell
python -m pip install pynput
```

If PowerShell prevents activation of the virtual environment, you can invoke its Python directly instead:

```powershell
.\.venv-fixed\Scripts\python.exe -m pip install -r requirements.txt
```

---

## ▶️ Run the Application

From the `src` directory, with the virtual environment activated:

```powershell
python main.py
```

Or, without activating the environment:

```powershell
.\.venv-fixed\Scripts\python.exe main.py
```

The app opens a topmost camera window. Allow camera access if Windows asks. Press `Esc` in the window to exit.

---

## 🎮 How to Use

1. 🖐️ Start the app and show one or both hands in the camera feed.
2. 🖱️ Click the text field in the external app where you want to type (for example, a browser search field or Notepad).
3. 🟢 Hover over the `LIVE: OFF` button and pinch to turn Live Typing **ON**. The status text changes to `LIVE TYPING: ON`.
4. 🔤 Hover over a letter, number, or special key and pinch to press it. Either hand can type.
5. 💡 Tap a word in the suggestion bar to complete the word you're typing, or to pick a likely next word. With Live Typing ON, the suggestion is typed into the active app.
6. 😀 Pinch `EMOJI` in the top-right corner to switch to the emoji and symbol keyboard. Pinch `ABC` (top-right or bottom-left) to return to letters.
7. 🤏 Release the pinch before selecting the next key. A held pinch does not repeat a key.
8. 🔴 Pinch the Live button again to turn Live Typing **OFF**.
9. 🚪 Press `Esc` while the keyboard window is focused, or close the window, to exit.

### 🔑 Virtual Keys

| Key | Action |
| --- | --- |
| Letter or number | Types that character when Live Typing is ON |
| Suggestion | Completes the current word or adds a likely next word |
| Emoji or symbol | Types it (emoji mode only) |
| Caps | Toggles the virtual keyboard's letter case |
| EMOJI / ABC | Switches between the letter keyboard and the emoji and symbol keyboard |
| Space | Sends a space |
| Backspace | Deletes the previous character in the preview and the active app |
| Enter | Sends Enter (for example, to submit a search) |
| LIVE: OFF / LIVE: ON | Enables or disables OS-level typing |

> 💡 The on-screen text preview is maintained by the app. It is not the destination text field; the active external application receives keys only while Live Typing is ON.

---

## 📂 Project Structure

```text
AI-Dynamic-Virtual-Keyboard/
├── README.md
├── .gitignore
└── src/
    ├── main.py                 # Camera loop, two-hand tracking, keyboard UI, suggestions, emoji, and key dispatch
    ├── requirements.txt        # Python dependencies
    └── .vscode/
        └── settings.json       # Local VS Code interpreter settings, if present
```

The `.venv-fixed` folder is created locally during installation and contains the Python virtual environment; it is not application source code.

---

## 🔧 Troubleshooting

### ❌ `ModuleNotFoundError` for `cv2`, `mediapipe`, `pygame`, or `pynput`

The app is probably running with a different Python interpreter, or the dependencies were not installed in the active environment.

```powershell
cd src
.\.venv-fixed\Scripts\Activate.ps1
python --version
python -m pip install -r requirements.txt
python main.py
```

Use Python 3.12 and check that `python --version` reports the virtual environment's interpreter. In VS Code, select `src\.venv-fixed\Scripts\python.exe` as the Python interpreter, or open a new integrated terminal after selecting it.

### ❌ `module 'mediapipe' has no attribute 'solutions'`

The app uses MediaPipe's `solutions` API, which newer MediaPipe releases don't include. Install the pinned version in a Python 3.12 environment:

```powershell
python -m pip install mediapipe==0.10.14
```

### 🚫 PowerShell says script execution is disabled

Run the app without activating the environment:

```powershell
.\.venv-fixed\Scripts\python.exe main.py
```

### 📷 "Could not open webcam"

- Connect the webcam and make sure no other app is using it.
- Allow camera access in Windows privacy settings.
- Restart the app after granting access.
- The app currently opens camera index `0`; systems with multiple cameras may require choosing a different camera.

### 🤏 Hand or pinch is not detected reliably

- Improve lighting and keep the hand fully visible in the camera frame.
- Keep both the thumb tip and index fingertip in view.
- Move the hand so the index fingertip is over the intended key before pinching.
- Release the pinch between key presses; a single continuous pinch intentionally triggers only one key.
- If pinches trigger by accident, lower `PINCH_DISTANCE` near the top of `main.py`. If they are missed, raise it.

### 😀 Emoji show as boxes or outlines

Emoji are drawn with the Windows `Segoe UI Emoji` font. If it's missing or the display shows outlines, the keys still type correctly when Live Typing is ON.

### ⌨️ Keys appear in the wrong application or nowhere

- Click the destination text field before enabling Live Typing.
- Confirm the status reads `LIVE TYPING: ON`.
- Make sure the intended application is the active window. Keystrokes are sent to the active app, not to the app under a particular screen coordinate.
- Some secure fields or elevated applications may block simulated input. Avoid password fields.

### 📌 The camera window is not staying on top

The app uses OpenCV's `WND_PROP_TOPMOST` window property. Reinstall the declared OpenCV dependency in the active environment:

```powershell
python -m pip install --force-reinstall opencv-python==4.11.0.86
```

### 🔇 No click sound or mixer initialization error

Check that Windows has an available audio output device, then restart the app.

---

## 👨‍💻 Development

Activate the virtual environment from `src` before running or editing the app:

```powershell
.\.venv-fixed\Scripts\Activate.ps1
```

The application entry point is `src/main.py`; dependencies are maintained in `src/requirements.txt`.

---

## 👤 Author

**Ali Khan**

---

## 📄 License

This project is released under the **MIT License**.

---

<p align="center">Made with ❤️ by <b>Ali Khan</b></p>
