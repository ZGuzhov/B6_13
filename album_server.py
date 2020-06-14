from bottle import route, run, HTTPError, request

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_PATH = "sqlite:///albums.sqlite3"
Base = declarative_base()

class Album(Base):
    """
    Описывает структуру таблицы album для хранения записей музыкальной библиотеки
    """
    __tablename__ = "album"

    id = sa.Column(sa.INTEGER, primary_key=True)
    year = sa.Column(sa.INTEGER)
    artist = sa.Column(sa.TEXT)
    genre = sa.Column(sa.TEXT)
    album = sa.Column(sa.TEXT)

def connect_db():
    """
    Устанавливает соединение к базе данных, создает таблицы, если их еще нет и возвращает объект сессии 
    """
    engine = sa.create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)
    return session()

# поиск альбомов по названию артиста
# образец запроса в браузере, можно менять название артиста для получения других данных:
# http://localhost:8080/albums/Beatles
def artist_find(artist):
    """
    Находит все альбомы в базе данных по заданному артисту
    """
    session = connect_db()
    albums = session.query(Album).filter(Album.artist == artist).all()
    return albums

@route("/albums/<artist>")
def albums(artist):
    albums_list = artist_find(artist)
    if not albums_list:
        message = "Альбомов {} не найдено".format(artist)
        result = HTTPError(404, message)
    else:
        album_names = []
        n = 0
        for album in albums_list:
            n += 1
            album_names.append(str(n) + ". " + album.album)
        result = '<span style="font-weight: 600">Исполнитель: {}, количество альбомов: {}</span><br>'.format(artist, n)
        result += "<br>".join(album_names)
    return result

# добавление альбомов в базу данных
# образец запроса, его можно копировать и вставлять в консоль, достаточно изменять нужные поля: 
# http -f POST http://localhost:8080/albums year="2020" artist="New Artist" genre="Rock" album="Super"
def album_add_db(album):
    """
    Добавляем новый альбом в базу данных
    """
    session = connect_db()
    session.add(album)
    session.commit()

def album_find(album):
    """
    Находит альбом в базе данных по заданному названию и возвращаем результат поиска
    """
    session = connect_db()
    if session.query(Album).filter(Album.album == album).first():
        return True
    else:
        return False

@route("/albums", method="POST")
def album_add():
    try:
        album = Album(
            year = int(request.forms.get("year")),
            artist = request.forms.get("artist"),
            genre = request.forms.get("genre"),
            album = request.forms.get("album")
        )
    except ValueError as err:
        message = "В поле year должно быть введено целое число"
        result = HTTPError(415, message)
    else:
        if album_find(album.album):
            message = "Альбом {} уже существует в базе данных".format(album.album)
            result = HTTPError(409, message)
        else:
            album_add_db(album)
            result = "Данные успешно сохранены"

    return result

if __name__ == "__main__":
    print("Запускайте GET и POST запросы отдельно друго от друга, иначе будут зависания.")
    print("Это происходит потому, что используется bottle, который является базовым и однопоточным Web сервером.")
    run(host="localhost", port=8080, debug=True)