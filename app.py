import streamlit as st
from rag_setup import qa_chain

st.title("🔧 HVAC Business Assistant (RAG + Hugging Face + SQLite)")
query = st.text_input("Ask me about work orders, technicians, customers, quotes...")

if query:
    answer = qa_chain.run(query)
    st.write("🤖", answer)