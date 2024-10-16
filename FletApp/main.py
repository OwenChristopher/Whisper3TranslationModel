# main.py

import flet
from flet import (
    Page,
    View,
    Text,
    TextField,
    Dropdown,
    DropdownItem,
    ElevatedButton,
    Column,
    Row,
    ListView,
    ListTile,
    Divider,
    IconButton,
    ProgressRing,
    SnackBar,
    AlertDialog,
    FilePicker,
    FilePickerResultEvent,
)
import requests
import base64
import io
import re

# -------------------- API Module -------------------- #

API_BASE_URL = 'http://localhost:8000'  # Update if your backend is hosted elsewhere

def set_objective(objective, target_language, user_language, country):
    payload = {
        "objective": objective,
        "target_language": target_language,
        "user_language": user_language,
        "country": country
    }
    response = requests.post(f"{API_BASE_URL}/set_objective", json=payload)
    response.raise_for_status()
    return response.json()

def send_text_message(session_id, message):
    payload = {"message": message}
    response = requests.post(f"{API_BASE_URL}/send_message/{session_id}", json=payload)
    response.raise_for_status()
    return response.json()

def send_audio_message(session_id, audio_file_path):
    files = {'file': open(audio_file_path, 'rb')}
    response = requests.post(f"{API_BASE_URL}/process_audio/{session_id}", files=files)
    response.raise_for_status()
    return response.json()

def get_summary(session_id):
    response = requests.get(f"{API_BASE_URL}/summary/{session_id}")
    response.raise_for_status()
    return response.json()

def synthesize_text(text):
    payload = {"text": text}
    response = requests.post(f"{API_BASE_URL}/synthesize_text", json=payload, stream=True)
    response.raise_for_status()
    return response.content  # Returns binary audio data

# -------------------- Utility Functions -------------------- #

language_code_map = {
    'English': 'en-US',
    'Spanish': 'es-ES',
    'French': 'fr-FR',
    'Chinese': 'zh-CN',
    # Add more languages as needed
}

def parse_assistant_response(assistant_response):
    prefix_pattern = r'^\[(USER|TARGET|CAUTION|SUMMARY)\]\s+'
    match = re.match(prefix_pattern, assistant_response)
    if match:
        message_type = match.group(1).upper()
        message = re.sub(prefix_pattern, '', assistant_response).strip()
        return message_type, message
    else:
        return 'ASSISTANT', assistant_response

# -------------------- Helper Functions -------------------- #

def show_popup(state, title, message):
    state["popup_title"] = title
    state["popup_message"] = message
    state["popup_open"] = True

def close_popup(state, e):
    state["popup_open"] = False

def show_summary(state, message):
    state["summary_message"] = message
    state["summary_open"] = True

def close_summary(state, e):
    state["summary_open"] = False

def show_caution(state, message):
    state["caution_message"] = message
    state["caution_open"] = True

def close_caution(state, e):
    state["caution_open"] = False

def get_color(message_type):
    if message_type == 'USER':
        return flet.colors.BLUE
    elif message_type == 'TARGET':
        return flet.colors.GREEN
    elif message_type in ['CAUTION', 'SUMMARY']:
        return flet.colors.RED
    elif message_type == 'SYSTEM':
        return flet.colors.GREY
    else:
        return flet.colors.BLACK

# -------------------- Components -------------------- #

# Navigation Bar
def NavigationBar(navigate):
    return Row(
        controls=[
            ElevatedButton(
                text="Home",
                icon=flet.icons.HOME,
                on_click=lambda e: navigate('/')
            ),
            ElevatedButton(
                text="Translate",
                icon=flet.icons.TRANSLATE,
                on_click=lambda e: navigate('/translate')
            ),
            ElevatedButton(
                text="History",
                icon=flet.icons.HISTORY,
                on_click=lambda e: navigate('/history')
            ),
            ElevatedButton(
                text="Reset Session",
                icon=flet.icons.RESTART_ALT,
                on_click=lambda e: navigate('reset_session')
            ),
        ],
        alignment="center",
        spacing=10,
    )

