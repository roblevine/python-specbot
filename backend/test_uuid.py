import uuid

# Test the UUID from the fixtures
test_uuid = "a1b2c3d4-5678-90ab-cdef-123456789abc"
print(f"Test UUID: {test_uuid}")

# Try to parse it as UUID
try:
    parsed = uuid.UUID(test_uuid)
    print(f"Parsed UUID: {parsed}")
    print(f"Version: {parsed.version}")
except Exception as e:
    print(f"Error: {e}")

# Generate a valid UUID v4
valid_uuid = str(uuid.uuid4())
print(f"Valid UUIDv4: {valid_uuid}")
