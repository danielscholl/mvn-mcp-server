"""Data types for Maven MCP Server.

This module contains Pydantic models for request validation and response formatting.
"""

from enum import Enum
from typing import List
from pydantic import BaseModel, Field, field_validator


class ErrorCode(str, Enum):
    """Error codes for Maven tools."""
    
    INVALID_INPUT_FORMAT = "INVALID_INPUT_FORMAT"
    INVALID_TARGET_COMPONENT = "INVALID_TARGET_COMPONENT"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    DEPENDENCY_NOT_FOUND = "DEPENDENCY_NOT_FOUND"
    VERSION_NOT_FOUND = "VERSION_NOT_FOUND"
    MAVEN_API_ERROR = "MAVEN_API_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


class MavenVersionCheckRequest(BaseModel):
    """Request model for checking Maven version existence."""
    
    dependency: str = Field(description="Maven dependency in groupId:artifactId format")
    version: str = Field(description="Version string to check")
    packaging: str = Field(default="jar", description="Package type (jar, war, etc.)")
    classifier: str | None = Field(default=None, description="Optional classifier")
    
    @field_validator("dependency")
    @classmethod
    def validate_dependency(cls, v: str) -> str:
        """Validate the dependency format (groupId:artifactId)."""
        if not v or not isinstance(v, str):
            raise ValueError("Dependency cannot be empty")
        
        # Check for groupId:artifactId format
        if ":" not in v or v.count(":") != 1:
            raise ValueError("Dependency must be in groupId:artifactId format")
        
        return v
    
    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate the version string."""
        if not v or not isinstance(v, str):
            raise ValueError("Version cannot be empty")
        return v


class MavenLatestVersionRequest(BaseModel):
    """Request model for getting latest Maven version."""
    
    dependency: str = Field(description="Maven dependency in groupId:artifactId format")
    packaging: str = Field(default="jar", description="Package type (jar, war, etc.)")
    classifier: str | None = Field(default=None, description="Optional classifier")
    
    @field_validator("dependency")
    @classmethod
    def validate_dependency(cls, v: str) -> str:
        """Validate the dependency format (groupId:artifactId)."""
        if not v or not isinstance(v, str):
            raise ValueError("Dependency cannot be empty")
        
        # Check for groupId:artifactId format
        if ":" not in v or v.count(":") != 1:
            raise ValueError("Dependency must be in groupId:artifactId format")
        
        return v


class MavenLatestComponentVersionRequest(BaseModel):
    """Request model for finding latest component version."""
    
    dependency: str = Field(description="Maven dependency in groupId:artifactId format")
    version: str = Field(description="Version string to use as reference")
    target_component: str = Field(description="Component to find the latest version for ('major', 'minor', or 'patch')")
    packaging: str = Field(default="jar", description="Package type (jar, war, etc.)")
    classifier: str | None = Field(default=None, description="Optional classifier")
    
    @field_validator("dependency")
    @classmethod
    def validate_dependency(cls, v: str) -> str:
        """Validate the dependency format (groupId:artifactId)."""
        if not v or not isinstance(v, str):
            raise ValueError("Dependency cannot be empty")
        
        # Check for groupId:artifactId format
        if ":" not in v or v.count(":") != 1:
            raise ValueError("Dependency must be in groupId:artifactId format")
        
        return v
    
    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate the version string."""
        if not v or not isinstance(v, str):
            raise ValueError("Version cannot be empty")
        return v
    
    @field_validator("target_component")
    @classmethod
    def validate_target_component(cls, v: str) -> str:
        """Validate the target component."""
        if v not in ["major", "minor", "patch"]:
            raise ValueError("Target component must be one of 'major', 'minor', or 'patch'")
        return v


class MavenEnhancedVersionCheckRequest(BaseModel):
    """Request model for enhanced version checking with all version updates."""
    
    dependency: str = Field(description="Maven dependency in groupId:artifactId format")
    version: str = Field(description="Version string to check and use as reference")
    packaging: str = Field(default="jar", description="Package type (jar, war, etc.)")
    classifier: str | None = Field(default=None, description="Optional classifier")
    
    @field_validator("dependency")
    @classmethod
    def validate_dependency(cls, v: str) -> str:
        """Validate the dependency format (groupId:artifactId)."""
        if not v or not isinstance(v, str):
            raise ValueError("Dependency cannot be empty")
        
        # Check for groupId:artifactId format
        if ":" not in v or v.count(":") != 1:
            raise ValueError("Dependency must be in groupId:artifactId format")
        
        return v
    
    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate the version string."""
        if not v or not isinstance(v, str):
            raise ValueError("Version cannot be empty")
        return v


class MavenDependencyItem(BaseModel):
    """Model for a single Maven dependency item in a batch request."""
    
    dependency: str = Field(description="Maven dependency in groupId:artifactId format")
    version: str = Field(description="Version string to check and use as reference")
    packaging: str = Field(default="jar", description="Package type (jar, war, etc.)")
    classifier: str | None = Field(default=None, description="Optional classifier")
    
    @field_validator("dependency")
    @classmethod
    def validate_dependency(cls, v: str) -> str:
        """Validate the dependency format (groupId:artifactId)."""
        if not v or not isinstance(v, str):
            raise ValueError("Dependency cannot be empty")
        
        # Check for groupId:artifactId format
        if ":" not in v or v.count(":") != 1:
            raise ValueError("Dependency must be in groupId:artifactId format")
        
        return v
    
    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate the version string."""
        if not v or not isinstance(v, str):
            raise ValueError("Version cannot be empty")
        return v


class MavenBatchVersionCheckRequest(BaseModel):
    """Request model for batch version checking with all version updates."""
    
    dependencies: List[MavenDependencyItem] = Field(description="List of Maven dependencies to check")
    
    @field_validator("dependencies")
    @classmethod
    def validate_dependencies(cls, v: List[MavenDependencyItem]) -> List[MavenDependencyItem]:
        """Validate the dependencies list."""
        if not v or len(v) == 0:
            raise ValueError("At least one dependency is required")
        return v