#!/usr/bin/python -u
from flask import Flask
from flask import request
import sqlite3
from datetime import datetime
import requests
import os

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("PARCEL_TRACKER_ACCESS_TOKEN")
DISCORD_WEBHOOK_URL = os.getenv("PARCEL_TRACKER_DISCORD_WEBHOOK")

if not os.path.exists('database_files'):
    os.makedirs('database_files')


def insert_data(data):
    conn = sqlite3.connect('database_files/data.db')
    c = conn.cursor()
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS data (
            trackingnumber nvarchar(50),
            checkpoint_date nvarchar(50),
            tracking_detail nvarchar(100),
            delivery_status nvarchar(50)
        )
        ''')
    c.execute("INSERT INTO data (trackingnumber,tracking_detail,delivery_status,checkpoint_date) VALUES (?,?,?,?)", (data))
    conn.commit()
    conn.close()


@app.route('/update', methods=['POST'])
def update_tracking():
    if request.args.get('token') != ACCESS_TOKEN:
        print(request.args.get('token'))
        return 'Invalid access token', 403

    request_content = request.json

    trackingnumber = request_content['data']['tracking_number']
    tracking_detail = request_content['data']['origin_info']['trackinfo'][1]["tracking_detail"]
    delivery_status = request_content['data']['origin_info']['trackinfo'][1]["checkpoint_delivery_status"]
    checkpoint_date = request_content['data']['origin_info']['trackinfo'][1]["checkpoint_date"]

    insert_data((trackingnumber, tracking_detail,
                delivery_status, checkpoint_date))

    checkpoint_timestamp = datetime.strptime(
        checkpoint_date, "%Y-%m-%d %H:%M:%S")

    requests.post(DISCORD_WEBHOOK_URL, json={
        'content': f'<@!258313258853859338>\nNew tracking update for {trackingnumber}:\n{tracking_detail} / {delivery_status} @ <t:{int(checkpoint_timestamp.timestamp())}:f>'
    })

    print("%s: trachking update for: %s" %
          (datetime.now(), request_content['data']['tracking_number']))

    return "OK", 200


@app.route("/health")
def hello_world():
    return "OK", 200
