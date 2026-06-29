import os
import yaml
from typing import Dict, Any

DEFAULT_CONFIG = {
    "evolution": {
        "pop_size": 1000,
        "n_generations": 10000,
        "crossover_prob": 0.7,
        "mutation_prob": 0.15,
        "eliminate_duplicates": False,
        "seed": None,
    },
    "surrogate": {
        "enabled": True,
        "hidden_dim": 128,
        "embedding_dim": 32,
        "batch_size": 256,
        "compile": True,
        "mixed_precision": True,
        "retrain_every": 200,
        "exact_eval_every": 100,
        "n_initial_samples": 500,
        "surrogate_epochs": 30,
        "min_r2": 0.90,
    },
    "exact_eval": {
        "batch_size": 5,
        "use_numba": True,
        "parity_tolerance": 1e-4,
    },
    "fitness": {
        "weights": {
            "effort": 1.0,
            "adjacency": 1.5,
            "finger_balance": 0.8,
            "same_finger": 2.0,
            "violations": 50.0,
            "workflow_coherence": 30.0,
            "learning_curve": 0.5,
            "app_coherence": 5.0,
            "trackball_proximity": 2.0,
        },
        "shortcut_importance_overrides": {},
        "missing_important_threshold": 6.0,
        "violation_sub_weights": {
            "duplicate": 10.0,
            "l0_displacement": 50.0,
            "missing_important": 5000000.0,
            "cross_layer_duplicate": 8.0,
            "group_split": 200.0,
            "thumb_occupancy": 200.0,
            "arrow_order": 500000.0,
            "hand_bias": 2000.0,
            "mouse_layer_access": 5000.0,
            "arrow_scattered": 5000000.0,
            "layer7_unreachable": 50000000.0,
        }
    },
    "output": {
        "build_dir": "build",
        "checkpoint_interval": 500,
        "verbose": True,
    },
    "profiling": {
        "enabled": False,
    },
}

class Config:
    def __init__(self, data: Dict[str, Any]):
        self._data = data
    
    @property
    def raw(self):
        return self._data.copy()
    
    def get(self, key: str, default=None):
        parts = key.split(".")
        data = self._data
        for part in parts:
            if isinstance(data, dict) and part in data:
                data = data[part]
            else:
                return default
        return data
    
    def to_dict(self):
        return self._data.copy()
    
    @classmethod
    def load(cls, path: str) -> "Config":
        if not os.path.exists(path):
            return cls(DEFAULT_CONFIG.copy())
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        merged = _merge_dicts(DEFAULT_CONFIG.copy(), data)
        return cls(merged)
    
    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            yaml.dump(self._data, f, default_flow_style=False)

def _merge_dicts(base: Dict, override: Dict) -> Dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_dicts(result[key], value)
        else:
            result[key] = value
    return result
