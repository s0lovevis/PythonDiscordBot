import asyncio
import random
import discord
import shutil
import os
from discord.ext.commands import Bot
from discord.ext import commands


class YamBot(Bot):
    """
    Основной класс бота.
    """

    async def on_ready(self):
        """
        Уведомляет разработчика об успешном запуске бота.
        """
        print('Бот работает')

    async def on_message(self, message):
        """
        Позволяет принимать команды от других ботов.
        """
        ctx = await self.get_context(message)
        await self.invoke(ctx)


def data_clear():
    """
    Очищает временное хранилище музыки.
    """
    shutil.rmtree(f'music', ignore_errors=True)
    os.makedirs('music', exist_ok=True)


class YamCommands(commands.Cog):
    """
    Содержит команды для класса бота YamBot.
    """

    def __init__(self, bot, yam_client):
        """
        Конструктор класса.
        bot: главный класс(YamBot), для которого предназначены функции YamCommands.
        yam_client: клиент Яндекс Музыки.
        """
        self.bot = bot
        self.yam_client = yam_client
        self.track_list = []
        self.is_playing = False

    @commands.command(aliases=['h'])
    async def help(self, ctx):
        """
        Выводит список доступных команд и их описание.
        ctx: Класс Context из discord.py, содержащий информацию о боте.
        """

        pr = self.bot.command_prefix
        help_text = f'**{pr}play, {pr}p **- Выполнить поиск по названию\n' \
                    f'**{pr}play_artist, {pr}pa **- Выполнить поиск альбомов по имени исполнителя\n' \
                    f'**{pr}show_playlist, {pr}pl **- Отобразить очередь воспроизведения\n' \
                    f'**{pr}skip, {pr}s **- Пропустить трек. Можно ввести как число треков, так и их номера (]s 2-5)\n' \
                    f'**{pr}join, {pr}j **- Переместить бота в ваш канал.'
        await ctx.send(help_text)

    @commands.command()
    async def silent_join(self, ctx):
        """
        Подключает бота к каналу пользователя.
        """
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

    @commands.command(aliases=['j'])
    async def join(self, ctx):
        """
        Подключает бота к каналу пользователя и уведомляет его об этом.
        ctx: Класс Context из discord.py, содержащий информацию о боте.
        """
        await self.silent_join(ctx)
        await ctx.send(f'Подключен к каналу {ctx.author.voice.channel}')

    @commands.command(aliases=['l'])
    async def leave(self, ctx):
        """
        Отключает бота от канала.
        ctx: Класс Context из discord.py, содержащий информацию о боте.
        """
        await ctx.voice_client.disconnect()
        self.track_list = []
        data_clear()
        await ctx.send(f'Отключен от канала {ctx.author.voice.channel}')

    @commands.command(aliases=['p'])
    async def play(self, ctx, *search_input):
        """
        Производит поиск треков и альбомов с названием search_input и воспроизводит один из них.
        search_input: Название трека, по которому выполняется поиск.
        ctx: Класс Context из discord.py, содержащий информацию о боте.
        """
        search_input = ' '.join(search_input)
        await self.silent_join(ctx)

        track_search = self.yam_client.search(search_input, type_='track')['tracks']['results']
        album_search = self.yam_client.search(search_input, type_='album')["albums"]["results"]

        if len(track_search) > 0:
            track_choose = f'Выберите трек, написав его номер в списке:\n'
            for i in range(min(4, len(track_search))):
                track_choose += f'{i + 1}. {track_search[i]["title"]} от {track_search[i]["artists"][0]["name"]}\n'
            await ctx.send(track_choose)

        if len(album_search) > 0:
            album_choose = f'Выберите альбом, написав его номер в списке:\n'
            for i in range(min(4, len(album_search))):
                if album_search[i]["artists"]:
                    album_choose += f'{min(4, len(track_search)) + i + 1}. **{album_search[i]["title"]}**' \
                                    f' от {album_search[i]["artists"][0]["name"]}, ' \
                                    f'треков: {album_search[i]["track_count"]}\n'
                else:
                    album_choose += f'{min(4, len(track_search)) + i + 1}. **{album_search[i]["title"]}** ' \
                                    f'от неизвестного исполнителя, треков: {album_search[i]["track_count"]}\n'
            await ctx.send(album_choose)

        msg = await self.bot.wait_for("message")
        track_num = int(msg.content) - 1

        if track_num < min(4, len(track_search)):
            self.download(track_search[track_num])
            if ctx.voice_client.is_playing():
                await ctx.send(f'**{self.track_list[-1]["name"]}** '
                               f'от {self.track_list[-1]["author"]} Добавлен в очередь')
        else:
            album_id = album_search[track_num - min(4, len(track_search))]["id"]
            album_tracks = self.yam_client.albums_with_tracks(album_id)["volumes"][0]
            for i in album_tracks:
                self.download(i)
            await ctx.send(f'Треков добавлено в очередь: {len(album_tracks)}')

        if not self.is_playing:
            await self.start_player(ctx)

    @commands.command(aliases=['pa'])
    async def play_artist(self, ctx, *artist_name):
        """
        Производит поиск всех альбомов исполнителя artist_name и воспроизводит один из них.
        artist_name: имя искомого музыкального исполнителя.
        ctx: Класс Context из discord.py, содержащий информацию о боте.
        """
        artist_name = ' '.join(artist_name)
        await self.silent_join(ctx)

        artist_search = self.yam_client.search(artist_name, type_='artist')["artists"]["results"]
        artist_albums = self.yam_client.artists_direct_albums(artist_search[0]["id"])
        sorted_artist_albums = sorted(artist_albums, key=lambda k: k['year'], reverse=True)

        artist_album_choose = f'Выберите альбом, написав его номер в списке:\n'
        for i in range(len(sorted_artist_albums)):
            artist_album_choose += f'{i + 1}. **{sorted_artist_albums[i]["title"]}**, ' \
                                   f'{sorted_artist_albums[i]["year"]}, ' \
                                   f'треков: {sorted_artist_albums[i]["track_count"]}\n'
        await ctx.send(artist_album_choose)

        msg = await self.bot.wait_for("message")
        if msg.content.isdigit():
            track_num = int(msg.content) - 1

            album_id = sorted_artist_albums[track_num]["id"]
            artist_album_tracks = self.yam_client.albums_with_tracks(album_id)["volumes"][0]
            for i in artist_album_tracks:
                self.download(i)
            await ctx.send(f'Треков добавлено в очередь: {len(artist_album_tracks)}')

            if not self.is_playing:
                await self.start_player(ctx)

    async def start_player(self, ctx):
        """
        Воспроизводит треки из очереди self.track_list.
        ctx: Класс Context из discord.py, содержащий информацию о боте.
        """
        self.is_playing = True
        while self.track_list:
            if not ctx.voice_client.is_playing():
                await self.play_track(ctx, self.track_list[0])
                del self.track_list[0]
            await asyncio.sleep(1)
        self.is_playing = False
        data_clear()

    @commands.command()
    async def play_track(self, ctx, track):
        track = eval(str(track))
        """
        Воспроизводит трек `track`.
        ctx: Класс Context из discord.py, содержащий информацию о боте.
        track: словарь, характеризующий воспроизводимый трек.
        """
        ctx.voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=f'{track["route"]}'))
        await ctx.send(f'Воспроизведение **{track["name"]}** от {track["author"]}')

    @commands.command(aliases=['pl'])
    async def show_playlist(self, ctx):
        """
        Выводит плейлист треков.
        ctx: Класс Context из discord.py, содержащий информацию о боте.
        """
        show_text = f'Треков в очереди {len(self.track_list)}:\n'
        for i in range(len(self.track_list)):
            show_text += f'{i + 1}. **{self.track_list[i]["name"]}** от {self.track_list[i]["author"]}\n'
        await ctx.send(show_text)

    @commands.command(aliases=['s'])
    async def skip(self, ctx, skip_amount=''):
        """
        Пропускает заданное число треков.
        ctx: Класс Context из discord.py, содержащий информацию о боте.
        skip_amount: Количество пропускаемых треков. Может быть как числом, так и интервалом(3-7)
        """
        if '-' in skip_amount:
            skip_amount = list(map(int, skip_amount.split('-')))
            del self.track_list[skip_amount[0] - 1:skip_amount[1] - 1]
            await ctx.send(f'Из плейлиста удалены треки с {skip_amount[0]} по {skip_amount[1]}')

        elif skip_amount.isalnum():
            del self.track_list[:int(skip_amount) - 1]
            await ctx.send(f'Из плейлиста удалено {skip_amount} треков')
            ctx.voice_client.stop()
        elif skip_amount == '':
            await ctx.send(f'Трек пропущен')
            ctx.voice_client.stop()

    def download(self, track):
        """
        Скачивает трек и добавляет его в плейлист.
        track: Название трека, который мы скачиваем
        """
        track_route = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(10))
        os.makedirs('music', exist_ok=True)
        track.download(f'music\\{track_route}.mp3', bitrate_in_kbps=192)
        track_data = {
            "route": f'music\\{track_route}.mp3',
            "name": track["title"],
            "author": track["artists"][0]["name"]
        }
        self.track_list.append(track_data)
