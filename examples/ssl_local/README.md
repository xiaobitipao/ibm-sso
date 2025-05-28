# certificate

## Create a self-signed certificate 

[Adding HTTPS to FastAPI](https://medium.com/@mariovanrooij/adding-https-to-fastapi-ad5e0f9e084e)

```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```
