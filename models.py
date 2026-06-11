from sqlalchemy import String, Text, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    def __repr__(self):
        return f'Имя: {self.name}'


class Address(Base):
    __tablename__ = 'address'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped['User'] = mapped_column(ForeignKey('user.id'))
    city: Mapped[str] = mapped_column(String(30), nullable=True)
    email_address: Mapped[str] = mapped_column(String(50), nullable=True)

    def __repr__(self):
        return f'Город: {self.city}'

    
class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    
    def __repr__(self):
        return f'Название: {self.name}'
    

class Item(Base):
    __tablename__ = 'item'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    category_id: Mapped['Category'] = mapped_column(ForeignKey('category.id'))
    description: Mapped[str] = mapped_column(Text(300))
    price: Mapped[float] = mapped_column(Float)
    discount_price: Mapped[float] = mapped_column(Float, nullable=True)

    def __repr__(self):
        return f'Название: {self.name}'
