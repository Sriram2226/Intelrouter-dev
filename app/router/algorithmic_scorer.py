import re
from typing import Dict
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from app.config import REASONING_KEYWORDS, SYSTEM_DESIGN_KEYWORDS, CODE_INDICATORS


# Download required NLTK data (punkt_tab for NLTK 3.8+)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt_tab', quiet=True)
    except:
        # Fallback to old punkt for older NLTK versions
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
        # Fallback to old resource name for older NLTK versions
        try:
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except:
            pass

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)


lemmatizer = WordNetLemmatizer()


def extract_features(query: str) -> Dict[str, float]:
    """Extract NLP features from query."""
    query_lower = query.lower()
    
    # Basic features
    query_length = len(query)
    word_count = len(word_tokenize(query))
    sentence_count = len(sent_tokenize(query))
    
    # Tokenization and POS tagging
    tokens = word_tokenize(query)
    pos_tags = pos_tag(tokens)
    
    # POS patterns indicating complexity
    # Verbs, conjunctions, and complex structures
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
    
    # Question complexity (multiple question marks, question words)
    question_words = ['what', 'why', 'how', 'when', 'where', 'which', 'who']
    question_count = sum(1 for word in question_words if word in query_lower)
    has_multiple_questions = query.count('?') > 1
    
    return {
        "query_length": query_length,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "complex_pos_ratio": complex_pos_ratio,
        "reasoning_ratio": reasoning_ratio,
        "system_design_ratio": system_design_ratio,
        "code_ratio": code_ratio,
        "question_count": question_count,
        "has_multiple_questions": 1.0 if has_multiple_questions else 0.0
    }


def score_difficulty(query: str) -> str:
    """
    Algorithmic difficulty scorer.
    Returns: EASY, HARD, or UNSURE
    """
    features = extract_features(query)
    
    # Scoring thresholds
    easy_threshold = 0.3
    hard_threshold = 0.7
    
    score = 0.0
    
    # Query length (normalized)
    if features["word_count"] > 50:
        score += 0.15
    elif features["word_count"] < 10:
        score -= 0.1
    
    # Sentence count
    if features["sentence_count"] > 3:
        score += 0.15
    
    # Reasoning keywords
    score += features["reasoning_ratio"] * 0.2
    
    # System design keywords
    score += features["system_design_ratio"] * 0.2
    
    # Code indicators
    score += features["code_ratio"] * 0.15
    
    # POS complexity
    score += features["complex_pos_ratio"] * 0.1
    
    # Question complexity
    if features["question_count"] > 2 or features["has_multiple_questions"]:
        score += 0.15
    
    # Normalize score to [0, 1]
    score = max(0.0, min(1.0, score))
    
    # Classification
    if score < easy_threshold:
        return "EASY"
    elif score > hard_threshold:
        return "HARD"
    else:
        return "UNSURE"

