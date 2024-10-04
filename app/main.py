import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    while True:
        logging.info("I'm here!")
        time.sleep(5)

if __name__ == '__main__':
    main()