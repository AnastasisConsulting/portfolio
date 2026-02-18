# main_app/engine/coral_bootstrapper.py

import numpy as np
from typing import List

try:
    # This script assumes it's running in an environment where pycoral is installed.
    from pycoral.utils.edgetpu import make_interpreter
    print("INFO: pycoral library imported successfully.")
except ImportError:
    # If pycoral is not installed, create a dummy function to avoid crashing the app on import.
    def make_interpreter(model_path):
        raise ImportError(f"pycoral library not found. Cannot create interpreter for {model_path}")
    print("WARNING: pycoral library not found. CoralInterface will not be functional.")


class CoralInterface:
    """
    Manages the lifecycle and inference of a Coral-accelerated TFLite model.
    This class acts as a hardware abstraction layer.
    """

    def __init__(self, model_path: str):
        """
        Initializes the interface and loads the model onto the Edge TPU.

        Args:
            model_path (str): The file path to the compiled .tflite model.
        """
        self.model_path = model_path
        self.interpreter = None
        self.is_loaded = False
        try:
            # Load the Edge TPU delegate and create the interpreter
            self.interpreter = make_interpreter(self.model_path)
            self.interpreter.allocate_tensors()
            self.is_loaded = True
            print(f"✅ Coral model loaded successfully from: {self.model_path}")
        except Exception as e:
            # This will catch errors if the device isn't connected or the model is invalid.
            print(f"⛔️ Failed to load Coral model. Error: {e}")
            self.is_loaded = False

    def embed(self, sentences: List[str]) -> np.ndarray:
        """
        Encodes a list of sentences into vector embeddings using the Coral TPU.

        Args:
            sentences (List[str]): A list of sentences to encode.

        Returns:
            np.ndarray: A numpy array where each row is an embedding.
        """
        if not self.is_loaded:
            raise RuntimeError("Coral model is not loaded. Cannot create embeddings.")

        input_details = self.interpreter.get_input_details()[0]
        output_details = self.interpreter.get_output_details()[0]

        # Process each sentence individually, as required by many Edge TPU encoder models.
        embeddings = []
        for sentence in sentences:
            self.interpreter.set_tensor(input_details['index'], np.array([sentence]))
            self.interpreter.invoke()
            embedding = self.interpreter.get_tensor(output_details['index'])[0]
            embeddings.append(embedding)
        
        return np.array(embeddings)

    @staticmethod
    def calculate_cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculates the cosine similarity between two embeddings."""
        dot_product = np.dot(emb1, emb2)
        norm_product = np.linalg.norm(emb1) * np.linalg.norm(emb2)
        return 0.0 if norm_product == 0 else dot_product / norm_product