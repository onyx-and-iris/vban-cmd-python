import vban_cmd

def main():
    with vban_cmd.connect('potato', ip=ip, port=port, streamname=streamname, bps=bps, channel=channel) as vban:
        for param in ['A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'mono', 'mute']:
            setattr(vban.strip[0], param, True)
            print(getattr(vban.strip[0], param))
            setattr(vban.strip[0], param, False)
            print(getattr(vban.strip[0], param))


if __name__ == '__main__':
    kind_id = 'potato'
    ip = 'ws.local'
    port=6980
    streamname = 'testing'
    bps = 57600
    channel=3

    main()