# Objective Form
def ObjectiveForm(state, page, navigate):
    objective = flet.Ref[TextField]()
    target_lang = flet.Ref[Dropdown]()
    user_lang = flet.Ref[Dropdown]()
    country_dd = flet.Ref[Dropdown]()

    languages = ["English", "Spanish", "French", "Chinese"]
    countries = ["United States", "China", "Spain", "France"]

    def submit(e):
        obj = objective.current.value
        tgt_lang = target_lang.current.value
        usr_lang = user_lang.current.value
        cnt = country_dd.current.value

        if not obj:
            show_popup(state, "Error", "Objective cannot be empty.")
            page.update()
            return

        state["is_processing"] = True
        page.update()

        try:
            response = set_objective(obj, tgt_lang, usr_lang, cnt)
            state["session_id"] = response['session_id']
            page.snack_bar = SnackBar(Text("Objective set successfully!"), open=True)
            page.snack_bar.open = True
            page.update()
            navigate('/translate')
        except Exception as ex:
            show_popup(state, "Error", f"Failed to set objective: {ex}")
        finally:
            state["is_processing"] = False
            page.update()

    return Column(
        controls=[
            Text("Set Your Objective", style="headlineMedium"),
            TextField(label="Objective", ref=objective, required=True),
            Dropdown(
                label="Your Language",
                ref=user_lang,
                options=[DropdownItem(text=lang) for lang in languages],
                value="English"
            ),
            Dropdown(
                label="Target Language",
                ref=target_lang,
                options=[DropdownItem(text=lang) for lang in languages],
                value="English"
            ),
            Dropdown(
                label="Country/Region",
                ref=country_dd,
                options=[DropdownItem(text=ct) for ct in countries],
                value="United States"
            ),
            ElevatedButton(
                text="Start Session",
                on_click=submit,
                disabled=state["is_processing"]
            ),
            ProgressRing(width=20, height=20, visible=state["is_processing"])
        ],
        spacing=10,
        alignment="start",
    )

# Conversation History
def ConversationHistoryView(state):
    return Column(
        controls=[
            Text("Conversation Logs", style="headlineMedium"),
            ListView(
                expand=True,
                spacing=5,
                padding=10,
                auto_scroll=True,
                controls=[
                    ListTile(
                        title=Text(item['recipient'], weight="bold", color=get_color(item['type'])),
                        subtitle=Text(item['content'])
                    ),
                    Divider()
                ] for item in state["history"]
            )
        ],
        expand=True,
        scroll="auto",
    )

# Popup Dialog
def PopupDialogComponent(state, close_popup_func):
    if state["popup_open"]:
        dialog = AlertDialog(
            title=Text(state["popup_title"]),
            content=Text(state["popup_message"]),
            actions=[
                ElevatedButton("Close", on_click=close_popup_func)
            ],
            on_dismiss=close_popup_func
        )
        return dialog
    return None

# Summary Dialog
def SummaryDialog(state, close_summary_func):
    if state["summary_open"]:
        dialog = AlertDialog(
            title=Text("Conversation Summary"),
            content=Text(state["summary_message"]),
            actions=[
                ElevatedButton("Close", on_click=close_summary_func)
            ],
            on_dismiss=close_summary_func
        )
        return dialog
    return None

# Caution Dialog
def CautionDialog(state, close_caution_func):
    if state["caution_open"]:
        dialog = AlertDialog(
            title=Text("Caution"),
            content=Text(state["caution_message"]),
            actions=[
                ElevatedButton("Close", on_click=close_caution_func)
            ],
            on_dismiss=close_caution_func
        )
        return dialog
    return None

# Text-to-Speech
def TextToSpeechComponent(state, page):
    if state["translated_text"]:
        # Escape quotes and newlines to prevent JS errors
        safe_text = state["translated_text"].replace('"', '\\"').replace('\n', '\\n')
        lang_code = language_code_map.get(state["target_language"], 'en-US')
        js = f"""
            var msg = new SpeechSynthesisUtterance("{safe_text}");
            msg.lang = "{lang_code}";
            window.speechSynthesis.speak(msg);
        """
        page.client.execute_js(js)

