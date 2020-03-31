# VSCode Rest Client

## Set Up

Download the following to set up VSCode Rest Client:

- VSCode: https://code.visualstudio.com/download

- VSCode Extension Rest Client: https://marketplace.visualstudio.com/items?itemName=humao.rest-client 

- VSCode Extension GUID Insert: https://marketplace.visualstudio.com/items?itemName=heaths.vscode-guid

Open workspace, ensure Rest Client and GUID Insert are enabled on workspace. Go to `Preferences` > `Extensions`, search for the two extensions above (Rest Client & GUID) and select enable. 

</br>

## Constructing Request

### Request Variables

Think of request variable as attaching a name metadata to the underlying request. This counts as a empty line. Format, either `//` or `#` followed my space and `@name` then space and the name of your request as seen below:

```http
# @name nameOfRequest
```

</br>

### Request Line

The first non-empty line of the selection is the Request Line. `GET` and `POST` request line examples below. 

#### GET
If request method is omitted, request will be treated as GET, as shown below:

```http
http://myexample.come HTTP/1.1
```

```http
GET http://myexample.come HTTP/1.1
```

#### POST

```http
POST http://myexample.come HTTP/1.1
```

</br>

### Request Headers

The lines immediately after the request line to first empty line are parsed as Request Headers.

Format:
```http
field-name: field-value
```

By default REST Client Extension will add a User-Agent header with value vscode-restclient in your request if you don't explicitly specify. 

```http
User-Agent: rest-client
Content-Type: application/json
```

</br>

### Request Body

Add a blank line after the Request Headers, all content after it will be treated as Request Body. 

Json example:

```http
POST https://example.com/comments HTTP/1.1
content-type: application/json

{
    "name": "sample",
    "time": "Wed, 21 Oct 2015 18:27:50 GMT"
}
```

XML example:

```xml
<request>
    <name>This is an example</name>
</request>
```

Specify file path to use as a body:

```http
< ./example.xml
```


</br>

## Using VSCode Rest Client

### Shortcuts

<b> All shortcuts only available in http file: </b>

- Cancel Request `Cmd`+`Option`+`K`
- Send Request `Cmd`+`Option`+`R`
- Re-run Last Request `Cmd`+`Option`+`L`
- Request History `Cmd`+`Option`+`H`
- Clear History `fn`+`F1` type Rest Client: Clear Request History
- List of requests and variables `Cmd`+`Shift`+`O`
- List of environments `Cmd`+`Option`+`E`
- Open settings `Cmd`+`,`

</br>

### Environment Variables 

Environment variables are store in `settings.json` file located in `.vscode` folder. An example can be seen [here](../.vscode/settings.json) of how to set up file. 

In http file, ensure at the bottom right corner the environment you wish to use is selected. As default this is set to `no environment`. `$shared` variables will be available even when no environment is selected. 

Enironment variables can be used in a class by surounding text with curly braces and the name of variable inside `{{GUID}}`.

In this repo a `sample-mhs-environment` has been created in the settings file, to be used as sample content. 

</br>

### File Variables

Only available to file declared in, example below:

```http
@baseUrl = https://example.com
```

Can be used in file as shown below:

```http
POST {{baseUrl}}:80 HTTP/1.1
```

</br>

### Generate UUID

Currently it is only possible to generate UUID manual using an extension. To generator new UUID, `fn` + `F1` and type `Insert GUID` where needed. Currently an environment variable is used in settings.json for this to be easily changed in all http files. 

</br>

### Response Panel 

Response panel appear on the right side on a seperate tab once a request has been sent and a response returned. 

In response panel click More Actions to:
- Fold body
- Unfold body

#### Save Response

Save response, click save icon in response panel:
- Click the Open button to open the saved response file in current workspace<br>
- Click Copy Path to copy the saved response path to clipboard

Save response body, click Save Response Body button
- As default this will save according to the response MIME type, i.e. content-type: application/json, will save as json
- Overwrite the MIME type and extension mapping with below setting:
    <br>
    ```http
    "rest-client.mimeAndFileExtensionMapping": {
        "application/atom+xml": "xml"
    }
    ```

</br>

### Tips

In VSCode Explorer under `OUTLINE`, contains file and request variables for the http file currently selected. 

Hover over total duration to view duration details of Socket, DNS, TCP, First Byte and Download.

![Image of total duration](./documentation/vscode-total-duration.png)

</br>
Hover over response size to view the breakdown response size details of headers and body.

![Image of response size](./documentation/vscode-response-size.png )

</br>

## custom

### Structure

### Message examples

All messages have are locted under message file. This contains a pretty print version to enable easy reading and make ulterations where needed to the correctly formatted version listed in file. 

