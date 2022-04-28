from subprocess import run as srun
from telegram.ext import CommandHandler

from bot import LOGGER, dispatcher
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import sendMessage


def shell(update, context):
    message = update.effective_message
    cmd = message.text.split(' ', 1)
    if len(cmd) == 1:
        return sendMessage('No command to execute was given.', context.bot, update.message)
    cmd = cmd[1]
    process = srun(cmd, capture_output=True, shell=True)
    reply = ''
    stderr = process.stderr.decode('utf-8')
    stdout = process.stdout.decode('utf-8')
    if len(stdout) != 0:
        reply += f"*Stdout*\n<code>{stdout}</code>\n"
        LOGGER.info(f"Shell - {cmd} - {stdout}")
    if len(stderr) != 0:
        reply += f"*Stderr*\n<code>{stderr}</code>\n"
        LOGGER.error(f"Shell - {cmd} - {stderr}")
    if len(reply) > 3000:
        with open('shell_output.txt', 'w') as file:
            file.write(reply)
        with open('shell_output.txt', 'rb') as doc:
            context.bot.send_document(
                document=doc,
                filename=doc.name,
                reply_to_message_id=message.message_id,
                chat_id=message.chat_id)
    elif len(reply) != 0:
        sendMessage(reply, context.bot, update.message)
    else:
        sendMessage('No Reply', context.bot, update.message)

def medialink(update, context):
    message = update.effective_message
    cmd = message.text.split(' ', 1)
    if len(cmd) == 1:
        message.reply_text('Send any Direct-URL to generate It\'s detailed Mediainfo')
        return
    cmd = f'mediainfo {cmd[1]}'
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    reply = ''
    stderr = stderr.decode()
    stdout = stdout.decode()
    if stdout:
        reply += f"*Result*\n{stdout}\n"
        # LOGGER.info(f"Shell - {cmd} - {stdout}")
    if stderr:
        reply += f"*Error*\n{stderr}\n"
        # LOGGER.error(f"Shell - {cmd} - {stderr}")
    if len(reply) > 3000:
        with open('mediainfo.txt', 'w') as file:
            file.write(reply)
        with open('mediainfo.txt', 'rb') as doc:
            context.bot.send_document(
                document=doc,
                filename=doc.name,
                reply_to_message_id=message.message_id,
                chat_id=message.chat_id)
    else:
        message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


MEDIALINK_HANDLER = CommandHandler(BotCommands.MedialinkCommand, medialink, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
dispatcher.add_handler(MEDIALINK_HANDLER)
SHELL_HANDLER = CommandHandler(BotCommands.ShellCommand, shell, 
                                                  filters=CustomFilters.owner_filter, run_async=True)
dispatcher.add_handler(SHELL_HANDLER)
