import asyncio
import concurrent.futures
import os
import time
from functools import lru_cache
from typing import List, Dict, Any, Optional

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from sqlalchemy.exc import SQLAlchemyError

from database import ChatHistory, get_db_session
from config import HF_MODEL_NAME, MAX_NEW_TOKENS, TEMPERATURE
from logger import get_logger

# Get logger
logger = get_logger()

# Initialize executor for threaded operations
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# Initialize HuggingFace API token from environment variable
HUGGINGFACEHUB_API_TOKEN = os.environ.get("HUGGINGFACEHUB_API_TOKEN", "")

# LLM response timeout in seconds
LLM_TIMEOUT = 30

class Chatbot:
    def __init__(self, model_name=HF_MODEL_NAME):
        """Initialize the chatbot with a specified model."""
        try:
            self.llm = HuggingFaceHub(
                repo_id=model_name,
                huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
                model_kwargs={
                    "temperature": TEMPERATURE,
                    "max_new_tokens": MAX_NEW_TOKENS,
                    "repetition_penalty": 1.2,  # Prevent repetitive responses
                }
            )
            
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
                llm=self.llm,
                prompt=self.prompt,
                memory=self.memory,
                verbose=False
            )
            logger.info(f"Chatbot initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize chatbot: {str(e)}")
            raise

    async def get_response_async(self, user_input: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get a response from the chatbot asynchronously."""
        start_time = time.time()
        result = {"success": False, "response": "", "error": None}
        
        try:
            # Run the model prediction in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                executor, 
                self._get_llm_response_with_timeout, 
                user_input
            )
            
            result["success"] = True
            result["response"] = response
            
            # Save the conversation to the database if user_id is provided
            if user_id:
                await loop.run_in_executor(
                    executor,
                    self.save_conversation,
                    user_id, user_input, response
                )
                
            logger.info(f"Response generated in {time.time() - start_time:.2f}s")
            return result
            
        except concurrent.futures.TimeoutError:
            error_msg = "The model took too long to respond. Please try again."
            logger.error(f"LLM response timeout for user {user_id}")
            result["error"] = error_msg
            return result
            
        except Exception as e:
            error_msg = "Sorry, I'm having trouble generating a response. Please try again."
            logger.error(f"Error generating response: {str(e)}")
            result["error"] = error_msg
            return result

    def _get_llm_response_with_timeout(self, user_input: str) -> str:
        """Get LLM response with timeout protection."""
        try:
            # Using a default timeout to avoid hanging
            response = self.conversation.predict(input=user_input)
            return response
        except Exception as e:
            logger.error(f"Error in LLM response generation: {str(e)}")
            raise

    def save_conversation(self, user_id: int, user_message: str, bot_response: str) -> bool:
        """Save the conversation to the database."""
        try:
            with get_db_session() as db:
                chat_history = ChatHistory(
                    user_id=user_id,
                    user_message=user_message,
                    bot_response=bot_response
                )
                db.add(chat_history)
                db.commit()
                logger.info(f"Conversation saved for user {user_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Database error saving conversation: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving conversation: {str(e)}")
            return False
    
    async def load_conversation_history(self, user_id: int) -> List[ChatHistory]:
        """Load conversation history for a specific user asynchronously."""
        try:
            loop = asyncio.get_event_loop()
            history = await loop.run_in_executor(
                executor,
                self._load_history_from_db,
                user_id
            )
            
            # Reset the current memory
            self.memory.clear()
            
            # Add history to memory
            for chat in history:
                self.memory.save_context({"input": chat.user_message}, {"output": chat.bot_response})
            
            logger.info(f"Loaded {len(history)} conversation records for user {user_id}")
            return history
        except Exception as e:
            logger.error(f"Error loading conversation history: {str(e)}")
            return []

    def _load_history_from_db(self, user_id: int) -> List[ChatHistory]:
        """Load history from database (runs in thread executor)."""
        try:
            with get_db_session() as db:
                return db.query(ChatHistory).filter(
                    ChatHistory.user_id == user_id
                ).order_by(ChatHistory.timestamp).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error loading history: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading history: {str(e)}")
            raise

# Create a cached chatbot instance for better performance
@lru_cache(maxsize=1)
def get_chatbot():
    """Get a cached chatbot instance."""
    return Chatbot()
