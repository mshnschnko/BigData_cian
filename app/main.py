import time
import logging
from parser.SP_Parser import run_parser


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('parser.log', mode='a'),
                        logging.StreamHandler()
                    ])


def main():
    while True:
        logging.info("I'm here!")
        # run_parser()
        time.sleep(5)


if __name__ == '__main__':
    main()
