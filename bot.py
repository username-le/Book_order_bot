from datetime import date
import telebot 
import gspread
from telebot import types
import discord, json, asyncio, gspread
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from discord import client 
import gspread
import pandas as pd
from aiogram.types import ReplyKeyboardRemove,     ReplyKeyboardMarkup, KeyboardButton,     InlineKeyboardMarkup, InlineKeyboardButton

# gc = gspread.oauth(
# credentials_filename='path/to/the/credentials.json',
# authorized_user_filename='path/to/the/authorized_user.json'

gc = gspread.service_account()
sht2 = gc.open_by_url('https://docs.google.com/spreadsheets/d/1Wmf06JxKjdLR_Bol7OHNezrnGKTrjRxivYbLiISIN9o/edit#gid=925157153')

token = '6211937733:AAE42w0HbjlHSDWEG0GHn5fbgPjyPWUyW_M'
bot = telebot.TeleBot(token)


wks = gc.open("books").worksheet('Books_list')
wks2 = gc.open("books").worksheet('Order')

ord_list = []
col_name = wks.col_values(2)
col_author = wks.col_values(1)
book_naming = ',\n'.join(col_name)
author_naming = ',\n'.join(col_author)

df = pd.DataFrame(columns=['time','book','name', 'lastname', 'username', 'phone','comment'])

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True) 
    btn1 = types.KeyboardButton("Я знаю, что почитать")
    btn2 = types.KeyboardButton("Огласите весь список, пожалуйста")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 
                     text="Привет, {0.first_name}! Я бот для выбора книг. Нажмите на значок".format(message.from_user), 
                     reply_markup=markup)
    

        
@bot.message_handler(content_types=['text'])
def func(message):
    if(message.text == "Огласите весь список, пожалуйста"):
        keyboard = types.InlineKeyboardMarkup()
        key_name = types.InlineKeyboardButton(text='По названию', callback_data='name')
        keyboard.add(key_name)
        key_author = types.InlineKeyboardButton(text='По автору', callback_data='author')
        keyboard.add(key_author)
        bot.send_message(message.from_user.id, text='Выберите, как удобнее', reply_markup=keyboard)  

    elif(message.text == "Я знаю, что почитать"):
        bot.send_message(message.chat.id, text= 'Введите название книги')
        bot.register_next_step_handler(message, client_phone)
        
   
    
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "name":
        msg = book_naming
    elif call.data == "author":
        msg = author_naming
    bot.send_message(call.message.chat.id, msg)
        

@bot.message_handler(commands=['number'])
def client_phone(message):
    
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить телефон", request_contact=True)
    
    keyboard.add(button_phone) 
    bot.send_message(message.chat.id, 'Нажмите на кнопку, чтобы отправить номер для связи', reply_markup=keyboard)
      
    time = datetime.datetime.now().strftime("%d.%m.%Y %I:%M")
    df['time'] = [time]
    book_to_ord = str(message.text) 
    df['book'] = [book_to_ord]
    

@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None: 
        name = str(message.contact.first_name)
        lastname = str(message.contact.last_name)
        username = str(message.from_user.username)
       
        phone = str(message.contact.phone_number)
        df['phone'] = [phone]
        df['name'] = [name]
        df['lastname'] = [lastname]
        df['username'] = [username]
     
    bot.send_message(message.chat.id, 'Если нужно, оставьте комментарий или поставьте прочерк')    
    bot.register_next_step_handler(message, client_comment)
    
@bot.message_handler(content_types=['comment'])
def client_comment(message):
    
    comment = str(message.text)
    df['comment'] = [comment]
    df.fillna('')
    for index, row in df.iterrows(): 
        wks2.append_row([row.time, row.book, row.name, row.lastname,row.username, row.phone, row.comment])
    bot.send_message(message.chat.id, 'Спасибо! В ближайшее время мы свяжемся с вами')

bot.polling(none_stop=True)
