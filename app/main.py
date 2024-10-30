import time
import logging

# TODO:
# from parser import <оформить как класс или функцию, чтобы вызывать из мейна>

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('parser.log', mode='a'),
                        logging.StreamHandler()
                    ])

def main():
    while True:
        logging.info("I'm here!")
        time.sleep(5)

if __name__ == '__main__':
    main()