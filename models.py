from sqlalchemy import Column, Integer, Boolean, String, select, BigInteger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


# DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_RkIy9Ctf5bph@ep-fragrant-butterfly-a8t65nyw-pooler.eastus2.azure.neon.tech/neondb?ssl=require"
DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_RkIy9Ctf5bph@ep-fragrant-butterfly-a8t65nyw-pooler.eastus2.azure.neon.tech/neondb"# FIX: Use connect_args instead of "sslmode=require"
engine = create_async_engine(
    DATABASE_URL,
)
async_session = async_sessionmaker(engine)


class BaseModel(AsyncAttrs, DeclarativeBase):
    pass


class User(BaseModel):
    __tablename__ = 'Logins_user'
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger)
    name = Column(String)
    role = Column(String,default='user')
    sending = Column(Boolean, default=False)



class Login(BaseModel):
    __tablename__ = 'Logins_logins_model'
    id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)
    status = Column(Boolean, default=True)


async def get_users():
    async with async_session() as session:
        user = await session.execute(select(User).where(User.sending==True))
        users = user.scalars().all()
        return users

async def get_users_all():
    async with async_session() as session:
        user = await session.execute(select(User.tg_id))
        users = user.scalars().all()
        return users



async def create_user(tg_id, sending, name):
    async with async_session() as session:
        user = await session.execute(select(User).where(User.tg_id == tg_id))
        user = user.scalar_one_or_none()
        if user:
            user.sending = sending
        else:
            user = User(tg_id=tg_id, sending=sending, name=name)  # Fix here
            session.add(user)  # Add the user to the session
        await session.commit()




async def get_login():
    async with async_session() as session:
        result = await session.execute(select(Login))
        logins = result.scalars().all()
        return logins

async def get_login1():
    async with async_session() as session:
        result = await session.execute(select(Login))
        logins = result.scalars().all()
        return logins


async def create_login(login: str, password: str,status:bool):
    async with async_session() as session:
        async with session.begin():
            existing_login = await session.execute(select(Login).where(Login.login == login))
            existing_login = existing_login.scalar_one_or_none()
            if existing_login:
                existing_login.password = password
                existing_login.status = status
                session.add(existing_login)
                await session.commit()
                return existing_login
            else:
                new_login = Login(login=login, password=password,status=status)
                session.add(new_login)
                await session.commit()
                return new_login

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)