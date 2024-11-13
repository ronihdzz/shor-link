import psycopg2
from settings import settings


def test_connection():
    try:
        # Reemplaza esta URL con la de tu base de datos
        connection_url = settings.DATABASE_URL
        
        connection = psycopg2.connect(connection_url)
        
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"Conexión exitosa. Versión de la base de datos: {db_version}")
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error al conectar a la base de datos: {error}")
        
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Conexión cerrada.")

if __name__ == "__main__":
    test_connection()
