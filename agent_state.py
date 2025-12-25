import os
import sqlite3
import faiss
import pickle
from sentence_transformers import SentenceTransformer

class AgentState:
    def __init__(self, db_path="memory/sqlite.db", faiss_path="memory/faiss_index"):
        # --- Create memory directories ---
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(faiss_path, exist_ok=True)

        # --- SQLite structured memory ---
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

        # --- FAISS semantic memory ---
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.embedding_dim = 384
        self.faiss_path = faiss_path
        self.metadata_file = os.path.join(faiss_path, "metadata.pkl")
        self._load_faiss_index()

    # -----------------------------
    # SQLite tables
    # -----------------------------
    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                date TEXT PRIMARY KEY,
                level TEXT,
                test_score INTEGER
            )
        """)
        self.conn.commit()

    def save_progress(self, date, level, test_score):
        self.cursor.execute(
            "INSERT OR REPLACE INTO user_progress VALUES (?,?,?)",
            (date, level, test_score)
        )
        self.conn.commit()

    # -----------------------------
    # FAISS memory
    # -----------------------------
    def _load_faiss_index(self):
        index_file = os.path.join(self.faiss_path, "index.faiss")
        if os.path.exists(index_file):
            self.index = faiss.read_index(index_file)
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, "rb") as f:
                    self.metadata = pickle.load(f)
            else:
                self.metadata = []
        else:
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.metadata = []

    def add_to_faiss(self, text, category=None, mistake=None):
        vec = self.embedding_model.encode([text]).astype("float32")
        self.index.add(vec)
        self.metadata.append({"text": text, "category": category, "mistake": mistake})
        self._save_faiss()

    def _save_faiss(self):
        faiss.write_index(self.index, os.path.join(self.faiss_path, "index.faiss"))
        with open(self.metadata_file, "wb") as f:
            pickle.dump(self.metadata, f)

    def query_faiss(self, query_text, top_k=5):
        vec = self.embedding_model.encode([query_text]).astype("float32")
        D, I = self.index.search(vec, top_k)
        results = []
        for idx in I[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])
        return results
