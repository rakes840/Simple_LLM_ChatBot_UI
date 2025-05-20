from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
import os
from db import ChatHistory, get_db
from config import HF_MODEL_NAME, MAX_NEW_TOKENS, TEMPERATURE
from dotenv import load_dotenv
load_dotenv()
#from langchain_huggingface import HuggingFaceEndpoint
#from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
# Initialize HuggingFace API token from environment variable

# You'll need to set this in your environment: export HUGGINGFACEHUB_API_TOKEN=your_token

HUGGINGFACEHUB_API_TOKEN = os.environ.get("HF_TOKEN", "")

class Chatbot:
    def __init__(self, model_name=HF_MODEL_NAME):
        """Initialize the chatbot with a specified model."""
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.3",
            task="text-generation",
            max_new_tokens=700,
            do_sample=False,
            repetition_penalty=1.03,
            temperature = TEMPERATURE,
            typical_p = 0.95
        )
        
        self.chat_model = ChatHuggingFace(llm=self.llm)       
        
        # Set up the conversation template
        template = """The following is a friendly conversation between a human and an AI assistant.

Current conversation:

{history}

Human: {input}

AI: """
        self.prompt = PromptTemplate(
            input_variables=["history", "input"], 
            template=template
        )

        self.memory = ConversationBufferMemory(return_messages=True)
        self.conversation = ConversationChain(
            llm=self.chat_model,
            prompt=self.prompt,
            memory=self.memory,
            verbose=False
        )

    def get_response(self, user_input, user_id=None):
        """Get a response from the chatbot for the given user input."""
        response = self.conversation.predict(input=user_input)
        # Save the conversation to the database if user_id is provided
        if user_id:
            self.save_conversation(user_id, user_input, response)
        return response

    def save_conversation(self, user_id, user_message, bot_response):
        """Save the conversation to the database."""
        db = get_db()
        chat_history = ChatHistory(
            user_id=user_id,
            user_message=user_message,
            bot_response=bot_response
        )

        db.add(chat_history)
        db.commit()

    def load_conversation_history(self, user_id):
        """Load conversation history for a specific user."""
        db = get_db()
        history = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).order_by(ChatHistory.timestamp).all()
        # Reset the current memory
        self.memory.clear()
        # Add history to memory
        for chat in history:
            self.memory.save_context({"input": chat.user_message}, {"output": chat.bot_response})
        return history

# Create a chatbot instance

def get_chatbot():
    return Chatbot()
 





