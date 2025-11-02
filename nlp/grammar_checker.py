import torch
from gramformer import Gramformer

class GrammarChecker:
    """Handles loading and running the Gramformer model for error correction."""
    
    def __init__(self):
        self.gf = None
        # Check if CUDA is available and set the device accordingly
        self.use_gpu = torch.cuda.is_available() 

    def load_model(self):
        """Loads the Gramformer model using GPU if available."""
        if self.gf is None:
            # Note: We use the corrector model (models=1) 
            # Gramformer handles the downloading of the necessary 300-400MB T5 model here.
            print(f"Loading Gramformer model. Using GPU: {self.use_gpu}")
            try:
                self.gf = Gramformer(models=1, use_gpu=self.use_gpu)
                print("Gramformer model loaded successfully.")
            except Exception as e:
                print(f"Error loading Gramformer: {e}. Falling back to CPU/disabling NLP.")
                self.gf = None
                self.use_gpu = False # Disable GPU usage if load fails

    def unload_model(self):
        """Unloads the Gramformer model to free memory."""
        if self.gf is not None:
            print("Unloading Gramformer model and clearing memory.")
            self.gf = None
            if self.use_gpu:
                # Attempt to clear VRAM
                torch.cuda.empty_cache() 

    # def check_line(self, text: str) -> list[tuple[int, int, str, str]]:
    #     """
    #     Checks a single line of text for grammatical errors.
    #     Returns a list of tuples: (start_index, end_index, error_text, suggestion)
    #     """
    #     if self.gf is None:
    #         return []

    #     # Gramformer function to get edits: 
    #     # get_edits returns a list of dictionaries with error details.
    #     # This is a much better way to get the error span and suggestion!
    #     edits = self.gf.get_edits(text)
        
    #     results = []
    #     for edit in edits:
    #         # We need to map the edit indices back to the original text
    #         # Example edit: {'error_type': 'PUNCT', 'start': 10, 'end': 11, 'correction': ' '}
    #         # We'll rely on Gramformer's indices which are generally char-based.
            
    #         start_index = edit.get('start', 0)
    #         end_index = edit.get('end', len(text))
            
    #         # Extract the actual text that has the error
    #         error_text = text[start_index:end_index]
            
    #         # The corrected text is given by the 'correction' field
    #         suggestion = edit.get('correction', '')
            
    #         # We are interested in the start, end, the error text, and the suggestion
    #         if error_text and suggestion:
    #              results.append((start_index, end_index, error_text, suggestion))
            
    #     return results
    
    def check_line(self, text: str) -> list[tuple[int, int, str, str]]:
        """
        Checks a single line of text for grammatical errors.
        Returns a list of tuples: (start_index, end_index, error_text, suggestion)
        """
        if self.gf is None:
            return []
        
        # 1. Get the corrected version of the text
        corrected_sentences = self.gf.correct(text, max_candidates=1)
        
        if not corrected_sentences:
            return []
            
        corrected_text = list(corrected_sentences)[0]
        
        if corrected_text.strip() == text.strip():
            return []

        # 2. Get the list of edits (this is where the format can be tricky)
        # We rely on Gramformer's internal comparison of 'text' and 'corrected_text'.
        edits = self.gf.get_edits(text, corrected_text)
        
        results = []
        for edit_tuple in edits:
            try:
                # 1. Extract the correction data (Suggestion and Error Text)
                # We assume these two are correctly reported by Gramformer:
                error_text = str(edit_tuple[1])     # The incorrect word/phrase (e.g., 'has')
                suggestion = str(edit_tuple[4])     # The suggested correction (e.g., 'have')
                
                # We discard simple punctuation/insertion errors that are one character or empty.
                if len(error_text) < 1:
                    continue

                # 2. 🌟 CRITICAL FIX: Find the correct character indices using Python's string search (index())
                # This bypasses the faulty indices returned by Gramformer's tuple (indices 2, 3, 5, 6).
                
                # Find the starting index of the 'error_text' in the original 'text'.
                start_index = text.find(error_text)
                
                if start_index != -1:
                    # Calculate the end index based on the length of the error text found.
                    end_index = start_index + len(error_text)
                    
                    # 3. Validation: Ensure the found span actually contains the word.
                    # We check if the span is reasonable and within the text bounds.
                    if end_index <= len(text) and start_index >= 0:
                        results.append((start_index, end_index, error_text, suggestion))

            except (TypeError, IndexError, ValueError) as e:
                # Skip malformed edits
                continue
            
        return results

