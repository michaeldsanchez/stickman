from random import randint
from time import sleep
from sys import exit
import socket


class Socket:
    def __init__(self):
        """
        binds the server socket for online mode and keeps the
        connection open for sending and receiving messages using
        client and server sockets. 1 message at a time.
        """
        # for testing without online
        # self.local_machine = socket.gethostbyname('localhost')
        self.local_machine = socket.gethostbyname(socket.gethostname())
        self.reserved_port = 7777
        self.server_socket = socket.socket()
        self.server_socket.bind((self.local_machine, self.reserved_port))

    def client(self, opponent_ip, sent_msg, is_one_way=True):
        """
        connects client socket to opponent's server socket for
        sending and sometimes receiving messages, it is closed
        after every function call.

        :param opponent_ip: stored in player object upon creation.
        :param sent_msg: the message being sent to server socket.
        :param is_one_way: receive message only if param is false.

        :return: received message is is_one_way param is false.
        """
        recv_msg = None
        client_socket = socket.socket()

        client_socket.connect((opponent_ip, self.reserved_port))

        client_socket.send(sent_msg.encode('ascii'))

        if is_one_way is False:
            recv_msg = client_socket.recv(1024).decode('ascii')

        client_socket.close()
        return recv_msg

    def server(self, sent_msg=None, is_one_way=True, time_out=0.0):
        """
        receives connection from opponent's client socket for
        receiving and sometimes sending messages, the client
        socket is closed after every function call.

        :param sent_msg: optional, is is_one_way is false.
        :param is_one_way: send message only if param is false.
        :param time_out: time before server socket stops listening.

        :return: received message in every case
        """
        self.server_socket.listen(1)

        self.server_socket.settimeout(time_out)
        client_socket, addr = self.server_socket.accept()
        self.server_socket.settimeout(0.0)

        recv_msg = client_socket.recv(1024)

        if is_one_way is False:
            client_socket.send(sent_msg.encode('ascii'))

        client_socket.close()
        return recv_msg.decode('ascii')


class Player:
    def __init__(self, name=None, player_type=0, opponent_ip=None):
        """
        stores and keeps track of player and opponent's stats
        for the game, as well as the current player type and
        opponent's ip address. initialization of this object
        also creates a socket object.

        :param name: player name, taken during online_setup only
        :param player_type: either a 2 (client) or a 1 (server)
        :param opponent_ip: taken during online_setup only
        """
        self.name = name
        self.player_type = player_type
        self.socket = Socket()

        self.win = 0
        self.loss = 0
        self.winning_words = list()
        self.guessed_words = list()
        self.failed_words = list()

        self.opponent = None
        self.opponent_ip = opponent_ip
        self.opponent_guessed_words = list()

        # 1st connection, receives opponent's name otherwise exits the game.
        if self.player_type == 1:
            connection_retry = 'y'
            while connection_retry == 'y':
                try:
                    self.opponent = self.socket.server(self.name, is_one_way=False, time_out=15.0)
                except socket.timeout:
                    connection_retry = input("\nO~O Sorry, player 2 took too long! Type 'y' to try again...\n").lower()
            if self.opponent is None:
                exit('\nThank you for trying!~\n\nlove,\n-porcupal')
            print('Connected!\nYou are playing against {}.\n'.format(self.opponent))

        elif self.player_type == 2:
            while self.opponent is None:
                try:
                    self.opponent = self.socket.client(self.opponent_ip, self.name, is_one_way=False)
                except ConnectionRefusedError:
                    print('~Attempting to connect...\n')
                    sleep(5)
            if self.opponent is None:
                exit('\nThank you for trying!~\n\nlove, \n-porcupal')
            print('Connected!\nYou are playing against {}.\n'.format(self.opponent))


    def change_player_type(self):
        """
        change player type either 1 (server socket)
        or 2 (client socket)
        """
        if self.player_type == 1:
            self.player_type = 2
        elif self.player_type == 2:
            self.player_type = 1

    def end_game_stats(self):
        """
        gathers and prints all of the stats for the local
        player and their opponent if applicable
        """
        # offline player
        if self.player_type == 0:
            print('You had {} wins, and {} losses\nYour guessed words were {}\nYou failed to guess {}\n'
                  .format(self.win, self.loss, self.guessed_words, self.failed_words))
        else:
            print('\n\nYou had {} wins, and {} losses\n'
                  'Your winning words were {}\n'
                  'Your guessed words were {}\n'
                  'You failed to guess {}\n'
                  '{} guessed these words {}'
                  .format(self.win, self.loss, self.winning_words, self.guessed_words,
                          self.failed_words, self.opponent, self.opponent_guessed_words))
        if self.win > self.loss:
            print('\nYOU WIN IT ALL!!~~')
        elif self.win < self.loss:
            print('\nYou lost this time V~V')
        elif self.win == self.loss:
            print('\nWHOoOaA!! it was a tie...')


