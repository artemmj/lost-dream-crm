from src.kafka.consumer import normalize_kafka_header


def test_normalize_kafka_header_accepts_bytes():
    assert normalize_kafka_header((b"event_type", b"customer.created.v1")) == "customer.created.v1"


def test_normalize_kafka_header_accepts_text():
    assert normalize_kafka_header(("event_type", "customer.updated.v1")) == "customer.updated.v1"
