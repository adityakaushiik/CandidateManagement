from sqlalchemy import create_engine, text
from config.config import get_settings


def main():
    s = get_settings()
    engine = create_engine(s.DATABASE_URL)
    print("Connecting to:", s.DATABASE_URL.split("@")[-1])
    with engine.connect() as conn:
        print("alembic_version:")
        try:
            res = conn.execute(text("SELECT version_num FROM alembic_version"))
            print([r[0] for r in res])
        except Exception as e:
            print("(no alembic_version table)", e)
        print("users columns:")
        try:
            res = conn.execute(
                text(
                    """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'users'
                ORDER BY ordinal_position
                """
                )
            )
            for row in res:
                print(row)
        except Exception as e:
            print("(users not found)", e)


if __name__ == "__main__":
    main()
