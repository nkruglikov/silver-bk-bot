import bkbot

import os
import sys
import configparser

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8-sig')
commands = {value: key for key, value in config['COMMANDS'].items()}

def detect_routes(path):
    routes = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if filename.endswith('.txt'):
                routes.append(filename)
        break
    return routes

def select_route():
    print('Available routes:')
    for no, route in enumerate(routes, 1):
        print('  {0:2}. {1}'.format(no, route[:-4]))

#    no = int(input('Number: ')) - 1
#    route = routes[no]
#    return route

def run(fh, bot):
    for string in map(lambda x: x.strip(), fh):
        command, *arguments = map(lambda x: x.strip(), string.split(':'))
        for i in range(len(arguments)):
            try:
                arguments[i] = int(arguments[i])
            except ValueError:
                pass

        if command in commands:
            print(command)
            exec('bot.{0}(*arguments)'.format(commands[command]))
        elif command.startswith('%'):
            try:
                route = command[1:]
                print('Route: ' + route)
                route_fh = open('routes\\' + route + '.txt')
                run(route_fh, bot)
            except FileNotFoundError:
                print('Wrong route name')
        elif command == 'ОТЛАДКА':
            route_fh = sys.stdin
            run(route_fh, bot)
        elif command == 'ВЫХОД':
            return
        else:
            print('Wrong command!')


routes = detect_routes('routes')
route = select_route()

with bkbot.Engine(silent=False) as engine:
    login = config['USER']['login']
    password = config['USER']['password']
    bot = bkbot.Bot(login, password, engine)

    #fh = open('routes\\' + route)
    fh = sys.stdin
    run(fh, bot)
