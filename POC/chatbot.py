import time
import logging
from functools import lru_cache
from typing import Optional, Dict
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from sqlalchemy.exc import SQLAlchemyError
import os
from db import ChatHistory, get_db
from config import HF_MODEL_NAME, TEMPERATURE
from dotenv import load_dotenv

load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv('HF_TOKEN_new')

logger = logging.getLogger(__name__)

class Chatbot:
    def __init__(self, model_name=HF_MODEL_NAME):
        try:
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
            template = """The following is a friendly conversation between a human and an AI assistant.
Current conversation:
{history}
Human: {input}
AI:"""
            self.prompt = PromptTemplate(
                input_variables=["history", "input"],
                template=template
            )
            self.user_session_memories: Dict[str, ConversationBufferMemory] = {}
            logger.info(f"Chatbot initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize chatbot: {str(e)}")
            raise

    def _memory_key(self, user_id: str, session_id: Optional[str]) -> str:
        return f"{user_id}:{session_id}" if session_id else str(user_id)

    def get_memory(self, user_id: str, session_id: Optional[str]) -> ConversationBufferMemory:
        key = self._memory_key(user_id, session_id)
        if key not in self.user_session_memories:
            self.user_session_memories[key] = ConversationBufferMemory(return_messages=True)
        return self.user_session_memories[key]

    def reset_memory(self, user_id: str, session_id: Optional[str] = None):
        key = self._memory_key(user_id, session_id)
        self.user_session_memories[key] = ConversationBufferMemory(return_messages=True)
        logger.info(f"Memory reset for user {user_id}, session {session_id}")

    def get_response(self, user_input: str, user_id: str, session_id: Optional[str] = None) -> str:
        start_time = time.time()
        try:
            memory = self.get_memory(user_id, session_id)
            conversation = ConversationChain(
                llm=self.chat_model,
                prompt=self.prompt,
                memory=memory,
                verbose=False
            )
            response = conversation.predict(input=user_input)
            logger.info(f"Response generated in {time.time() - start_time:.2f}s")
            return response
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "Sorry, I'm having trouble generating a response. Please try again."

    def save_conversation(self, user_id: int, user_message: str, bot_response: str, session_id: Optional[int] = None) -> bool:
        try:
            with get_db() as db:
                chat_history = ChatHistory(
                    user_id=user_id,
                    session_id=session_id,
                    user_message=user_message,
                    bot_response=bot_response,
                    timestamp=time.time()
                )
                db.add(chat_history)
                db.commit()
                logger.info(f"Conversation saved for user {user_id} in session {session_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Database error saving conversation: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving conversation: {str(e)}")
            return False

    def load_conversation_history(self, user_id: int, session_id: Optional[int] = None) -> bool:
        try:
            with get_db() as db:
                query = db.query(ChatHistory).filter(ChatHistory.user_id == user_id)
                if session_id:
                    query = query.filter(ChatHistory.session_id == session_id)
                history = query.order_by(ChatHistory.timestamp).all()
                memory = self.get_memory(user_id, session_id)
                memory.clear()
                for chat in history:
                    memory.save_context({"input": chat.user_message}, {"output": chat.bot_response})
                logger.info(f"Loaded {len(history)} conversation records for user {user_id}, session {session_id}")
                return True
        except Exception as e:
            logger.error(f"Error loading conversation history: {str(e)}")
            return False

@lru_cache(maxsize=1)
def get_chatbot():
    return Chatbot()
