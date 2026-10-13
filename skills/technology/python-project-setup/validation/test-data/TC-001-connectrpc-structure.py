# TC-001: ConnectRPC Enterprise Project Structure Fixture
# Recognizes buf.yaml, backend/proto/, backend/src/[project]/api/gen/, tests/, and uv.lock

CONNECTRPC_MANIFEST_EVIDENCE = """
# backend/buf.yaml
version: v1
name: buf.build/org/my-service
deps:
  - buf.build/connectrpc/elixir
"""

class ConnectRPCProjectDetector:
    def __init__(self, file_tree: list[str]):
        self.file_tree = file_tree

    def is_connectrpc_template(self) -> bool:
        # Detects schema-first ConnectRPC structure
        required = [
            "backend/buf.yaml",
            "backend/proto/service/v1/service.proto",
            "backend/src/service/api/gen/service_pb2.py",
            "backend/uv.lock",
            "tests/conftest.py"
        ]
        return all(path in self.file_tree for path in required)

