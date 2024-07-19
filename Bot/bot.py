import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
from handlers import (
    start, select_language, menu, departure, select_departure, 
    destination, select_destination, date_selection_text, 
    date_selection, duration_selection, room_selection, select_country,
     cancel ,notify_price_change , back_to_menu,typeSelection,monthSelection ,monthSelectionText,flexibleSelectionText,flexibleSelection,handle_custom_duration
)
from constants import LANGUAGE, MENU, COUNTRY, DEPARTURE, DESTINATION, DATE_SELECTION, DURATION_SELECTION, ROOM_SELECTION,NOTIFY,TYPE,MONTH_SELECTION ,FLEXIBLE_SELECTION,TYPING_DURATION

from utils import (
   create_database
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the bot."""
    application = Application.builder().token("7041455118:AAGvfiLkxY3KLsukDJiczePrhkWrqbpwS9U").build()
    create_database()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [CallbackQueryHandler(select_language)],
             MENU: [CallbackQueryHandler(menu)],
            DEPARTURE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, departure),
                CallbackQueryHandler(select_departure)
            ],
            DESTINATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, destination),
                CallbackQueryHandler(select_destination)
            ]
            ,COUNTRY: [CallbackQueryHandler(select_country)],
            TYPE: [
                CallbackQueryHandler(typeSelection)
            ],
    MONTH_SELECTION: [ MessageHandler(filters.TEXT & ~filters.COMMAND, monthSelectionText),
                CallbackQueryHandler(monthSelection)
                              

            ],
    FLEXIBLE_SELECTION: [ MessageHandler(filters.TEXT & ~filters.COMMAND, flexibleSelectionText),
                CallbackQueryHandler(flexibleSelection)
                              

            ],
            DATE_SELECTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, date_selection_text),
                CallbackQueryHandler(date_selection)
            ],
            DURATION_SELECTION: [CallbackQueryHandler(duration_selection)],
            TYPING_DURATION:[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_duration)],
            ROOM_SELECTION: [CallbackQueryHandler(room_selection)],
            NOTIFY: [
                CallbackQueryHandler(notify_price_change, pattern='notify_price_change'),
                CallbackQueryHandler(back_to_menu, pattern='back_to_menu')
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
