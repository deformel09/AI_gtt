в папке dataset в нашем случае(Rover-1) лежит coco8.yaml в нем собраны пути к изображениям(файл с путями), 

путь к обученной модели будет лежать по ссылке в консоли после ее обучения

linux команды:

TAB-показывает возможные вариант команд если есть другие совпадения, если их мало поочередно будет выбирать

sudo - Права администратора(если вылезает permission dined, вставляется в начале команды) 
cat -  Просмотр текста файла (cat ~/catkin_ws/src/clover/clover/launch/clover.launch)
(sudo) nano - Текстовый редактор (использовать вместе с sudo, применяется как cat)
cd - перемещение по папкам![[Pasted image 20260318125537.png|516]]
ls - команда просмотра содержимого каталога (если что можно смотреть содержимое определенной папки пользуясь путем ls catkin_ws/)
pip3 - установщик(библиотек для python, pip3 install (название библиотеки) пример pip3 install opencv-python )
python3 - (запускать .py файлы, можно так же пользоваться путем пример python3 camera.py)

пароль от клевера: "raspberry"


doc:
[ultralytics](https://docs.ultralytics.com/modes/train/)
[roboflow]( https://docs.roboflow.com/developer/python-sdk/using-the-python-sdk)
[clover](https://clover.coex.tech/ru)

Модуль А:
- Обязательно создаем папку даже если пустая и файлы тоже
- Прошивка через balenaeatcher прошивку брать из документации clover лежит в doc
- Установка библиотек на происходит с помощью команды pip3 install (название библиотеки) пример pip3 install opencv-python, pip3 install ros
- Настройка камеры - настройка фокусного расстояние, и просмотр clover.launch файл на правильность расположения камеры 
	- направление обзора камеры `direction_z`: вниз (`down`) или вверх (`up`); 
	- направление, в которое указывает шлейф камеры `direction_y`: назад (`backward`) или вперед (`forward`).
