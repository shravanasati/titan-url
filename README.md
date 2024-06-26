# titan-url

Titan URL is a modern, free and open source URL shortener.

View it here: https://titanurl.vercel.app.

<br>

## Features

- Free and open source
- Custom as well as random aliases
- No sign up required

<br>


## API Usage

titan-url offers a free and easy to use Rest API for integrating titan-url into your application. And no API key is required! 

The API is rate-limited to 300 reqs/min and 6 req/s.

The only public endpoint is:
```
POST https://titanurl.vercel.app/shorten
```

The payload for the POST request must be json. The json payload must have these fields:

```json
{
	"original-url": "the url you want to shorten",
	"alias-type": "either custom or random",
	"alias": "custom-alias", // can be omitted if the alias-type is random
	"qr": true // optional, request a QR code of the shortened link
}
```

The response will also be of json type.
```json
{
	"ok": true,
	"message": "https://titanurl.vercel.app/demo",
	"analytics_url": "https://titanurl.vercel.app/analytics/someAnalyticsID"
}
```

If a QR code was also requested, then the response will contain a `qr_code` field which is the base64-encoded PNG data URI of the QR image, which might look something like this:

```
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMsAAADLAQAAA...
```

Whether the request to the API is successfull or not, the response json schema will always be the same. Make sure to check the `ok` key to know whether the request was successfull or not. In case the request fails, the `message` key will contain the error message.

## Example extensions

The following apps have leveraged the titan-url API to shorten URLs.

- [titan-url-cli](https://github.com/shravanasati/titan-url-cli) - A terminal client for titan-url.
- [Alfred Discord Bot](https://github.com/alvinbengeorge/Discord) - An all in one Discord bot.

## Setting up the Development Environment

1. Clone the repository.

```
git clone https://github.com/shravanasati/titan-url.git
```

2. Create and activate virtual environment.

```
python -m venv venv
```

```
./venv/Scripts/Activate.ps1
```

for windows

```
source ./venv/bin/activate
```

for unix like systems.

3. Install all dependencies.

```
pip install -r requirements.txt
```

```
npm i
```

4. Run the app.

```
npm run dev
```

This will run the webpack watcher, minifying the javascript files in `src/` to `static/scripts`.

```
stella run
```

This will run the flask app with a browser window with live reload enabled.

```
stella run server
```

This will run the flask app only with live reload enabled.