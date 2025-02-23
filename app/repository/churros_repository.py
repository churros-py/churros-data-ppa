from app.repository.base import BaseRepository, T
from app.repository.dynamic_query_mixin import DynamicQueryMixin

class ChurrosRepository(BaseRepository[T], DynamicQueryMixin[T]):
    pass
