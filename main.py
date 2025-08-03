import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# Configuration - Get token from environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '2048178042:AAHBeWLbetY60rnaSI0EwIRVpfwC9S7vnhM')
API_HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://address.free.nf',
    'referer': 'https://address.free.nf/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'x-master-key': '$2a$10$J3gIK1CkGigFQ44wiHU7rOvllDUrMSPANQ7p3Ubht9OP8VECMUrw6'
}
API_URL = 'https://api.jsonbin.io/v3/b/687e4ddaae596e708fb94ce8/latest'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message and fetch country list"""
    await update.message.reply_text(
        "🌍 Welcome to the Address Bot!\n"
        "Fetching available countries..."
    )
    
    try:
        response = requests.get(API_URL, headers=API_HEADERS)
        if response.status_code == 200:
            data = response.json()
            records = data['record']
            
            # Create country map
            country_map = {}
            for entry in records:
                country = entry.get('country', '').strip()
                if country and country not in country_map:
                    country_map[country] = entry
            
            # Store in context for later use
            context.user_data['country_map'] = country_map
            
            # Create keyboard
            keyboard = [
                [InlineKeyboardButton(country, callback_data=country)]
                for country in sorted(country_map.keys())
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "Please select a country:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "❌ Failed to fetch country data. Please try again later."
            )
    except Exception as e:
        await update.message.reply_text(
            f"⚠️ An error occurred: {str(e)}"
        )

async def handle_country_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle country selection from inline keyboard"""
    query = update.callback_query
    await query.answer()
    
    country = query.data
    country_map = context.user_data.get('country_map', {})
    
    if country in country_map:
        info = country_map[country]
        
        # Clean up data
        phone = info.get('phone_number') or info.get('phone e_number') or "N/A"
        postal = info.get('postal_code') or info.get('p postal_code') or "N/A"
        gender = info.get('gender') or info.get('g gender') or "N/A"
        city = info.get('city_town_village') or info.get('city_tow wn_village') or "N/A"
        street = info.get('street') or "N/A"
        name = info.get('full_name') or "N/A"
        flag = info.get('flag') or ""
        
        # Format response
        response = (
            f"🏛️ Official Address for {country} {flag}\n\n"
            f"🔹 Full Name: {name}\n"
            f"🔹 Street: {street}\n"
            f"🔹 City/Town: {city}\n"
            f"🔹 Postal Code: {postal}\n"
            f"🔹 Entity Type: {gender}\n"
            f"🔹 Phone Number: {phone}"
        )
        
        await query.edit_message_text(response)
    else:
        await query.edit_message_text("❌ Country data not found. Please try /start again.")

def main():
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_country_selection))
    
    # Start the Bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
