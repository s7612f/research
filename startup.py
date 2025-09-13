import argparse
import json
import web_interface


def main():
    parser = argparse.ArgumentParser(description='Start web interface with optional mode')
    parser.add_argument('--mode', choices=['research', 'chatbot'], default='research')
    parser.add_argument('--uncensored', action='store_true', help='Start chatbot in uncensored mode')
    args = parser.parse_args()

    with open('config.json') as f:
        config = json.load(f)
    config.setdefault('chatbot', {})['default_mode'] = args.mode
    if args.uncensored:
        config['chatbot']['force_uncensored'] = True
    web_interface.run_server(config)

if __name__ == '__main__':
    main()
