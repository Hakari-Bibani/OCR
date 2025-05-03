"""
Kurdish Natural Language Processing tools adapted from AsoSoft resources.
"""

import re
import os
import unicodedata

class KurdishTokenizer:
    """
    A simple tokenizer for Kurdish language text.
    """
    
    def __init__(self):
        # Define punctuation characters
        self.punctuation = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~«»""''•…–—"""
        
        # Define Kurdish alphabet (Sorani)
        self.kurdish_letters = "ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنوۆەهیێ"
        
        # Compile regex patterns
        self.word_pattern = re.compile(r'[\w\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+')
        self.sentence_pattern = re.compile(r'[^\.!\?]+[\.!\?]')
    
    def normalize(self, text):
        """
        Normalize Kurdish text by standardizing characters and removing diacritics.
        """
        # Replace Arabic Kaf with Kurdish Kaf
        text = text.replace('ك', 'ک')
        
        # Replace Arabic Yeh with Kurdish Yeh
        text = text.replace('ي', 'ی')
        
        # Replace Arabic/Persian Heh with Kurdish Heh
        text = text.replace('ه‌', 'ە')
        
        # Remove diacritics (harakat)
        normalized = ''.join(c for c in unicodedata.normalize('NFD', text) 
                             if not unicodedata.category(c).startswith('Mn'))
        
        # Remove ZWNJ character
        normalized = normalized.replace('\u200c', '')
        
        return normalized
    
    def tokenize(self, text):
        """
        Tokenize Kurdish text into words.
        """
        # Normalize text first
        text = self.normalize(text)
        
        # Find all words
        words = self.word_pattern.findall(text)
        
        # Filter out empty strings and non-Kurdish characters
        words = [word for word in words if word.strip()]
        
        return words
    
    def sentence_tokenize(self, text):
        """
        Split text into sentences.
        """
        # Normalize text first
        text = self.normalize(text)
        
        # Simple sentence splitting based on punctuation
        sentences = self.sentence_pattern.findall(text)
        
        # If no sentences found with punctuation, just return the whole text
        if not sentences and text.strip():
            sentences = [text]
            
        return [s.strip() for s in sentences if s.strip()]

class KurdishStemmer:
    """
    A basic stemmer for Kurdish language.
    """
    
    def __init__(self):
        # Common Kurdish prefixes and suffixes
        self.prefixes = ['نە', 'بە', 'دە', 'هەڵ', 'دا', 'ڕا']
        self.suffixes = ['ەکان', 'ەکە', 'ێک', 'ان', 'یش', 'ە', 'ی', 'م', 'ت', 'ی', 'مان', 'تان', 'یان']
    
    def stem(self, word):
        """
        Remove common prefixes and suffixes from Kurdish words.
        """
        # Start with the word
        stemmed = word
        
        # Remove prefixes
        for prefix in self.prefixes:
            if stemmed.startswith(prefix) and len(stemmed) > len(prefix) + 2:
                stemmed = stemmed[len(prefix):]
                break
        
        # Remove suffixes
        for suffix in self.suffixes:
            if stemmed.endswith(suffix) and len(stemmed) > len(suffix) + 2:
                stemmed = stemmed[:-len(suffix)]
                break
        
        return stemmed

# Example usage
if __name__ == "__main__":
    # Example Kurdish text (Sorani)
    text = """
    کوردستان وڵاتێکی جوانە و خەڵکەکەی زۆر میهرەبانن. زمانی کوردی یەکێکە 
    لە زمانە هیندۆئەورووپییەکان و چەندین دیالێکتی هەیە.
    """
    
    # Initialize tokenizer
    tokenizer = KurdishTokenizer()
    
    # Tokenize
    words = tokenizer.tokenize(text)
    print(f"Words: {words}")
    
    # Sentence tokenize
    sentences = tokenizer.sentence_tokenize(text)
    print(f"Sentences: {sentences}")
    
    # Stemming
    stemmer = KurdishStemmer()
    stemmed_words = [stemmer.stem(word) for word in words]
    print(f"Stemmed words: {stemmed_words}")
