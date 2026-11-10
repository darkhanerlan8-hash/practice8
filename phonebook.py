
import json
from pathlib import Path
from psycopg2.extras import Json
from connect import get_connection

BASE = Path(__file__).resolve().parent

def setup():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    name VARCHAR(100),
                    phone VARCHAR(30)
                )
            """)
            for file in ["functions.sql", "procedures.sql"]:
                sql = (BASE / file).read_text(encoding="utf-8")
                cur.execute(sql)

def show(rows):
    if not rows:
        print("No contacts found")
    for name, phone in rows:
        print(name, "-", phone)

def main():
    setup()

    while True:
        print("\n===== PHONEBOOK =====")
        print("1. Search contacts")
        print("2. Add or update contact")
        print("3. Add multiple contacts")
        print("4. Show contacts by page")
        print("5. Delete contact")
        print("6. Show all contacts")
        print("0. Exit")

        choice = input("Choose: ")

        if choice == "0":
            break

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:

                    if choice == "1":
                        p = input("Search: ")
                        cur.execute(
                            "SELECT * FROM search_contacts(%s)",
                            (p,)
                        )
                        show(cur.fetchall())

                    elif choice == "2":
                        name = input("Name: ")
                        phone = input("Phone: ")
                        cur.execute(
                            "CALL upsert_contact(%s, %s)",
                            (name, phone)
                        )
                        print("Saved!")

                    elif choice == "3":
                        n = int(input("How many contacts? "))
                        data = []

                        for i in range(n):
                            print("Contact", i + 1)
                            name = input("Name: ")
                            phone = input("Phone: ")
                            data.append({
                                "name": name,
                                "phone": phone
                            })

                        cur.execute(
                            "CALL bulk_insert_contacts(%s, %s)",
                            (Json(data), Json([]))
                        )
                        invalid = cur.fetchone()[0]
                        print("Invalid data:", invalid)

                    elif choice == "4":
                        limit = int(input("Page size: "))
                        page = int(input("Page number: "))
                        if limit <= 0 or page <= 0:
                            print("Enter positive numbers")
                            continue
                        offset = (page - 1) * limit
                        cur.execute(
                            "SELECT * FROM get_contacts_page(%s, %s)",
                            (limit, offset)
                        )
                        show(cur.fetchall())

                    elif choice == "5":
                        mode = input("Delete by name or phone? (n/p): ")
                        if mode == "n":
                            name = input("Name: ")
                            if not name:
                                continue
                            cur.execute(
                                "CALL delete_contact(%s, %s)",
                                (name, None)
                            )
                        elif mode == "p":
                            phone = input("Phone: ")
                            if not phone:
                                continue
                            cur.execute(
                                "CALL delete_contact(%s, %s)",
                                (None, phone)
                            )
                        else:
                            print("Invalid choice")
                            continue
                        print("Delete completed!")

                    elif choice == "6":
                        cur.execute(
                            "SELECT * FROM contacts ORDER BY name"
                        )
                        show(cur.fetchall())

                    else:
                        print("Invalid choice")

        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
