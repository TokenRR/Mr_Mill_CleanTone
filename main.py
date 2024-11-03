import sys
# from interfaces import website
# from interfaces.app import desktop
# from interfaces.bot import tg_bot

def main():
    if len(sys.argv) < 2:
        return
    
    # interface = sys.argv[1].lower()

    # if interface == 'desktop':
    #     desktop.run()
    # elif interface == 'telegram':
    #     tg_bot.run()
    # elif interface == 'web':
    #     website.run()
    # else:
    #     print(f"Unknown interface: {interface}")

if __name__ == "__main__":
    main()
