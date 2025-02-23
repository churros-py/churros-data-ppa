import re
from sqlmodel import select
from typing import List, Generic, cast, Optional
from fastapi import HTTPException
from app.repository.base import T

class DynamicQueryMixin(Generic[T]):
    def _parse_method_name(self, method_name: str):
        pattern = r"find_by_(\w+)"
        match = re.match(pattern, method_name)
        if not match:
            raise HTTPException(status_code=400, detail=f"Invalid query method: '{method_name}'")
        return match.group(1).split("_")

    def _validate_field(self, field_name: str):
        if field_name not in ["and", "or"]:
            if not hasattr(self.model, field_name):
                raise HTTPException(
                    status_code=400,
                    detail=f"Field '{field_name}' does not exist in {self.model.__name__}"
                )

    def _extract_filters(self, field_parts: List[str], args: List):
        fields = []
        skip_keywords = ["and", "or", "order", "group", "limit"]
        for field in field_parts:
            if field in skip_keywords:
                continue
            self._validate_field(field)
            fields.append(field)
        if len(fields) != len(args):
            raise HTTPException(
                status_code=400,
                detail=f"Method expects {len(fields)} parameters, but got {len(args)}"
            )
        return [getattr(self.model, field) == value for field, value in zip(fields, args)]

    def _extract_group_by(self, field_parts: List[str]) -> Optional[str]:
        if "group" in field_parts and "by" in field_parts:
            idx = field_parts.index("group")
            if idx + 2 < len(field_parts) and field_parts[idx + 1] == "by":
                group_field = field_parts[idx + 2]
                self._validate_field(group_field)
                return group_field
        return None

    def _extract_order_by(self, field_parts: List[str]) -> Optional[str]:
        if "order" in field_parts and "by" in field_parts:
            idx = field_parts.index("order")
            if idx + 2 < len(field_parts) and field_parts[idx + 1] == "by":
                order_field = field_parts[idx + 2]
                self._validate_field(order_field)
                order_type = field_parts[idx + 3].upper() if (idx + 3 < len(field_parts) and field_parts[idx + 3] in ["asc", "desc"]) else "ASC"
                return f"{order_field} {order_type}"
        return None

    def _extract_limit(self, field_parts: List[str]) -> Optional[int]:
        if "limit" in field_parts:
            idx = field_parts.index("limit")
            if idx + 1 < len(field_parts):
                try:
                    return int(field_parts[idx + 1])
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid limit value: {field_parts[idx + 1]}")
        return None

    def _generate_query(self, method_name: str, *args) -> List[T]:
        try:
            field_parts = self._parse_method_name(method_name)
            filters = self._extract_filters(field_parts[:field_parts.index("group")] if "group" in field_parts else field_parts, list(args))
            order_by = self._extract_order_by(field_parts)
            group_by = self._extract_group_by(field_parts)
            limit = self._extract_limit(field_parts)

            query = select(self.model).where(*filters)

            if group_by:
                query = query.group_by(getattr(self.model, group_by))
            if order_by:
                order_attr = getattr(self.model, order_by.split()[0])
                query = query.order_by(order_attr.desc() if "DESC" in order_by else order_attr.asc())
            if limit:
                query = query.limit(limit)

            return cast(List[T], self.session.exec(query).all())

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    def __getattr__(self, name: str):
        if name.startswith("find_by_"):
            def method(*args):
                return self._generate_query(name, *args)
            return method
        raise HTTPException(status_code=400, detail=f"Invalid repository method: '{name}'")
