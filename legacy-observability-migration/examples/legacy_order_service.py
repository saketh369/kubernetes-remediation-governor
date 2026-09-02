"""A small sample 'legacy' module used by docs/examples to demonstrate
scanning and instrumentation. Not part of the package itself."""


def get_config_value(key):
    return {"timeout": 30}.get(key)


def process_order(order_id, items):
    if not items:
        raise ValueError("order has no items")
    total = 0
    for item in items:
        if item.get("price") is None:
            continue
        total += item["price"]
    return {"order_id": order_id, "total": total}


def notify_customer(order_id, email):
    # legacy side effect: sends an email via some external system
    print(f"Notifying {email} about order {order_id}")
