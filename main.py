import sqlite3


class OrmField:
    """
    Базовый класс для полей в ORM модели.

    Атрибуты:
        primary_key (bool): Определяет, является ли поле первичным ключом.
        sql_type (str): SQL тип поля в базе данных.
        expected_type (type): Ожидаемый тип данных поля в Python.
    """

    def __init__(self, primary_key=False, sql_type=None, expected_type=None):
        self.primary_key = primary_key
        self.sql_type = sql_type
        self.expected_type = expected_type


class OrmInteger(OrmField):
    """
    Класс поля для целочисленных значений. Наследуется от OrmField.
    """

    def __init__(self, primary_key=False):
        super().__init__(primary_key=primary_key, sql_type='INTEGER',
                         expected_type=int)


class OrmText(OrmField):
    """
    Класс поля для текстовых значений. Наследуется от OrmField.
    """

    def __init__(self, primary_key=False):
        super().__init__(primary_key=primary_key, sql_type='TEXT',
                         expected_type=str)


class OrmFloat(OrmField):
    """
    Класс поля для значений с плавающей точкой. Наследуется от OrmField.
    """

    def __init__(self, primary_key=False):
        super().__init__(primary_key=primary_key, sql_type='REAL',
                         expected_type=float)


class OrmModelMeta(type):
    """
    Метакласс для ORM моделей. Автоматически создает таблицы в базе данных
    в соответствии с определенными полями модели.

    Методы:
        _create_table(cls): Создает таблицу в базе данных для модели.
    """

    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)
        cls._fields = {k: v for k, v in dct.items() if isinstance(v, OrmField)}
        cls._table_name = name.lower()
        if name != 'OrmModel':
            cls._create_table(cls)
        return cls

    @staticmethod
    def _create_table(cls):
        with sqlite3.connect(cls._db_path) as conn:
            primary_key = None
            fields = []

            for field_name, field in cls._fields.items():
                field_definition = f"{field_name} {field.sql_type}"
                if field.primary_key:
                    if field.sql_type == 'INTEGER':
                        field_definition += ' PRIMARY KEY AUTOINCREMENT'
                    else:
                        field_definition += " PRIMARY KEY"
                    primary_key = field_name
                fields.append(field_definition)
            if not primary_key:
                fields.insert(0, "id INTEGER PRIMARY KEY AUTOINCREMENT")

            fields_sql = ", ".join(fields)

            sql = (f"CREATE TABLE IF NOT EXISTS "
                   f"{cls._table_name} ({fields_sql})")
            conn.execute(sql)
            conn.commit()


class OrmModel(metaclass=OrmModelMeta):
    """
    Базовый класс для ORM моделей.
    Использует OrmModelMeta в качестве метакласса.

    Методы:
        save(): Валидирует и сохраняет объект модели в базу данных.
        all(): Возвращает все записи из таблицы модели.
        filter(**kwargs): Фильтрует записи в таблице по заданным критериям.
    """
    _db_path = 'sqlite3.db'

    def __init__(self, **kwargs):
        for field_name in self._fields:
            setattr(self, field_name, kwargs.get(field_name))

    def save(self):
        with sqlite3.connect(self._db_path) as conn:
            fields_to_insert = {}
            for field_name in self._fields:
                field_value = getattr(self, field_name)
                field = self._fields[field_name]

                if not field.primary_key:
                    if not isinstance(field_value, field.expected_type):
                        raise TypeError(
                            f"Поле '{field_name}' должно "
                            f"соответствовать типу {field.expected_type}, "
                            f"получен {type(field_value)}."
                        )

                fields_to_insert[field_name] = field_value

            columns = ', '.join(fields_to_insert.keys())
            placeholders = ', '.join(['?'] * len(fields_to_insert))
            values = list(fields_to_insert.values())

            sql = (f"INSERT INTO {self._table_name} ({columns})"
                   f"VALUES ({placeholders})")
            conn.execute(sql, values)
            conn.commit()

    @classmethod
    def all(cls):
        with sqlite3.connect(cls._db_path) as conn:
            sql = f"SELECT * FROM {cls._table_name}"
            cursor = conn.execute(sql)
            return cursor.fetchall()

    @classmethod
    def filter(cls, **kwargs):
        with sqlite3.connect(cls._db_path) as conn:
            conditions = ' AND '.join([f"{k} = ?" for k in kwargs])
            sql = f"SELECT * FROM {cls._table_name} WHERE {conditions}"
            cursor = conn.execute(sql, tuple(kwargs.values()))
            return cursor.fetchall()

# # Пример создания таблицы
# class SomeTable(OrmModel):
#     pk = OrmInteger(primary_key=True)
#     field_1 = OrmText()
#     field_2 = OrmInteger()
#     field_3 = OrmFloat()


# # Пример создания записи в таблице
# new_record = SomeTable(field_1='text4', field_2=42, field_3=34.5)
# new_record.save()

# # Пример получения всех записей из таблицы
# all_records = SomeTable.all()
# print(all_records)

# # Пример фильтрации записей по значению
# filtered_records = SomeTable.filter(field_1='text')
# print(filtered_records)
