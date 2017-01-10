# groot-meme-service

## Install Django for Python 2.7
```
pip install django
```

## Run Application
From folder groot-meme-service/groot_meme_service
```
python manage.py runserver
```

## API Documentation

### GET /memes/browse
`curl -X GET http://localhost:8000/memes/browse'
```json
[{"user":"Steve Jobs", "url":"http://www.imgur.com/gallery/AAAAA", "score":0}]
```

### GET /memes/query
`curl -X GET -d '{"user" => "Steve Jobs"}' http://localhost:8000/memes/query`
```json
{"user":"Steve Jobs", "url":"http://www.imgur.com/gallery/AAAAA", "score":0}
```

### POST /memes/upload
`curl -X POST -d '{"user" => "Steve Jobs", "url" => "http://www.imgur.com/gallery/AAAAA"}' http://localhost:8000/memes/upload`
```json
OK
```
