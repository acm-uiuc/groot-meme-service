# groot-meme-service

## Install / Setup
1. Clone repo:

    ```
    git clone https://github.com/acm-uiuc/groot-meme-service
    cd groot-meme-service
    ```

2. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

3. Copy settings template:

    ```
    cd groot_meme_service
    cp settings.template.py settings.py
    ```

4. Add your DB credentials to settings.py.

## Run Application
From project root directory:
```
export FLASK_APP=groot_meme_service.app
flask run
```

## Meme Routes

### GET /memes

Returns first 25 memes in given order.

**Params**:

- `netid` - Optional. Filter by user who submitted meme.
- `order` - Optional. Options: 'random' - random order, 'latest' - freshest memes
    - Default: 'random'

### GET /memes/:meme_id

Returns given meme.

### POST /memes

**Params**:

- `url` - Required. Direct image url of the meme. Must have `png` or `jpg` extension.
- `title` - Optional. Title of your meme.
