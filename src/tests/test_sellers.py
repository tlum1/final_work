import pytest
from fastapi import status
from sqlalchemy import select

from src.models import entities



# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(db_session, async_client):
    data = {"first_name": "vasya", "last_name": "pupkin", "email": "123@mail.com", "password": "awesome_paswd"}
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    all_sellers = await db_session.execute(select(entities.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 1


# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller1 = entities.Seller(id=1, first_name="Vasya", last_name="Onegin", email="123@email.com" , password="password123123")
    seller2 = entities.Seller(id=2, first_name="Petya", last_name="Pupkin", email="123@email.com" , password="password123123")


    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    # assert len(response.json()["books"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [{"id": seller1.id, "first_name": "Vasya", "last_name": "Onegin", "email": "123@email.com"},
                  {"id": seller2.id, "first_name": "Petya", "last_name": "Pupkin", "email": "123@email.com"},
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = entities.Seller(id=1, first_name="Vasya", last_name="Onegin", email="123@email.com" , password="password123123")
    db_session.add(seller)
    
    # добавим книги продавцу
    book = entities.Book(id=333, author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=1)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {"id": seller.id,
                               "first_name": "Vasya",
                               "last_name": "Onegin",
                               "email": "123@email.com",
                               "books": [{
                                    "id": 333,
                                    "author": "Pushkin",
                                    "title": "Eugeny Onegin",
                                    "year": 2001,
                                    "count_pages": 104
                                    }]
                               }

# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = entities.Seller(id=1, first_name="Vasya", last_name="Onegin", email="123@email.com," , password="password123123")

    db_session.add(seller)
    
    # добавим книги продавцу
    book = entities.Book(id=333, author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=1)

    db_session.add(book)

    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(entities.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0
    
    all_sellers = await db_session.execute(select(entities.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0
    
    all_seller_books = await db_session.execute(select(entities.Book).where(entities.Book.seller_id == seller.id))
    res = all_seller_books.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления продавца
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = entities.Seller(id=1, first_name="Vasya", last_name="Onegin", email="123@email.com" , password="password123123")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json={"first_name": "vasya", "last_name": "pupkin", "email": "123@mail.com", "id": seller.id},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(entities.Seller, seller.id)
    assert res.first_name == "vasya"
    assert res.last_name == "pupkin"
    assert res.email == "123@mail.com"
    assert res.id == seller.id
    
    
    
