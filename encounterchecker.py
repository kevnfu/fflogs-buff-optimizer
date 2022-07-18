from __future__ import annotations
from typing import List, Dict, Tuple, Iterator, Any

from enums import Encounter

class EncounterChecker:
	encounter = Encounter.DSU
	def __init__(self, reportCode: str, client: FFClient):
		self._client = client
