import pandas as pd
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update 
from telegram.ext import CallbackContext ,ConversationHandler 
from utils import (
    suggest_closest_matches, get_destinations_for_departure,getCountriesFotDepar, create_duration_keyboard, 
    create_room_selection_keyboard,create_individual_room_keyboard,chunk_list
)
from scraper import (get_package_deal ,get_package_deal_for_month ,get_package_deal_for_flexible)
from messages import messages
from constants import LANGUAGE, MENU,COUNTRY, DEPARTURE, DESTINATION, DATE_SELECTION, DURATION_SELECTION, ROOM_SELECTION,NOTIFY,TYPE,MONTH_SELECTION ,FLEXIBLE_SELECTION,TYPING_DURATION
from datetime import datetime
from telegram.constants import ParseMode
import sqlite3
from itertools import zip_longest


departures_df = pd.read_csv('departure.csv')


async def display_menu(update: Update, context: CallbackContext):
    lang = context.user_data['language']
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton(messages[lang]['SPackage'], callback_data='package')],
        [InlineKeyboardButton(messages[lang]['settingName'], callback_data='settings')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text=messages[lang]['menu'].format(user=user.mention_html()), 
        reply_markup=reply_markup, parse_mode="HTML"
    )



async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("English", callback_data='en')],
        [InlineKeyboardButton("svenska", callback_data='se')],
        [InlineKeyboardButton("العربية", callback_data='ar')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(messages['en']['start'], reply_markup=reply_markup)
    return LANGUAGE

async def select_language(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['language'] = query.data
    await display_menu(update, context)
    return MENU

async def display_menu(update: Update, context: CallbackContext):
    lang = context.user_data['language']
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton(messages[lang]['SPackage'], callback_data='package')],
        [InlineKeyboardButton(messages[lang]['settingName'], callback_data='settings')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text=messages[lang]['menu'].format(user=user.mention_html()), 
        reply_markup=reply_markup, parse_mode="HTML"
    )


async def menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data['language']
    if query.data == 'package':
        await query.edit_message_text(text=messages[lang]['departure'])
        return DEPARTURE
    elif query.data == 'settings':
        await query.edit_message_text(text=messages[lang]['settings'])
        return ConversationHandler.END

async def departure(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    lang = context.user_data['language']
    try:
     departure_choices = departures_df['departure'].unique().tolist()
     suggestions = suggest_closest_matches(user_input, departure_choices)
     keyboard = [[InlineKeyboardButton(suggestion[0], callback_data=suggestion[0])] for suggestion in suggestions]
     reply_markup = InlineKeyboardMarkup(keyboard)
     await update.message.reply_text(text=messages[lang]['oneOf'], reply_markup=reply_markup)
     return DEPARTURE
    except:
      await update.message.reply_text(text=messages[lang]['noDeparture'])
      return DEPARTURE

async def select_departure(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['departure'] = query.data
    countries = getCountriesFotDepar(query.data)
    countries.sort()
    context.user_data['countries'] = countries
    lang = context.user_data['language']
    keyboard = []
    for chunk in chunk_list(countries, 4):
        keyboard.append([InlineKeyboardButton(country, callback_data=country) for country in chunk])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=messages[lang]['country'], reply_markup=reply_markup)
    return COUNTRY

async def select_country(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['country'] = query.data
    destinations = get_destinations_for_departure(context.user_data['departure'] , query.data)
    context.user_data['destinations'] = destinations
    lang = context.user_data['language']
    await query.edit_message_text(text=messages[lang]['destination'])
    return DESTINATION

async def destination(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    lang = context.user_data['language']
    destination_choices = context.user_data['destinations']
    suggestions = suggest_closest_matches(user_input, destination_choices)
    keyboard = [[InlineKeyboardButton(suggestion[0], callback_data=suggestion[0])] for suggestion in suggestions]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
     await update.message.reply_text(text=messages[lang]['oneOf'], reply_markup=reply_markup)
     return DESTINATION
    except:
        await update.message.reply_text(text=messages[lang]['noDestunation'])
        return DEPARTURE

async def select_destination(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['destination'] = query.data
    lang = context.user_data['language']
    
    keyboard = [
        [InlineKeyboardButton("find the cheapest package in month", callback_data='month')],
        [InlineKeyboardButton("find the cheapest package by date", callback_data='date')],
        [InlineKeyboardButton("find the cheapest package by flexible date", callback_data='flexible')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(messages[lang]['type'], reply_markup=reply_markup)
    return TYPE

async def typeSelection(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['type'] = query.data
    lang = context.user_data['language']
    if query.data == 'month':
        await query.edit_message_text(text=messages[lang]['month'])
        return MONTH_SELECTION
    elif query.data == 'date':
        await query.edit_message_text(text=messages[lang]['date'])
        return DATE_SELECTION
    elif query.data == 'flexible':
        await query.edit_message_text(text=messages[lang]['flexible'])
        return FLEXIBLE_SELECTION
    
  

async def monthSelection(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_input = query.data
    try:
        # Validate the date format
        datetime.strptime(user_input, "%Y-%m")
        context.user_data['date'] = user_input
        keyboard = create_duration_keyboard()
        await query.edit_message_text(
            text=messages[context.user_data['language']]['duration'],
            reply_markup=keyboard
        )
        return DURATION_SELECTION
    except ValueError:
        await query.edit_message_text(messages[context.user_data['language']]['invalidDate'])
        return MONTH_SELECTION
 

async def monthSelectionText(update: Update, context: CallbackContext) -> int:

    user_input = update.message.text
    try:
        # Validate the date format
        datetime.strptime(user_input, "%Y-%m")
        context.user_data['date'] = user_input
        keyboard = create_duration_keyboard()
        await update.message.reply_text(
            text=messages[context.user_data['language']]['duration'],
            reply_markup=keyboard
        )
        return DURATION_SELECTION
    except ValueError:
        await update.message.reply_text(messages[context.user_data['language']]['invalidDate'])
        return MONTH_SELECTION



async def flexibleSelection(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_input = query.data
    try:
        # Validate the date format
        context.user_data['flexible'] = user_input
        await query.edit_message_text(text=messages[context.user_data['language']]['date'])
        return DATE_SELECTION
    except ValueError:
        await query.edit_message_text(messages[context.user_data['language']]['invalidDate'])
        return TYPE
 

async def flexibleSelectionText(update: Update, context: CallbackContext) -> int:

    user_input = update.message.text
    try:
        # Validate the date format
        
        context.user_data['flexible'] = user_input
        await update.message.reply_text(text=messages[context.user_data['language']]['date'])
        return DATE_SELECTION
    except ValueError:
        await update.message.reply_text(messages[context.user_data['language']]['invalidDate'])
        return TYPE




async def date_selection_text(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    try:
        # Validate the date format
        datetime.strptime(user_input, "%Y-%m-%d")
        context.user_data['date'] = user_input
        keyboard = create_duration_keyboard()
        await update.message.reply_text(
            text=messages[context.user_data['language']]['duration'],
            reply_markup=keyboard
        )
        return DURATION_SELECTION
    except ValueError:
        await update.message.reply_text(messages[context.user_data['language']]['invalidDate'])
        return DATE_SELECTION

async def date_selection(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_input = query.data
    try:
        # Validate the date format
        datetime.strptime(user_input, "%Y-%m-%d")
        context.user_data['date'] = user_input
        keyboard = create_duration_keyboard()
        await query.edit_message_text(
            text=messages[context.user_data['language']]['duration'],
            reply_markup=keyboard
        )
        return DURATION_SELECTION
    except ValueError:
        await query.edit_message_text(messages[context.user_data['language']]['invalidDate'])
        return DATE_SELECTION

async def duration_selection(update: Update, context: CallbackContext) -> int:
    context.user_data['rooms'] = [{'adults': 1, 'children': 0}]
    keyboard = create_room_selection_keyboard(context.user_data['rooms'] ,context.user_data['language'])    
    query = update.callback_query
    await query.answer()

    if query.data == 'custom_duration':
        
        await query.edit_message_text(
            text=messages[context.user_data['language']]['enter_duration']
        )
        return TYPING_DURATION  
    else:    
       context.user_data['duration'] = query.data
       await query.edit_message_text(
       text=messages[context.user_data['language']]['roomSelection'],
        reply_markup=keyboard
    )
       return ROOM_SELECTION

async def handle_custom_duration(update: Update, context: CallbackContext) -> int:
    
    context.user_data['rooms'] = [{'adults': 1, 'children': 0}]
    keyboard = create_room_selection_keyboard(context.user_data['rooms'] ,context.user_data['language'])       
    user_input = update.message.text
    context.user_data['duration'] = user_input
    await update.message.reply_text(
        text=messages[context.user_data['language']]['roomSelection'],
        reply_markup=keyboard
    )
    return ROOM_SELECTION



async def room_selection(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == 'add_room':
        context.user_data['rooms'].append({'adults': 1, 'children': 0})
    elif query.data.startswith('edit_room_'):
        room_index = int(query.data.split('_')[-1])
        room = context.user_data['rooms'][room_index]
        keyboard = create_individual_room_keyboard(room_index, room, context.user_data['language'])
        await query.edit_message_text(
            text=f"Edit Room {room_index + 1}:",
            reply_markup=keyboard
        )
        return ROOM_SELECTION
    elif query.data.startswith('increase_adults_') or query.data.startswith('decrease_adults_') or \
         query.data.startswith('increase_children_') or query.data.startswith('decrease_children_'):
        room_index = int(query.data.split('_')[-1])
        room = context.user_data['rooms'][room_index]
        if 'increase_adults' in query.data:
            room['adults'] += 1
        elif 'decrease_adults' in query.data and room['adults'] > 1:
            room['adults'] -= 1
        elif 'increase_children' in query.data:
            room['children'] += 1
        elif 'decrease_children' in query.data and room['children'] > 0:
            room['children'] -= 1
        keyboard = create_individual_room_keyboard(room_index, room, context.user_data['language'])
        await query.edit_message_text(
            text=f"Edit Room {room_index + 1}:",
            reply_markup=keyboard
        )
        return ROOM_SELECTION
    elif query.data == 'back_to_room_selection':
        keyboard = create_room_selection_keyboard(context.user_data['rooms'], context.user_data['language'])
        await query.edit_message_text(
            text=messages[context.user_data['language']]['roomSelection'],
            reply_markup=keyboard
        )
        return ROOM_SELECTION
    elif query.data == 'confirm_room_selection':
        rooms = context.user_data['rooms']
        departure = context.user_data['departure']
        
        destination = context.user_data['destination']
        date = context.user_data['date']
        duration = context.user_data['duration']
        await query.edit_message_text(
            text=messages[context.user_data['language']]['searching'].format(
                departure=departure, destination=destination, date=date, duration=duration
            ))
        if context.user_data['type'] == "date":
            package_deal = get_package_deal(departure, destination, date, duration, rooms)
        elif context.user_data['type'] == "month":
           package_deal = get_package_deal_for_month(departure, destination, date, duration, rooms)
        elif context.user_data['type'] == "flexible":
           days = context.user_data['flexible']
           package_deal = get_package_deal_for_flexible(departure, destination, date,days, duration, rooms)     
           
           
                 
        if not package_deal:
            keyboard = [
                
                [InlineKeyboardButton("Back to Menu", callback_data='back_to_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=messages[context.user_data['language']]['notFound'].format(
                    departure=departure, destination=destination, date=date, duration=duration
                ),reply_markup=reply_markup)
            
            return NOTIFY
        else:
            message_text = messages[context.user_data['language']]['result'].format(
                departure=departure, destination=destination, date=date, duration=duration,
                name=package_deal['name'], location=package_deal['location'],
                flight=package_deal['flight'], price=package_deal['price'],
                details=package_deal['details'], url=package_deal['url']
            )
            keyboard = [
                [InlineKeyboardButton("Notify me if price changes", callback_data='notify_price_change')],
                [InlineKeyboardButton("Back to Menu", callback_data='back_to_menu')]
            ]
            context.user_data['price'] = package_deal['floatPrice']
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                text=message_text, reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            return NOTIFY

    keyboard = create_room_selection_keyboard(context.user_data['rooms'], context.user_data['language'])
    await query.edit_message_text(
        text=messages[context.user_data['language']]['roomSelection'],
        reply_markup=keyboard
    )
    return ROOM_SELECTION

async def notify_price_change(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    deal = {
        'departure': context.user_data['departure'],
        'destination': context.user_data['destination'],
        'date': context.user_data['date'],
        'duration': context.user_data['duration'],
        'price': context.user_data['price']
    }

    # Save the user's notification request to SQLite
    conn = sqlite3.connect('user_preferences.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO price_notifications (user_id, departure, destination, date, duration, price)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, deal['departure'], deal['destination'], deal['date'], deal['duration'], deal['price']))
    conn.commit()
    conn.close()
    keyboard = [[InlineKeyboardButton("Back to Menu", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("You will be notified if the price changes." ,reply_markup=reply_markup)
    
    return NOTIFY

async def back_to_menu(update: Update, context: CallbackContext) -> int:
    await display_menu(update, context)
    return MENU

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Operation cancelled. Thank you!")
    return ConversationHandler.END