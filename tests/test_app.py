"""
test_app.py - Comprehensive pytest test suite for FindIt College Lost & Found Portal.
Covers homepage, form validations, SQLite persistence, search, multi-filters,
recovery workflow, image upload security, and error handling.
"""

import io
import pytest
from database import (
    CATEGORIES,
    CAMPUS_LOCATIONS,
    insert_item,
    get_item_by_id,
    update_item_status,
)


def test_homepage_loads_successfully(client):
    """1. Test that the homepage loads with status code 200 and expected branding."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"FindIt" in response.data
    assert b"Recover Misplaced Belongings Across Campus" in response.data
    assert b"Lost Items" in response.data
    assert b"Found Items" in response.data
    assert b"Recovered" in response.data


def test_create_valid_lost_item_report(client):
    """2. Test creating a valid lost item report and redirecting to its detail view."""
    response = client.post(
        "/report/lost",
        data={
            "item_name": "Hydro Flask 750ml Blue",
            "category": "Water Bottles",
            "location": "Central Library",
            "item_date": "2026-10-20",
            "description": "Left on 2nd floor silent study table near window.",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Hydro Flask 750ml Blue" in response.data
    assert b"Central Library" in response.data
    assert b"Water Bottles" in response.data
    assert b"Lost Item" in response.data


def test_create_valid_found_item_report(client):
    """3. Test creating a valid found item report."""
    response = client.post(
        "/report/found",
        data={
            "item_name": "TI-84 Plus CE Graphing Calculator",
            "category": "Electronics",
            "location": "Science & Engineering Block",
            "item_date": "2026-10-19",
            "description": "Found on desk in Room 302 after calculus lecture.",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"TI-84 Plus CE Graphing Calculator" in response.data
    assert b"Found Item" in response.data
    assert b"Science &amp; Engineering Block" in response.data or b"Science & Engineering Block" in response.data


def test_required_fields_validation(client):
    """4. Test that missing required fields trigger validation errors (400 Bad Request)."""
    # Missing item_name
    r1 = client.post(
        "/report/lost",
        data={
            "item_name": "",
            "category": "Keys",
            "location": "Campus Ground & Parking",
            "item_date": "2026-10-20",
            "description": "Bike keys with red keychain.",
        },
    )
    assert r1.status_code == 400
    assert b"Item name is required." in r1.data

    # Missing location
    r2 = client.post(
        "/report/lost",
        data={
            "item_name": "Bike Keys",
            "category": "Keys",
            "location": "",
            "item_date": "2026-10-20",
            "description": "Bike keys with red keychain.",
        },
    )
    assert r2.status_code == 400
    assert b"Campus location is required." in r2.data

    # Missing description
    r3 = client.post(
        "/report/lost",
        data={
            "item_name": "Bike Keys",
            "category": "Keys",
            "location": "Campus Ground & Parking",
            "item_date": "2026-10-20",
            "description": "",
        },
    )
    assert r3.status_code == 400
    assert b"Description is required." in r3.data


def test_invalid_category_rejected(client):
    """5. Test that unsupported categories are rejected with validation error."""
    response = client.post(
        "/report/lost",
        data={
            "item_name": "Gold Watch",
            "category": "SuperFakeCategoryThatDoesNotExist",
            "location": "Auditorium",
            "item_date": "2026-10-20",
            "description": "Gold wrist watch left during assembly.",
        },
    )
    assert response.status_code == 400
    assert b"Please select a valid item category." in response.data


def test_search_partial_and_case_insensitive(client, app):
    """6. Test that search matches partial words and is case-insensitive."""
    with app.app_context():
        insert_item({
            "item_name": "Stainless Steel Milton Bottle",
            "category": "Water Bottles",
            "report_type": "Lost",
            "location": "Central Library",
            "item_date": "2026-10-20",
            "description": "Silver finish with scratch on base.",
            "status": "Lost",
        })
        insert_item({
            "item_name": "Black Leather Backpack",
            "category": "Bags",
            "report_type": "Found",
            "location": "Main Canteen / Cafeteria",
            "item_date": "2026-10-20",
            "description": "Contains notebook and stationery.",
            "status": "Found",
        })

    # Search for partial lowercase term 'milton'
    res_search1 = client.get("/items?q=milton")
    assert res_search1.status_code == 200
    assert b"Stainless Steel Milton Bottle" in res_search1.data
    assert b"Black Leather Backpack" not in res_search1.data

    # Search for term in description 'stationery'
    res_search2 = client.get("/items?q=stationery")
    assert res_search2.status_code == 200
    assert b"Black Leather Backpack" in res_search2.data
    assert b"Stainless Steel Milton Bottle" not in res_search2.data


def test_filters_return_correct_reports(client, app):
    """7. Test filtering by report type, category, location, and status."""
    with app.app_context():
        insert_item({
            "item_name": "College Student ID Card",
            "category": "ID Cards",
            "report_type": "Found",
            "location": "Computer Labs",
            "item_date": "2026-10-20",
            "description": "Found near workstation 14.",
            "status": "Found",
        })
        insert_item({
            "item_name": "Winter Navy Hoodie",
            "category": "Clothing",
            "report_type": "Lost",
            "location": "Sports Complex & Gym",
            "item_date": "2026-10-18",
            "description": "Left on spectator bench.",
            "status": "Lost",
        })

    # Filter by Category: ID Cards
    res_cat = client.get("/items?category=ID+Cards")
    assert b"College Student ID Card" in res_cat.data
    assert b"Winter Navy Hoodie" not in res_cat.data

    # Filter by Report Type: Lost
    res_type = client.get("/items?type=Lost")
    assert b"Winter Navy Hoodie" in res_type.data
    assert b"College Student ID Card" not in res_type.data

    # Filter by Location: Computer Labs
    res_loc = client.get("/items?location=Computer+Labs")
    assert b"College Student ID Card" in res_loc.data
    assert b"Winter Navy Hoodie" not in res_loc.data


def test_combined_search_and_filters(client, app):
    """8. Test combining keyword search and filters simultaneously."""
    with app.app_context():
        insert_item({
            "item_name": "Red Nike Backpack",
            "category": "Bags",
            "report_type": "Lost",
            "location": "Central Library",
            "item_date": "2026-10-20",
            "description": "Red backpack with laptop compartment.",
            "status": "Lost",
        })
        insert_item({
            "item_name": "Blue Adidas Backpack",
            "category": "Bags",
            "report_type": "Lost",
            "location": "Sports Complex & Gym",
            "item_date": "2026-10-20",
            "description": "Blue sports bag.",
            "status": "Lost",
        })

    # Combined: query 'Red' AND category 'Bags' AND location 'Central Library'
    res = client.get("/items?q=Red&category=Bags&location=Central+Library")
    assert res.status_code == 200
    assert b"Red Nike Backpack" in res.data
    assert b"Blue Adidas Backpack" not in res.data


def test_recovered_status_workflow(client, app):
    """9. Test updating item status to Recovered and preventing duplicate state transitions."""
    with app.app_context():
        item_id = insert_item({
            "item_name": "Wireless Noise Cancelling Earbuds",
            "category": "Electronics",
            "report_type": "Lost",
            "location": "Central Library",
            "item_date": "2026-10-18",
            "description": "Black charging case with stickers.",
            "status": "Lost",
        })

    # Update to Recovered via POST
    post_res = client.post(f"/items/{item_id}/recover", follow_redirects=True)
    assert post_res.status_code == 200
    assert b"marked as Recovered" in post_res.data
    assert b"This item is marked as Recovered!" in post_res.data

    # Verify status changed in database
    with app.app_context():
        item = get_item_by_id(item_id)
        assert item["status"] == "Recovered"

    # Attempting to recover again should be safely acknowledged
    repeat_res = client.post(f"/items/{item_id}/recover", follow_redirects=True)
    assert repeat_res.status_code == 200
    assert b"already been marked as Recovered" in repeat_res.data


def test_invalid_image_upload_rejected(client):
    """10. Test that unsafe/disallowed image formats (e.g. .exe, .sh, .py) are rejected."""
    fake_script = (io.BytesIO(b"print('malicious script')"), "payload.py")

    response = client.post(
        "/report/lost",
        data={
            "item_name": "Test Item With Bad File",
            "category": "Other",
            "location": "Main Canteen / Cafeteria",
            "item_date": "2026-10-20",
            "description": "Attempting invalid file extension upload.",
            "image": fake_script,
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert b"Unsupported image format" in response.data


def test_valid_image_upload_accepted(client):
    """11. Test that valid image upload (.png) is accepted, saved, and served securely."""
    # 1x1 transparent PNG file binary
    png_data = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    valid_file = (io.BytesIO(png_data), "photo.png")

    response = client.post(
        "/report/found",
        data={
            "item_name": "Spectacles with Black Frame",
            "category": "Other",
            "location": "Central Library",
            "item_date": "2026-10-20",
            "description": "Reading glasses with black frame and blue case.",
            "image": valid_file,
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Spectacles with Black Frame" in response.data
    assert b"/uploads/" in response.data


def test_nonexistent_item_returns_404(client):
    """12. Test that querying an invalid item ID returns a custom 404 page."""
    response = client.get("/items/99999")
    assert response.status_code == 404
    assert b"Report or Page Not Found" in response.data
    assert b"404" in response.data


def test_invalid_status_database_exception(app):
    """13. Test that update_item_status raises ValueError when given an invalid status."""
    with app.app_context():
        item_id = insert_item({
            "item_name": "Umbrella",
            "category": "Other",
            "report_type": "Lost",
            "location": "Auditorium",
            "item_date": "2026-10-20",
            "description": "Black folding umbrella.",
            "status": "Lost",
        })

        with pytest.raises(ValueError, match="Invalid status"):
            update_item_status(item_id, "NonExistentStatus")
