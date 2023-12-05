<h1 align="center">Простая ORM модель</h1>
Тестовое задание:</br>
Написать очень простую django-подобную ORM модель на python.
Спроектировать архитектуру решения так, чтобы в дальнейшем его можно было легко расширять (например, использовать различные базы данных, добавлять новые типы полей).
Использовать сторонние библиотеки, реализующие ORM-модели нельзя.

# Установка
### 1. Клонируйте репозиторий
```bash
git clone https://github.com/ragimov700/irs_test.git
```
### 2. Перейдите в папку с проектом
```bash
cd irs_test
```
# Примеры использования
### Создание таблицы:
```python
class SomeTable(OrmModel):
    pk = OrmInteger(primary_key=True)
    field_1 = OrmText()
    field_2 = OrmInteger()
    field_3 = OrmFloat()
```
### Создание записи в таблице:
```python
new_record = SomeTable(field_1='text', field_2=42, field_3=34.5)
new_record.save()
```
### Получение всех записей из таблицы:
```python
all_records = SomeTable.all()
print(all_records)
```
### Фильтрация записей:
```python
filtered_records = SomeTable.filter(field_1='text')
print(filtered_records)
```
---
<h5 align="center">Автор: <a href="https://github.com/ragimov700">Sherif Ragimov</a></h5>
