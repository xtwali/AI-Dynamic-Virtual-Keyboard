# AI Dynamic Virtual Keyboard

A webcam-based, hands-free virtual keyboard. The application tracks one hand with MediaPipe, displays a keyboard over the camera feed, and detects a pinch gesture to select keys. When **Live Typing** is enabled, selected keys are sent to the currently active desktop application using `pynput`.

> **Safety:** Live Typing starts OFF. Turn it on only after focusing the intended text field. Keystrokes go to whichever application is active, so do not use Live Typing in password fields or other sensitive inputs.

## Features

- Real-time hand landmark tracking with MediaPipe and OpenCV.
- Mirrored camera feed with virtual keyboard controls.
- Pinch-to-press gesture using the index fingertip and thumb.
- Virtual letter and number keys, with a Caps toggle for letter case.
- Space, Backspace, and Enter keys.
- Optional OS-level typing in the active application, including browsers, text editors, and other standard apps.
- Live Typing starts OFF and can be toggled from the virtual keyboard.
- One key press per pinch, with a 0.4-second cooldown.
- OpenCV window configured to stay on top of other windows.
- Click sound and an on-screen preview of the typed text.

## How It Works

1. OpenCV reads and mirrors webcam frames.
2. MediaPipe Hands detects hand landmarks.
3. The index fingertip position determines which virtual key is hovered.
4. A pinch is detected when the index fingertip and thumb tip are close together while hovering over a key.
5. Pygame draws the keyboard and preview onto the camera frame.
6. When Live Typing is ON, `pynput` sends the selected key to the active application.

## Requirements

- Windows 10 or later (the documented setup uses PowerShell and the Windows Python launcher).
- Python 3.12.
- A webcam.
- A working audio output device for the key-click sound.
- Permission for Python to access the camera.

The project dependencies are listed in [`src/requirements.txt`](src/requirements.txt):

- OpenCV
- MediaPipe
- Pygame
- NumPy
- pynput

## Get the Source

```powershell
git clone https://github.com/Zaid2044/AI-Dynamic-Virtual-Keyboard.git
cd AI-Dynamic-Virtual-Keyboard
```

## Installation

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

## Run the Application

From the `src` directory, with the virtual environment activated:

```powershell
python main.py
```

Or, without activating the environment:

```powershell
.\.venv-fixed\Scripts\python.exe main.py
```

The app opens a topmost camera window. Allow camera access if Windows asks.

## How to Use

1. Start the app and position your hand so it is visible in the camera feed.
2. Click the text field in the external app where you want to type (for example, a browser search field or Notepad).
3. Hover over the `LIVE: OFF` virtual button and pinch your thumb and index finger to turn Live Typing ON. The status text changes to `LIVE TYPING: ON`.
4. Hover over a letter, number, or special key and pinch to press it.
5. Release the pinch before selecting the next key. A held pinch does not repeat a key.
6. Pinch the Live button again to turn Live Typing OFF.
7. Press `Esc` while the keyboard window is focused, or close the window, to exit.

### Virtual Keys

| Key | Action |
| --- | --- |
| Letter or number | Types that character when Live Typing is ON |
| Caps | Toggles the virtual keyboard's letter case |
| Space | Sends a space |
| Backspace | Deletes the previous character in the active app |
| Enter | Sends Enter (for example, to submit a search) |
| LIVE: OFF / LIVE: ON | Enables or disables OS-level typing |

The on-screen text preview is maintained by the app. It is not the destination text field; the active external application receives keys only while Live Typing is ON.

## Project Structure

```text
AI-Dynamic-Virtual-Keyboard/
├── README.md
├── .gitignore
└── src/
    ├── main.py                 # Camera loop, hand tracking, keyboard UI, and key dispatch
    ├── requirements.txt        # Python dependencies
    └── .vscode/
        └── settings.json       # Local VS Code interpreter settings, if present
```

The `.venv-fixed` folder is created locally during installation and contains the Python virtual environment; it is not application source code.

## Troubleshooting

### `ModuleNotFoundError` for `cv2`, `mediapipe`, `pygame`, or `pynput`

The app is probably running with a different Python interpreter or the dependencies were not installed in the active environment.

```powershell
cd src
.\.venv-fixed\Scripts\Activate.ps1
python --version
python -m pip install -r requirements.txt
python main.py
```

Use Python 3.12 and check that `python --version` reports the virtual environment's interpreter. In VS Code, select `src\.venv-fixed\Scripts\python.exe` as the Python interpreter, or open a new integrated terminal after selecting it.

### PowerShell says script execution is disabled

Run the app without activating the environment:

```powershell
.\.venv-fixed\Scripts\python.exe main.py
```

### “Could not open webcam”

- Connect the webcam and make sure no other app is using it.
- Allow camera access in Windows privacy settings.
- Restart the app after granting access.
- The app currently opens camera index `0`; systems with multiple cameras may require choosing a different camera.

### Hand or pinch is not detected reliably

- Improve lighting and keep the hand fully visible in the camera frame.
- Keep both the thumb tip and index fingertip in view.
- Move the hand so the index fingertip is over the intended key before pinching.
- Release the pinch between key presses; a single continuous pinch intentionally triggers only one key.

### Keys appear in the wrong application or nowhere

- Click the destination text field before enabling Live Typing.
- Confirm the status reads `LIVE TYPING: ON`.
- Make sure the intended application is the active window. Keystrokes are sent to the active app, not to the app under a particular screen coordinate.
- Some secure fields or elevated applications may block simulated input. Avoid password fields.

### The camera window is not staying on top

The app uses OpenCV's `WND_PROP_TOPMOST` window property. Reinstall the declared OpenCV dependency in the active environment:

```powershell
python -m pip install --force-reinstall opencv-python==4.11.0.86
```

### No click sound or mixer initialization error

Check that Windows has an available audio output device, then restart the app.

## Development

Activate the virtual environment from `src` before running or editing the app:

```powershell
.\.venv-fixed\Scripts\Activate.ps1
```

The application entry point is `src/main.py`; dependencies are maintained in `src/requirements.txt`.

## Author

**Ali Khan**

## License

The project documentation identifies this project as MIT-licensed. A standalone `LICENSE` file is not currently included in the repository.
