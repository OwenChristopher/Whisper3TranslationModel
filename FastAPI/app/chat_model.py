# app/chat_model.py
import openai  # Updated import for OpenAI
from openai import OpenAI
import json  # For JSON transformation
import os

class LLMChat:
    def __init__(
        self, 
        api_key=os.getenv("WEIRD_CHINESE_KEY"),  # OpenAI API key
        base_url="https://api.gpts.vin/v1",  # OpenAI API base URL
        model_name='gpt-4o-mini',  # Updated model name
        user_language='English',
        target_language='Chinese',
        country='China',  # Added country parameter for cultural context
        initial_message="""
        1. I'm in China right now, and I need help with talking to a taxi driver. 
        2. I need to go to Hongqiao station. 
        3. Besides that, I'm in a big hurry, so make sure that the driver takes the fastest route. 
        4. Also, I'm going to Hebei province, can you ask the driver for any recommendation for visiting there
        """,
        temperature=0,
    ):
        """
        Initializes the LLMChat with OpenAI's API and communication parameters.
        """
        self.model_name = model_name
        self.user_language = user_language
        self.target_language = target_language
        self.country = country
        self.initial_message = initial_message
        self.temperature = temperature

        # Concise system message
        self.system_content = (
            f"""You are a multilingual assistant that communicates with a target based on the user's requirements. Your main goal is to minimize the amount of communication between you and the user.

1. **Prefixes and Languages:**
   - When addressing the target, use `[TARGET]` and communicate in {self.target_language}.
   - When addressing the user, use `[USER]` and communicate in {self.user_language}.

2. **Behavior:**
   - Act like a user but speak in the target's language, which is {self.target_language}.
   - Ensure to communicate requirements to the user or ask the target questions one by one.

3. **Response Rules:**
   - Always respond in the native language of the person you are addressing:
     - `[USER]`: {self.user_language}
     - `[TARGET]`: {self.target_language}
   - Format all your replies to start with `[USER]`, `[TARGET]`, `[CAUTION]`, or `[SUMMARY]` followed by a space and then the message.
   - Do not include any additional text, descriptions, markdown notation, or prompts.
   - Use only the actual message content suitable for Text-to-Speech without any annotations or explanations.
   - Ensure each reply contains only one prefix and one message, so reply must be in the format of - [PERSON] Content - and nothing else.
 For example, this behavior is incorrect because it has two messages at the same time:
  [TARGET] 请带我去虹桥火车站，走最快的路线。另外，你能推荐一下河北省哪里好玩？ 
  [USER] I've communicated your request to the taxi driver. Do you have any further questions?
 The correct way will be only saying the first part intended for target, and wait for his reply before talking back to user:
  [TARGET] 请带我去虹桥火车站，走最快的路线。另外，你能推荐一下河北省哪里好玩？ 
 Another example of incorrect behavior is the case where you receive a reply from target, but talking to user back to take the toll road:
 Target Message: 是的，当然！你想走收费公路还是免费公路？收费公路将为您节省约 1.5 小时的时间
 Assistant reply: [USER] Please take the toll road to save time.
 Intended behavior is to reply back to target that we will take the toll road, because user is in hurry:
 Target Message: 是的，当然！你想走收费公路还是免费公路？收费公路将为您节省约 1.5 小时的时间
 Assistant reply: [TARGET] 请走收费公路，以节省时间。

4. **Handling Sensitive Topics and Tips:**
   - **General Sensitive Topics:**
     - If the user asks about sensitive topics that can be regarded as inappropriate or offensive in {self.country}, raise a caution prefixed with `[CAUTION]` and provide recommendations.
   - **Handling Gratitude and Tips:**
     - If the user wants to thank the driver or give a tip, evaluate its appropriateness in {self.country}.
     - If giving a tip is inappropriate or offensive:
       - Respond with `[CAUTION]` in {self.user_language}.
       - Inform the user that giving a tip may not be appropriate in {self.country}.
       - Suggest alternative ways to express gratitude, such as saying "Thank you for your cooperation."
     - If giving a tip is appropriate:
       - Proceed to convey the message prefixed with `[TARGET]` in {self.target_language}.

5. **Requesting Additional Information:**
   - If the target asks for additional information that you don't know, ask the user about it, starting with `[USER]`.

6. **Conversation Completion:**
   - When the conversation goal is achieved, notify the user with a concise summary prefixed with `[SUMMARY]`, and finish by asking whether the user has more questions.

"""
        )

        # Initialize conversation history with the system message and initial user message
        self.history = [
            {"type": "system", "recipient": "assistant", "content": self.system_content},
            {"type": "user", "recipient": "assistant", "content": self.initial_message}
        ]

        # Initialize OpenAI client
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

        print(f"Initialized OpenAI model '{self.model_name}' with base URL '{base_url}'.")

    def prepare_history_for_api(self):
        """
        Transforms the internal history format to the format expected by OpenAI's Chat Completion API.

        :return: List of messages with 'role' and 'content' keys.
        """
        api_history = []
        for msg in self.history:
            if msg['type'].lower() == 'system':
                api_message = {
                    "role": "system",
                    "content": msg['content']
                }
            elif msg['type'].lower() == 'user':
                api_message = {
                    "role": "user",
                    "content": msg['content']
                }
            elif msg['type'].lower() in ['assistant', 'summary', 'caution']:
                # All assistant-related types map to 'assistant' role
                api_message = {
                    "role": "assistant",
                    "content": f"[{msg['recipient'].upper()}] " + msg['content']
                }
            else:
                # Default to 'assistant' role for any other types to prevent errors
                api_message = {
                    "role": "assistant",
                    "content": "[SYSTEM ERROR] " + msg['content']
                }
            api_history.append(api_message)
        return api_history

    def call_model(self):
        """
        Invokes the OpenAI model with the current conversation history and processes the assistant's response.
        """
        try:
            # Prepare history in the format expected by OpenAI's API
            api_messages = self.prepare_history_for_api()
            print(f'API history: {api_messages}')

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=api_messages,
                temperature=self.temperature
            )

            assistant_reply = response.choices[0].message.content.strip()
            print(f'Assistant reply: {assistant_reply}')

            message_type, recipient, message = self.extract_message_components(assistant_reply)
            print(f'Message Type: {message_type}, Recipient: {recipient}, Message: {message}')

            if message_type and recipient and message:
                if message_type in ['CAUTION', 'SUMMARY']:
                    self.history.append({
                        "type": message_type,
                        "recipient": "user",
                        "content": message
                    })
                else:
                    self.history.append({
                        "type": "assistant",
                        "recipient": recipient,
                        "content": message
                    })
                # Note: In API mode, we do not wait for user input; instead, the front end handles it.
            else:
                # Invalid format; respond with system error
                caution_message = "System error: Invalid response format."
                print(f"Assistant Message: [CAUTION] {caution_message}")
                self.history.append({
                    "type": "assistant",
                    "recipient": "User",
                    "content": caution_message
                })
        except Exception as e:
            print(f"Error during model invocation: {e}")
            # Append a caution message indicating a system error
            caution_message = "System error occurred during processing."
            self.history.append({
                "type": "assistant",
                "recipient": "User",
                "content": caution_message
            })

    def extract_message_components(self, assistant_reply):
        """
        Extracts the message type, recipient, and content from the assistant's reply.

        :param assistant_reply: The full reply from the assistant.
        :return: Tuple containing the message type ('USER', 'TARGET', 'CAUTION', 'SUMMARY'), recipient ('User', 'Target'), and the message.
        """
        prefixes = ["[USER] ", "[TARGET] ", "[CAUTION] ", "[SUMMARY] "]
        for prefix in prefixes:
            if assistant_reply.startswith(prefix):
                message_type = prefix.strip("[] ").upper()
                if message_type == "TARGET":
                    recipient = "Target"
                elif message_type in ["SUMMARY", "CAUTION"]:
                    recipient = "User"
                else:
                    recipient = "User"  # Default to User for any other types
                message = assistant_reply[len(prefix):].strip()
                return message_type, recipient, message
        # If no valid prefix found
        print('Invalid format of assistant reply.')
        return None, None, None

    def send_message(self, user_message):
        """
        Accepts a user message, appends it to history, calls the model, and returns the assistant's response.

        :param user_message: The message sent by the user.
        :return: The assistant's reply.
        """
        if user_message.lower() == 'q':
            return "Chat session has been terminated."

        print(f'User Message: {user_message}')
        self.history.append({
            "type": "user",
            "recipient": "assistant",
            "content": user_message
        })
        self.call_model()

        # Get the latest assistant message
        for msg in reversed(self.history):
            if msg['type'] == 'assistant' or msg['type'] in ['SUMMARY', 'CAUTION']:
                return msg['content']
        return "No response from assistant."

    def get_history_json(self):
        """
        Returns the conversation history in JSON format.

        :return: JSON string of the conversation history.
        """
        return json.dumps(self.history, ensure_ascii=False, indent=2)
