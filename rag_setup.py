import os
from extract_data import get_all_chunks
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFaceHub

# Hugging Face token
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "" 

# Get chunks from DB #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
chunks = get_all_chunks()

# Use HF Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Build vector DB
vectorstore = Chroma.from_texts(chunks, embeddings, persist_directory="db")
vectorstore.persist()

# Load HF LLM
llm = HuggingFaceHub(repo_id="mistralai/Mistral-7B-Instruct-v0.1", model_kwargs={"temperature": 0.3, "max_length": 512})

# Create RAG chain
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())