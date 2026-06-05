from dataclasses import dataclass
from typing import Optional
@dataclass
class Task:
    name: str
    priority_num: int   # 0, 1, 2
    color: str
    burst_time: int     # Tempo total de execução 
    