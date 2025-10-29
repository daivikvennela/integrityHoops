import os
import psycopg2


def main() -> None:
    url = os.getenv("DATABASE_URL")
    if not url:
        print("SKIP: DATABASE_URL not set")
        return
    sslmode = os.getenv("PGSSLMODE", "require")
    conn = psycopg2.connect(url, connect_timeout=5, sslmode=sslmode)
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    assert cur.fetchone()[0] == 1
    cur.close()
    conn.close()
    print("OK: DATABASE_URL connection and simple query")


if __name__ == "__main__":
    main()


