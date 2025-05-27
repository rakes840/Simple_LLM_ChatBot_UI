File "c:\Rakesh\Working_GenAI_Project_POC\Simple_ChatGPT_UI\.venv\Lib\site-packages\passlib\handlers\bcrypt.py", line 620, in _load_backend_mixin
    version = _bcrypt.__about__.__version__
              ^^^^^^^^^^^^^^^^^
(trapped) error reading bcrypt version
Traceback (most recent call last):
  File "c:\Rakesh\Working_GenAI_Project_POC\Simple_ChatGPT_UI\.venv\Lib\site-packages\passlib\handlers\bcrypt.py", line 620, in _load_backend_mixin
    version = _bcrypt.__about__.__version__
              ^^^^^^^^^^^^^^^^^
Traceback (most recent call last):
  File "c:\Rakesh\Working_GenAI_Project_POC\Simple_ChatGPT_UI\.venv\Lib\site-packages\passlib\handlers\bcrypt.py", line 620, in _load_backend_mixin
    version = _bcrypt.__about__.__version__
              ^^^^^^^^^^^^^^^^^
", line 620, in _load_backend_mixin
    version = _bcrypt.__about__.__version__
              ^^^^^^^^^^^^^^^^^
    version = _bcrypt.__about__.__version__
              ^^^^^^^^^^^^^^^^^
              ^^^^^^^^^^^^^^^^^
AttributeError: module 'bcrypt' has no attribute '__about__'
C:\Rakesh\Working_GenAI_Project_POC\Simple_ChatGPT_UI\V5_Chat_LLM_UI_Functionality\chatbot.py:60: LangChainDeprecationWarning: Please see the migration guide at: https://python.langchain.com/docs/versions/migrating_memory/  
  self.user_session_memories[key] = ConversationBufferMemory(return_messages=True)
C:\Rakesh\Working_GenAI_Project_POC\Simple_ChatGPT_UI\V5_Chat_LLM_UI_Functionality\chatbot.py:72: LangChainDeprecationWarning: The class `ConversationChain` was deprecated in LangChain 0.2.7 and will be removed in 1.0. Use :meth:`~RunnableWithMessageHistory: https://python.langchain.com/v0.2/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html` instead.
  conversation = ConversationChain(
Error generating response: (ReadTimeoutError("HTTPSConnectionPool(host='router.huggingface.co', port=443): Read timed out. (read timeout=120)"), '(Request ID: b9fedcdb-f38e-4469-a444-3a85be46807c)')
