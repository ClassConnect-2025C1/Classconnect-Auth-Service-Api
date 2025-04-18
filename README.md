# TemplatePython

El servicio se encuentra desplegado en Render y es posible enviar una petición de healthcheck:
[https://templatepython.onrender.com/healthcheck](https://classconnect-auth-service-api.onrender.com)

## Notification

### POST /auth/notification

#### **Request:**
```json
{
    "email": "email@example.com",
    "to": "destination_number",
    "channel": "channel_name"
}
```
Los valores que pueden tomar los campos son:
 * email: email del usuario a verificar  
 * to: numero donde se envia la notificacion, debe respetar el formato E.164 **_"+ codigo_pais numero"_**. Ejemplo *"+15005550006"*.
 * channel: canal por el cual se enviara la notificacion. Los valores posibles son **_"sms"_** o **_"whatsapp"_**.  

#### **Response**  
```
Notificacion enviada con exito:
 * Status code: 200, OK
 * Body: (vacio)
```
Casos de error:  
```
Bad Request
 * status code: 400
 * Body: "One or more fields are missing or invalid"
```

```
Servicio externo no pudo enviar
 * Status Code: 404
 * Body: Notification rejected by provider
```

## Verification

### POST /auth/verification

#### **Request:**
```json
{
    "email": "email@example.com",
    "pin": "verification_pin"
}
```
Los valores que pueden tomar los campos son:
 * email: email del usuario a verificar  
 * pin: pin del usuario para verificar cuenta. 

#### **Response**  
Caso de exito  
```
Notificacion enviada con exito:
 * Status code: 200, OK
 * Body: (vacio)
```
Casos de error:  
```
El usuario ya estaba verificado
 * status code: 404
 * Body: "User already verified"
```
```
Pin ingresado no es correcto
 * Status Code: 401
 * Body: "Invalid verification pin"
```
```
Pin ingresado esta expirado
 * Status Code: 410
 * Body: "Verification pin expired"
```