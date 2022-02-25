import vban_cmd
from time import sleep

def main():
    with vban_cmd.connect('potato', ip='ws.local') as vban:
        pass

if __name__ == '__main__':
    main()
