import aiosqlite
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment

from config import settings
from utils import get_path_to_excel_file, get_excel_filename_today
from logging_config import logger


async def create_db():
    async with aiosqlite.connect(settings.DATABASE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS registration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name_parent TEXT,
                name_child TEXT,
                age_child INTEGER,
                delivery TEXT,
                delivery_id INTEGER
                )
        ''')
        await db.commit()


async def add_user(user_id: int,
                   name_parent: str,
                   name_child: str,
                   age_child: int,
                   delivery: str,
                   delivery_id: int):
    async with aiosqlite.connect(settings.DATABASE) as db:
        try:
            await db.execute("""INSERT INTO registration (
                user_id,
                name_parent,
                name_child,
                age_child,
                delivery,
                delivery_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                name_parent,
                name_child,
                age_child,
                delivery,
                delivery_id)
            )
            await db.commit()
        except aiosqlite.IntegrityError as error:
            logger.error(f"Ошибка {error} ")


async def fetch_all_data(db_path=settings.DATABASE):
    query = """SELECT name_parent, name_child, age_child, delivery FROM registration"""

    async with aiosqlite.connect(db_path) as db:
        async with db.execute(query) as cursor:
            # columns = [description[0] for description in cursor.description]
            rows = await cursor.fetchall()

    return rows


async def is_user_registration(user_id, db_path=settings.DATABASE):
    query = """SELECT 1 FROM registration WHERE user_id = ? LIMIT 1"""

    async with aiosqlite.connect(db_path) as db:
        async with db.execute(query, (user_id, )) as cursor:
            result = await cursor.fetchone()
            return result is not None


async def save_all_data_to_excel(rows=None):
    if rows is None:
        return

    excel_file_path = await get_path_to_excel_file(excel_filename=await get_excel_filename_today())

    columns = ['ФИО работника', 'Имя ребенка', 'Возраст', 'Доставка']
    df = pd.DataFrame(rows, columns=columns)
    df.insert(0, 'Номер', range(1, len(df) + 1))

    df.to_excel(excel_file_path, index=False)

    workbook = load_workbook(excel_file_path)
    worksheet = workbook.active

    column_settings = {
        'A': {"width": 8, "alignment": Alignment(horizontal='center')},
        'B': {"width": 32, "alignment": Alignment(horizontal='left')},
        'C': {"width": 20, "alignment": Alignment(horizontal='left')},
        'D': {"width": 9, "alignment": Alignment(horizontal='center')},
        'E': {"width": 50, "alignment": Alignment(horizontal='left')},
    }
    for column, data in column_settings.items():
        if worksheet[f"{column}1"].value is not None:
            worksheet.column_dimensions[column].width = data["width"]
        for cell in worksheet[column]:
            cell.alignment = data["alignment"]

    workbook.save(excel_file_path)
    workbook.close()

