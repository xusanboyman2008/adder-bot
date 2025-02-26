from sqlalchemy import Column, Integer, String, select, BigInteger, ForeignKey, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine('sqlite+aiosqlite:///database.sqlite3')
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "User"

    id = Column(BigInteger, index=True, primary_key=True)  # User ID
    name = Column(String, unique=True, nullable=True)


class Channels(Base):
    __tablename__ = "Channels"
    id = Column(Integer, primary_key=True, autoincrement=True)  # Ensure autoincrement
    is_required = Column(Boolean, default=False, nullable=True)
    channel_id = Column(String)


class Counter(Base):
    __tablename__ = "Counter"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("User.id"))
    channel_id = Column(BigInteger, ForeignKey("Channels.id"))
    count = Column(BigInteger, nullable=True, default=0)


class InviteTracker(Base):
    __tablename__ = "InviteTracker"

    id = Column(Integer, primary_key=True, index=True)
    inviter_id = Column(BigInteger, ForeignKey('User.id'))
    invited_id = Column(BigInteger, unique=True)  # Prevent duplicate invites


async def create_channel(channel_id, action=False):
    async with async_session() as session:
        r = await session.execute(select(Channels).where(Channels.channel_id == channel_id))
        res = r.scalar_one_or_none()
        if not res:
            t = session.add(Channels(channel_id=channel_id, is_required=action))
            await session.commit()
            await session.flush()
            return t
        await session.commit()
        return res


async def get_channel(action=False):
    async with async_session() as session:
        if action=='all':
            r = await session.execute(select(Channels))
            res = r.scalars().all()
            return res
        r = await session.execute(select(Channels).where(Channels.is_required == action))
        res = r.scalars().all()
        if res:
            return res


async def get_or_create_user(user_id, name=None):
    async with async_session() as session:
        user = await session.execute(select(User).where(User.id == user_id))
        result = user.scalar_one_or_none()
        if not result:
            user = User(id=user_id, name=name)
            session.add(user)
            await session.commit()
        return result


async def increment_invite_count(inviter_id, invited_id, channel_id):
    async with async_session() as session:
        existing_invite = await session.execute(select(InviteTracker).where(InviteTracker.invited_id == invited_id))
        result = existing_invite.scalar_one_or_none()
        if not result:
            session.add(InviteTracker(inviter_id=inviter_id, invited_id=invited_id))
            usere = await session.execute(select(User).where(User.id == int(inviter_id)))
            user = usere.scalar_one_or_none()
            if user:
                ch = await session.execute(
                    select(Counter).where(Counter.user_id == str(inviter_id)).filter(Counter.channel_id == channel_id))
                r = ch.scalar_one_or_none()
                if r:
                    r.count += 1
                else:
                    session.add(Counter(user_id=inviter_id, count=1, channel_id=channel_id))
                    await session.commit()
                    await session.flush()
            await session.commit()


async def get_top_invites(channel_id, limit=10):
    async with async_session() as session:
        result = await session.execute(
            select(Counter).where(Counter.channel_id == channel_id).filter(Counter.count).limit(limit))
        return result.scalars().all()


async def me(user_id, channel_id):
    async with async_session() as session:
        result = await session.execute(
            select(Counter).where(Counter.channel_id == channel_id).filter(Counter.user_id == user_id))
        return result.scalars().first()


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
