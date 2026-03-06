from sqlalchemy.orm import Mapped, mapped_column
from database import BaseModel


class UrlsModel(BaseModel):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str]
    counter: Mapped[int] = mapped_column(default=0)