class Stickman:
    """
    player selects either offline or online during class
    initialization. If offline, player object is created.
    otherwise, online_setup function called with user input
    player type (1 or 2).
    """
    def __init__(self):
        print('Welcome to Stickman!\n')
        self.local_player = None

        mode = None
        while mode != 'online' and mode != 'offline':
            mode = input('Online or Offline?\n').lower()

        if mode == 'offline':
            self.local_player = Player()

        elif mode == 'online':
            player_type = None
            while player_type != 1 and player_type != 2:
                try:
                    player_type = int(input('\nAre you player 1 or player 2?\n'))
                except ValueError:
                    print("Must be '1' or '2'")

            if player_type == 1:
                self.online_setup(player_type)

            elif player_type == 2:
                self.online_setup(player_type)

    def online_setup(self, player_type):
        """
        prints the local player's ip. creates player object using
        player name, player type, and user input opponent_ip.

        :param player_type: either 1 or 2
        """
        local_player_name = input('\nWhat is your name?\n')
        print('\nSend this IP ({}) to your opponent!'.format(socket.gethostbyname(socket.gethostname())))
        opponent_ip = input("What is your opponent's IP?:\n")
        self.local_player = Player(local_player_name, player_type, opponent_ip)

    def present_restart_option(self):
        """
        restarts the game and calls the change_player_type function
        from the player object. otherwise exits, end_game_stats prints

        :return: True (restart) or False (exit)
        """
        restart_option = None
        while restart_option != 'y' and restart_option != 'n':
            restart_option = input('Would you like to keep playing Y or N?').lower()
        if restart_option == 'y':
            if self.local_player.player_type != 0:
                self.local_player.change_player_type()
            return True
        if restart_option == 'n':
            return False

    @staticmethod
    def search_count_replace(word_for_indexing, char, board):
        """
        searches a word for all cases of the char param in a
        word or string using the list of that word or string.

        :param word_for_indexing: list of word or string
        :param char: the character being searched recursively
        :param board: game board, updated with the word
        """
        searched_char_count = word_for_indexing.count(char)
        while searched_char_count != 0:
            searched_char_count -= 1
            char_ind = word_for_indexing.index(char)
            board[char_ind] = char
            word_for_indexing[char_ind] = '$'

    def local_win(self, word):
        """
        updates the player object every time the game ends
        with a win for local_player and loss for opponent,
        as well as the word used for that game.

        :param word: the word used in the current game.
        """
        if self.local_player.player_type == 1:
            self.local_player.loss += 1
            self.local_player.opponent_guessed_words.append(word)
            print('You lost v~v\n{} guessed your word, {}\n'.format(self.local_player.opponent, word))
        elif self.local_player.player_type == 2:
            self.local_player.win += 1
            self.local_player.guessed_words.append(word)
            print("YOU WIN!!\n{}'s word was {}\n".format(self.local_player.opponent, word))
        else:
            self.local_player.win += 1
            self.local_player.guessed_words.append(word)
            print('YOU WIN!!\n The word was {}\n'.format(word))

    def local_loss(self, word):
        """
        updates the player object every time the game ends
        with a loss for local_player and win for opponent,
        as well as the word used for that game.

        :param word: the word used in the current game
        """
        if self.local_player.player_type == 1:
            self.local_player.win += 1
            self.local_player.winning_words.append(word)
            print("YOU WIN!!\n{} couldn't guess {}\n".format(self.local_player.opponent, word))
        elif self.local_player.player_type == 2:
            self.local_player.loss += 1
            self.local_player.failed_words.append(word)
            print("You lost v~v\n{}'s word was {}\n".format(self.local_player.opponent, word))
        else:
            self.local_player.loss += 1
            self.local_player.failed_words.append(word)
            print('You lost v~v\nThe word was {}\n'.format(word))

    def run_game(self):
        """
        the game itself, prints the board, stages, and a list
        of all incorrect characters already guessed on every attempt
        """
        # online - receiving or sending game word from/ to opponent (3 minutes limit)
        if self.local_player.player_type == 1:
            word = input('Type a word for your opponent, no cheating!\n').lower()
            self.local_player.socket.client(self.local_player.opponent_ip, word)

        elif self.local_player.player_type == 2:
            word = self.local_player.socket.server(time_out=180.0)

        # offline - receives word from one of the text files depending on selected difficulty
        else:
            file_selection = None
            while file_selection != 'easy' \
                    and file_selection != 'normal' \
                    and file_selection != 'hard' \
                    and file_selection != 'brutal':
                file_selection = input('\nChoose your difficulty\nEasy, Normal, Hard, Brutal\n').lower()
            with open('the_{}_library.txt'.format(file_selection), 'r') as selection:
                library = selection.read()
            organized_library = library.split(',')
            word = organized_library[randint(1, 51)].replace('\n', '')

        stages = ['             ',
                  '_______      ',
                  '|     v      ',
                  '|     |      ',
                  '|     0      ',
                  '|    /?\     ',
                  '|___ / \     ',
                  '    R I P    ']
        word_for_indexing = list(word)
        board = ['_'] * len(word)
        self.search_count_replace(word_for_indexing, ' ', board)
        master_incorrect_list = []
        master_correct_list = []
        win = False
        wrong = 0

        # game loop, repeated until there are more wrong guesses than stages minus the RIP text
        while wrong < len(stages) - 1:
            if self.local_player.player_type == 2:          # player 2 guesses a word and sends to player 1
                player_guess = input('\nGuess a letter:\n').strip().lower()
                self.local_player.socket.client(self.local_player.opponent_ip, player_guess)
            elif self.local_player.player_type == 1:        # player 1 waits 3 minutes for player 2 guess
                player_guess = self.local_player.socket.server(time_out=180.0)
            else:
                player_guess = input('\nGuess a letter:\n').strip().lower()

            if player_guess == '':
                print('You gotta take a guess...\n')
            # checks whether character has already been guessed, and whether is is a correct/ incorrect guess
            elif len(player_guess) >= 1:
                set_player_guess = set(player_guess) - set(master_correct_list)
                set_incorrect = set_player_guess - set(word_for_indexing)
                set_correct = set_player_guess - set_incorrect          # final set of characters not yet guessed

                for each in set_correct:
                    self.search_count_replace(word_for_indexing, each, board)

                # appends the appropriate lists with the current guessed character or list of characters
                wrong += len(list(set_incorrect - set(master_incorrect_list)))
                master_incorrect_list += list(set_incorrect - set(master_incorrect_list))
                master_correct_list += list(set_correct - set(master_incorrect_list))

            # updates the stage after an incorrect guess
            current_stage = wrong + 1
            print(' '.join(board) + '\n' + str(master_incorrect_list))
            print('\n'.join(stages[0: current_stage]))

            if '_' not in board and wrong <= 6:         # win conditions
                win = True
                self.local_win(word)
                break

        if not win or wrong > 6:            # loss conditions
            self.local_loss(word)

stickman = Stickman()

try:
    stickman.run_game()
    # game restarts until statement is False, user input 'no'
    while stickman.present_restart_option():
        stickman.run_game()
except (ConnectionRefusedError, socket.timeout):
    print('{} has disconnected! O~O'.format(stickman.local_player.opponent))

stickman.local_player.end_game_stats()
print('Thank you for playing!!\n\nlove,\n-porcupal~')
