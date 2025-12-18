from typing import Optional

import pandas as pd


class ResultStore:
    def __init__(self):
        self._final_df: Optional[pd.DataFrame] = None
        self._resumos: Optional[dict] = None
        self._periodo: Optional[tuple] = None

    def set_result(self, final_df: pd.DataFrame, resumos: dict) -> None:
        self._final_df = final_df
        self._resumos = resumos

    def set_period(self, inicio, fim) -> None:
        self._periodo = (inicio, fim)

    def get_result(self) -> Optional[pd.DataFrame]:
        return self._final_df

    def get_resumos(self) -> Optional[dict]:
        return self._resumos

    def get_period(self) -> Optional[tuple]:
        return self._periodo


result_store = ResultStore()
