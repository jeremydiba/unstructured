import json

from unstructured.ingest.connector.local import LocalIngestDoc, SimpleLocalConfig
from unstructured.ingest.connector.registry import (
    create_ingest_doc_from_dict,
    create_ingest_doc_from_json,
)
from unstructured.ingest.interfaces import ProcessorConfig, ReadConfig

doc = LocalIngestDoc(
    path="test_unstructured_ingest/example-docs/layout-parser-paper.pdf",
    connector_config=SimpleLocalConfig(input_path="test_unstructured_ingest/example-docs/"),
    processor_config=ProcessorConfig(),
    read_config=ReadConfig(),
)
source_meta = doc.source_metadata
serialized_json = doc.to_json()


def test_manual_deserialization():
    deserialized_doc = LocalIngestDoc.from_json(serialized_json)
    assert source_meta == deserialized_doc.source_metadata


def test_registry_from_json():
    deserialized_doc = create_ingest_doc_from_json(serialized_json)
    assert source_meta == deserialized_doc.source_metadata


def test_registry_from_dict():
    serialized_dict: dict = json.loads(serialized_json)
    deserialized_doc = create_ingest_doc_from_dict(serialized_dict)
    assert source_meta == deserialized_doc.source_metadata
