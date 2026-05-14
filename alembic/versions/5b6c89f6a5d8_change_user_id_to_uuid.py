"""change user id to uuid

Revision ID: 5b6c89f6a5d8
Revises: 94c897711b43
Create Date: 2026-05-13 23:20:00.000000

"""

from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "5b6c89f6a5d8"
down_revision: Union[str, Sequence[str], None] = "94c897711b43"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

USER_TABLE = "user_users"
REFRESH_TABLE = "auth_refresh_tokens"
UUID_TYPE = postgresql.UUID(as_uuid=True)


def _get_pk_name(table_name: str) -> str:
    inspector = sa.inspect(op.get_bind())
    pk = inspector.get_pk_constraint(table_name)
    return pk["name"] or f"{table_name}_pkey"


def _get_index_names(table_name: str, column_name: str) -> list[str]:
    inspector = sa.inspect(op.get_bind())
    return [
        index["name"]
        for index in inspector.get_indexes(table_name)
        if index.get("column_names") == [column_name]
    ]


def _get_fk_names(table_name: str, *, column_name: str, referred_table: str) -> list[str]:
    inspector = sa.inspect(op.get_bind())
    names: list[str] = []

    for fk in inspector.get_foreign_keys(table_name):
        if (
            fk.get("referred_table") == referred_table
            and fk.get("constrained_columns") == [column_name]
            and fk.get("name")
        ):
            names.append(fk["name"])

    return names


def _populate_uuid_columns() -> None:
    connection = op.get_bind()
    user_table = sa.table(
        USER_TABLE,
        sa.column("id", sa.Integer()),
        sa.column("uuid_id", UUID_TYPE),
    )
    refresh_table = sa.table(
        REFRESH_TABLE,
        sa.column("user_id", sa.Integer()),
        sa.column("uuid_user_id", UUID_TYPE),
    )

    user_id_map: dict[int, uuid.UUID] = {}
    users = connection.execute(sa.select(user_table.c.id)).all()

    for row in users:
        new_uuid = uuid.uuid4()
        user_id_map[row.id] = new_uuid
        connection.execute(
            sa.update(user_table)
            .where(user_table.c.id == row.id)
            .values(uuid_id=new_uuid)
        )

    for old_id, new_uuid in user_id_map.items():
        connection.execute(
            sa.update(refresh_table)
            .where(refresh_table.c.user_id == old_id)
            .values(uuid_user_id=new_uuid)
        )


def _populate_integer_columns() -> None:
    connection = op.get_bind()
    user_table = sa.table(
        USER_TABLE,
        sa.column("id", UUID_TYPE),
        sa.column("legacy_id", sa.Integer()),
        sa.column("created_at", sa.DateTime()),
    )
    refresh_table = sa.table(
        REFRESH_TABLE,
        sa.column("user_id", UUID_TYPE),
        sa.column("legacy_user_id", sa.Integer()),
    )

    user_id_map: dict[uuid.UUID, int] = {}
    users = connection.execute(
        sa.select(user_table.c.id)
        .order_by(user_table.c.created_at.asc(), user_table.c.id.asc())
    ).all()

    for next_id, row in enumerate(users, start=1):
        user_id_map[row.id] = next_id
        connection.execute(
            sa.update(user_table)
            .where(user_table.c.id == row.id)
            .values(legacy_id=next_id)
        )

    for user_uuid, old_id in user_id_map.items():
        connection.execute(
            sa.update(refresh_table)
            .where(refresh_table.c.user_id == user_uuid)
            .values(legacy_user_id=old_id)
        )


