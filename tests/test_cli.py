from unittest.mock import Mock, patch
import requests
import cli

ITEM = {"id": 1, "product_name": "Nutella", "brands": "Ferrero", "barcode": "1",
        "price": 5.99, "stock": 20, "ingredients_text": "Sugar"}

def resp(status, data = None, message = "OK"):
    mock = Mock(status_code = status, content = b"x" if status != 204 else b"")
    mock.json.return_value = {"success": status < 400, "message": message, "data": data}
    return mock

@patch("cli.requests.get")
def test_view_all(mock_get, capsys):
    mock_get.return_value = resp(200, [ITEM])
    cli.view_all()
    assert "Nutella" in capsys.readouterr().out

@patch("cli.requests.get", side_effect = requests.ConnectionError("refused"))
def test_view_all_api_down(mock_get, capsys):
    cli.view_all()
    assert "Could not reach the API" in capsys.readouterr().out

@patch("builtins.input", side_effect = ["1"])
@patch("cli.requests.get")
def test_view_one(mock_get, mock_input, capsys):
    mock_get.return_value = resp(200, ITEM)
    cli.view_one()
    assert "Sugar" in capsys.readouterr().out

@patch("builtins.input", side_effect = ["99"])
@patch("cli.requests.get")
def test_view_one_not_found(mock_get, mock_input, capsys):
    mock_get.return_value = resp(404, message = "Item not found")
    cli.view_one()
    assert "Item not found" in capsys.readouterr().out

@patch("builtins.input", side_effect = ["Milk", "Brand", "123", "abc", "2.5", "x", "4"])
@patch("cli.requests.post")
def test_add_item_retries_invalid_numbers(mock_post, mock_input, capsys):
    mock_post.return_value = resp(201, ITEM)
    cli.add_item()
    sent = mock_post.call_args.kwargs["json"]
    assert sent["price"] == 2.5 and sent["stock"] == 4
    assert "valid" in capsys.readouterr().out

@patch("builtins.input", side_effect = [""])
@patch("cli.requests.post")
def test_add_item_empty_name(mock_post, mock_input):
    cli.add_item()
    mock_post.assert_not_called()

@patch("builtins.input", side_effect = ["1", "9.99", "7"])
@patch("cli.requests.patch")
def test_update_item(mock_patch, mock_input):
    mock_patch.return_value = resp(200, ITEM)
    cli.update_item()
    assert mock_patch.call_args.kwargs["json"] == {"price": 9.99, "stock": 7}

@patch("builtins.input", side_effect = ["1", "abc", ""])
@patch("cli.requests.patch")
def test_update_item_invalid_number(mock_patch, mock_input, capsys):
    cli.update_item()
    mock_patch.assert_not_called()
    assert "Invalid" in capsys.readouterr().out

@patch("builtins.input", side_effect = ["1"])
@patch("cli.requests.delete")
def test_delete_item(mock_delete, mock_input, capsys):
    mock_delete.return_value = resp(204)
    cli.delete_item()
    assert "deleted" in capsys.readouterr().out

@patch("builtins.input", side_effect = ["b", "123", "y", "3.5", "10"])
@patch("cli.requests.post")
@patch("cli.requests.get")
def test_find_by_barcode_and_import(mock_get, mock_post, mock_input, capsys):
    mock_get.return_value = resp(200, {"product_name": "Almond Milk", "brands": "Silk"})
    mock_post.return_value = resp(201, ITEM)
    cli.find_on_api()
    assert mock_post.call_args.args[0].endswith("/inventory/import/123")
    assert "Imported" in capsys.readouterr().out

@patch("builtins.input", side_effect = ["n", "milk"])
@patch("cli.requests.get")
def test_find_by_name(mock_get, mock_input, capsys):
    mock_get.return_value = resp(200, [{"product_name": "Milk", "brands": "X", "barcode": "5"}])
    cli.find_on_api()
    assert "barcode: 5" in capsys.readouterr().out

@patch("builtins.input", side_effect = ["b", "000"])
@patch("cli.requests.get")
def test_find_api_failure(mock_get, mock_input, capsys):
    mock_get.return_value = resp(502, message = "External API failure")
    cli.find_on_api()
    assert "502" in capsys.readouterr().out

@patch("builtins.input", side_effect = ["9", "0"])
def test_main_invalid_then_quit(mock_input, capsys):
    cli.main()
    output = capsys.readouterr().out
    assert "Invalid choice" in output and "Goodbye" in output