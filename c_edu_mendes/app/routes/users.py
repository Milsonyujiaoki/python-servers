from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.schemas import Message, UserList, UserPublic, UserSchema
from app.security import get_current_user, get_hashed_password

router = APIRouter(prefix="/users", tags=["users"])


# =====================================================
# CRUD USERS
# =====================================================


@router.post(
    "/", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: UserSchema, session: AsyncSession = Depends(get_session)
) -> UserPublic:
    result = await session.execute(
        select(User).where(
            (User.email == user.email)
            | (User.username == user.name)
            | (User.cpf_cnpj == user.cpf_cnpj)
        )
    )
    db_user: User | None = result.scalar_one_or_none()
    if db_user:
        if db_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Usuário com email já existe.",
            )
        elif db_user.username == user.name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Usuário com nome já existe.",
            )
        elif db_user.cpf_cnpj == user.cpf_cnpj:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Usuário com CPF/CNPJ já existe.",
            )

    db_user = User(
        username=user.name,
        cpf_cnpj=user.cpf_cnpj,
        email=user.email,
        password=get_hashed_password(user.password),
        birth_date=user.birth_date,
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return UserPublic(
        id=db_user.id,
        name=db_user.username,
        email=db_user.email,
    )


@router.get("/", response_model=UserList, status_code=status.HTTP_200_OK)
async def get_all_users(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
) -> UserList:
    result = await session.execute(select(User).offset(offset).limit(limit))
    users_db = result.scalars().all()
    return UserList(
        users=[
            UserPublic(id=user.id, name=user.username, email=user.email)
            for user in users_db
        ]
    )


@router.get(
    "/{user_id}",
    response_model=UserPublic,
)
async def get_user(
    user_id: UUID, session: AsyncSession = Depends(get_session)
) -> UserPublic:
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
        )
    return user


@router.put(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
)
async def update_user(
    user_id: UUID,
    user_update: UserSchema,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> UserPublic:

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para atualizar este usuário.",
        )

    try:
        current_user.username = user_update.name
        current_user.email = user_update.email
        current_user.cpf_cnpj = user_update.cpf_cnpj
        current_user.password = get_hashed_password(user_update.password)
        current_user.birth_date = user_update.birth_date

        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)
        return current_user

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="name, email or cpf_cnpj already exists",
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=Message,
)
async def delete_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Message:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para deletar este usuário.",
        )
    await session.delete(current_user)
    await session.commit()
    return Message(message="User deleted with success")
