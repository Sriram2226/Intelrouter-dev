from sentence_transformers import SentenceTransformer
import logging
import sys

logging.basicConfig(level=logging.DEBUG)
print("Starting SentenceTransformer download test...")
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Success! Model loaded.")
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
