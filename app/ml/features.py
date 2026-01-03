"""
Shared feature extraction module for training and inference.
Ensures feature parity between training and inference pipelines.
"""
import re
from typing import Dict, List
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag
from app.config import REASONING_KEYWORDS, SYSTEM_DESIGN_KEYWORDS, CODE_INDICATORS

# Download NLTK data if needed
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt_tab', quiet=True)
    except:
        try:
            nltk.download('punkt', quiet=True)
        except:
            pass

try:
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    try:
        nltk.download('averaged_perceptron_tagger_eng', quiet=True)
    except:
        try:
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except:
            pass


def extract_text_features(query: str) -> Dict[str, float]:
    """
    Extract text-based features from query.
    Returns normalized feature vector.
    """
    query_lower = query.lower()
    
    # Basic statistics
    query_length = len(query)
    words = word_tokenize(query)
    word_count = len(words)
    sentence_count = len(sent_tokenize(query))
    
    # Token-based features
    tokens = word_tokenize(query)
    pos_tags = pos_tag(tokens) if tokens else []
    
    # POS patterns
    verb_count = sum(1 for _, tag in pos_tags if tag.startswith('VB'))
    conjunction_count = sum(1 for _, tag in pos_tags if tag in ['CC', 'IN'])
    complex_pos_ratio = (verb_count + conjunction_count) / max(len(tokens), 1)
    
    # Keyword matching
    reasoning_score = sum(1 for keyword in REASONING_KEYWORDS if keyword in query_lower)
    system_design_score = sum(1 for keyword in SYSTEM_DESIGN_KEYWORDS if keyword in query_lower)
    code_score = sum(1 for keyword in CODE_INDICATORS if keyword in query_lower)
    
    # Normalize keyword scores
    reasoning_ratio = reasoning_score / max(len(REASONING_KEYWORDS), 1)
    system_design_ratio = system_design_score / max(len(SYSTEM_DESIGN_KEYWORDS), 1)
    code_ratio = code_score / max(len(CODE_INDICATORS), 1)
    
    # Question complexity
    question_words = ['what', 'why', 'how', 'when', 'where', 'which', 'who']
    question_count = sum(1 for word in question_words if word in query_lower)
    has_multiple_questions = query.count('?') > 1
    
    # Code indicators (punctuation, brackets)
    has_code_punctuation = bool(re.search(r'[{}();=]', query))
    has_brackets = bool(re.search(r'[\[\](){}]', query))
    
    # Character-level features
    uppercase_ratio = sum(1 for c in query if c.isupper()) / max(len(query), 1)
    digit_ratio = sum(1 for c in query if c.isdigit()) / max(len(query), 1)
    
    return {
        "query_length": float(query_length),
        "word_count": float(word_count),
        "sentence_count": float(sentence_count),
        "complex_pos_ratio": float(complex_pos_ratio),
        "reasoning_ratio": float(reasoning_ratio),
        "system_design_ratio": float(system_design_ratio),
        "code_ratio": float(code_ratio),
        "question_count": float(question_count),
        "has_multiple_questions": 1.0 if has_multiple_questions else 0.0,
        "has_code_punctuation": 1.0 if has_code_punctuation else 0.0,
        "has_brackets": 1.0 if has_brackets else 0.0,
        "uppercase_ratio": float(uppercase_ratio),
        "digit_ratio": float(digit_ratio),
    }


def extract_tfidf_features(queries: List[str], vectorizer=None):
    """
    Extract TF-IDF features. Used during training with fit, 
    during inference with transform only.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    if vectorizer is None:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=5000,
            lowercase=True,
            stop_words='english',
            min_df=2,
            max_df=0.95
        )
        return vectorizer.fit_transform(queries), vectorizer
    else:
        return vectorizer.transform(queries), vectorizer


def combine_features(text_features: Dict[str, float], tfidf_vector) -> List[float]:
    """
    Combine text features and TF-IDF vector into single feature array.
    Returns flat feature vector for model input.
    """
    import numpy as np
    
    # Extract text feature values in consistent order
    text_feature_order = [
        "query_length", "word_count", "sentence_count", "complex_pos_ratio",
        "reasoning_ratio", "system_design_ratio", "code_ratio", "question_count",
        "has_multiple_questions", "has_code_punctuation", "has_brackets",
        "uppercase_ratio", "digit_ratio"
    ]
    
    text_feature_array = [text_features[k] for k in text_feature_order]
    
    # Convert TF-IDF sparse matrix to dense array
    if hasattr(tfidf_vector, 'toarray'):
        tfidf_array = tfidf_vector.toarray()[0].tolist()
    else:
        tfidf_array = tfidf_vector.tolist() if isinstance(tfidf_vector, list) else []
    
    # Combine features
    combined = text_feature_array + tfidf_array
    
    return combined