# Audio Recorder
def AudioRecorderComponent(state, page):
    file_picker = FilePicker(on_result=lambda e: on_file_picked(e, state, page))

    def on_file_picked(e: FilePickerResultEvent, state, page):
        if e.files:
            file = e.files[0]
            audio_path = file.path
            state["is_processing"] = True
            page.update()
            try:
                response = send_audio_message(state["session_id"], audio_path)
                assistant_response = response.get('assistant_response', '')
                summary = response.get('summary', '')

                message_type, message = parse_assistant_response(assistant_response)

                state["history"].append({
                    "type": message_type,
                    "recipient": "Assistant",
                    "content": message
                })

                state["translated_text"] = message

                if message_type == 'CAUTION':
                    show_caution(state, message)
                elif message_type == 'SUMMARY':
                    show_summary(state, message)

            except Exception as ex:
                show_popup(state, "Error", f"Failed to process audio: {ex}")
            finally:
                state["is_processing"] = False
                page.update()

    def record_audio(e):
        file_picker.pick_files(allowed_extensions=["wav", "mp3"], allow_multiple=False)

    return Column(
        controls=[
            ElevatedButton(
                text="Upload Audio",
                icon=flet.icons.MIC,
                on_click=record_audio
            ),
            ProgressRing(visible=state["is_processing"])
        ],
        alignment="center",
        horizontal_alignment="center",
    )

# Text Input
def TextInputComponent(state, page):
    user_text = flet.Ref[TextField]()

    def submit_text(e):
        message = user_text.current.value.strip()
        if not message:
            show_popup(state, "Error", "Message cannot be empty.")
            page.update()
            return

        state["history"].append({
            "type": "USER",
            "recipient": "Assistant",
            "content": message
        })
        page.update()

        state["is_processing"] = True
        page.update()

        try:
            response = send_text_message(state["session_id"], message)
            assistant_response = response.get('assistant_response', '')
            summary = response.get('summary', '')

            message_type, msg = parse_assistant_response(assistant_response)

            state["history"].append({
                "type": message_type,
                "recipient": "Assistant",
                "content": msg
            })

            state["translated_text"] = msg

            if message_type == 'CAUTION':
                show_caution(state, msg)
            elif message_type == 'SUMMARY':
                show_summary(state, msg)

        except Exception as ex:
            show_popup(state, "Error", f"Failed to send message: {ex}")
        finally:
            state["is_processing"] = False
            user_text.current.value = ""
            page.update()

    return Column(
        controls=[
            TextField(
                label="Enter your message",
                ref=user_text,
                multiline=True,
                rows=3,
                hint_text="Type your message here..."
            ),
            ElevatedButton(
                text="Submit",
                on_click=submit_text,
                disabled=state["is_processing"]
            ),
            ProgressRing(visible=state["is_processing"])
        ],
        spacing=10,
    )

# Translation View
def TranslationView(state, page, navigate):
    return Column(
        controls=[
            NavigationBar(navigate),
            Row(
                controls=[
                    # Left Column: Audio Recorder and Text Input
                    Column(
                        controls=[
                            Text("Record Your Audio", style="headlineMedium"),
                            AudioRecorderComponent(state, page),
                            Divider(),
                            Text("Or Enter Text", style="headlineMedium"),
                            TextInputComponent(state, page),
                        ],
                        spacing=20,
                        width=350
                    ),
                    # Right Column: Conversation History
                    Column(
                        controls=[
                            ConversationHistoryView(state)
                        ],
                        expand=True
                    )
                ],
                spacing=20
            ),
            # Text-to-Speech Execution
            TextToSpeechComponent(state, page),
            # Popup Dialogs
            PopupDialogComponent(state, lambda e: close_popup(state, e)),
            SummaryDialog(state, lambda e: close_summary(state, e)),
            CautionDialog(state, lambda e: close_caution(state, e)),
        ],
        expand=True,
        alignment="start",
        spacing=20,
    )

# History View
def HistoryView(state, navigate):
    return Column(
        controls=[
            NavigationBar(navigate),
            Text("Translation History", style="headlineMedium"),
            ListView(
                expand=True,
                spacing=5,
                padding=10,
                auto_scroll=True,
                controls=[
                    ListTile(
                        title=Text(item['recipient'], weight="bold", color=get_color(item['type'])),
                        subtitle=Text(item['content'])
                    ),
                    Divider()
                ] for item in state["history"]
            )
        ],
        expand=True,
        scroll="auto",
    )

# Home View
def HomeView(state, page, navigate):
    return Column(
        controls=[
            NavigationBar(navigate),
            Text("Welcome to the Translation App", style="headlineLarge"),
            Text("Seamlessly translate text and speech between multiple languages using our AI-powered tool.", style="bodyMedium"),
            ObjectiveForm(state, page, navigate)
        ],
        alignment="center",
        spacing=20,
        horizontal_alignment="center",
    )

# -------------------- Initialize Views -------------------- #

