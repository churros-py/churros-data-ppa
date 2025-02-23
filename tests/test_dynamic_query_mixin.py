import pytest
from fastapi import HTTPException
from sqlmodel import SQLModel, Field
from typing import List, Any
from pychurros.dynamic_query_mixin import DynamicQueryMixin

class Dummy(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str
    status: str
    category: str
    age: int

class FakeResult:
    def __init__(self, results: List[Any]):
        self._results = results
    def all(self) -> List[Any]:
        return self._results

class FakeSession:
    def __init__(self, results: List[Any] = None):
        self.results = results or []
    def exec(self, query: Any) -> FakeResult:
        return FakeResult(self.results)

class DummyRepository(DynamicQueryMixin[Dummy]):
    def __init__(self, session: FakeSession):
        self.session = session
        self.model = Dummy

def test_parse_method_name_valid():
    repo = DummyRepository(FakeSession())
    parts = repo._parse_method_name("find_by_name_and_email")
    assert parts == ["name", "and", "email"]

def test_parse_method_name_invalid():
    repo = DummyRepository(FakeSession())
    with pytest.raises(HTTPException) as excinfo:
        repo._parse_method_name("invalid_method")
    assert "Invalid query method" in str(excinfo.value.detail)

def test_validate_field_valid():
    repo = DummyRepository(FakeSession())
    repo._validate_field("name")

def test_validate_field_invalid():
    repo = DummyRepository(FakeSession())
    with pytest.raises(HTTPException) as excinfo:
        repo._validate_field("nonexistent")
    assert "does not exist" in str(excinfo.value.detail)

def test_extract_filters_success():
    repo = DummyRepository(FakeSession())
    parts = ["name", "and", "email"]
    filters = repo._extract_filters(parts, ["Alice", "alice@example.com"])
    assert len(filters) == 2

def test_extract_filters_mismatch():
    repo = DummyRepository(FakeSession())
    parts = ["name", "and", "email"]
    with pytest.raises(HTTPException) as excinfo:
        repo._extract_filters(parts, ["Alice"])
    assert "expects 2 parameters" in str(excinfo.value.detail)

def test_extract_order_by_with_direction():
    repo = DummyRepository(FakeSession())
    parts = ["name", "order", "by", "email", "desc"]
    order_by = repo._extract_order_by(parts)
    assert order_by == "email DESC"

def test_extract_order_by_default():
    repo = DummyRepository(FakeSession())
    parts = ["name", "order", "by", "email"]
    order_by = repo._extract_order_by(parts)
    assert order_by == "email ASC"

def test_extract_group_by():
    repo = DummyRepository(FakeSession())
    parts = ["status", "group", "by", "category"]
    group_by = repo._extract_group_by(parts)
    assert group_by == "category"

def test_extract_limit_success():
    repo = DummyRepository(FakeSession())
    parts = ["age", "limit", "5"]
    limit = repo._extract_limit(parts)
    assert limit == 5

def test_extract_limit_invalid():
    repo = DummyRepository(FakeSession())
    parts = ["age", "limit", "xyz"]
    with pytest.raises(HTTPException) as excinfo:
        repo._extract_limit(parts)
    assert "Invalid limit value" in str(excinfo.value.detail)

def test_generate_query_success():
    fake_results = [{"id": 1, "name": "Alice", "email": "alice@example.com", "status": "Active", "category": "A", "age": 30}]
    session = FakeSession(results=fake_results)
    repo = DummyRepository(session)

    result = repo._generate_query("find_by_name_and_email", "Alice", "alice@example.com")
    assert result == fake_results

def test_generate_query_with_group_order_limit():
    fake_results = [{"id": 2, "name": "Bob", "email": "bob@example.com", "status": "Active", "category": "B", "age": 25}]
    session = FakeSession(results=fake_results)
    repo = DummyRepository(session)

    result = repo._generate_query("find_by_status_group_by_category_order_by_age_desc_limit_10", "Active")
    assert result == fake_results

def test_getattr_dynamic_method():
    fake_results = [{"id": 1, "name": "Alice", "email": "alice@example.com", "status": "Active", "category": "A", "age": 30}]
    session = FakeSession(results=fake_results)
    repo = DummyRepository(session)
    dynamic_method = getattr(repo, "find_by_name_and_email")
    result = dynamic_method("Alice", "alice@example.com")
    assert result == fake_results

def test_getattr_invalid_method():
    repo = DummyRepository(FakeSession())
    with pytest.raises(HTTPException) as excinfo:
        getattr(repo, "invalid_method")
    assert "Invalid repository method" in str(excinfo.value.detail)

def test_invalid_field_in_query():
    repo = DummyRepository(FakeSession())
    with pytest.raises(HTTPException) as excinfo:
        repo._generate_query("find_by_nonexistent", "value")

    assert "Field 'nonexistent' does not exist" in str(excinfo.value.detail)
