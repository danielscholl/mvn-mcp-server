# ADR-004: Direct Maven Central HTTP Integration

## Status
**Accepted** - 2025-01-24

## Context
To check Maven dependency versions and retrieve artifact information, we needed to integrate with Maven Central repository. The choice was between using existing Maven libraries (which require JVM) or implementing direct HTTP integration.

## Decision
Implement **direct HTTP integration** with Maven Central APIs using Python's `requests` library.

## Rationale
1. **No JVM Dependency**: Pure Python solution without Java/Maven installation requirements
2. **Full Control**: Complete control over caching, retries, and error handling
3. **Lightweight**: Just HTTP calls, no heavy Maven machinery
4. **Dual API Strategy**: Can use both metadata XML and Solr JSON APIs
5. **MCP Alignment**: Better suited for lightweight MCP server deployment

## Alternatives Considered
1. **Maven Libraries (via Py4J or subprocess)**
   - **Pros**: Official implementation, handles edge cases, full Maven features
   - **Cons**: Requires JVM, heavyweight, subprocess complexity, harder to deploy
   - **Decision**: Rejected due to deployment complexity and resource requirements

2. **Third-party Python Libraries**
   - **Pros**: Some abstraction, potentially fewer bugs
   - **Cons**: Limited options, most are unmaintained, still do HTTP underneath
   - **Decision**: Rejected due to lack of quality options

## Implementation Approach

### 1. Metadata XML API
```python
def get_metadata(self, group_id: str, artifact_id: str) -> ElementTree:
    """Fetch maven-metadata.xml."""
    url = f"{self.metadata_base_url}/{group_path}/{artifact_id}/maven-metadata.xml"
    response = requests.get(url, timeout=self.timeout)
    response.raise_for_status()
    return ET.fromstring(response.content)
```

### 2. Solr Search API (Fallback)
```python
def search_versions(self, group_id: str, artifact_id: str) -> List[str]:
    """Search using Solr API when metadata unavailable."""
    params = {
        "q": f"g:{group_id} AND a:{artifact_id}",
        "core": "gav",
        "rows": "100",
        "wt": "json"
    }
    response = requests.get(self.search_base_url, params=params)
    return self._parse_search_response(response.json())
```

### 3. Artifact Existence Check
```python
def check_version_exists(self, group_id: str, artifact_id: str, version: str) -> bool:
    """Use HEAD request to check existence without downloading."""
    url = self._construct_artifact_url(group_id, artifact_id, version)
    response = requests.head(url, timeout=self.timeout)
    return response.status_code == 200
```

## API Endpoints Used
1. **Metadata**: `https://repo1.maven.org/maven2/{group_path}/{artifact}/maven-metadata.xml`
2. **Search**: `https://search.maven.org/solrsearch/select`
3. **Artifacts**: `https://repo1.maven.org/maven2/{group_path}/{artifact}/{version}/{artifact}-{version}.{ext}`

## Consequences
**Positive:**
- No JVM or Maven installation required
- Simple deployment as pure Python package
- Full control over HTTP behavior
- Efficient HEAD requests for existence checks
- Can optimize caching and retries

**Negative:**
- Must reimplement Maven coordinate parsing
- Need to handle Maven repository layout rules
- Potential for bugs in edge cases Maven handles
- Must track API changes ourselves

## Success Criteria
- Successfully resolve 99%+ of real-world Maven artifacts
- Handle both old and new Maven Central API formats
- Graceful fallback between metadata and search APIs
- Proper error messages for common failures