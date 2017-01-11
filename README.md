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
```
python groot_meme_service/app.py
```

Do `export MEME_DEBUG=True` to run Flask in debug mode, if desired.

## Meme Routes

### GET /memes

Returns first 25 memes in given order.

**Params**:

- `netid` - Optional. Filter by user who submitted meme.
- `order` - Optional. Options: 'random' - random order, 'latest' - freshest memes
    - Default: 'random'

### POST /memes

**Params**:

- `url` - Required. Direct image url of the meme. Must have `png` or `jpg` extension.
- `token` - Required. Session token to authenticate poster.
- `title` - Optional. Title of your meme.

### GET /memes/:meme_id

Returns given meme.

### DELETE /memes/:meme_id

Requires admin access. Deletes a meme.

**Params**:
- `token` - Required. Session token to authenticate user.


### GET /memes/unapproved

Requires admin access. Returns all unapproved memes.

**Params**:
- `token` - Required. Session token to authenticate user.

### PUT /memes/:meme_id/approve

Requires admin access. Approves a meme to be publicly viewable.

**Params**:
- `token` - Required. Session token to authenticate user.


