import socket
import ujson
import machine


html = """<!DOCTYPE html>
            <html>
              <head>
                <title>ESP32 Setup</title>
                <style>
                  body {
                    font-family: Arial, sans-serif;
                    background: #f4f4f4;
                    padding: 20px;
                    color: #333;
                  }
                  .container {
                    max-width: 400px;
                    margin: auto;
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                  }
                  h2 {
                    text-align: center;
                    color: #0077cc;
                  }
                  input[type="text"],
                  input[type="password"] {
                    width: 100%;
                    padding: 10px;
                    margin-top: 5px;
                    margin-bottom: 15px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                  }
                  input[type="submit"] {
                    width: 100%;
                    background-color: #0077cc;
                    color: white;
                    padding: 10px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    cursor: pointer;
                  }
                  input[type="submit"]:hover {
                    background-color: #005fa3;
                  }
                </style>
              </head>
              <body>
                <div class="container">
                  <h2>Configure Wi-Fi and MQTT</h2>
                  <form action="/" method="POST">
                    <label>WiFi SSID:</label>
                    <input name="ssid" type="text" required>

                    <label>WiFi Password:</label>
                    <input name="password" type="password">

                    <label>MQTT Server IP:</label>
                    <input name="mqtt" type="text" required>

                    <label>MQTT Username:</label>
                    <input name="mqtt_user" type="text">

                    <label>MQTT Password:</label>
                    <input name="mqtt_pass" type="password">

                    <input type="submit" value="Save">
                  </form>
                </div>
              </body>
            </html>
            """


def save_config(data):
    with open("config.json", "w") as f:
        ujson.dump(data, f)

def parse_form(body):
    params = {}
    for pair in body.split("&"):
        key, val = pair.split("=")
        params[key] = val.replace("+", " ")
    return params

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print("Web server running at http://192.168.4.1")

while True:
    cl, addr = s.accept()
    print("Client connected:", addr)
    req = cl.recv(1024)
    req = req.decode("utf-8")
    
    if "POST" in req:
        body = req.split("\r\n\r\n")[1]
        data = parse_form(body)
        save_config({
            "ssid": data["ssid"],
            "password": data["password"],
            "mqtt": data["mqtt"],
            "mqtt_user": data["mqtt_user"],
            "mqtt_pass": data["mqtt_pass"]
        })
        response = """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
                        <!DOCTYPE html>
                        <html>
                        <head>
                          <title>Saved</title>
                          <style>
                            body {
                              font-family: Arial, sans-serif;
                              text-align: center;
                              padding-top: 100px;
                              background-color: #f4f4f4;
                            }
                            .message {
                              display: inline-block;
                              padding: 20px 40px;
                              background-color: #e0ffe0;
                              border: 2px solid #4CAF50;
                              border-radius: 10px;
                              font-size: 20px;
                              color: #2d662d;
                            }
                          </style>
                        </head>
                        <body>
                          <div class="message">Configuration saved!<br>Restarting...</div>
                        </body>
                        </html>
                        """

        cl.send(response)
        cl.close()
        machine.reset()
    else:
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + html
        cl.send(response)
        cl.close()

