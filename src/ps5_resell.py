PS5_TRADE_IN_PRICES = {
    "PlayStation 5 Disc Edition": 260,
    "PlayStation 5 Digital Edition": 220,
    "PlayStation 5 Slim Disc Edition": 300,
    "PlayStation 5 Slim Digital Edition": 260,
    "PlayStation 5 Pro": 500,
}

EXTRA_CONTROLLER_VALUE = 30


def get_ps5_resell_price(edition, controller_count):
    base_price = PS5_TRADE_IN_PRICES.get(edition)

    if base_price is None:
        return None

    extra_controllers = max(0, controller_count - 1)
    controller_bonus = extra_controllers * EXTRA_CONTROLLER_VALUE

    return {
        "base": base_price,
        "controller_bonus": controller_bonus,
        "total": base_price + controller_bonus,
    }