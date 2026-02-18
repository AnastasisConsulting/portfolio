import os
import urllib.request
import numpy as np
from sentence_transformers import SentenceTransformer

# --- Model Details ---
MODEL_URL = "https://coral.ai/static/models/edgetpu/all-MiniLM-L6-v2_quant_edgetpu.tflite"
MODEL_FILE = "all-MiniLM-L6-v2_quant_edgetpu.tflite"

def download_model():
    """Downloads the TFLite model file if it doesn't exist."""
    if not os.path.exists(MODEL_FILE):
        print(f"Downloading model: {MODEL_FILE}...")
        try:
            urllib.request.urlretrieve(MODEL_URL, MODEL_FILE)
            print("Download complete.")
        except Exception as e:
            print(f"Error downloading model: {e}")
            exit()
    else:
        print(f"Model '{MODEL_FILE}' already exists.")

def get_embedding(sentence: str, tokenizer, interpreter) -> np.ndarray:
    """
    Tokenizes a sentence and runs it through the TFLite interpreter
    to get the embedding vector.
    """
    # Tokenize the sentence
    inputs = tokenizer.encode(sentence, return_tensors='np')
    input_ids = inputs.astype(np.int32)

    # Set the input tensor
    interpreter.set_tensor(interpreter.get_input_details()[0]['index'], input_ids)
    
    # Run inference
    interpreter.invoke()
    
    # Get the output tensor (the sentence embedding)
    embedding = interpreter.get_tensor(interpreter.get_output_details()[0]['index'])[0]
    
    return embedding

def main():
    """Main function to download, load, and run the sentence encoder."""
    # Ensure the model file is available
    download_model()

    print("\nLoading tokenizer and interpreter...")
    try:
        # 1. Load the tokenizer from the sentence-transformers library
        #    This specific tokenizer is required for this model.
        tokenizer = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2').tokenizer

        # 2. Load the TFLite model and delegate to the Edge TPU
        
        print("Model loaded successfully on Edge TPU.")
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # --- Run an example ---
    test_sentence = "This is a test of the sentence encoder."
    
    print(f"\nGenerating embedding for: '{test_sentence}'")
    
    # Get the embedding vector for the sentence
    
    # Normalize the vector for similarity calculations


if __name__ == '__main__':
    main()