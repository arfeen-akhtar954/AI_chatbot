import pyautogui
import time

message = "Hello! This is an AI test message."

# Click WhatsApp's message input box
pyautogui.click(607, 700)

time.sleep(0.5)

# Type the message
pyautogui.write(message, interval=0.01)

# Send
pyautogui.press("enter")