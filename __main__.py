import vban_cmd
from time import sleep

def test_set_parameter():
    with vban_cmd.connect('potato', ip='ws.local') as vban:
        for param in ['A1']:
            for i in range(3):
                setattr(vban.strip[i], param, True)
                print(getattr(vban.strip[i], param))
                setattr(vban.strip[i], param, False)
                print(getattr(vban.strip[i], param))


if __name__ == '__main__':
    test_set_parameter()
