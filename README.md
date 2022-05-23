# Музыкальный бот для дискорда #

# Что это? #
Это музыкальный бот для дискорда, взаимодействующий с api яндекс музыки. На момент его написания(в октябре) в интернете было что-то похожее, но с очень ограниченным функционалом и не особо рабочее. Этот бот работает и треки воспроизводит стабильно.

### Важно! Бот написан под винду) ###

## Инструкция по использованию ##
* Переходим по ссылочке: https://discord.com/api/oauth2/authorize?client_id=899248710444281876&permissions=8&scope=bot. Вылезает предложение добавить бота на ваш сервер, выбираем сервер, на который хотим его добавить.
* Бот появился на сервере, но он не онлайн. Нужно запустить его локально на нашем пк:
  + Скачиваем архив из гита, октрываем его. Внутри еще один архив с exe-шником проигрывателя ffmpeg.exe. Этот архив тоже распоковываем.
  + Создаём проект в пайчарме. Все разархивированные ранее файлы, перемещаем туда.
  + Пайчарм предлагает нам подтянуть библиотеки, прописанные в **requirements.txt**. Дополнительн в терминал пайчарма прописываем **python3 -m pip install -U discord.py[voice]**
  + В файл **config.json** пишем свой логин и пароль от аккаунта яндекс
  + Запускаем файл **main.py**. Если всё хорошо, то в консоли будет напдпись *Бот работает* и статус бот в дискорде станет онлайн
* Теперь про то, как пользоваться ботом:
  + Чтобы узнать комманды пишем *]help* в чат дискорда
  + Пишем ]join, чтобы добавить бота в голосовой канал, в котором мы находимся
  + Ну а дальше следуем руководству из ]help :)
  + Чтобы кикнуть бота, пишем в чат ]leave
