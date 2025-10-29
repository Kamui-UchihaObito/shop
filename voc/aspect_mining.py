"""Extract coarse aspects from review texts."""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List

ASPECT_KEYWORDS: Dict[str, set[str]] = {
    "物流": {"物流", "快递", "配送", "到货"},
    "价格": {"价格", "便宜", "优惠", "折扣"},
    "品质": {"质量", "做工", "材质", "体验"},
    "服务": {"客服", "回复", "服务", "售后"},
}


def extract_aspects(texts: Iterable[str]) -> Dict[str, List[str]]:
    buckets: Dict[str, List[str]] = defaultdict(list)
    for text in texts:
        for aspect, keywords in ASPECT_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                buckets[aspect].append(text)
    return dict(buckets)
