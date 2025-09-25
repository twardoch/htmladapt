# this_file: src/htmladapt/algorithms/matcher.py
"""Element matching algorithms for content reconciliation."""

import hashlib
import logging
from typing import Dict, List, Optional, Tuple

from bs4 import Tag, NavigableString

try:
    from rapidfuzz import fuzz
except ImportError:
    fuzz = None

try:
    import xxhash
except ImportError:
    xxhash = None

logger = logging.getLogger(__name__)


class ElementMatcher:
    """Multi-strategy element matching for HTML reconciliation.

    Implements perfect ID matching, hash-based matching, and fuzzy matching
    with configurable similarity thresholds.
    """

    def __init__(self, similarity_threshold: float = 0.7) -> None:
        """Initialize the element matcher.

        Args:
            similarity_threshold: Minimum similarity score for fuzzy matching
        """
        self.similarity_threshold = similarity_threshold
        self._content_cache: dict[str, str] = {}

    def match_elements(
        self,
        edited_elements: list[Tag],
        original_elements: list[Tag]
    ) -> list[tuple[Tag | None, Tag | None, float]]:
        """Match edited elements with original elements.

        Args:
            edited_elements: Elements from edited document
            original_elements: Elements from original document

        Returns:
            List of tuples: (edited_element, original_element, confidence_score)
            None values indicate unmatched elements
        """
        matches = []
        used_original_indices = set()

        for edited_elem in edited_elements:
            best_match = None
            best_score = 0.0
            best_original_idx = -1

            for idx, original_elem in enumerate(original_elements):
                if idx in used_original_indices:
                    continue

                score = self._calculate_similarity(edited_elem, original_elem)

                if score > best_score and score >= self.similarity_threshold:
                    best_match = original_elem
                    best_score = score
                    best_original_idx = idx

            if best_match is not None:
                matches.append((edited_elem, best_match, best_score))
                used_original_indices.add(best_original_idx)
            else:
                matches.append((edited_elem, None, 0.0))

        # Add unmatched original elements
        for idx, original_elem in enumerate(original_elements):
            if idx not in used_original_indices:
                matches.append((None, original_elem, 0.0))

        return matches

    def _calculate_similarity(self, elem1: Tag, elem2: Tag) -> float:
        """Calculate similarity score between two elements.

        Args:
            elem1: First element
            elem2: Second element

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Strategy 1: Perfect ID matching (highest priority)
        id_score = self._id_similarity(elem1, elem2)
        if id_score == 1.0:
            return 1.0

        # Strategy 2: Hash-based content matching
        hash_score = self._hash_similarity(elem1, elem2)
        if hash_score == 1.0:
            return 0.95  # Slightly lower than perfect ID match

        # Strategy 3: Fuzzy text matching
        text_score = self._text_similarity(elem1, elem2)

        # Strategy 4: Structural similarity
        structure_score = self._structure_similarity(elem1, elem2)

        # Combine scores with weights
        combined_score = (
            id_score * 0.4 +
            hash_score * 0.3 +
            text_score * 0.2 +
            structure_score * 0.1
        )

        return combined_score

    def _id_similarity(self, elem1: Tag, elem2: Tag) -> float:
        """Calculate ID-based similarity.

        Args:
            elem1: First element
            elem2: Second element

        Returns:
            1.0 if IDs match exactly, 0.0 otherwise
        """
        id1 = elem1.get('id')
        id2 = elem2.get('id')

        if id1 and id2 and id1 == id2:
            return 1.0

        return 0.0

    def _hash_similarity(self, elem1: Tag, elem2: Tag) -> float:
        """Calculate hash-based content similarity.

        Args:
            elem1: First element
            elem2: Second element

        Returns:
            1.0 if content hashes match, 0.0 otherwise
        """
        hash1 = self._get_content_hash(elem1)
        hash2 = self._get_content_hash(elem2)

        return 1.0 if hash1 == hash2 else 0.0

    def _text_similarity(self, elem1: Tag, elem2: Tag) -> float:
        """Calculate text-based fuzzy similarity.

        Args:
            elem1: First element
            elem2: Second element

        Returns:
            Fuzzy similarity score between 0.0 and 1.0
        """
        if fuzz is None:
            logger.warning("rapidfuzz not available, using simple text matching")
            return self._simple_text_similarity(elem1, elem2)

        text1 = self._get_element_text(elem1)
        text2 = self._get_element_text(elem2)

        if not text1 or not text2:
            return 0.0

        # Use rapidfuzz for accurate fuzzy matching
        similarity = fuzz.ratio(text1, text2) / 100.0
        return similarity

    def _simple_text_similarity(self, elem1: Tag, elem2: Tag) -> float:
        """Simple text similarity fallback when rapidfuzz is not available.

        Args:
            elem1: First element
            elem2: Second element

        Returns:
            Simple similarity score
        """
        text1 = self._get_element_text(elem1)
        text2 = self._get_element_text(elem2)

        if text1 == text2:
            return 1.0
        elif text1 and text2:
            # Simple Jaccard similarity on words
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())

            if not words1 and not words2:
                return 1.0

            intersection = words1 & words2
            union = words1 | words2

            return len(intersection) / len(union) if union else 0.0

        return 0.0

    def _structure_similarity(self, elem1: Tag, elem2: Tag) -> float:
        """Calculate structural similarity between elements.

        Args:
            elem1: First element
            elem2: Second element

        Returns:
            Structural similarity score
        """
        # Compare tag names
        if elem1.name != elem2.name:
            return 0.0

        # Compare attributes (excluding generated IDs)
        attrs1 = {k: v for k, v in elem1.attrs.items() if not k.startswith('id')}
        attrs2 = {k: v for k, v in elem2.attrs.items() if not k.startswith('id')}

        if attrs1 == attrs2:
            return 1.0

        # Partial attribute matching
        common_attrs = set(attrs1.keys()) & set(attrs2.keys())
        total_attrs = set(attrs1.keys()) | set(attrs2.keys())

        if not total_attrs:
            return 1.0  # Both have no attributes

        return len(common_attrs) / len(total_attrs)

    def _get_content_hash(self, element: Tag) -> str:
        """Generate content hash for an element.

        Args:
            element: Element to hash

        Returns:
            Content hash string
        """
        element_id = id(element)
        if element_id in self._content_cache:
            return self._content_cache[element_id]

        # Get normalized content for hashing
        content = self._get_element_text(element)
        tag_info = f"{element.name}:{element.attrs}"
        hash_input = f"{tag_info}|{content}".encode()

        if xxhash:
            content_hash = xxhash.xxh64(hash_input).hexdigest()
        else:
            content_hash = hashlib.sha256(hash_input).hexdigest()[:16]

        self._content_cache[element_id] = content_hash
        return content_hash

    def _get_element_text(self, element: Tag) -> str:
        """Extract normalized text content from element.

        Args:
            element: Element to extract text from

        Returns:
            Normalized text content
        """
        if hasattr(element, 'get_text'):
            text = element.get_text(separator=' ', strip=True)
        else:
            text = str(element).strip()

        # Normalize whitespace
        return ' '.join(text.split())

    def clear_cache(self) -> None:
        """Clear the content cache."""
        self._content_cache.clear()