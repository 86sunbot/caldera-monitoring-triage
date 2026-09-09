"""
Client for Site Registry service.
Enforces jurisdiction and regional compliance boundaries (ISO 42001 A.7).
"""

from typing import Dict, Tuple


class SiteRegistryClient:
    """Mock Site Registry mapping clinical trial sites to geographic regions."""

    def __init__(self, simulate_500: bool = False):
        self.simulate_500 = simulate_500
        # Mock site-to-country registry
        self._registry: Dict[str, str] = {
            "SITE-101": "UK",
            "SITE-102": "DE",
            "SITE-103": "FR",
            "SITE-404": "RESTRICTED_REGION_X",  # Explicitly subject to data sovereignty restriction
        }
        self._restricted_regions = {"RESTRICTED_REGION_X", "EMBARGOED_TERRITORY"}

    def get_site_country(self, site_id: str) -> str:
        """Fetch site country. Simulates HTTP 500 if error injection is active."""
        if self.simulate_500:
            raise RuntimeError("HTTP 500: Site Registry Service Unavailable")
        return self._registry.get(site_id, "UNKNOWN")

    def is_region_restricted(self, site_id: str) -> Tuple[bool, str, str]:
        """
        Evaluates whether a site is restricted by regional cross-border data transfer laws.
        Returns: (is_restricted, country, justification)
        """
        country = self.get_site_country(site_id)
        if country in self._restricted_regions:
            return (
                True,
                country,
                f"Data sovereignty restriction: {country} data cannot cross study processing boundary."
            )
        return (False, country, "")
