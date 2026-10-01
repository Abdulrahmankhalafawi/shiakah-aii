import sqlite3

def init_database():
    conn = sqlite3.connect('fashion_stock.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            style TEXT NOT NULL,
            gender TEXT NOT NULL,
            image_url TEXT
        )
    ''')
    
    # Data in English
    sample_data = [
        ('Casual White T-Shirt', 'shirt', 'casual', 'unisex', 'https://via.placeholder.com/150'),
        ('Blue Denim Jeans', 'pants', 'casual', 'unisex', 'https://via.placeholder.com/150'),
        ('Classic Black Blazer', 'blazer', 'formal', 'men', 'https://via.placeholder.com/150'),
        ('Elegant Evening Dress', 'dress', 'formal', 'women', 'https://via.placeholder.com/150'),
        ('White Casual Sneakers', 'shoes', 'casual', 'unisex', 'https://via.placeholder.com/150')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO inventory (title, category, style, gender, image_url)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_data)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully with English inventory data!")

if __name__ == '__main__':
    init_database()