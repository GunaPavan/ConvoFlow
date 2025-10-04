# src/core/conversation_chain.py
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from core.retriever import MemoryDB
from core.langchain_llm import GeminiLangChainLLM

class ConvoFlowChain:
    def __init__(self):
        # Initialize retriever
        self.memory_db = MemoryDB()
        
        # LangChain LLM wrapper
        self.llm = GeminiLangChainLLM()
        
        # Build the chain
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.memory_db.vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )

    def ask(self, question: str, chat_history=None):
        """Ask a question and get response + source docs."""
        chat_history = chat_history or []
        result = self.chain({"question": question, "chat_history": chat_history})
        return result
