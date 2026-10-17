import re
import time
import tkinter as tk

import pyautogui
import pyperclip

from open_ai import ask_model


# ============================================================
# SETTINGS
# ============================================================

KASHFEEN_NAME = "Kashfeen"

# Your WhatsApp / screen coordinates
# Keep/change these according to your screen.
CHAT_CLICK = (518, 748)

TEXT_START = (469, 141)
TEXT_END = (713, 664)

# Send button / message box
MESSAGE_BOX = (562, 690)


# ============================================================
# COPY SELECTED WHATSAPP CHAT
# ============================================================

def copy_selected_text() -> str:

    pyautogui.click(*CHAT_CLICK)

    time.sleep(0.5)

    # Select WhatsApp chat text
    pyautogui.moveTo(*TEXT_START)

    pyautogui.dragTo(
        *TEXT_END,
        duration=1.0,
        button="left"
    )

    pyautogui.hotkey("ctrl", "c")

    time.sleep(0.5)

    # Read clipboard
    clipboard = tk.Tk()
    clipboard.withdraw()

    try:
        selected_text = clipboard.clipboard_get()
    except Exception:
        selected_text = ""
    finally:
        clipboard.destroy()

    return selected_text


# ============================================================
# EXTRACT LATEST MESSAGE FROM KASHFEEN
# ============================================================

def get_latest_kashfeen_message(chat_text: str) -> str:

    if not chat_text:
        return ""

    chat_text = chat_text.replace("\r\n", "\n")
    chat_text = chat_text.replace("\r", "\n")
    chat_text = chat_text.replace("\u200e", "")

    # --------------------------------------------------------
    # Format normally looks approximately like:
    #
    # [10:45 am, 27/9/2026] Kashfeen: hello
    #
    # or
    #
    # 10:45 am, 27/9/2026] Kashfeen: hello
    #
    # --------------------------------------------------------

    message_pattern = re.compile(
        r"""
        (?P<header>
            \[?
            \d{1,2}:\d{2}\s*(?:am|pm)
            (?:,\s*\d{1,2}/\d{1,2}/\d{2,4})?
            \]?
            \s*
            (?P<sender>[^:\n]+)
            :
        )
        \s*
        (?P<message>.*?)
        (?=
            \n\s*\[?
            \d{1,2}:\d{2}\s*(?:am|pm)
            |
            \Z
        )
        """,
        re.IGNORECASE | re.VERBOSE | re.DOTALL
    )

    messages = []

    for match in message_pattern.finditer(chat_text):

        sender = match.group("sender").strip()
        message = match.group("message").strip()

        messages.append(
            {
                "sender": sender,
                "message": message
            }
        )

    # --------------------------------------------------------
    # Find the LAST message belonging to Kashfeen
    # --------------------------------------------------------

    latest = None

    for msg in messages:

        if msg["sender"].strip().lower() == KASHFEEN_NAME.lower():

            latest = msg["message"]

    if latest:
        return clean_message(latest)

    # --------------------------------------------------------
    # FALLBACK
    #
    # If WhatsApp copied text doesn't contain timestamps in
    # the expected format, look for "Kashfeen:"
    # --------------------------------------------------------

    simple_pattern = re.compile(
        r"(?im)(?:^|\n)\s*(?:\[[^\]]+\]\s*)?(?P<sender>[^:\n]+?)\s*:\s*(?P<message>.*?)(?=\n\s*(?:\[[^\]]+\]\s*)?(?:Kashfeen|Kashish|[A-Za-z][A-Za-z0-9_ ]+)\s*:|\Z)",
        re.DOTALL
    )

    last_match = ""

    for match in simple_pattern.finditer(chat_text):
        sender = match.group("sender").strip()
        message = match.group("message").strip()
        if sender.lower() == KASHFEEN_NAME.lower():
            last_match = message

    if last_match:
        return clean_message(last_match)

    for line in reversed(chat_text.splitlines()):
        line = line.strip()
        if not line or "kashfeen" not in line.lower():
            continue
        if ":" in line:
            prefix, message = line.split(":", 1)
            if "kashfeen" in prefix.lower():
                return clean_message(message)

    return ""


# ============================================================
# CLEAN MESSAGE
# ============================================================

def clean_message(message: str) -> str:

    message = message.strip()

    # Remove WhatsApp deleted-message text
    deleted_patterns = [
        "You deleted this message",
        "This message was deleted",
        "You deleted this message."
    ]

    for pattern in deleted_patterns:

        if pattern.lower() in message.lower():

            lines = message.splitlines()

            lines = [
                line
                for line in lines
                if pattern.lower() not in line.lower()
            ]

            message = "\n".join(lines)

    # Remove extra spaces
    message = re.sub(r"\s+", " ", message)

    return message.strip()


# ============================================================
# SEND MESSAGE TO WHATSAPP
# ============================================================

def send_whatsapp_message(reply: str):

    if not reply:
        return

    pyperclip.copy(reply)

    time.sleep(0.2)

    pyautogui.click(*MESSAGE_BOX)

    time.sleep(0.2)

    pyautogui.hotkey("ctrl", "v")

    time.sleep(0.2)

    pyautogui.press("enter")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 50)
    print("WhatsApp Kashish Bot")
    print("=" * 50)

    # Copy WhatsApp conversation
    chat_text = copy_selected_text()

    print("\n--- COPIED CHAT ---")
    print(chat_text)

    if not chat_text or not chat_text.strip():
        print("\nClipboard was empty. Select the WhatsApp chat first, then run the bot again.")
        raise SystemExit

    # Extract ONLY latest Kashfeen message
    latest_message = get_latest_kashfeen_message(chat_text)

    print("\n--- LATEST KASHFEEN MESSAGE ---")
    print(latest_message)

    if not latest_message:

        print("\nNo Kashfeen message found.")
        print("Possible reasons:")
        print("1. The chat selection was empty or wrong.")
        print("2. WhatsApp text is not in a standard chat format.")
        print("3. The copied message is not from Kashfeen.")
        print("4. The selected area did not include the message text.")
        print("Bot stopped.")

    else:

        # Ask Ollama
        reply = ask_model(latest_message)

        print("\n--- KASHISH REPLY ---")
        print(reply)

        # Send reply
        send_whatsapp_message(reply)

        print("\nMessage sent.")