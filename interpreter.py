import bkbot

import os
import sys
import configparser

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8-sig')
commands = {value: key for key, value in config['COMMANDS'].items()}
system_commands = config['SYSTEM COMMANDS']
messages = config['MESSAGES']

def detect_routes(path):
    routes = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if filename.endswith('.txt'):
                routes.append(filename)
        break
    return routes

def print_routes(routes):
    print(messages['available_routes'])
    for no, route in enumerate(routes, 1):
        print('  {0:2}. {1}'.format(no, route[:-4]))

def print_commands():
    print(messages['available_commands'])
    for command in sorted(set(commands) | set(system_commands.values())):
        print(command)

def run(fh, bot):
    if fh == sys.stdin:
        print('> ', end='')
        sys.stdout.flush()
        
    for string in map(lambda x: x.strip(), fh):
        command, *arguments = map(lambda x: x.strip(), string.split(':'))
        for i in range(len(arguments)):
            try:
                arguments[i] = int(arguments[i])
            except ValueError:
                pass

        execute_command(command, arguments)
        
        if fh == sys.stdin:
            print('> ', end='')
            sys.stdout.flush()

def execute_command(command, arguments):
    if command in commands:
        print(command)
        try:
            exec('bot.{0}(*arguments)'.format(commands[command]))
        except bkbot.BotParsingError as err:
            print(messages['parsing_error'])
        except bkbot.BotUsageError:
            print(messages['usage_error'])
        except Exception as err:
            print(messages['error'])
            print(err)
    elif command.startswith('%'):
        try:
            route = command[1:]
            route_fh = open('routes\\' + route + '.txt')
            print(messages['route'] + ': ' + route)
            run(route_fh, bot)
        except FileNotFoundError:
            print(messages['route_name_error'])
    elif command == system_commands['debug']:
        route_fh = sys.stdin
        run(route_fh, bot)
    elif command == system_commands['exit']:
        return
    elif command == system_commands['commands']:
        print_commands()
    elif command == system_commands['routes']:
        routes = detect_routes('routes')
        print_routes(routes)
    else:
        print(messages['command_error'])


def main():
    routes = detect_routes('routes')

    with bkbot.Engine(silent=False) as engine:
        login = config['USER']['login']
        password = config['USER']['password']
        print(messages['welcome'])
        print(messages['loading'])
        bot = bkbot.Bot(login, password, engine)
        print_routes(routes)

        fh = sys.stdin
        run(fh, bot)

main()
