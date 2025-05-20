import time
import logging
from functools import lru_cache
from typing import Optional

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from sqlalchemy.exc import SQLAlchemyError

from db import ChatHistory, get_db
from config import HF_MODEL_NAME, MAX_NEW_TOKENS, TEMPERATURE

# Set up logging
logger = logging.getLogger(__name__)

class Chatbot:
    def __init__(self, model_name=HF_MODEL_NAME):
        """Initialize the chatbot with a specified model."""
        try:
            # Initialize the LLM
            self.llm = HuggingFaceHub(
                repo_id=model_name,
                task="text-generation",
                model_kwargs={
                    "max_new_tokens": MAX_NEW_TOKENS,
                    "do_sample": True,
                    "temperature": TEMPERATURE,
                    "repetition_penalty": 1.03
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

    def get_response(self, user_input: str, user_id: Optional[int] = None) -> str:
        """Get a response from the chatbot."""
        start_time = time.time()
        
        try:
            # Get response from the model
            response = self.conversation.predict(input=user_input)
            
            # Save the conversation to the database if user_id is provided
            if user_id:
                self.save_conversation(user_id, user_input, response)
                
            logger.info(f"Response generated in {time.time() - start_time:.2f}s")
            return response
            
        except Exception as e:
            error_msg = "Sorry, I'm having trouble generating a response. Please try again."
            logger.error(f"Error generating response: {str(e)}")
            return error_msg

    def save_conversation(self, user_id: int, user_message: str, bot_response: str) -> bool:
        """Save the conversation to the database."""
        try:
            with get_db() as db:
                # Calculate response time in milliseconds
                response_time = int(time.time() * 1000)
                
                chat_history = ChatHistory(
                    user_id=user_id,
                    user_message=user_message,
                    bot_response=bot_response,
                    response_time=response_time
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
    
    def load_conversation_history(self, user_id: int) -> bool:
        """Load conversation history for a specific user."""
        try:
            with get_db() as db:
                history = db.query(ChatHistory).filter(
                    ChatHistory.user_id == user_id
                ).order_by(ChatHistory.timestamp).all()
            
            # Reset the current memory
            self.memory.clear()
            
            # Add history to memory
            for chat in history:
                self.memory.save_context({"input": chat.user_message}, {"output": chat.bot_response})
            
            logger.info(f"Loaded {len(history)} conversation records for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error loading conversation history: {str(e)}")
            return False

# Create a cached chatbot instance for better performance
@lru_cache(maxsize=1)
def get_chatbot():
    """Get a cached chatbot instance."""
    return Chatbot()
