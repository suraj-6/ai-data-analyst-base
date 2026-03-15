import sqlite3
import random
from datetime import date, timedelta

DB_PATH = "sales.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.executescript("""
CREATE TABLE IF NOT EXISTS products (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,
    category TEXT NOT NULL,
    price    REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS sales (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER REFERENCES products(id),
    quantity   INTEGER NOT NULL,
    revenue    REAL NOT NULL,
    sale_date  TEXT NOT NULL,
    region     TEXT NOT NULL
);
""")

products = [
    (1, "Laptop Pro",      "Electronics", 1299.99),
    (2, "Wireless Mouse",  "Electronics",   29.99),
    (3, "Standing Desk",   "Furniture",    499.99),
    (4, "Ergonomic Chair", "Furniture",    349.99),
    (5, "Python Course",   "Education",     79.99),
    (6, "Monitor 4K",      "Electronics",  699.99),
    (7, "Notebook Pack",   "Education",     14.99),
    (8, "Desk Lamp",       "Furniture",     59.99),
]
c.executemany("INSERT OR IGNORE INTO products VALUES (?,?,?,?)", products)

regions = ["North", "South", "East", "West"]
start = date(2024, 1, 1)

for _ in range(600):
    p = random.choice(products)
    qty = random.randint(1, 12)
    d = (start + timedelta(days=random.randint(0, 364))).isoformat()
    c.execute(
        "INSERT INTO sales (product_id, quantity, revenue, sale_date, region) VALUES (?,?,?,?,?)",
        (p[0], qty, round(p[3] * qty, 2), d, random.choice(regions))
    )

conn.commit()
conn.close()
print("Done — sales.db seeded with 600 rows.")