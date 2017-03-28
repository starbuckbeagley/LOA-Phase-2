"""
Lines of Action client
Starbuck Beagley
"""

import socket
import argparse
import Player
import Display
import pickle
import time


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--computer_player", help="computer opponent is desired", action="store_true")
    args = parser.parse_args()

    computer_player = False

    if args.computer_player:
        computer_player = True

    rows = 8
    cols = 8
    player1 = Player.Player(1, 'x')
    player2 = Player.Player(2, 'o')
    display = Display.Display(rows, cols)
    current_player = player1

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = 7667
    s.connect((host, port))

    if computer_player:
        s.sendall(pickle.dumps([0, 1, []]))
    else:
        s.sendall(pickle.dumps([0, 0, []]))
    msg_in = s.recv(1024)
    msg = pickle.loads(msg_in)
    if msg[0] == 5:
        print(msg[1])
        return 0

    while 1:
        display.show_board(msg[2])
        time.sleep(1)

        s.sendall(pickle.dumps([8, 1, []]))
        msg_in = s.recv(1024)
        msg = pickle.loads(msg_in)

        if msg[0] == 8:
            if msg[1] != 0:
                print(msg[1])
                time.sleep(1)
                break
        else:
            print("Error receiving check for win from server")
            time.sleep(1)
            break

        if computer_player and current_player == player2:
            print("\n**Computer's move**\n")
            time.sleep(1)
            s.sendall(pickle.dumps([3, "comp", []]))
            msg_in = s.recv(1024)
            msg = pickle.loads(msg_in)
            print(msg[1])
            time.sleep(1)
            current_player = player1
        else:
            print("\n**" + str(current_player) + "'s move**")
            user_in = input("Enter piece and destination coordinates, row before column, separated by a space: ")
            print("")
            time.sleep(1)
            if user_in.lower() == "q":
                s.sendall(pickle.dumps([9, 1, []]))
                print("Game quit!")
                time.sleep(1)
                break
            else:
                l = list("".join(user_in.split()))
                s.sendall(pickle.dumps([current_player.get_number(), l, []]))
                msg_in = s.recv(1024)
                msg = pickle.loads(msg_in)
                if msg[0] == 5:
                    print(msg[1])
                    time.sleep(1)
                else:
                    print(msg[1])
                    time.sleep(1)
                    if current_player == player1:
                        current_player = player2
                    else:
                        current_player = player1
    s.close()


if __name__ == '__main__':
    main()
