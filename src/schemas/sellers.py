from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from .books import ReturnedBookWithoutSellerID

__all__ = ["IncomingSeller", "ReturnedAllSellers", "ReturnedSeller", "BaseSeller"]


# Базовый класс "Продавца", содержащий поля, необходимы для создания объекта
class BasePostSeller(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    
    
class BaseSeller(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BasePostSeller):
    @field_validator("password")  # Валидатор, что длина пароля более 10-ти символов
    @staticmethod
    def validate_password(val: int):
        if len(val) <= 10:
            raise PydanticCustomError("Validation error", "Password too short!")
        return val


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):
    books: list[ReturnedBookWithoutSellerID]


# Класс для возврата массива объектов "Продавец"
class ReturnedAllSellers(BaseModel):
    sellers: list[BaseSeller]
