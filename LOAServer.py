"""
Lines of Action server
Starbuck Beagley
"""

import socket
import pickle
import Player
import random
import Board
import Move


def main():
    rows = 8
    cols = 8
    player1 = Player.Player(1, 'x')
    player2 = Player.Player(2, 'o')
    board = Board.Board(rows, cols, player1, player2)
    move = Move.Move(board, player1, player2)
    current_player = player1
    computer_player = False
    board.reset_board()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = 7667
    server_socket.bind((host, port))

    server_socket.listen(5)
    client_socket, addr = server_socket.accept()

    print("Got connection from %s" % str(addr))

    msg_in = client_socket.recv(1024)
    msg = pickle.loads(msg_in)

    if msg[0] == 0:
        if msg[1] == 1:
            computer_player = True
        client_socket.sendall(pickle.dumps([0, "", board.get_grid()]))
    else:
        err_msg = "Server needs to know if player 2 is computer. Stopping server."
        print(err_msg)
        client_socket.sendall(pickle.dumps([5, err_msg, board.get_grid()]))
        return 0

    while True:
        msg_in = client_socket.recv(1024)
        msg = pickle.loads(msg_in)

        if msg[0] == 9:
            print("User quit. Stopping server.")
            break
        elif msg[0] == 8:
            if move.check_for_win(player1) or move.check_for_win(player2):
                resp = [8, "\n\(*o*)/\(*o*)/\(*o*)/ " +
                        str(current_player) +
                        " wins! \(*o*)/\(*o*)/\(*o*)/\n", board.get_grid()]
                client_socket.sendall(pickle.dumps(resp))
                break
            else:
                client_socket.sendall(pickle.dumps([8, 0, board.get_grid()]))
        elif 0 < msg[0] < 4:
            resp = form_response(msg, move, current_player, player2, computer_player, board, cols)
            if resp[0] == 3:
                current_player = player1
            elif resp[0] == msg[0]:
                if msg[0] == 1:
                    current_player = player2
                else:
                    current_player = player1
            client_socket.sendall(pickle.dumps(resp))

    client_socket.close()
    return 0


def form_response(msg, move, current_player, player2, computer_player, board, cols):
    """
    Forms response to client based upon client input
    :param msg: message from client
    :param move: Move object, checks move legality
    :param current_player: current player
    :param player2: Player object
    :param computer_player: true if player2 is computer
    :param board: Board object
    :param cols: number of columns of game board
    :return: message to send to client
    """
    a = []

    if computer_player and current_player == player2:
        a = get_computer_move(player2, move)
        result = move.make_move(current_player, a[0], a[1], a[2], a[3])
        return [msg[0],
                "(^u^) " + result[1][0:6] + "Computer" + result[1][14:] + " (^u^)\n",
                board.get_grid()]
    elif len(msg[1]) != 4 or not translate(msg[1], a, cols):
        return [5, "(v_v) Please enter valid coordinates (v_v)\n", board.get_grid()]
    else:
        result = move.make_move(current_player, a[0], a[1], a[2], a[3])
        if result[0] == 0:
            return [5, "(v_v) " + result[1] + " (v_v)\n", board.get_grid()]
        elif result[0] == 1:
            return [msg[0], "(^u^) " + result[1] + " (^u^)\n", board.get_grid()]


def get_computer_move(player, move):
    """
    Gets a random, legal move for computer player
    :param player: which player computer represents, for move legality
    :param move: Move object, checks move legality
    :return: computer's move if random move is legal, recursive call otherwise
    """
    r1 = random.randint(0, 7)
    c1 = random.randint(0, 7)
    r2 = random.randint(0, 7)
    c2 = random.randint(0, 7)
    while 1:
        if move.legal_move(player, r1, c1, r2, c2) == "Legal":
            a = [r1, c1, r2, c2]
            return a
        else:
            return get_computer_move(player, move)


def translate(l, a, c):
    """
    Translates user input into numbers for processing
    :param l: user input
    :param a: list to put translated move into
    :param c: number of columns of board
    :return: true if user input is valid, false otherwise
    """
    try:
        i = int(l[0])
        a.append(i)
    except ValueError:
        return False
    for j in range(97, 97 + c):
        if l[1].lower() == chr(j):
            a.append(j - 97)
            break
        elif j == (97 + c):
            return False
    try:
        i = int(l[2])
        a.append(i)
    except ValueError:
        return False
    for j in range(97, 97 + c):
        if l[3].lower() == chr(j):
            a.append(j - 97)
            break
        elif j == (97 + c):
            return False
    return True


if __name__ == '__main__':
    main()
