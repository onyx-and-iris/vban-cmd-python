import vban_cmd
from time import sleep

def main():
    with vban_cmd.connect('potato', ip='ws.local') as vban:
        for i in range(100):
            print(vban.bus[3].levels.all)

if __name__ == '__main__':
    main()
