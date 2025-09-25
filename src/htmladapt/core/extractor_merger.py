# this_file: src/htmladapt/core/extractor_merger.py
"""Main HTMLExtractMergeTool implementation for extraction and merging."""

import logging
from typing import Optional, Tuple

from bs4 import BeautifulSoup, Tag

from htmladapt.algorithms.id_generation import IDGenerator
from htmladapt.algorithms.matcher import ElementMatcher
from htmladapt.core.config import ProcessingConfig
from htmladapt.core.parser import HTMLParser

logger = logging.getLogger(__name__)


class HTMLExtractMergeTool:
    """Main tool for HTML content extraction and merging.

    Provides bidirectional HTML document transformation that preserves
    structural integrity while enabling seamless content modification.
    """

    def __init__(
        self,
        config: Optional[ProcessingConfig] = None,
        llm_reconciler=None  # Optional LLM integration
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
        self.element_matcher = ElementMatcher(self.config.similarity_threshold)

        logger.info(f"Initialized HTMLExtractMergeTool with profile: {self.config.performance_profile}")

    def extract(self, html: str) -> Tuple[str, str]:
        """Extract content from HTML document.

        Creates both a superset document (original with IDs) and subset document
        (translatable content only) for later merging.

        Args:
            html: Original HTML content

        Returns:
            Tuple of (superset_html, subset_html)
        """
        logger.info("Starting HTML extraction process")

        try:
            # Parse the original HTML
            original_soup = self.parser.parse(html)

            # Register existing IDs to avoid collisions
            self._register_existing_ids(original_soup)

            # Create superset: original HTML with added IDs
            superset_soup = self._create_superset(original_soup)

            # Create subset: translatable content only
            subset_soup = self._create_subset(superset_soup)

            superset_html = str(superset_soup)
            subset_html = str(subset_soup)

            logger.info(f"Extraction complete. Superset: {len(superset_html)} chars, Subset: {len(subset_html)} chars")

            return superset_html, subset_html

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise

    def merge(
        self,
        edited_subset: str,
        original_subset: str,
        superset: str,
        original: str
    ) -> str:
        """Merge edited content back into the original structure.

        Args:
            edited_subset: Edited subset content
            original_subset: Original subset for comparison
            superset: Original with IDs (superset document)
            original: Original HTML document

        Returns:
            Final merged HTML document
        """
        logger.info("Starting HTML merge process")

        try:
            # Parse all inputs
            edited_soup = self.parser.parse(edited_subset)
            original_subset_soup = self.parser.parse(original_subset)
            superset_soup = self.parser.parse(superset)
            original_soup = self.parser.parse(original)

            # Match elements between edited and original subsets
            matches = self._match_subset_elements(edited_soup, original_subset_soup)

            # Apply changes to superset
            merged_soup = self._apply_changes_to_superset(matches, superset_soup)

            # Clean up generated IDs (optional, based on config)
            final_soup = self._cleanup_generated_ids(merged_soup)

            result_html = str(final_soup)

            logger.info(f"Merge complete. Result: {len(result_html)} chars")

            return result_html

        except Exception as e:
            logger.error(f"Merge failed: {e}")
            raise

    def _register_existing_ids(self, soup: BeautifulSoup) -> None:
        """Register existing element IDs to avoid collisions.

        Args:
            soup: Parsed HTML document
        """
        for element in soup.find_all(attrs={"id": True}):
            self.id_generator.register_existing_id(element['id'])

    def _create_superset(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Create superset document by adding IDs to text-containing elements.

        Args:
            soup: Original parsed document

        Returns:
            Superset document with IDs
        """
        # Make a copy to avoid modifying the original
        superset_soup = BeautifulSoup(str(soup), features=self.parser._available_parsers[0])

        for element in superset_soup.find_all():
            if self._is_text_containing_element(element):
                if not element.get('id'):
                    element['id'] = self.id_generator.generate_id(element.name)

        return superset_soup

    def _create_subset(self, superset_soup: BeautifulSoup) -> BeautifulSoup:
        """Create subset document with only translatable content.

        Args:
            superset_soup: Superset document with IDs

        Returns:
            Subset document with translatable content
        """
        # Start with minimal HTML structure
        subset_soup = BeautifulSoup('<html><body></body></html>', features=self.parser._available_parsers[0])
        body = subset_soup.body

        for element in superset_soup.find_all():
            if self._is_translatable_element(element):
                # Create a copy of the element with its ID
                new_elem = subset_soup.new_tag(element.name)
                if element.get('id'):
                    new_elem['id'] = element['id']

                # Add text content
                text_content = self._extract_text_content(element)
                if text_content:
                    new_elem.string = text_content

                body.append(new_elem)

        return subset_soup

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
        if element.name in ['script', 'style', 'meta', 'link', 'head', 'title']:
            return False

        # Check if element has direct text content (not just child element text)
        direct_text = ""
        for content in element.contents:
            if hasattr(content, 'strip') and content.strip():
                direct_text += content.strip()

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
        if hasattr(element, 'get_text'):
            # Get text from immediate children only, not nested elements
            texts = []
            for content in element.contents:
                if hasattr(content, 'strip'):  # NavigableString
                    text = content.strip()
                    if text:
                        texts.append(text)
                elif hasattr(content, 'get_text'):  # Tag
                    text = content.get_text(separator=' ', strip=True)
                    if text:
                        texts.append(text)
            return ' '.join(texts)
        return str(element).strip()

    def _match_subset_elements(
        self,
        edited_soup: BeautifulSoup,
        original_subset_soup: BeautifulSoup
    ) -> list:
        """Match elements between edited and original subset documents.

        Args:
            edited_soup: Edited subset document
            original_subset_soup: Original subset document

        Returns:
            List of element matches
        """
        edited_elements = list(edited_soup.find_all())
        original_elements = list(original_subset_soup.find_all())

        return self.element_matcher.match_elements(edited_elements, original_elements)

    def _apply_changes_to_superset(
        self,
        matches: list,
        superset_soup: BeautifulSoup
    ) -> BeautifulSoup:
        """Apply matched changes to the superset document.

        Args:
            matches: Element matches from subset comparison
            superset_soup: Superset document to modify

        Returns:
            Modified superset document
        """
        for edited_elem, original_elem, confidence in matches:
            if edited_elem and original_elem and confidence >= self.config.similarity_threshold:
                # Find corresponding element in superset by ID
                element_id = original_elem.get('id')
                if element_id:
                    superset_elem = superset_soup.find(attrs={'id': element_id})
                    if superset_elem:
                        # Update text content while preserving structure and attributes
                        new_text = self._extract_text_content(edited_elem)

                        # Preserve existing attributes and structure
                        # Replace only the text content, not the entire element
                        if new_text:
                            # Clear only text content, keep child elements
                            for content in list(superset_elem.contents):
                                if hasattr(content, 'strip'):  # It's a NavigableString
                                    content.extract()

                            # Add new text at the beginning
                            if superset_elem.contents:
                                superset_elem.insert(0, new_text)
                            else:
                                superset_elem.string = new_text

        return superset_soup

    def _cleanup_generated_ids(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove generated IDs from the final document.

        Args:
            soup: Document to clean up

        Returns:
            Document with generated IDs removed
        """
        for element in soup.find_all(attrs={'id': True}):
            if self.id_generator.is_generated_id(element['id']):
                del element['id']

        return soup

    def validate_html(self, content: str) -> Tuple[bool, list[str]]:
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
            "config_profile": self.config.performance_profile,
            "available_parsers": self.parser.available_parsers,
            "id_generator_stats": self.id_generator.stats,
            "similarity_threshold": self.config.similarity_threshold,
        }