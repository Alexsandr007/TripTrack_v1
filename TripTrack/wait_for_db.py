# wait_for_db.py
import time
import psycopg2
import os

def wait_for_db():
    """Ждет пока база данных станет доступной"""
    print("🕐 Waiting for database...")
    host = os.getenv('POSTGRES_HOST', 'postgres')
    port = os.getenv('POSTGRES_PORT', '5432')
    dbname = os.getenv('POSTGRES_DB', 'triptrack')
    user = os.getenv('POSTGRES_USER', 'triptrack_user')
    password = os.getenv('POSTGRES_PASSWORD', 'triptrack_password')
    
    for i in range(30):  # 30 попыток
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password
            )
            conn.close()
            print("✅ Database is ready!")
            return True
        except Exception as e:
            print(f"❌ Database not ready yet (attempt {i+1}/30): {e}")
            time.sleep(2)
    
    print("❌ Could not connect to database after 30 attempts")
    return False

if __name__ == "__main__":
    wait_for_db()