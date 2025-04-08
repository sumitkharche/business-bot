from flask import Flask, request, jsonify
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

app = Flask(__name__)

# Load Chroma DB and setup embedding
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
chroma_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# Initialize Ollama and RetrievalQA Chain
llm = Ollama(model="llama2")
qa_chain = RetrievalQA.from_chain_type(llm, retriever=chroma_db.as_retriever())

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json['message']
        result = qa_chain({"query": user_message})
        return jsonify({'response': result['result']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)