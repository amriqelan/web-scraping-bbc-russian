import requests
from bs4 import BeautifulSoup
import sqlite3

def extract_articles_and_sentences(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        articles = []

        if 'bbc' in url:
            articles_section = soup.find('section', class_='bbc-iinl4t')
            if articles_section:
                article_items = articles_section.find_all('li', class_='ebmt73l0')
                for article_item in article_items:
                    article_text = article_item.get_text(separator=' ')
                    articles.append(article_text)

        return articles
    except Exception as e:
        print(f"Error processing URL: {url}\nError: {e}")
        return []

if __name__ == '__main__':
    url = 'https://www.bbc.com/russian'  

    articles = extract_articles_and_sentences(url)

    db_connection = sqlite3.connect('articles.db')
    db_cursor = db_connection.cursor()

    db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY,
            url TEXT,
            article_text TEXT
        )
    ''')

    articles_added = 0

    for article in articles:
        db_cursor.execute('SELECT COUNT(*) FROM articles WHERE url=? AND article_text=?', (url, article))
        count = db_cursor.fetchone()[0]

        if count == 0:
            db_cursor.execute('INSERT INTO articles (url, article_text) VALUES (?, ?)', (url, article))
            db_connection.commit()
            articles_added += 1

    db_connection.close()

    print(f"Extracted {len(articles)} articles from {url} and stored {articles_added} articles in the database.")
