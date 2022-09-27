from random import *

def logs(string): #метод для вывода всякой информации о разработке чтобы не искать все лишние принты в коде
    available = False
    if available:
        print(string)


class Dot:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.status = True

    def is_correct_for_board(self, size_board):
        if (self.x>=0) and (self.x<size_board) and (self.y>=0) and (self.y<size_board):
            return True
        else:
            return False

    def neighbour_dots(self):
        return [Dot(self.y+1,self.x),Dot(self.y-1,self.x),Dot(self.y,self.x+1),Dot(self.y,self.x-1)]


    def is_alive(self):
        return self.status

    def destroy(self):
        self.status=False

    def get_x(self):
        return self.x
    def get_y(self):
        return self.y

    def __eq__(self, other):
        return (self.x==other.x) and (self.y==other.y) and (self.status==other.status)

    def __str__(self):
        return f"Палуба {self.y} {self.x}"

class ShipException(Exception):
    def __init__(self, text):
        self.txt = text

class Ship:
    def __init__(self,nose_position, length, horizontal = True):
        self.dots = []
        self.length = len(self.dots)
        self.nose_position=nose_position
        self.horizontal=horizontal
        for i in range(length):
            if self.horizontal:
                dot = Dot(nose_position[0],nose_position[1]+i)
            else:
                dot = Dot(nose_position[0]+i, nose_position[1])
            self.dots.append(dot)

    def __str__(self):
        return f'корабль{[str(dot) for dot in self.dots]}'

    def get_alive_dots(self):
        dots = []
        for dot in self.dots:
            if dot.is_alive():
                dots.append(dot)
        return dots

    def is_alive(self):
        return len(self.get_alive_dots())>0

    def get_damage(self, dot):
        logs(f"нанесён урон {self} {dot}")
        if not(dot in self.dots):
            raise ShipException('попытка обратиться к не своей палубе')
        dot.destroy()
        return True

class BoardException(Exception):
    def __init__(self, text):
        self.txt = text

class Board:
    def __init__(self):
        self.ships = []
        self.misses = []
        self.size = 6
        if self.size<0:
            raise ValueError(f'размер не может быть отрицательным')

    def get_size(self):
        return self.size
    def get_ships(self):
        return self.ships

    def get_alive_ships(self):
        ships=[]
        for ship in self.ships:
            if ship.is_alive():
                ships.append(ship)
        return ships

    def get_all_ships_dots(self):
        dots = []
        for ship in self.ships:
            dots+=ship.dots
        return dots

    def get_all_forbidden_dots(self):
        dots=[]
        for ship in self.ships:
            for dot in ship.dots:
                dots+=dot.neighbour_dots()
        dots+=self.get_all_ships_dots()
        return dots

    def add_ship(self, ship):
        logs(ship)
        for dot in ship.dots:
            logs(dot)
            if (dot.get_y()>=self.size) or (dot.get_y()<0) or (dot.get_x()<0) or (dot.get_x()>=self.size):
                raise BoardException(f"{dot} out of Board")
        self.ships.append(ship)
        return True

    def add_random_ship(self, size_of_ship):
        timeout = 100
        it = 0
        while True:
            ship = Ship([randint(0, self.size - 1), randint(0, self.size - 1)], size_of_ship, choice([True, False]))
            correct_dots_count = 0
            for dot in ship.dots:
                if not (dot in self.get_all_forbidden_dots()) and dot.is_correct_for_board(self.size):
                    correct_dots_count+=1
                else:continue
            if correct_dots_count ==size_of_ship:
                self.add_ship(ship)
                return True
            it+=1
            if it == timeout:
                raise BoardException(f'невозможно добавить корабль длиной {size_of_ship}')

    def attack(self, y,x):
        destination_dot = Dot(y,x)
        for ship in self.ships:
            for dot in ship.dots:
                if destination_dot == dot:
                    ship.get_damage(dot)
                    return True
        self.misses.append([y,x])
        return False

    def contour(self):
        pass

    def render(self,enemy=False):
        vert_border_symbol='|'
        matrix = [['-' for i in range(self.size)] for i in range(self.size)]
        render_strings = []
        render_strings.append(vert_border_symbol.join(['E']+[str(i) for i in range(self.size)]))
        for miss in self.misses:
            matrix[miss[0]][miss[1]]='T'
        for ship in self.ships:
            for square in ship.dots:
                if square.is_alive():
                    if not enemy:
                        matrix[square.get_y()][square.get_x()]='S'
                else:
                    matrix[square.get_y()][square.get_x()] = 'X'
        for i in range(len(matrix)):
            string = matrix[i].copy()
            string.insert(0, str(i))
            render_strings.append(vert_border_symbol.join(string))

        for e in render_strings:
            print(e)


