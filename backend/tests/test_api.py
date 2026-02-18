from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_parse_endpoint_still_works():
    payload = {'content': 'Sugar – Rs. 6,000 (50 kg)'}
    response = client.post('/parse', json=payload)

    assert response.status_code == 200
    body = response.json()
    assert 'request_id' in body
    assert body['results'][0]['items'][0]['product_name'] == 'Sugar'


def test_parse_image_rejects_unsupported_content_type():
    response = client.post(
        '/parse-image',
        files={'file': ('invoice.txt', b'not an image', 'text/plain')},
    )
    assert response.status_code in {415, 503}


def test_export_xlsx_returns_binary_workbook():
    payload = {
        'results': [
            {
                'input_index': 0,
                'items': [
                    {
                        'product_name': 'Sugar',
                        'quantity': 50,
                        'unit': 'kg',
                        'price': 6000,
                        'price_type': 'total',
                        'derived_unit_price': 120,
                        'raw_line': 'Sugar – Rs. 6,000 (50 kg)',
                        'confidence': 1.0,
                    }
                ],
            }
        ]
    }
    response = client.post('/export/xlsx', json=payload)

    assert response.status_code == 200
    assert response.headers['content-type'].startswith(
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    assert response.content[:2] == b'PK'