def upgrade() -> None:
    """Upgrade schema."""
    user_pk_name = _get_pk_name(USER_TABLE)
    refresh_user_fk_names = _get_fk_names(
        REFRESH_TABLE,
        column_name="user_id",
        referred_table=USER_TABLE,
    )
    refresh_user_fk_name = (
        refresh_user_fk_names[0]
        if refresh_user_fk_names
        else "auth_refresh_tokens_user_id_fkey"
    )
    user_id_indexes = _get_index_names(USER_TABLE, "id")
    refresh_user_id_indexes = _get_index_names(REFRESH_TABLE, "user_id")

    op.add_column(USER_TABLE, sa.Column("uuid_id", UUID_TYPE, nullable=True))
    op.add_column(REFRESH_TABLE, sa.Column("uuid_user_id", UUID_TYPE, nullable=True))

    _populate_uuid_columns()

    op.alter_column(USER_TABLE, "uuid_id", existing_type=UUID_TYPE, nullable=False)
    op.alter_column(
        REFRESH_TABLE,
        "uuid_user_id",
        existing_type=UUID_TYPE,
        nullable=False,
    )

    op.drop_constraint(refresh_user_fk_name, REFRESH_TABLE, type_="foreignkey")

    for index_name in refresh_user_id_indexes:
        op.drop_index(index_name, table_name=REFRESH_TABLE)

    for index_name in user_id_indexes:
        op.drop_index(index_name, table_name=USER_TABLE)

    op.drop_constraint(user_pk_name, USER_TABLE, type_="primary")

    op.drop_column(REFRESH_TABLE, "user_id")
    op.drop_column(USER_TABLE, "id")
    op.execute("DROP SEQUENCE IF EXISTS user_users_id_seq")

    op.alter_column(
        USER_TABLE,
        "uuid_id",
        existing_type=UUID_TYPE,
        new_column_name="id",
    )
    op.alter_column(
        REFRESH_TABLE,
        "uuid_user_id",
        existing_type=UUID_TYPE,
        new_column_name="user_id",
    )

    op.create_primary_key(user_pk_name, USER_TABLE, ["id"])
    op.create_index(op.f("ix_auth_refresh_tokens_user_id"), REFRESH_TABLE, ["user_id"], unique=False)
    op.create_foreign_key(
        refresh_user_fk_name,
        REFRESH_TABLE,
        USER_TABLE,
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    user_pk_name = _get_pk_name(USER_TABLE)
    refresh_user_fk_names = _get_fk_names(
        REFRESH_TABLE,
        column_name="user_id",
        referred_table=USER_TABLE,
    )
    refresh_user_fk_name = (
        refresh_user_fk_names[0]
        if refresh_user_fk_names
        else "auth_refresh_tokens_user_id_fkey"
    )
    refresh_user_id_indexes = _get_index_names(REFRESH_TABLE, "user_id")

    op.add_column(USER_TABLE, sa.Column("legacy_id", sa.Integer(), nullable=True))
    op.add_column(REFRESH_TABLE, sa.Column("legacy_user_id", sa.Integer(), nullable=True))

    _populate_integer_columns()

    op.alter_column(USER_TABLE, "legacy_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column(
        REFRESH_TABLE,
        "legacy_user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.drop_constraint(refresh_user_fk_name, REFRESH_TABLE, type_="foreignkey")

    for index_name in refresh_user_id_indexes:
        op.drop_index(index_name, table_name=REFRESH_TABLE)

    op.drop_constraint(user_pk_name, USER_TABLE, type_="primary")

    op.drop_column(REFRESH_TABLE, "user_id")
    op.drop_column(USER_TABLE, "id")

    op.alter_column(
        USER_TABLE,
        "legacy_id",
        existing_type=sa.Integer(),
        new_column_name="id",
    )
    op.alter_column(
        REFRESH_TABLE,
        "legacy_user_id",
        existing_type=sa.Integer(),
        new_column_name="user_id",
    )

    op.execute("DROP SEQUENCE IF EXISTS user_users_id_seq")
    op.execute("CREATE SEQUENCE user_users_id_seq")
    op.execute("ALTER SEQUENCE user_users_id_seq OWNED BY user_users.id")
    op.execute("ALTER TABLE user_users ALTER COLUMN id SET DEFAULT nextval('user_users_id_seq')")
    op.execute(
        """
        SELECT setval(
            'user_users_id_seq',
            COALESCE((SELECT MAX(id) FROM user_users), 1),
            EXISTS (SELECT 1 FROM user_users)
        )
        """
    )

    op.create_primary_key(user_pk_name, USER_TABLE, ["id"])
    op.create_index(op.f("ix_user_users_id"), USER_TABLE, ["id"], unique=False)
    op.create_index(op.f("ix_auth_refresh_tokens_user_id"), REFRESH_TABLE, ["user_id"], unique=False)
    op.create_foreign_key(
        refresh_user_fk_name,
        REFRESH_TABLE,
        USER_TABLE,
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
