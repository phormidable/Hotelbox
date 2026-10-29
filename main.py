# main.py
import sys
from game_controller import GameController


def main():
    controller = GameController()
    controller.run()


if __name__ == "__main__":
    main()
    sys.exit()