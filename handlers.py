from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.urls import UrlsModel

router = APIRouter()


@router.post("/shorten", response_model=dict)
async def shorten(url: str, session: AsyncSession = Depends(get_db)):
    try:
        new_url = UrlsModel(url=url)
        session.add(new_url)
        await session.commit()
        await session.refresh(new_url)

        return {
            "id": new_url.id
        }

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных"
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{short_id}")
async def get_url(short_id: int, session: AsyncSession = Depends(get_db)):
    try:
        result = await session.execute(
            select(UrlsModel).where(UrlsModel.id == short_id)
        )
        url_model = result.scalar_one_or_none()

        if not url_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="URL не найден"
            )

        url_model.counter += 1
        await session.commit()

        return RedirectResponse(url=url_model.url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка базы данных"
        )


@router.get("/stats/{short_id}", response_model=dict)
async def get_stats(short_id: int, session: AsyncSession = Depends(get_db)):
    try:
        result = await session.execute(
            select(UrlsModel).where(UrlsModel.id == short_id)
        )
        url_model = result.scalar_one_or_none()

        if not url_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"URL не найден"
            )

        return {
            "counter": url_model.counter
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка базы данных"
        )
