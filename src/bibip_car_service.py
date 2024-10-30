import csv
import os
import re
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel, ValidationError
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


root_dir = r'D:\Dev\de-project-bibip\temdir'


# Определение индексов для моделей, автомобилей и продаж
class ModelIndex:
    def __init__(self, model_id: int, position_in_data_file: int):
        self.model_id = model_id
        self.position_in_data_file = position_in_data_file


class CarIndex:
    def __init__(self, car_id: str, position_in_data_file: int):
        self.car_id = car_id
        self.position_in_data_file = position_in_data_file


class SalesIndex:
    def __init__(self, sales_id: str, position_in_data_file: int):
        self.sale_id = sales_id
        self.position_in_data_file = position_in_data_file


# Основной класс CarService для обработки данных
class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        self.model_index: list[ModelIndex] = []
        self.car_index: list[CarIndex] = []
        self.sales_index: list[SalesIndex] = []
        self._initialize_indexes()      # Инициализация индексов при создании объекта

    def _initialize_indexes(self):      # Чтение и создание индексов моделей, автомобилей и продаж

        split_model_lines = self._read_file("models_index.txt")
        self.model_index = [ModelIndex(int(l[0]), int(l[1])) for l in split_model_lines]

        split_car_lines = self._read_file("cars_index.txt")
        self.car_index = [CarIndex(l[0], int(l[1])) for l in split_car_lines]

        split_sales_lines = self._read_file("sales_index.txt")
        self.sales_index = [SalesIndex(str(l[0]), int(l[1])) for l in split_sales_lines]

    def _format_path(self, filename: str) -> str:
        return os.path.join(self.root_directory_path, filename)

    def _read_file(self, filename: str) -> list[list[str]]:
        file_path = self._format_path(filename)
        if not os.path.exists(file_path):
            return []

        with open(file_path, "r") as f:
            lines = f.readlines()
            split_lines = [line.strip().split(",") for line in lines]
            return split_lines

#  Сохранение моделей. Добавление новой модели и обновление файла индексов
    def add_model(self, model: Model) -> Model:
        # Сохраняем новую модель в файл models.txt       
        with open(self._format_path("models.txt"), "a") as f:       
            str_model = f"{model.id},{model.name},{model.brand}".ljust(500)
            f.write(str_model + "\n")

        # Создаем и добавляем новый индекс модели в список индексов
        new_mi = ModelIndex(model.id, len(self.model_index))
        self.model_index.append(new_mi)
        
        # Сортируем индексы моделей по ID модели, чтобы обеспечить их упорядоченность
        self.model_index.sort(key=lambda x: x.model_id)

        # Сохраняем обновленный список индексов в файл models_index.txt
        with open(self._format_path("models_index.txt"), "w") as f:
            for current_mi in self.model_index:
                str_model = f"{current_mi.model_id},{current_mi.position_in_data_file}".ljust(50)
                f.write(str_model + "\n")

        return model

# Сохранение автомобилей. Добавление автомобилей и обновление файла индексов
    def add_car(self, car: Car) -> Car:

        with open(self._format_path("cars.txt"), "a") as f:     # Сохраняем новую машину в файл cars.txt
            str_car = f"{car.vin},{car.model},{car.price},{car.date_start},{car.status}".ljust(500)
            f.write(str_car + "\n")

        # Создаем и добавляем новый индекс модели в список индексов
        new_ci = CarIndex(car.vin, len(self.car_index))
        self.car_index.append(new_ci)
        self.car_index.sort(key=lambda x: x.car_id)

        # Сохраняем обновленный список индексов в файл cars_index.txt
        with open(self._format_path("cars_index.txt"), "w") as f:
            for current_ci in self.car_index:
                str_car = f"{current_ci.car_id},{current_ci.position_in_data_file}".ljust(50)
                f.write(str_car + "\n")

        return car

#  Сохранение продаж. Запись новой продажи и обновление индекса продаж
    def sell_car(self, sale: Sale) -> Car:
        #  Открываем файл sales.txt в режиме добавления, формируем строку из данных о продаже.
        with open(self._format_path("sales.txt"), "a") as f:    
            str_sales = f"{sale.sales_number},{sale.car_vin},{sale.sales_date},{sale.cost}".ljust(500)
            f.write(str_sales + "\n")

        # Обновление файла индексов продаж sales_index.txt
        new_si = SalesIndex(sale.sales_number, len(self.sales_index))
        self.sales_index.append(new_si)
        self.sales_index.sort(key=lambda x: x.sale_id)

        #  Обновление файла индексов продаж sales_index.txt и перезаписываем его актуальным списком индексов продаж.
        with open(self._format_path("sales_index.txt"), "w") as f:
            for current_si in self.sales_index:
                str_sales = f"{current_si.sale_id},{current_si.position_in_data_file}".ljust(50)
                f.write(str_sales + "\n")

        # Поиск машины по VIN
        car_position = next((ci.position_in_data_file for ci in self.car_index if ci.car_id == sale.car_vin), None)
        if car_position is None:
            raise ValueError(f"Машина с VIN {sale.car_vin} не найдена.")

        # Обновление статуса машины на "sold"
        with open(self._format_path("cars.txt"), "r+") as f:
            car_lines = f.readlines()
            car_data = car_lines[car_position].strip().split(",")
            car_data[4] = "sold"
            car_lines[car_position] = ",".join(car_data).ljust(500) + "\n"
            f.seek(0)
            f.writelines(car_lines)

        # Возвращаем объект машины с обновленным статусом "sold", чтобы подтвердить её продажу.
        return Car(
            vin=car_data[0],
            model=int(car_data[1]),
            price=Decimal(car_data[2]),
            date_start=datetime.fromisoformat(car_data[3]),
            status=CarStatus.sold
        )

