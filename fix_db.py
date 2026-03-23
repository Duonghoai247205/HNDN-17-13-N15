import psycopg2
import sys

try:
    print("Connecting to database...")
    conn = psycopg2.connect(
        host='localhost',
        port=5433,
        user='odoo',
        password='odoo',
        dbname='odoo-fitdnu'
    )
    cur = conn.cursor()
    
    print("Deleting orphaned records from project_du_an and cong_viec_task...")
    cur.execute('TRUNCATE project_du_an CASCADE;')
    cur.execute('TRUNCATE cong_viec_task CASCADE;')
    
    conn.commit()
    print("Cleanup successful.")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals() and conn:
        cur.close()
        conn.close()