class Player:
    def __init__(self, name = 'Вася Бензин'):
        self.board = Board()
        self.name = name
        self.moves = []

    def move(self, enemy):
        print('Твоя доска:')
        self.board.render()
        print('Доска противника:')
        enemy.board.render(enemy=True)
        inputs = self.player_input(rules='player_attack',input_text='введите координаты квадрата противника через запятую')
        logs(inputs)
        return inputs



    def player_input(self, rules, input_text):
        if rules == 'place_ships':
            while True:
                inputs = input(input_text)
                if len(inputs.split(','))==1:
                    print('некорректный ввод')
                    continue
                splitted_inputs = inputs.split(' ')
                if len(splitted_inputs) < 2:
                    logs(splitted_inputs)
                    splitted_inputs=splitted_inputs[0]
                    logs(splitted_inputs.split(',')[0])
                    if splitted_inputs.split(',')[0].isdigit() and splitted_inputs.split(',')[1].isdigit():
                        if (0 <= int(splitted_inputs.split(',')[0]) < self.board.get_size()) and (
                                0 <= int(splitted_inputs.split(',')[1]) < self.board.get_size()):
                            return [int(splitted_inputs.split(',')[0]), int(splitted_inputs.split(',')[1]),True]
                        else:
                            print('координаты за доской')
                    else:
                        print('координаты некорректны')
                else:
                    if splitted_inputs[-1] == 'r':
                        splitted_inputs = splitted_inputs[0]
                        if splitted_inputs.split(',')[0].isdigit() and splitted_inputs.split(',')[1].isdigit():
                            if (0 <= int(splitted_inputs.split(',')[0]) < self.board.get_size()) and (
                                    0 <= int(splitted_inputs.split(',')[1]) < self.board.get_size()):
                                return [int(splitted_inputs.split(',')[0]), int(splitted_inputs.split(',')[1]), False]
                            else:
                                print('координаты за доской')
                        else:
                            print('координаты некорректны')
                    else:
                        print('вы имели в виду "r"?')
        if rules == 'player_attack':
            while True:
                inputs = input(input_text)
                logs(len(inputs.split(',')))
                if len(inputs.split(','))==2:
                    inputs= inputs.split(',')
                    if inputs[0].isdigit() and inputs[1].isdigit():
                        inputs = [int(input) for input in inputs]
                        if 0<=inputs[0]<self.board.get_size() and 0<=inputs[1]<self.board.get_size():
                            if not([inputs[0],inputs[1]]in self.moves):
                                self.moves.append([inputs[0],inputs[1]])
                                return [inputs[0],inputs[1]]
                            else:print('такой ход уже был')
                        else:
                            print('координаты за доской')
                    else:print('неправильные координаты2')
                else:
                    print('неправильные координаты1')
                    continue


    def place_ships(self, ships_table):
        for element in ships_table:
            for i in range(element[1]):
                self.board.render()
                print('размещение кораблей введите координаты по типу "y,x r", где y и x - координаты носа и добавьте r если необходимо вертикальное размещение')
                inputs = self.player_input('place_ships', f'разместите свой {element[0]}-Палубный корабль {element[1]}:')
                ship = Ship([inputs[0],inputs[1]],element[0],inputs[2])
                self.board.add_ship(ship)



class AI(Player):
    def __init__(self, name='Киборг Убийца'):
        self.board = Board()
        self.name = name
        self.moves = []

    def place_ships(self, ships_table):
        for element in ships_table:
            for i in range(element[1]):
                self.board.add_random_ship(element[0])

    def move(self,enemy):
        while True:
            move = [randint(0, self.board.get_size()-1),randint(0, self.board.get_size()-1)]
            if move in self.moves:
                continue
            else:
                return move

class Game:
    def __init__(self,player_one=Player(),player_two=AI()):
        self.players = [player_one,player_two]
        #таблица количества и размера кораблей
        self.ships_table = [[3,1],[2,2],[1,4]]

    def start(self):
        for player in self.players:
            player.place_ships(self.ships_table)
        attacker = self.players[0]
        attacked = self.players[1]
        while len(self.players[0].board.get_alive_ships())>0 and len(self.players[1].board.get_alive_ships())>0:
            logs(f'{len(self.players[0].board.get_alive_ships())},{len(self.players[1].board.get_alive_ships())}')
            move = attacker.move(attacked)
            attack = attacked.board.attack(move[0],move[1])
            if not attack:
                attacker,attacked = attacked,attacker
        attacked.board.render()
        print(f'{attacker.name} победил!')







#game = Game(AI(),AI()) #битва инвалидов
game = Game()
game.start()
