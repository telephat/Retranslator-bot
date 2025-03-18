import requests
import configparser
import json
import datetime, time
import telebot
import os
from dotenv import load_dotenv

load_dotenv("data.env")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
api_token = os.environ.get("api_token")
api_url = os.environ.get("api_url")
problems_dict = {}
current_time = round(time.time())
severity = 2
problems_list = []

def api_request(method, params, token = None):
    headers = {'Content-Type': 'application/json-rpc'}
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params, 
        "id": 1,
        "auth": token
    }

    try:
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    
def add_problem(dict, host, data):
    if host in dict:
        if isinstance(dict[host], list):
            dict[host].append(data)
        else:
            dict[host] = dict[host] + list(data)
    else:
        dict[host] = []
        dict[host].append(data)
    return dict

def seconds_to_dhm(seconds):
    if seconds != 0:
        days = seconds//(3600*24)
        seconds %= 3600*24
        hours = seconds//3600
        seconds %= 3600
        minutes = seconds//60
        result = f"{days}d {hours}h {minutes}m"
    return result

def get_problem_list(groupid):
    objectid = "0"
    problems_list = []
    problems_dict = {}
    problem_req = {
        "output": "extend",
        "selectAcknowledges": "extend",
        "selectTags": "extend",
        "selectSuppressionData": "extend",
        "groupids": groupid,
        #"recent": True,
        "sortfield": ["eventid"],
        "sortorder": "DESC"
    }
    problem_response = api_request("problem.get", problem_req, api_token)
    for each in problem_response['result']:
        if int(each['severity']) >= severity:
            problems_list.append((each['objectid'], each['clock'], each['r_clock']))
    for each in problems_list:
        objectid = each[0]
        trigger_req = {
            "triggerids": objectid,  
            "output": ["description"], 
            "selectHosts": ["host", "hostid"]
        }
        hostid_response = api_request("trigger.get", trigger_req, api_token)
        hostname = hostid_response['result'][0]['hosts'][0]['host']
        problemname = hostid_response['result'][0]['description']
        problemtime_seconds = int(each[1])
        problemtime = seconds_to_dhm(current_time - problemtime_seconds)
        if each[2] == "0":
            problemresolved = "X"
        else:
            problemresolved = "Y"
        add_problem(problems_dict, hostname, [problemname, problemtime, problemresolved])
    
    return problems_dict    

#print(get_problem_list(41))
todisplay = ""
# for host, data in get_problem_list(41).items():
#     todisplay += f"*{host}* \n"
#     for problem in data:
#         #print(f"\t{problem[1]}    {problem[0]}")
#         todisplay += f"\t{problem[1]}    {problem[0]}\n"



bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Компакт-бот оповещений заббикса")

@bot.message_handler(commands=['getcurrentproblemsilo'])
def send_status(message):
    todisplay = ""
    for host, data in get_problem_list(41).items():
        todisplay += f"*{host}* \n"
        for problem in data:
            #print(f"\t{problem[1]}    {problem[0]}")
            todisplay += f"\t{problem[1]}    {problem[0]}\n"
    bot.send_message(message.chat.id, todisplay, parse_mode="Markdown")

@bot.message_handler(commands=['agent_problems'])
def send_status(message):
    todisplay = ""
    for zabbix_group in [40, 39, 38, 37, 36]:
        for host, data in get_problem_list(zabbix_group).items():
            todisplay += f"*{host}* \n"
            for problem in data:
                #print(f"\t{problem[1]}    {problem[0]}")
                todisplay += f"\t{problem[1]}    {problem[0]}\n"
    bot.send_message(message.chat.id, todisplay, parse_mode="Markdown")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.infinity_polling()
#print(todisplay)

#группы 40, 39, 38, 37, 36
#группа 41
