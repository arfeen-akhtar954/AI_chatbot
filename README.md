# WhatsApp AI Chatbot

A small Python desktop automation project that drafts a WhatsApp reply using a
locally running Ollama model. It reads copied chat text from the WhatsApp
window, finds the latest message from a configured sender, asks the local
model for a reply, and pastes and sends that reply.

The project uses Ollama on your own computer; it does **not** send requests to
the hosted OpenAI API. The main automation is a one-shot script and relies on
fixed screen coordinates, so it must be configured for your display and used
with care.

## Features

- Reads text selected from the WhatsApp desktop window using the clipboard.
- Extracts the latest message from a sender name configured in `bot.py`.
- Generates a short conversational reply using the `llama3.2:1b` model through
  Ollama's local OpenAI-compatible API.
- Pastes and sends the generated reply through keyboard and mouse automation.
- Provides a separate command-line script to try the model without WhatsApp.
- Includes small utilities for sending a fixed test message and reading mouse
  cursor coordinates.

## Technologies

- Python
- Ollama with the `llama3.2:1b` model
- The OpenAI Python SDK, configured to call Ollama at
  `http://localhost:11434/v1`
- PyAutoGUI and Pyperclip for desktop and clipboard automation
- Tkinter (included with most Windows Python installations) for clipboard
  access

## Project structure

| File | Purpose |
| --- | --- |
| `bot.py` | Main one-shot WhatsApp workflow: copy chat text, find the latest configured sender message, generate a reply, and send it. |
| `open_ai.py` | Configures the local Ollama client, defines the reply prompt, and provides a command-line model test. |
| `send_message.py` | Sends a fixed test message to a hard-coded screen position. |
| `get_cursor.py` | Continuously prints the current mouse cursor coordinates. |
| `requirements.txt` | Lists the OpenAI Python SDK dependency. |

## Windows installation and setup

1. Install Python and Ollama for Windows. Make sure Python's `py` launcher is
   available in PowerShell.
2. Open PowerShell in the project folder and create and activate a virtual
   environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, allow locally-created scripts for your
   user, then activate the environment again:

   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the listed dependency and the GUI/clipboard packages imported by
   the scripts:

   ```powershell
   python -m pip install -r requirements.txt pyautogui pyperclip
   ```

   `requirements.txt` currently lists only the OpenAI SDK; PyAutoGUI and
   Pyperclip are also needed to run the desktop scripts.
4. Start Ollama and download the model used by the code:

   ```powershell
   ollama pull llama3.2:1b
   ```

   Keep the Ollama application/service running while using the chatbot. The
   code connects to `localhost` on port `11434`.
5. Open WhatsApp Desktop (or WhatsApp Web in a browser) and display the chat
   you want the bot to read. Adjust the screen coordinates and configured
   sender in `bot.py` for your setup before running the automation.

## Configuration and environment variables

No environment variables are read by the current code, and no online API key
is required. `open_ai.py` configures the SDK with a local base URL and the
literal API-key value `"ollama"` required by the client; that value is a local
placeholder, not a secret.

The model name (`llama3.2:1b`), Ollama URL, reply prompt, sender name, and
WhatsApp screen coordinates are set directly in the Python source. In
particular, `bot.py` uses fixed coordinates for selecting the chat and message
area, so update them to match your screen before relying on the automation.

## Run the chatbot

With the virtual environment active and Ollama running, launch the main
workflow from PowerShell:

```powershell
python bot.py
```

The script copies the selected on-screen chat area, searches the copied text
for the latest message from the configured sender, generates a reply, and
sends it through WhatsApp. It runs once per launch; it is not a background or
continuous monitor.

**Review the screen coordinates before running.** The script sends the
generated reply by pressing Enter, without asking for confirmation. It also
prints the copied chat text to the terminal, so avoid running it where that
output could be seen or recorded by others.

## Example usage

To test reply generation without using WhatsApp, run:

```powershell
python open_ai.py
```

Enter a message at the prompt. The script prints the model's generated reply;
it does not send a WhatsApp message.

The other utilities can be run separately:

```powershell
python get_cursor.py
python send_message.py
```

`get_cursor.py` prints cursor coordinates continuously until stopped.
`send_message.py` sends a hard-coded test message to its own fixed screen
coordinates, so check and adjust those coordinates before using it.

## Future improvements

- Move screen positions, sender, model, and Ollama URL into user-editable
  configuration.
- Add an explicit review/confirmation step before sending generated replies.
- Improve dependency tracking so a fresh install includes every required
  package.
- Add tests for extracting messages from copied WhatsApp text.
- Avoid printing the full copied conversation by default.
