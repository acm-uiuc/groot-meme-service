# groot-meme-service

## Install Flask for Python 2.7
```
pip install flask
```

## Run Application
From folder groot-meme-service/groot_meme_service
```
export FLASK_APP=app.py
flask run
```

## API Documentation
arg "order" in browse and query can be omitted or any of "random", "latest", "top", "rising"

### GET /memes/browse
`curl -X GET -d '{"order" => "random"}' http://localhost:8000/memes/browse'
```json
[{"user":"Steve Jobs", "url":"http://www.imgur.com/gallery/AAAAA", "score":0, "title":"Oranges"}]
```

### GET /memes/query
`curl -X GET -d '{"user" => "Steve Jobs", "order" => "random"}' http://localhost:8000/memes/query`
```json
{"user":"Steve Jobs", "url":"http://www.imgur.com/gallery/AAAAA", "score":0, "title":"Oranges"}
```

### POST /memes/upload
`curl -X POST -d '{"user" => "Steve Jobs", "url" => "http://www.imgur.com/gallery/AAAAA"}' http://localhost:8000/memes/upload`
```json
OK
```
