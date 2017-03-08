# groot-meme-service

Groot core development:

[![Join the chat at https://gitter.im/acm-uiuc/groot-development](https://badges.gitter.im/acm-uiuc/groot-development.svg)](https://gitter.im/acm-uiuc/groot-development?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Questions on how to add your app to Groot or use the Groot API:

[![Join the chat at https://gitter.im/acm-uiuc/groot-users](https://badges.gitter.im/acm-uiuc/groot-users.svg)](https://gitter.im/acm-uiuc/groot-users?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


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

## Authorization

For the purposes of `groot-meme-service` 'admin access' is granted to members of the ACM admin, corporate, and top4 committees, as given by `groot-group-service`.

## Meme Routes

**NOTE:** All routes require a HTTP Header called `Meme-Token` which must be set to a valid user session token.

### Meme Actions

#### GET /memes

Returns paginated memes in given order.

*Params*:

- `author` - Optional. Filter by user who submitted meme.
- `order` - Optional.
    - Options: 
        - 'latest' - freshest memes first
        - 'random' - random order
        - 'top' - memes sorted by number of votes descending
        - 'hottest' - memes sorted by number of votes ranked by recency
        - 'unapproved' - Requires admin access. Returns unapproved memes in ascending order by upload time.
    - Default: 'latest'

#### POST /memes

Registers a new meme.

*Params*:

- `url` - Required. Imgur url of the meme image. Must reference a valid [imgur](http://imgur.com) image (not a imgur gallery or album). Duplicate images are not allowed.
- `title` - Optional. Title of your meme.

#### GET /memes/:meme_id

Returns the requested meme.

### Admin Actions

#### DELETE /memes/:meme_id

Requires admin access. Deletes a meme.

#### PUT /memes/:meme_id/approve

Requires admin access. Approves a meme to be publicly viewable.

### Voting

#### PUT /memes/:meme_id/vote

Register a vote for the given meme.

#### DELETE /memes/:meme_id/vote

Retract a vote for the given meme.

## Contributing

Contributions to `groot-meme-service` are welcomed!

1. Fork the repo.
2. Create a new feature branch.
3. Add your feature / make your changes.
4. Install [pep8](https://pypi.python.org/pypi/pep8) and run `pep8 *.py` in the root project directory to lint your changes. Fix any linting errors.
5. Create a PR.
6. ???
7. Profit.
