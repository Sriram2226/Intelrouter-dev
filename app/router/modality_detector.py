"""
Modality detector: determines if a query is text, vision, or document-based.
Used to short-circuit the difficulty router and select the right model.
"""
from app.utils.logger import get_logger

logger = get_logger("intelrouter.router.modality_detector")


def detect_modality(query: str, has_image: bool = False, has_document: bool = False) -> str:
    """
    Detect the modality of the query.

    Returns:
        "vision"   - if an image is attached
        "document" - if a document (PDF/DOCX) is attached
        "text"     - default text query
    """
    if has_image:
        logger.info("   🖼️  Modality detected: VISION")
        return "vision"
    if has_document:
        logger.info("   📄 Modality detected: DOCUMENT")
        return "document"

    # Heuristic: check for image/document keywords in the query text
    q_lower = query.lower()
    image_hints = ["in this image", "look at the image", "in the picture", "what do you see"]
    doc_hints = ["in this document", "in this pdf", "the attached file", "from the doc"]

    if any(hint in q_lower for hint in image_hints):
        logger.info("   🖼️  Modality detected: VISION (heuristic)")
        return "vision"
    if any(hint in q_lower for hint in doc_hints):
        logger.info("   📄 Modality detected: DOCUMENT (heuristic)")
        return "document"

    return "text"