# Функция get_cars предназначена для получения списка машин, которые соответствуют нужному статусу "доступные для продажи".
    def get_cars(self, status: CarStatus) -> list[Car]:

        available_cars = []     # Создание пустого списка для доступных машин

        # Попытка открыть файл с машинами в режиме "чтение":
        try:
            with open(self._format_path("cars.txt"), "r") as f:
                for line in f:      # Cтрока — это информация об одной машине
                    car_data = line.strip().split(",")
                    if car_data[4].strip() == status.value:     # Проверка статуса машины (это 5-й элемент car_data[4]) 
                        car = Car(      # Если статус совпал, создается объект Car с деталями
                            vin=car_data[0],
                            model=int(car_data[1]),
                            price=Decimal(car_data[2]),
                            date_start=datetime.fromisoformat(car_data[3]),
                            status=CarStatus(car_data[4].strip())
                        )

                        # Машина добавляется в available_cars
                        available_cars.append(car)      

        # Обработка ошибок       
        except Exception as e:      
            print(f"Ошибка при чтении файла: {e}")

        return available_cars

# Детальная информация об автомобилях
    def get_car_info(self, vin: str) -> CarFullInfo | None:

        car_info = None     # Поиск информации о машине в cars.txt:
        with open(self._format_path("cars.txt"), "r") as f:
            for line in f:
                car_data = line.strip().split(",")
                if car_data[0] == vin:
                    car_info = {
                        'vin': car_data[0],
                        'model': int(car_data[1]),
                        'price': Decimal(car_data[2]),
                        'date_start': datetime.fromisoformat(car_data[3]),
                        'status': car_data[4].strip(),
                    }
                    break
        if car_info is None:        # Если VIN не найден в cars.txt, функция сразу возвращает None
            return None

        model_info = None       # Поиск модели машины в models.txt
        with open(self._format_path("models.txt"), "r") as f:
            for line in f:
                model_data = line.strip().split(",")
                if int(model_data[0]) == car_info['model']:
                    model_info = {
                        'name': model_data[1],
                        'brand': model_data[2]
                    }
                    break
        if model_info is None:      # Если модель не найдена, функция вызывает ошибку.
            raise ValueError(f"Данные про машину{['model']} не найдены")

        sale_info = None        # Поиск данных о продаже машины в sales.txt
        with open(self._format_path("sales.txt"), "r") as f:
            for line in f:
                sale_data = line.strip().split(",")
                if sale_data[1] == vin:     # VIN совпадает, сохраняем sale_info.
                    sale_info = {
                        'sales_date': datetime.fromisoformat(sale_data[2]),
                        'cost': Decimal(sale_data[3]),
                    }
                    break

        result = CarFullInfo(       # Функция собирает всю информацию в единый объект CarFullInfo
            vin=car_info['vin'],
            car_model_name=model_info['name'],
            car_model_brand=model_info['brand'],
            price=car_info['price'],
            date_start=car_info['date_start'],
            status=car_info['status'],
            sales_date=sale_info['sales_date'] if sale_info else None,
            sales_cost=sale_info['cost'] if sale_info else None
        )

        return result

