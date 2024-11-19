import logging
from parser.SP_Parser import run_parser


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('parser.log', mode='a', encoding='utf-8'),
                        logging.StreamHandler()
                    ])


def main():
    run_parser()


if __name__ == '__main__':
    main()
