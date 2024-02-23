from typing import Annotated

from fastapi import APIRouter, Depends, Response, status, HTTPException
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.entities import Seller, Book
from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSeller, BaseSeller


sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о продавце в БД.
@sellers_router.post("/", status_code=status.HTTP_201_CREATED)  # Прописываем модель ответа
async def create_book(
    seller: IncomingSeller, session: DBSession
):  # прописываем модель валидирующую входные данные и сессию как зависимость.
    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    new_book = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=seller.password,
    )
    session.add(new_book)
    await session.flush()


# Ручка, возвращающая всех продавцов
@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {"sellers": sellers}


# Ручка для получения продавца по его ИД
@sellers_router.get("/{seller_id}", response_model=ReturnedSeller)
async def get_seller(seller_id: int, session: DBSession):
    seller = await session.get(Seller, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    query = select(Book).where(Book.seller_id == seller_id)
    res = await session.execute(query)
    books = res.scalars().all()
    
    return {
        "id": seller.id,
        "first_name": seller.first_name,
        "last_name": seller.last_name,
        "email": seller.email,
        "books": books        
    }
    


# Ручка для удаления книги
@sellers_router.delete("/{seller_id}")
async def delete_book(seller_id: int, session: DBSession):
    deleted_book = await session.get(Seller, seller_id)
    ic(deleted_book)  # Красивая и информативная замена для print. Полезна при отладке.
    if deleted_book:
        await session.delete(deleted_book)

    return Response(status_code=status.HTTP_204_NO_CONTENT)  # Response может вернуть текст и метаданные.


# Ручка для обновления данных о продавце
@sellers_router.put("/{seller_id}", response_model=BaseSeller)
async def update_seller(seller_id: int, new_data: BaseSeller, session: DBSession):
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.email

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)