#  Oбновление VIN на новый VIN и переписывает файлы, чтобы сохранить изменения. 
    def update_vin(self, vin: str, new_vin: str) -> Car:

        car_position = None     # Поиск позиции машины по старому VIN в car_index
        for car_idx in self.car_index:
            if car_idx.car_id == vin:
                car_position = car_idx.position_in_data_file
                break
 
        with open(self._format_path("cars.txt"), "r") as f:     # Чтение всех строк из cars.txt для обновления VIN машины
            car_lines = f.readlines()

        car_data = car_lines[car_position].strip().split(",")   # Изменение VIN у найденной машины
        car_data[0] = new_vin       # Обновляем VIN на новый
        updated_car_line = ",".join(car_data).ljust(500) + "\n"
        car_lines[car_position] = updated_car_line

        for car_idx in self.car_index:      #  Обновление car_index с новым VIN
            if car_idx.car_id == vin:
                car_idx.car_id = new_vin
                break

        self.car_index.sort(key=lambda x: x.car_id)     # Перезапись файла car_index.txt с обновленным VIN
        with open(self._format_path("cars_index.txt"), "w") as f:
            for current_ci in self.car_index:
                str_car = f"{current_ci.car_id},{current_ci.position_in_data_file}".ljust(50)
                f.write(str_car + "\n")
 
        with open(self._format_path("cars.txt"), "w") as f:     # Перезапись файла cars.txt с обновленным VIN
            f.writelines(car_lines)
 
        return Car(     # Создание и возвращение обновленного объекта Car
            vin=str(car_data[0]),
            model=int(car_data[1]),
            price=Decimal(car_data[2]),
            date_start=datetime.fromisoformat(car_data[3]),
            status=CarStatus(car_data[4].strip())
        )            

# Удаление продажи автомобиля
    def revert_sale(self, sales_number: str) -> Car:

        sale_found = False      # Поиск записи продажи с заданным номером
        car_vin = None
        sales_lines = []

        with open(self._format_path("sales.txt"), "r") as f:        # Чтение файла sales.txt для поиска и удаления записи продажи
            for line in f:
                sale_data = line.strip().split(",")
                if sale_data[0] == sales_number:
                    sale_found = True
                    car_vin = sale_data[1]      # VIN автомобиля из найденной продажи
                    continue        # Пропускаем запись продажи, чтобы удалить её
                sales_lines.append(line.strip())
        if not sale_found:
            raise ValueError(f"Продажа с  номером {sales_number} не найдена.")

        car_position = None     # Поиск позиции автомобиля в car_index по VIN из продажи
        for car_idx in self.car_index:
            if car_idx.car_id == car_vin:
                car_position = car_idx.position_in_data_file
                break
        if car_position is None:
            raise ValueError(f"Машина с VIN {car_vin} не найдена.")
        with open(self._format_path("cars.txt"), "r") as f:     # Чтение файла cars.txt и изменение статуса автомобиля на "available"
            car_lines = f.readlines()

        car_data = car_lines[car_position].strip().split(",")
        car_data[4] = "available"       # Изменяем статус на доступный
        car_lines[car_position] = ",".join(car_data).ljust(500) + "\n"
        with open(self._format_path("sales.txt"), "w") as f:  # Перезапись файла sales.txt с удаленной записью продажи
            for line in sales_lines:
                f.write(line + "\n")
        with open(self._format_path("cars.txt"), "w") as f:     # Перезапись файла cars.txt с обновленным статусом автомобиля
            f.writelines(car_lines)

        return Car(     # Возврат обновленного объекта Car с изменённым статусом
            vin=str(car_data[0]),
            model=int(car_data[1]),
            price=Decimal(car_data[2]),
            date_start=datetime.fromisoformat(car_data[3]),
            status=CarStatus.available  # Установлен статус "available"
        )

# Перечень трех наиболее продаваемых моделей
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        # Словарь для подсчета продаж каждой модели
        sales_count = defaultdict(int)

        # Чтение файла продаж и подсчет количества продаж для каждой модели
        try:
            with open(self._format_path("sales.txt"), "r") as f:
                for line in f:
                    sale_data = line.strip().split(",")
                    car_vin = sale_data[1]

                    # Получаем информацию о машине по VIN
                    car_info = self.get_car_info(car_vin)  # Возвращает объект CarFullInfo

                    # Подсчитываем продажи для каждой модели
                    sales_count[car_info.car_model_name] += 1  # Используем имя модели в качестве ключа
        except Exception as e:
            print(f"Ошибка чтения файла sales: {e}")

        # Сортировка моделей по количеству продаж
        sorted_models = sorted(sales_count.items(), key=lambda item: (-item[1]))    # Сортировка по убыванию

        top_models = []     # Получение информации о лучших моделях
        try:
            with open(self._format_path("models.txt"), "r") as f:
                model_data_lines = f.readlines()

            for model_name, count in sorted_models[:3]:     # Получаем топ-3 модели
                model_info = None
                for line in model_data_lines:
                    model_data = line.strip().split(",")
                    if model_data[1] == model_name:     # Сравниваем имя модели
                        model_info = {
                            'brand': model_data[2]      # Предполагается, что бренд на третьем месте
                        }
                        break

                if model_info:
                    top_models.append(ModelSaleStats(
                        car_model_name=model_name,
                        brand=model_info['brand'],
                        sales_number=count
                    ))
        except ValidationError as e:
            print(f"Ошибка валидации для топ-моделей: {e}")
        except Exception as e:
            print(f"Ошибка обработки топ-моделей: {e}")

        return top_models
