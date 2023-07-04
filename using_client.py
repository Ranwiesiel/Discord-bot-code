import discord
from discord.ext import commands
from replit import db
import logging
import logging.handlers
import os
import requests
import json
import random as rd

intents = discord.Intents.default()
intents.message_content = True 

client = discord.Client(intents=intents)

if "responding" not in db.keys():
  db["responding"]= True

#tambah dan hapus database
def update_encouragements(pesan_baru):
  if "penambahan" in db.keys():
    penambahan= db["penambahan"]
    penambahan.append(pesan_baru)
    db["penambahan"]=penambahan
  else:
    db["penambahan"]= [pesan_baru]
    
def delete_encouragement(index):
  penambahan = db["penambahan"]
  if len(penambahan) > index:
    del penambahan[index]
  db["penambahan"]= penambahan

#macam-macam reaksi bot
kata_gaje= [
  "malas",
  "mager",
  "gak bisa"
]
respon_bot= [
  "Sabar banh..",
  "Enjoyy aja!",
  "Bisa bangg!!"
]


@client.event
async def on_message(pesan):
  if pesan.author == client.user:
    return

  isi_pesan = pesan.content
  if db["responding"]:
    options = respon_bot
    if "penambahan" in db.keys():
      options+= db["penambahan"]
      #options.append(db["penambahan"])   
    if any(kata in isi_pesan for kata in kata_gaje):
      await pesan.channel.send(rd.choice(options))
    
  if isi_pesan.startswith("$tambah"):
    penambahan_pesan= isi_pesan.split("$tambah ",1)[1]
    update_encouragements(penambahan_pesan)
    await pesan.channel.send("Pesan telah ditambahkan.")
    
  if isi_pesan.startswith("$hapus"):
    penambahan= []
    if "penambahan" in db.keys():
      for ind,kata in enumerate(db["penambahan"]):
        isi= isi_pesan.split("$hapus",1)[1].strip()
        if kata in isi:
          delete_encouragement(ind)
          penambahan= db["penambahan"]
    await pesan.channel.send(list(penambahan))
    
  if isi_pesan.startswith("$isi"):
    penambahan= []
    if "penambahan" in db.keys():
      penambahan= db["penambahan"]
    await pesan.channel.send(list(penambahan))
    
  if isi_pesan.startswith("$respon"):
    value= isi_pesan.split("$respon ",1)[1]
    
    if value.lower() == "true":
      db["responding"]= True
      await pesan.channel.send("Respon aktif.")
      
    if value.lower() == "false":
      db["responding"]= False
      await pesan.channel.send("Respon mati.")


my_secret = os.environ['Bot']
client.run(my_secret, log_handler=None)