import roboflow
from ultralytics import YOLO
rf = roboflow.Roboflow(api_key="99kj8GRsDU3ak1hSDEls") #указываем api ключ roboflow
project = rf.workspace("nofjwwv817-segez-fun").project("my-first-project-9mgrf") # указываем из ссылки проекта пример(https://app.roboflow.com/vova-22eef/rover-drsn7/1)
version = project.version(1) # версия проекта идет от еденицы
dataset = version.download("yolov8") # указываем Аннотацию данных (аннотация данных — условно тип данных где указываеться выделения классов детекции)

model = YOLO("yolov8n.pt") # какой версии YOLO мы хотим получить модель
results = model.train(data="./My-First-Project-1/data.yaml", epochs=100, imgsz=640) # указываем на yaml файл в датасете, epochs=100(количество поколений),imgsz=640(размер изображения в пикселях можно указать ш. и в. imgsz = (600, 800))