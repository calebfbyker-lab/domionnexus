from dataclasses import dataclass

@dataclass
class Quotas:
    max_concurrent: int = 2
    per_minute: int = 30

TENANTS = {
    "public": Quotas(max_concurrent=1, per_minute=10),
    "cfbk":   Quotas(max_concurrent=4, per_minute=120)
}


def get_quotas(tenant: str) -> Quotas:
    return TENANTS.get(tenant, TENANTS["public"])