def initialize_views(state, page, navigate):
    home_view = View(
        "/",
        controls=[
            HomeView(state, page, navigate)
        ]
    )

    translate_view = View(
        "/translate",
        controls=[
            TranslationView(state, page, navigate)
        ]
    )

    history_view = View(
        "/history",
        controls=[
            HistoryView(state, navigate)
        ]
    )

    return home_view, translate_view, history_view

# -------------------- Main Function -------------------- #

def main(page: Page):
    page.title = "Translation App"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "start"
    page.window_width = 1000
    page.window_height = 700

    # Global State Variables
    state = {
        "session_id": None,
        "history": [],
        "translated_text": "",
        "target_language": "English",
        "user_language": "English",
        "country": "United States",
        "is_processing": False,
        "popup_open": False,
        "popup_title": "",
        "popup_message": "",
        "summary_open": False,
        "summary_message": "",
        "caution_open": False,
        "caution_message": "",
    }

    # Initialize Views
    home_view, translate_view, history_view = initialize_views(state, page, lambda route: navigate(route, page, state))

    # Register Views
    page.views.append(home_view)

    # Handle Routing
    def route_change(e):
        navigate(e.route, page, state)

    def view_pop(e):
        navigate(page.route, page, state)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Popup Dialogs
    def PopupDialogComponent(state, close_popup_func):
        if state["popup_open"]:
            dialog = AlertDialog(
                title=Text(state["popup_title"]),
                content=Text(state["popup_message"]),
                actions=[
                    ElevatedButton("Close", on_click=close_popup_func)
                ],
                on_dismiss=close_popup_func
            )
            page.dialog = dialog
            dialog.open = True
            page.update()

    # Summary Dialog
    def SummaryDialog(state, close_summary_func):
        if state["summary_open"]:
            dialog = AlertDialog(
                title=Text("Conversation Summary"),
                content=Text(state["summary_message"]),
                actions=[
                    ElevatedButton("Close", on_click=close_summary_func)
                ],
                on_dismiss=close_summary_func
            )
            page.dialog = dialog
            dialog.open = True
            page.update()

    # Caution Dialog
    def CautionDialog(state, close_caution_func):
        if state["caution_open"]:
            dialog = AlertDialog(
                title=Text("Caution"),
                content=Text(state["caution_message"]),
                actions=[
                    ElevatedButton("Close", on_click=close_caution_func)
                ],
                on_dismiss=close_caution_func
            )
            page.dialog = dialog
            dialog.open = True
            page.update()

    # Text-to-Speech
    def TextToSpeechComponent(state, page):
        if state["translated_text"]:
            # Escape quotes and newlines to prevent JS errors
            safe_text = state["translated_text"].replace('"', '\\"').replace('\n', '\\n')
            lang_code = language_code_map.get(state["target_language"], 'en-US')
            js = f"""
                var msg = new SpeechSynthesisUtterance("{safe_text}");
                msg.lang = "{lang_code}";
                window.speechSynthesis.speak(msg);
            """
            page.client.execute_js(js)

    # Navigation Function
    def navigate(route, page, state):
        if route == 'reset_session':
            reset_session(state, page)
            return
        if route == '/':
            page.views.clear()
            page.views.append(home_view)
        elif route == '/translate':
            if not state["session_id"]:
                show_popup(state, "Error", "Please set your objective first.")
                PopupDialogComponent(state, lambda e: close_popup(state, e))
                return
            page.views.clear()
            page.views.append(translate_view)
        elif route == '/history':
            if not state["session_id"]:
                show_popup(state, "Error", "Please set your objective first.")
                PopupDialogComponent(state, lambda e: close_popup(state, e))
                return
            page.views.clear()
            page.views.append(history_view)
        page.update()

    # Reset Session Function
    def reset_session(state, page):
        state["session_id"] = None
        state["history"] = []
        state["translated_text"] = ""
        state["target_language"] = "English"
        state["user_language"] = "English"
        state["country"] = "United States"
        page.views.clear()
        page.views.append(home_view)
        page.update()

    # Attach Dialog Components
    def attach_dialogs(state, page):
        PopupDialogComponent(state, lambda e: close_popup(state, e))
        SummaryDialog(state, lambda e: close_summary(state, e))
        CautionDialog(state, lambda e: close_caution(state, e))

    # Initialize Dialogs
    attach_dialogs(state, page)

# -------------------- Run the App -------------------- #

if __name__ == "__main__":
    flet.app(target=main)
