
import os, json
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config.json')

DEFAULT = {
  'data_dir': '',
  'exclusions_agrup': [],
  'exclusions_frota': []
}

def get_config():
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                for k,v in DEFAULT.items():
                    cfg.setdefault(k, v)
                return cfg
    except Exception:
        pass
    return DEFAULT.copy()

def save_config(cfg: dict):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    return True

def update_data_dir(path: str) -> bool:
    if not path:
        cfg = get_config(); cfg['data_dir']=''; save_config(cfg); return True
    if os.path.isdir(path):
        cfg = get_config(); cfg['data_dir']=path; save_config(cfg); return True
    return False

def update_exclusions(excl_agr: list, excl_fro: list):
    cfg = get_config(); cfg['exclusions_agrup'] = list(dict.fromkeys(e.strip() for e in excl_agr if e.strip()))
    cfg['exclusions_frota'] = list(dict.fromkeys(e.strip() for e in excl_fro if e.strip()))
    save_config(cfg)
