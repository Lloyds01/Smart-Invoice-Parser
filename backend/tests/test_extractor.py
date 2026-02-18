from app.parser.extractor import extract_items


def test_dash_price_paren_qty_format():
    content = "Sugar – Rs. 6,000 (50 kg)"
    items = extract_items(content)

    assert len(items) == 1
    item = items[0]
    assert item.product_name == "Sugar"
    assert item.quantity == 50
    assert item.unit == "kg"
    assert item.price == 6000
    assert item.price_type == "total"
    assert item.derived_unit_price == 120


def test_paren_qty_at_price_format():
    content = "Wheat Flour (10kg @ 950)"
    items = extract_items(content)

    assert len(items) == 1
    item = items[0]
    assert item.product_name == "Wheat Flour"
    assert item.quantity == 10
    assert item.unit == "kg"
    assert item.price == 950
    assert item.price_type == "unit"
    assert item.derived_unit_price is None


def test_qty_and_price_per_unit_format():
    content = "Cooking Oil: Qty 5 bottles Price 1200/bottle"
    items = extract_items(content)

    assert len(items) == 1
    item = items[0]
    assert item.product_name == "Cooking Oil"
    assert item.quantity == 5
    assert item.unit == "bottles"
    assert item.price == 1200
    assert item.price_type == "unit"


def test_ignores_noise_lines():
    content = """
    Invoice # INV-1001
    Address: Main Street
    Tax 17%
    """
    items = extract_items(content)
    assert items == []


def test_splits_semicolon_multi_item_line():
    content = "Rice - Rs. 3000 (25 kg); Milk: Qty 2 l Price 200/l"
    items = extract_items(content)

    assert len(items) == 2
    assert items[0].product_name == "Rice"
    assert items[1].product_name == "Milk"
