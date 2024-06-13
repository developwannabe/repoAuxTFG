from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
from ultralytics import YOLO
import cv2
import os

class SimplePOSTHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/':
            ctype, pdict = cgi.parse_header(self.headers['content-type'])
            if ctype == 'multipart/form-data':
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                fields = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'}, keep_blank_values=1)
                if 'file' in fields:
                    file_item = fields['file']
                    if file_item.filename:
                        # Guardar el archivo temporalmente
                        temp_path = f"/tmp/{file_item.filename}"
                        with open(temp_path, "wb") as f:
                            f.write(file_item.file.read())
                        
                        # Procesar la imagen
                        output_img = self.eval_image(temp_path)
                        
                        # Enviar la imagen procesada
                        self.send_response(200)
                        self.send_header('Content-type', 'image/jpeg')
                        self.end_headers()
                        self.wfile.write(output_img)

                        # Eliminar el archivo temporal
                        os.remove(temp_path)
                    else:
                        self.send_error(400, "File is missing")
                else:
                    self.send_error(400, "File part not found in the request")
            else:
                self.send_error(400, "Bad Request: The content type must be multipart/form-data.")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
    
    def eval_image(self, image_path):
        model = YOLO('yolov8x.pt')
        results = model(image_path)
        for result in results:
            annotated_img = result.plot(labels=False)  # get CV2 image
            ret, jpeg = cv2.imencode('.jpg', annotated_img)
            return jpeg.tobytes()

def run(server_class=HTTPServer, handler_class=SimplePOSTHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    print("Server started on port 8000.")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
