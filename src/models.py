import os
import csv
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Optional
from pydantic import BaseModel


# Перечисление статусов автомобиля    
class CarStatus(StrEnum):
    available = "available"
    reserve = "reserve"
    sold = "sold"
    delivery = "delivery"

# Класс, представляющий автомобиль
class Car(BaseModel):
    vin: str
    model: int
    price: Decimal
    date_start:  Optional[datetime]
    status: CarStatus
    is_deleted: bool = False

    def index(self) -> str:
        return self.vin

    def to_string(self) -> str:
        return f"{self.vin},{self.model},{self.price},{self.date_start.isoformat()},{self.status},{int(self.is_deleted)}"

# Класс, представляющий модель автомобиля
class Model(BaseModel):
    id: int
    name: str
    brand: str

    def index(self) -> str:
        return str(self.id)

# Класс, представляющий продажу автомобиля
class Sale(BaseModel):
    sales_number: str
    car_vin: str
    sales_date:  Optional[datetime]
    cost: Decimal
    is_deleted: bool = False

    def index(self) -> str:
        return self.car_vin
    
    def to_string(self) -> str:
        return f"{self.sales_number},{self.car_vin},{self.sales_date.isoformat()},{self.cost},{int(self.is_deleted)}"

# Класс, представляющий полную информацию о автомобиле
class CarFullInfo(BaseModel):
    vin: str
    car_model_name: str
    car_model_brand: str
    price: Decimal
    date_start: Optional[datetime] = None
    status: CarStatus
    sales_date: Optional[datetime] = None
    sales_cost: Optional[Decimal] = None

# Класс, представляющий статистику продаж по модели
class ModelSaleStats(BaseModel):
    car_model_name: str
    brand: str
    sales_number: int
