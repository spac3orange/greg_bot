import asyncpg
from environs import Env
from config import logger
from typing import List, Dict, Tuple
import asyncio
import datetime


class Database:
    def __init__(self):
        self.env = Env()
        self.env.read_env(path='config/.env')

        self.user = self.env.str('DB_USER')
        self.password = self.env.str('DB_PASSWORD')
        self.host = self.env.str('DB_HOST')
        self.db_name = self.env.str('DB_NAME')
        self.db_port = self.env.str('DB_PORT')
        self.pool = None

    async def create_pool(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=self.user,
                password=self.password,
                host=self.host,
                database=self.db_name,
                port=self.db_port,
            )

        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while creating connection pool", error)
            print(error)

    async def close_pool(self):
        if self.pool:
            await self.pool.close()

    async def execute_query(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(query, *args)
        except (Exception, asyncpg.PostgresError) as error:
            print("Error while executing query", error)

    async def fetch_row(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        except (Exception, asyncpg.PostgresError) as error:
            print("Error while fetching row", error)

    async def fetch_all(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *args)
        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while fetching all", error)

    async def db_start(self) -> None:
        try:
            await self.create_pool()

            await self.execute_query("""
                CREATE TABLE IF NOT EXISTS girls (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    name TEXT,
                    age INTEGER,
                    games TEXT,
                    price INT,
                    avatar_path TEXT,
                    description TEXT,
                    balance INTEGER DEFAULT 0,
                    orders INT DEFAULT 0                    
                )
            """)

            await self.execute_query("""
                        CREATE TABLE IF NOT EXISTS withdraw_requests (
                            user_id BIGINT PRIMARY KEY,
                            username TEXT,
                            balance INT,
                            date TEXT,
                            status BOOLEAN DEFAULT False
                        )
                    """)

            logger.info('connected to database')

        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while connecting to DB", error)

    async def get_all_girls(self):
        try:
            query = "SELECT * FROM girls"
            return await self.fetch_all(query)
        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while getting all girls", error)

    async def delete_form(self, user_id: int) -> None:
        try:
            await self.execute_query("""
            DELETE FROM girls
            WHERE user_id = $1
            """, user_id)
            logger.info(f'Form {user_id} deleted')
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f'Error while deleting form {user_id}')

    async def change_withdraw_request_status(self, user_id: int, new_status: bool) -> None:
        try:
            await self.execute_query("""
                UPDATE withdraw_requests
                SET status = $1
                WHERE user_id = $2
            """, new_status, user_id)
            logger.info(f"Withdraw request status for user {user_id} changed successfully.")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while changing withdraw request status for user {user_id}", error)

    async def delete_wd_request(self, user_id: int) -> None:
        try:
            await self.execute_query("""
                DELETE FROM withdraw_requests
                WHERE user_id = $1
            """, user_id)
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while deleting wd_request for {user_id}", error)

    async def insert_girl_data(self, user_id: int, username: str, name: str,
                               age: int, games: str, avatar_path: str, description: str, price: int) -> None:
        try:
            query = """
                INSERT INTO girls (user_id, username, name, age, games, avatar_path, description, price)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (user_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    name = EXCLUDED.name,
                    age = EXCLUDED.age,
                    games = EXCLUDED.games,
                    avatar_path = EXCLUDED.avatar_path,
                    description = EXCLUDED.description,
                    price = EXCLUDED.price
            """
            await self.execute_query(query, user_id, username, name, age, games, avatar_path, description, price)
            logger.info(f"Data for user {user_id} inserted successfully.")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while inserting data for user {user_id} into DB", error)

    async def get_girl_data(self, user_id: int):
        try:
            query = """
                SELECT * FROM girls
                WHERE user_id = $1
            """
            return await self.fetch_row(query, user_id)
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while fetching data for user {user_id} from DB", error)

    async def create_withdraw_request(self, user_id: int, username: str, balance: int) -> None:
        try:
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            await self.execute_query("""
                INSERT INTO withdraw_requests (user_id, username, balance, date)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    balance = EXCLUDED.balance,
                    date = EXCLUDED.date
            """, user_id, username, balance, current_date)
            logger.info(f"Withdraw request for user {user_id} created successfully.")
        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while creating withdraw request for user {user_id}", error)

    async def get_withdraw_requests(self, user_id: int = None) -> list:
        try:
            if user_id is not None:
                withdraw_requests = await self.fetch_all("""
                    SELECT * FROM withdraw_requests
                    WHERE user_id = $1 AND status = False
                """, user_id)
            else:
                withdraw_requests = await self.fetch_all("""
                    SELECT * FROM withdraw_requests
                """)
            return withdraw_requests
        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while retrieving withdraw requests", error)
            return []


db = Database()