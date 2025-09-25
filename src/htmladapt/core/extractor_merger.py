# this_file: src/htmladapt/core/extractor_merger.py
"""Main HTMLExtractMergeTool implementation for extraction and merging."""

import logging
from typing import Optional, Tuple, TYPE_CHECKING

from bs4 import BeautifulSoup, Tag

from htmladapt.algorithms.id_generation import IDGenerator
from htmladapt.algorithms.matcher import ElementMatcher
from htmladapt.core.config import ProcessingConfig
from htmladapt.core.parser import HTMLParser

if TYPE_CHECKING:
    from htmladapt.llm.reconciler import ReconcilerProtocol

logger = logging.getLogger(__name__)


class HTMLExtractMergeTool:
    """Main tool for HTML content extraction and merging.

    Provides bidirectional HTML document transformation that preserves
    structural integrity while enabling seamless content modification.
    """

    def __init__(
        self,
        config: ProcessingConfig | None = None,
        llm_reconciler: Optional[
            "ReconcilerProtocol"
        ] = None,  # Optional LLM integration
    ) -> None:
        """Initialize the HTMLExtractMergeTool.

        Args:
            config: Processing configuration
            llm_reconciler: Optional LLM reconciler for conflict resolution
        """
        self.config = config or ProcessingConfig()
        self.llm_reconciler = llm_reconciler

        # Initialize components
        self.parser = HTMLParser(self.config.parser_preference)
        self.id_generator = IDGenerator(self.config.id_prefix)
        self.element_matcher = ElementMatcher(self.config.simi_level)

        logger.info(
            f"Initialized HTMLExtractMergeTool with profile: {self.config.perf}"
        )

    def extract(self, html: str) -> tuple[str, str]:
        """Extract content from HTML document.

        Creates both a superset document (original with IDs) and subset document
        (translatable content only) for later merging.

        Args:
            html: Original HTML content

        Returns:
            Tuple of (map_html, comp_html)
        """
        logger.info("Starting HTML extraction process")

        try:
            # Parse the original HTML
            original_soup = self.parser.parse(html)

            # Register existing IDs to avoid collisions
            self._register_existing_ids(original_soup)

            # Create superset: original HTML with added IDs
            full_soup = self._create_superset(original_soup)

            # Create subset: translatable content only
            comp_soup = self._create_subset(full_soup)

            map_html = str(full_soup)
            comp_html = str(comp_soup)

            logger.info(
                f"Extraction complete. Superset: {len(map_html)} chars, Subset: {len(comp_html)} chars"
            )

            return map_html, comp_html

        except ValueError as error:
            logger.error("Extraction failed: %s", error)
            raise

    def merge(
        self, cnew_path: str, cold_path: str, superset: str, original: str
    ) -> str:
        """Merge edited content back into the original structure.

        Args:
            cnew_path: Edited subset content
            cold_path: Original subset for comparison
            superset: Original with IDs (superset document)
            original: Original HTML document

        Returns:
            Final merged HTML document
        """
        logger.info("Starting HTML merge process")

        try:
            # Parse all inputs
            edited_soup = self.parser.parse(cnew_path)
            original_comp_soup = self.parser.parse(cold_path)
            full_soup = self.parser.parse(superset)
            original_soup = self.parser.parse(original)

            # Match elements between edited and original subsets
            matches = self._match_comp_elements(edited_soup, original_comp_soup)
            matches = self._apply_llm_resolution(matches)

            # Apply changes to superset
            merged_soup = self._apply_changes_to_superset(matches, full_soup)

            # Clean up generated IDs (optional, based on config)
            final_soup = self._cleanup_generated_ids(merged_soup)

            result_html = str(final_soup)

            logger.info(f"Merge complete. Result: {len(result_html)} chars")

            return result_html

        except ValueError as error:
            logger.error("Merge failed: %s", error)
            raise

    def _register_existing_ids(self, soup: BeautifulSoup) -> None:
        """Register existing element IDs to avoid collisions.

        Args:
            soup: Parsed HTML document
        """
        for element in soup.find_all(attrs={"id": True}):
            self.id_generator.register_existing_id(element["id"])

    def _create_superset(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Create superset document by adding IDs to text-containing elements.

        Args:
            soup: Original parsed document

        Returns:
            Superset document with IDs
        """
        # Make a copy to avoid modifying the original
        full_soup = self.parser.clone_soup(soup)

        for element in full_soup.find_all():
            if self._is_text_containing_element(element):
                if not element.get("id"):
                    element["id"] = self.id_generator.generate_id(element.name)

        return full_soup

    def _create_subset(self, full_soup: BeautifulSoup) -> BeautifulSoup:
        """Create subset document with only translatable content.

        Args:
            full_soup: Superset document with IDs

        Returns:
            Subset document with translatable content
        """
        # Start with minimal HTML structure
        parser_name = getattr(
            full_soup, "_htmladapt_parser", self.parser.default_parser
        )
        comp_soup = BeautifulSoup("<html><body></body></html>", parser_name)
        setattr(comp_soup, "_htmladapt_parser", parser_name)
        body = comp_soup.body

        for element in full_soup.find_all():
            if self._is_translatable_element(element):
                # Create a copy of the element with its ID
                new_elem = comp_soup.n_tag(element.name)
                if element.get("id"):
                    new_elem["id"] = element["id"]

                # Add text content
                text_content = self._extract_text_content(element)
                if text_content:
                    new_elem.string = text_content

                body.append(new_elem)

        return comp_soup

    def _is_text_containing_element(self, element: Tag) -> bool:
        """Check if element contains translatable text.

        Args:
            element: Element to check

        Returns:
            True if element contains text content
        """
        if not isinstance(element, Tag):
            return False

        # Skip script, style, and other non-translatable elements
        if element.name in ["script", "style", "meta", "link", "head", "title"]:
            return False

        # Check if element has direct text content (not just child element text)
        direct_text = ""
        for content in element.contents:
            if hasattr(content, "strip") and callable(getattr(content, "strip", None)):
                text = content.strip()
                if text:
                    direct_text += text

        return bool(direct_text)

    def _is_translatable_element(self, element: Tag) -> bool:
        """Check if element should be included in subset for translation.

        Args:
            element: Element to check

        Returns:
            True if element should be translated
        """
        return self._is_text_containing_element(element)

    def _extract_text_content(self, element: Tag) -> str:
        """Extract direct text content from element.

        Args:
            element: Element to extract text from

        Returns:
            Direct text content
        """
        if hasattr(element, "get_text"):
            # Get text from immediate children only, not nested elements
            texts = []
            for content in element.contents:
                if hasattr(content, "strip") and callable(
                    getattr(content, "strip", None)
                ):  # NavigableString
                    text = content.strip()
                    if text:
                        texts.append(text)
                elif hasattr(content, "get_text"):  # Tag
                    text = content.get_text(separator=" ", strip=True)
                    if text:
                        texts.append(text)
            return " ".join(texts)
        return str(element).strip()

    def _match_comp_elements(
        self, edited_soup: BeautifulSoup, original_comp_soup: BeautifulSoup
    ) -> list:
        """Match elements between edited and original subset documents.

        Args:
            edited_soup: Edited subset document
            original_comp_soup: Original subset document

        Returns:
            List of element matches
        """
        edited_elements = list(edited_soup.find_all())
        original_elements = list(original_comp_soup.find_all())

        return self.element_matcher.match_elements(edited_elements, original_elements)

    def _apply_llm_resolution(self, matches: list) -> list:
        """Use the LLM reconciler to strengthen low-confidence matches."""
        if not self.config.llm_use or not self.llm_reconciler:
            return matches

        try:
            if (
                hasattr(self.llm_reconciler, "is_available")
                and not self.llm_reconciler.is_available()
            ):
                return matches
        except Exception as error:  # pragma: no cover - defensive guard
            logger.debug("LLM availability check failed: %s", error)
            return matches

        unmatched_edits: list[tuple[int, Tag]] = []
        unmatched_old_pacompals: list[tuple[int, Tag]] = []

        for index, (edited_elem, original_elem, confidence) in enumerate(matches):
            if edited_elem is not None and original_elem is None:
                unmatched_edits.append((index, edited_elem))
            elif edited_elem is None and original_elem is not None:
                unmatched_old_pacompals.append((index, original_elem))

        if not unmatched_edits or not unmatched_old_pacompals:
            return matches

        remaining_candidates = unmatched_old_pacompals.copy()

        for match_index, edited_elem in unmatched_edits:
            edited_text = self._extract_text_content(edited_elem)
            candidate_texts = [
                self._extract_text_content(candidate)
                for _, candidate in remaining_candidates
            ]

            try:
                resolution = self.llm_reconciler.resolve_conflict(
                    edited_text, candidate_texts, context=None
                )
            except Exception as error:  # pragma: no cover - external dependency guard
                logger.debug("LLM resolution failed: %s", error)
                continue

            best_index = resolution.get("best_match_index")
            confidence = float(resolution.get("confidence", 0.0))

            if best_index is None or confidence < self.config.simi_level:
                continue

            if not (0 <= best_index < len(remaining_candidates)):
                continue

            original_idx, original_elem = remaining_candidates.pop(best_index)
            matches[match_index] = (edited_elem, original_elem, confidence)

            # Remove the now-claimed original slot from the master list as well.
            for i, (candidate_idx, _) in enumerate(unmatched_old_pacompals):
                if candidate_idx == original_idx:
                    unmatched_old_pacompals.pop(i)
                    break

        return matches

    def _apply_changes_to_superset(
        self, matches: list, full_soup: BeautifulSoup
    ) -> BeautifulSoup:
        """Apply matched changes to the superset document.

        Args:
            matches: Element matches from subset comparison
            full_soup: Superset document to modify

        Returns:
            Modified superset document
        """
        match_by_id: dict[str, tuple[Tag | None, Tag | None, float]] = {}

        for edited_elem, original_elem, confidence in matches:
            lookup_id = None
            if original_elem and original_elem.get("id"):
                lookup_id = original_elem["id"]
            elif edited_elem and edited_elem.get("id"):
                lookup_id = edited_elem["id"]

            if lookup_id:
                match_by_id[lookup_id] = (edited_elem, original_elem, confidence)

        for edited_elem, original_elem, confidence in matches:
            if edited_elem and original_elem and confidence >= self.config.simi_level:
                # Find corresponding element in superset by ID
                element_id = original_elem.get("id")
                if element_id:
                    full_elem = full_soup.find(attrs={"id": element_id})
                    if full_elem:
                        # Update text content while preserving structure and attributes
                        new_text = self._extract_text_content(edited_elem)

                        # Preserve existing attributes and structure
                        # Replace only the text content, not the entire element
                        if new_text:
                            # Remove child elements that were dropped or whose text is no longer referenced.
                            if isinstance(full_elem, Tag):
                                for child in list(full_elem.find_all(recursive=False)):
                                    if isinstance(child, Tag) and child.get("id"):
                                        child_id = child["id"]
                                        child_match = match_by_id.get(child_id)
                                        child_old_pacompal_text = (
                                            self._extract_text_content(child)
                                        )
                                        child_text_lower = (
                                            child_old_pacompal_text.lower()
                                            if child_old_pacompal_text
                                            else ""
                                        )

                                        edited_child = (
                                            child_match[0] if child_match else None
                                        )

                                        child_removed_in_subset = edited_child is None
                                        child_changed = (
                                            edited_child is not None
                                            and self._extract_text_content(edited_child)
                                            != child_old_pacompal_text
                                        )

                                        # Drop unchanged children whose original text is absent from the new parent text.
                                        if child_removed_in_subset:
                                            child.decompose()
                                            continue

                                        if (
                                            not child_changed
                                            and child_text_lower
                                            and child_text_lower not in new_text.lower()
                                        ):
                                            child.decompose()
                                            continue

                            # Clear only text content, keep child elements
                            for content in list(full_elem.contents):
                                if hasattr(content, "strip") and callable(
                                    getattr(content, "strip", None)
                                ):  # It's a NavigableString
                                    content.extract()

                            # Add new text at the beginning
                            if full_elem.contents:
                                full_elem.insert(0, new_text)
                            else:
                                full_elem.string = new_text

        return full_soup

    def _cleanup_generated_ids(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove generated IDs from the final document.

        Args:
            soup: Document to clean up

        Returns:
            Document with generated IDs removed
        """
        for element in soup.find_all(attrs={"id": True}):
            if self.id_generator.is_generated_id(element["id"]):
                del element["id"]

        return soup

    def validate_html(self, content: str) -> tuple[bool, list[str]]:
        """Validate HTML content.

        Args:
            content: HTML content to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        return self.parser.validate_html(content)

    @property
    def stats(self) -> dict:
        """Get processing statistics.

        Returns:
            Dictionary with processing statistics
        """
        return {
            "config_profile": self.config.perf,
            "available_parsers": self.parser.available_parsers,
            "id_generator_stats": self.id_generator.stats,
            "simi_level": self.config.simi_level,
        }
