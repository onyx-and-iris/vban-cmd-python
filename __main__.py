import vban_cmd
from time import sleep

def main():
    with vban_cmd.connect('potato', ip='ws.local') as vban:
        for i in range(100):
            print(vban.strip[5].A1)
            print(vban.strip[5].A2)

if __name__ == '__main__':
    main()
