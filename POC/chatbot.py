import logging
from typing import Optional, Dict
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
import os
from config import HF_MODEL_NAME, TEMPERATURE
from dotenv import load_dotenv

load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv('HF_TOKEN')

logger = logging.getLogger(__name__)

class Chatbot:
    def __init__(self, model_name=HF_MODEL_NAME):
        self.model_name = model_name
        self.llm = HuggingFaceEndpoint(
            repo_id=model_name,
            task="text-generation",
            max_new_tokens=700,
            do_sample=False,
            repetition_penalty=1.03,
            temperature=TEMPERATURE,
            typical_p=0.95
        )
        self.chat_model = ChatHuggingFace(llm=self.llm)
        self.prompt = PromptTemplate(
            input_variables=["history", "input"],
            template="""The following is a friendly conversation between a human and an AI assistant.
Current conversation:
{history}
Human: {input}
AI:"""
        )
        # Dict to hold memory per user_id/session_id
        self.user_memories: Dict[str, ConversationBufferMemory] = {}

    def get_memory(self, user_id: str, session_id: Optional[str] = None):
        key = f"{user_id}:{session_id}" if session_id else str(user_id)
        if key not in self.user_memories:
            self.user_memories[key] = ConversationBufferMemory(return_messages=True)
        return self.user_memories[key]

    def reset_memory(self, user_id: str, session_id: Optional[str] = None):
        key = f"{user_id}:{session_id}" if session_id else str(user_id)
        self.user_memories[key] = ConversationBufferMemory(return_messages=True)

    def get_response(self, user_input: str, user_id: str, session_id: Optional[str] = None) -> str:
        try:
            memory = self.get_memory(user_id, session_id)
            conversation = ConversationChain(
                llm=self.llm,
                prompt=self.prompt,
                memory=memory,
                verbose=False
            )
            response = conversation.predict(input=user_input)
            return response
        except Exception as e:
            logger.error(f"Error generating chatbot response: {str(e)}")
            return "Sorry, I couldn't process your request at this time."

def get_chatbot():
    # Singleton pattern if you want to share across app
    if not hasattr(get_chatbot, "_instance"):
        get_chatbot._instance = Chatbot()
    return get_chatbot._instance
