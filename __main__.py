import vbancmd

class ManyThings:
    def __init__(self, vban):
        self.vban = vban

    def things(self):
        # Set the mapping of the second input strip
        self.vban.strip[1].A3 = True
        print(f'Output A3 of Strip {self.vban.strip[1].label}: {self.vban.strip[1].A3}')

    def other_things(self):
        # Toggle mute for the leftmost output bus
        self.vban.bus[0].mute = not self.vban.bus[0].mute


def main():
    with vbancmd.connect(kind_id, ip=ip) as vban:
        do = ManyThings(vban)
        do.things()
        do.other_things()

if __name__ == '__main__':
    kind_id = 'potato'
    ip = '<ip address>'

    main()
