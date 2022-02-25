import vban_cmd
from time import sleep

def main():
    with vban_cmd.connect('potato', ip='ws.local') as vban:
        for i in range(8):
            print(vban.bus[i].levels.all)

if __name__ == '__main__':
    main()
