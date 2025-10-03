# ADR-008: Mock-Based Testing Strategy

## Status
**Accepted** - 2025-01-24

## Context
Testing an MCP server that integrates with external APIs (Maven Central) presents challenges. We needed a testing strategy that provides fast, reliable tests while ensuring good coverage. The choice was between integration tests with real APIs, mock-based unit tests, or a hybrid approach.

## Decision
Use **comprehensive mock-based testing** for all external service calls.

## Rationale
1. **No Network Dependencies**: Tests run offline and in CI/CD environments
2. **Fast Execution**: Full test suite runs in under 5 seconds
3. **Deterministic Results**: No flaky tests due to network issues
4. **Edge Case Testing**: Can simulate errors and unusual responses
5. **Cost-Free**: No API rate limiting or usage concerns

## Testing Patterns

### 1. Service Mocking
```python
@patch.object(MavenApiService, 'check_version_exists')
@patch.object(MavenApiService, 'search_versions')
def test_check_version_success(mock_search, mock_exists):
    # Arrange
    mock_exists.return_value = True
    mock_search.return_value = ["1.0.0", "1.0.1", "1.1.0", "2.0.0"]
    
    # Act
    result = check_version("com.example:lib", "1.0.0")
    
    # Assert
    assert result["status"] == "success"
    assert result["result"]["exists"] is True
    assert result["result"]["latest_versions"]["major"] == "2.0.0"
    
    # Verify mock calls
    mock_exists.assert_called_once_with("com.example", "lib", "1.0.0", "jar", None)
```

### 2. Error Simulation
```python
def test_maven_api_timeout():
    with patch.object(MavenApiService, 'get_metadata') as mock:
        mock.side_effect = requests.Timeout("Connection timeout")
        
        result = check_version("com.example:lib", "1.0.0")
        
        assert result["status"] == "error"
        assert result["error"]["code"] == "MAVEN_API_ERROR"
        assert "timeout" in result["error"]["message"].lower()
```

### 3. Test Data Fixtures
```python
@pytest.fixture
def sample_metadata_xml():
    """Real Maven metadata structure for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <metadata>
        <groupId>com.example</groupId>
        <artifactId>library</artifactId>
        <versioning>
            <versions>
                <version>1.0.0</version>
                <version>1.0.1</version>
                <version>1.1.0</version>
            </versions>
        </versioning>
    </metadata>"""
```

## Test Organization
```
tests/
├── services/           # Service layer unit tests
│   ├── test_cache.py       # CacheService tests
│   ├── test_maven_api.py   # MavenApiService tests
│   └── test_version.py     # VersionService tests
├── shared/            # Shared utilities tests
│   └── test_utils.py       # Validation, formatting tests
├── tools/             # Tool integration tests
│   ├── test_check_version.py
│   └── test_check_version_batch.py
└── resources/         # Test data files
    └── test-pom-files.xml
```

## Mock Boundaries
1. **Mock at Service Boundaries**: Mock service methods, not internal implementations
2. **Don't Mock Business Logic**: Version parsing, comparison logic tested directly
3. **Mock External I/O**: HTTP requests, file system, subprocess calls
4. **Use Real Data Models**: Pydantic models used as-is, not mocked

## Alternatives Considered
1. **Integration Tests with Real APIs**
   - **Pros**: Tests real behavior, catches API changes
   - **Cons**: Slow, network-dependent, flaky, rate limits
   - **Decision**: Rejected for primary testing, kept for smoke tests

2. **Hybrid Approach**
   - **Pros**: Balance of speed and realism
   - **Cons**: Complex test setup, maintenance burden
   - **Decision**: Rejected in favor of simplicity

3. **Contract Testing**
   - **Pros**: Validates API contracts
   - **Cons**: Complex setup, Maven Central doesn't provide contracts
   - **Decision**: Rejected due to lack of upstream support

## Consequences
**Positive:**
- Tests run in <5 seconds total
- 100% deterministic results
- Can test error conditions easily
- No external dependencies
- Works in any environment

**Negative:**
- May miss real API changes
- Mock maintenance burden
- Gap between tests and reality
- Need separate integration tests

## Success Criteria
- All tests run offline
- Full suite completes in <5 seconds
- No flaky tests
- >90% code coverage on business logic
- Easy to add new test cases