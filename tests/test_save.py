from app.ppa_repository import AbstractPersistable


class User:
    name: str

    def __init__(self, name: str) -> None:
        self.name = name


class UserRepository(AbstractPersistable[User]):
    pass


def test_should_save_entity():
    repository = UserRepository()
    user = User("Gustavo Valle")
    saved_user = repository.save(user)
    assert saved_user.name == user.name
    assert saved_user.id is not None
