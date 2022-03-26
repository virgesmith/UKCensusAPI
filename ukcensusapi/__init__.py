__version__ = "1.1.6"

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd  # type: ignore


class CensusAPI(ABC):

  URL: str

  @abstractmethod
  def get_geo_codes(self, la_codes: list[str], code_type: str) -> str:
    raise NotImplementedError()

  @abstractmethod
  def get_lad_codes(self, la_names: list[str]) -> list[str]:
    raise NotImplementedError()

  # @abstractmethod
  # def get_url(self, table_internal, query_params):

  @abstractmethod
  def get_data(self, table: str, query_params: dict[str, Any], r_compat: bool=False) -> pd.DataFrame:
    raise NotImplementedError()

  @abstractmethod
  def get_metadata(self, table_name: str) -> dict[str, Any]:
    raise NotImplementedError()

  @abstractmethod
  def load_metadata(self, table_name) -> dict[str, Any]:
    raise NotImplementedError()
