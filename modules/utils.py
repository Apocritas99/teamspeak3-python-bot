from Moduleloader import *
import Moduleloader
import Bot
import logging
from ts3.TS3Connection import TS3QueryException
__version__ = "0.3"
bot = None
logger = logging.getLogger("bot")


@Moduleloader.setup
def setup(ts3bot):
    global bot
    bot = ts3bot


@command('hello',)
@group('Server Admin',)
def hello(sender, msg):
    Bot.send_msg_to_client(bot.ts3conn, sender, "Hello Admin!")


@command('hello',)
@group('Moderator',)
def hello(sender, msg):
    Bot.send_msg_to_client(bot.ts3conn, sender, "Hello Moderator!")


@command('hello',)
@group('Normal',)
def hello(sender, msg):
    Bot.send_msg_to_client(bot.ts3conn, sender, "Hello Casual!")


@command('kickme', 'fuckme')
@group('.*',)
def kickme(sender, msg):
    ts3conn = bot.ts3conn
    ts3conn.clientkick(sender, 5, "Whatever.")


@command('multimove',)
@group('Server Admin', 'Moderator')
def multi_move(sender, msg):
    """
    Move all clients from one channel to another.
    :param sender: Client id of sender that sent the command.
    :param msg: Sent command.
    """
    channels = msg[len("!multimove "):].split()
    source_name = ""
    dest_name = ""
    source = None
    dest = None
    ts3conn = bot.ts3conn
    if len(channels) < 2:
        if sender != 0:
            Bot.send_msg_to_client(ts3conn, sender, "Usage: multimove source destination")
            return
    elif len(channels) > 2:
        channel_name_list = ts3conn.channel_name_list()
        for channel_name in channel_name_list:
            if msg[len("!multimove "):].startswith(channel_name):
                source_name = channel_name
                dest_name = msg[len("!multimove ") + len(source_name)+1:]
    else:
        source_name = channels[0]
        dest_name = channels[1]
    if source_name == "":
        Bot.send_msg_to_client(ts3conn, sender, "Source channel not found")
        return
    if dest_name == "":
        Bot.send_msg_to_client(ts3conn, sender, "Destination channel not found")
        return
    try:
        channel_candidates = ts3conn.channelfind_by_name(source_name)
        if len(channel_candidates) > 0:
            source = channel_candidates[0].get("cid", '-1')
        if source is None or source == "-1":
            Bot.send_msg_to_client(ts3conn, sender, "Source channel not found")
            return
    except TS3QueryException:
        Bot.send_msg_to_client(ts3conn, sender, "Source channel not found")
    try:
        channel_candidates = ts3conn.channelfind_by_name(dest_name)
        if len(channel_candidates) > 0:
            dest = channel_candidates[0].get("cid", '-1')
        if dest is None or dest == "-1":
            Bot.send_msg_to_client(ts3conn, sender, "Destination channel not found")
            return
    except TS3QueryException:
        Bot.send_msg_to_client(ts3conn, sender, "Destination channel not found")
    try:
        client_list = ts3conn.clientlist()
        client_list = [client for client in client_list if client.get("cid", '-1') == source]
        for client in client_list:
            clid = client.get("clid", '-1')
            logger.info("Found client in channel: " + client.get("client_nickname", "") + " id = " + clid)
            ts3conn.clientmove(int(dest), int(clid))
    except TS3QueryException as e:
        Bot.send_msg_to_client(ts3conn, sender, "Error moving clients: id = " +
                str(e.id) + e.message)


@command('version',)
@group('.*')
def send_version(sender, msg):
    Bot.send_msg_to_client(bot.ts3conn, sender, __version__)


@command('whoami',)
@group('.*')
def whoami(sender, msg):
    Bot.send_msg_to_client(bot.ts3conn, sender, "None of your business!")


@command('stop',)
@group('Server Admin',)
def stop_bot(sender, msg):
    Moduleloader.exit_all()
    bot.ts3conn.quit()
    logger.warning("Bot was quit!")


@command('restart',)
@group('Server Admin', 'Moderator',)
def restart_bot(sender, msg):
    Moduleloader.exit_all()
    bot.ts3conn.quit()
    logger.warning("Bot was quit!")
    import main
    main.restart_program()
