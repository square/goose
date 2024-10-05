from goose.synopsis.toolkit import active_files, get_os
from goose._logger import get_logger
from goose.utils.ask import ask_an_ai
from exchange.moderators import Moderator
from exchange.exchange import Exchange
from exchange.content import Text
from exchange.message import Message
from exchange.moderators.passive import PassiveModerator

class Synopsis(Moderator):
    """ Synopsis rewrites the chat into a single input message after every reply

    The goal of synopsis is to remove history artifacts that eat up the context budget
    and provide opportunities for the model to attend to the wrong content.

    When?
       - After every message (mostly tool use), we apply automatic context management
       - After every user input, we use an LLM to curate the context
    This is a compromise for speed, where we do fast updates as frequently as possible

    What?
      - [Automatic] Current file context
      - [Automatic] Current sytem state
      - (TODO) [Automatic] Loaded memories
      - [Curated] Summary of the plan, next step to solve
      - [Curated] Summary of the discussion so far

    At the moment, this is tightly coupled to the StatefulDeveloper toolkit as base. We
    could revisit how that works, because this applications shows some limitations in how the
    goose state is managed.
    """
    def __init__(self) -> None:
        super().__init__()
        self.curated_context = ""

    def rewrite(self, exchange: Exchange):
        logging = get_logger()

        # Get the last message, which would be either a user text or a user tool use
        last_message: Message = exchange.messages[-1]

        # The first message is the synopsis, after that we might have a number of tool usage, until we hit a new user message
        # [synopsis, tool_use, tool_result, tool_use, tool_result, ..., assistant_message, user_message]

        # Always update automated state
        system_context = self.get_system_context()

        logging.info([(message.role, message.content[0].__class__) for message in exchange.messages])
        if isinstance(last_message.content[0], Text):
            # We're in the state:
            # [synopsis, tool_use, tool_result, ..., user_message]
            # and we'll reset it to:
            # [synopsis]
            logging.info("full update")
            self.curated_context = self.get_curated_context(exchange)
            synopsis = Message.user('\n'.join((system_context, self.curated_context)))
            exchange.messages.clear()
            exchange.add(synopsis)
        else:
            # We're in the state
            # [synopsis, ..., tool_use, tool_result]
            # and we'll keep going but updated the synopsis
            # [new_synopsis, ..., tool_use, tool_result]
            logging.info("system only update")
            synopsis = Message.user('\n'.join((system_context, self.curated_context)))
            exchange.messages[0] = synopsis

        with open('synopsis.md', 'w') as f:
            f.write(synopsis.text)

    def get_system_context(self):
        return Message.load("system.md", files=active_files.values(), os=get_os()).text

    def get_curated_context(self, exchange):
        logging = get_logger()
        logging.info(exchange.messages)
        message = Message.load("curate.md", tools=exchange.tools, messages=exchange.messages)
        logging.info(message.text)
        exchange = exchange.replace(moderator=PassiveModerator(), tools=(), system='', messages=[])
        exchange.add(message)
        return exchange.generate().text
