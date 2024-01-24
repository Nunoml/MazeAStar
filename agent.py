import copy
import warehouse
import math

def obtain_direction_from_input(inputv):
    if inputv == (1, 0):
        return 0
    elif inputv == (0, 1):
        return 1  # type: ignore
    elif inputv == (-1, 0):
        return 2  # type: ignore
    elif inputv == (0, -1):
        return 3  # type: ignore
    return -1


def obtain_input_from_direction(direc):
    inputv = (0, 0)
    if direc == 0:
        inputv = (1, 0)
    elif direc == 1:
        inputv = (0, 1)  # type: ignore
    elif direc == 2:
        inputv = (-1, 0)  # type: ignore
    elif direc == 3:
        inputv = (0, -1)  # type: ignore
    return inputv
class AgentState:
    id_count = 0

    def __init__(self, x, y, ambient, carry, orientation, floor, cost, objectives=None):
        self.id = AgentState.id_count
        AgentState.id_count = AgentState.id_count + 1
        self.x = x
        self.y = y
        # Como listas em python são mutaveis, e passando os valores de uma lista por uma função apenas passa a
        # referencia em memória, é necessario criar uma copia para ter listas iguais mas diferentes.
        self.ambient = warehouse.Warehouse(copy.deepcopy(ambient.w_map), ambient.x_max, ambient.y_max,
                                           copy.deepcopy(ambient.objectives), copy.deepcopy(ambient.end), copy.deepcopy(ambient.start))
        self.carrying_object = carry
        self.orientation = orientation
        self.input = obtain_input_from_direction(orientation)
        self.floor = floor
        self.cost = cost
        if objectives is None:
            objectives = []
        self.objectives = copy.deepcopy(objectives)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, compare):
        if isinstance(compare, AgentState):
            return self.id == compare.id
        return NotImplemented

class A_Star_AgentState(AgentState):
    def __init__(self, x, y, ambient, carry, orientation, floor, cost, objectives=None):
        AgentState.__init__(self, x, y, ambient, carry, orientation, floor, cost, objectives)

    def __hash__(self):
        value = "x"+str(self.x) + "y"+str(self.y)
        return hash(value)

    def __eq__(self, compare):
        if isinstance(compare, A_Star_AgentState):
            value = "x"+str(self.x) + "y"+str(self.y)
            comp = "x"+str(compare.x) + "y"+str(compare.y)
            return value == comp
        return NotImplemented

class Agent:
    id_count = 0

    def __init__(self, x, y, ambient: warehouse.Warehouse):
        self.id = Agent.id_count
        self.state = AgentState(x, y, ambient, False, 1, 0, 0)

        # Os objetivos escolhidos pelo agente.
        self.__objectives = []
        self.__visited = ambient.w_map
        Agent.id_count += 1

    # Usado como heuristica e decisão(Não é realmente o mais curto.)
    @staticmethod
    def calculate_closest_objective(state, goal_list):
        shortest = None
        shortest_distance = 0
        for goal in goal_list:
            coords = (abs(goal[0] - state.y), abs(goal[1] - state.x))
            distance = math.sqrt(pow(coords[1], 2) + pow(coords[0], 2))
            if shortest is not None:
                if distance < shortest_distance:
                    shortest_distance = distance
                    shortest = goal
            else:
                shortest_distance = distance
                shortest = goal
        return shortest

    # Usado como h(n)
    @staticmethod
    def calculate_to_pos(state, x, y):
        coords = (abs(y - state.y), abs(x - state.x))
        distance = math.sqrt(pow(coords[1], 2) + pow(coords[0], 2))
        return distance

    def calculate_distance_per_objective(self, ignore=None):
        if ignore is None:
            ignore = []

        objective_list = self.state.ambient.objectives
        objective_and_distance = []
        for i in objective_list:
            flag = False
            for test in ignore:
                if i == test:
                    flag = True
            if not flag:
                coords = (abs(i[0] - self.state.y), abs(i[1] - self.state.x))
                distance = math.sqrt(pow(coords[1], 2) + pow(coords[0], 2))
                objective_and_distance.append((i, distance))
        return objective_and_distance

    @staticmethod
    def __look_around(state):
        discovered = []

        if state.ambient.w_map[state.y + 1][state.x] == 0 or state.ambient.w_map[state.y + 1][state.x] == 4 or \
                state.ambient.w_map[state.y + 1][state.x] == 9:
            discovered.append((state.y + 1, state.x))
        if state.ambient.w_map[state.y - 1][state.x] == 0 or state.ambient.w_map[state.y - 1][state.x] == 4 or \
                state.ambient.w_map[state.y - 1][state.x] == 9:
            discovered.append((state.y - 1, state.x))
        if state.ambient.w_map[state.y][state.x + 1] == 0 or state.ambient.w_map[state.y][state.x + 1] == 4 or \
                state.ambient.w_map[state.y][state.x + 1] == 9:
            discovered.append((state.y, state.x + 1))
        if state.ambient.w_map[state.y][state.x - 1] == 0 or state.ambient.w_map[state.y][state.x - 1] == 4 or \
                state.ambient.w_map[state.y][state.x - 1] == 9:
            discovered.append((state.y, state.x - 1))

        return discovered

    # Algoritimo implementado no agente
    def think_depth_first(self, depth):
        visited = []
        for y in range(0, len(self.state.ambient.w_map) - 1):
            visited.append(copy.deepcopy(self.state.ambient.w_map[y]))
        stack = []
        i = 0
        cell_map = {}
        stack.append(self.state)
        cell_map[self.state] = None
        grabbed_state = None
        while len(stack) > 0 and i <= 100000:
            i += 1
            grabbed_state = stack.pop()
            if grabbed_state.floor == 9 and grabbed_state.carrying_object:
                print(grabbed_state.objectives)
                if len(grabbed_state.objectives) == 0:
                    print("Solution found")

                    # Obter o caminho para a solução.
                    ii = 0
                    final_path = []
                    currIt = grabbed_state
                    print("Obtaining final path, this might take a while...")
                    while currIt is not None and ii <= len(cell_map):
                        final_path.append(currIt)
                        currIt = cell_map[currIt]
                        # Segurança
                        ii += 1
                    final_path.reverse()
                    return final_path
                else:
                    print("Deposited object")
                    visited = []
                    for y in range(0, len(self.state.ambient.w_map) - 1):
                        visited.append(copy.deepcopy(self.state.ambient.w_map[y]))
                    visited[grabbed_state.y][grabbed_state.x] = 5
                    for next_cell in self.__look_around(grabbed_state):
                        # Calcula a direção
                        direction = ((next_cell[0] - grabbed_state.y), (next_cell[1] - grabbed_state.x))
                        # Roda até a direção desejada e move em relação ao estado atualmente obtido
                        new_state = AgentState(grabbed_state.x, grabbed_state.y, grabbed_state.ambient,
                                               grabbed_state.carrying_object, grabbed_state.orientation,
                                               grabbed_state.floor, grabbed_state.cost, grabbed_state.objectives)
                        new_state = self.move(
                            self.rotate_untill_direction(self.deposit_object(new_state),
                                                         obtain_direction_from_input(direction)))
                        # Acrescenta o estado ao stack
                        stack.append(new_state)
                        cell_map[new_state] = grabbed_state
            elif grabbed_state.floor == 4 and not grabbed_state.carrying_object:
                position = (grabbed_state.y, grabbed_state.x)
                if position in grabbed_state.objectives:
                    print("Found goal")
                    grabbed_state.objectives.remove(position)
                    visited = []
                    for y in range(0, len(self.state.ambient.w_map) - 1):
                        visited.append(copy.deepcopy(self.state.ambient.w_map[y]))
                    visited[grabbed_state.y][grabbed_state.x] = 5
                    for next_cell in self.__look_around(grabbed_state):
                        # Calcula a direção
                        direction = ((next_cell[0] - grabbed_state.y), (next_cell[1] - grabbed_state.x))
                        # Roda até a direção desejada e move em relação ao estado atualmente obtido
                        new_state = AgentState(grabbed_state.x, grabbed_state.y, grabbed_state.ambient,
                                               grabbed_state.carrying_object, grabbed_state.orientation,
                                               grabbed_state.floor, grabbed_state.cost, grabbed_state.objectives)
                        new_state = self.move(
                            self.rotate_untill_direction(self.carry_object(new_state),
                                                         obtain_direction_from_input(direction)))
                        # Acrescenta o estado ao stack
                        stack.append(new_state)
                        cell_map[new_state] = grabbed_state
                else:
                    visited[grabbed_state.y][grabbed_state.x] = 5
                    for next_cell in self.__look_around(grabbed_state):
                        # Calcula a direção
                        direction = ((next_cell[0] - grabbed_state.y), (next_cell[1] - grabbed_state.x))
                        # Roda até a direção desejada e move em relação ao estado atualmente obtido
                        new_state = AgentState(grabbed_state.x, grabbed_state.y, grabbed_state.ambient,
                                               grabbed_state.carrying_object, grabbed_state.orientation,
                                               grabbed_state.floor, grabbed_state.cost, grabbed_state.objectives)
                        new_state = self.move(
                            self.rotate_untill_direction(new_state, obtain_direction_from_input(direction)))
                        # Acrescenta o estado ao stack
                        stack.append(new_state)
                        cell_map[new_state] = grabbed_state
            elif visited[grabbed_state.y][grabbed_state.x] != 5 and grabbed_state.ambient.w_map[grabbed_state.y][
                grabbed_state.x] != 2:
                visited[grabbed_state.y][grabbed_state.x] = 5
                for next_cell in self.__look_around(grabbed_state):
                    # Calcula a direção
                    direction = ((next_cell[0] - grabbed_state.y), (next_cell[1] - grabbed_state.x))
                    # Roda até a direção desejada e move em relação ao estado atualmente obtido
                    new_state = AgentState(grabbed_state.x, grabbed_state.y, grabbed_state.ambient,
                                           grabbed_state.carrying_object, grabbed_state.orientation,
                                           grabbed_state.floor, grabbed_state.cost, grabbed_state.objectives)
                    new_state = self.move(
                        self.rotate_untill_direction(new_state, obtain_direction_from_input(direction)))
                    # Acrescenta o estado ao stack
                    stack.append(new_state)
                    cell_map[new_state] = grabbed_state

        print("No solution found")
        final_path = []
        return final_path

    def rotate_untill_direction(self, state, direction):
        while state.orientation != direction:
            state = self.rotate(1, state)
        return state

    # BUG: Correr o algoritimo mais de uma vez causa problemas na procura
    def think_astar(self):
        if self.state.objectives == []:
            objectives = self.calculate_distance_per_objective()
            for objective in objectives:
                self.state.objectives.append(objective[0])
        # obter o objetivo
        end_node = self.calculate_closest_objective(self.state, self.state.objectives)
        # obter o custo de chegar ao objetivo (f(n)) (ESTIMATIVA)
        end_cost = self.calculate_to_pos(self.state, end_node[1], end_node[0])
        # h = calculate_to_pos()
        start = A_Star_AgentState(self.state.x, self.state.y, self.state.ambient, self.state.carrying_object, self.state.orientation, self.state.floor, self.state.cost, self.state.objectives)

        open_set = set([start])
        closed_set = set([])

        reconstructed_path = []
        discovered_path = []
        #Reconstruir o caminho
        cell_map = {}
        cell_map[start] = start
        first_run = True

        print("Starting from x: " + str(self.state.x) + " y: " + str(self.state.y))
        print("Searching for x: " + str(end_node[1]) + " y: " + str(end_node[0]))
        while len(open_set) > 0:
            current_node = None
            # Encontrar o state mais barato
            for node in open_set:
                # Se current_node está vazio ou se g(node) + h(node) < g(current_node) + h(current_node)
                if current_node is None or node.cost + self.calculate_to_pos(node, end_node[1], end_node[
                    0]) < current_node.cost + self.calculate_to_pos(current_node, end_node[1], end_node[0]):
                    current_node = node

            if current_node is None:
                print("Solution not found!")
                return []

            open_set.remove(current_node)
            closed_set.add(current_node)

            if (current_node.y, current_node.x) == end_node:
                # Lógica objetivos. Para evitar problemas, sempre limpar o cell_map antes
                # de decidir continuar a correr por causa de como funciona o hash
                currIt = current_node
                path_to_reconstruct = []
                while cell_map[currIt] is not currIt:
                    path_to_reconstruct.append(currIt)
                    currIt = cell_map[currIt]
                path_to_reconstruct.reverse()
                reconstructed_path += path_to_reconstruct
                cell_map = {}

                if not current_node.carrying_object:
                    # Reset
                    open_set.clear()
                    closed_set.clear()
                    new_node = A_Star_AgentState(current_node.x, current_node.y, current_node.ambient, current_node.carrying_object, current_node.orientation, current_node.floor, current_node.cost, current_node.objectives)
                    new_node.objectives.remove(end_node)
                    cell_map[current_node] = current_node
                    # Calcular node inicial
                    new_node = self.carry_object(new_node)
                    open_set.add(new_node)
                    cell_map[new_node] = current_node
                    # Calcular node final
                    end_node = self.calculate_closest_objective(new_node, new_node.ambient.end)
                    end_cost = self.calculate_to_pos(new_node, end_node[1], end_node[0])
                elif current_node.carrying_object and len(current_node.objectives) > 0:
                    # Reset
                    open_set.clear()
                    closed_set.clear()
                    new_node = A_Star_AgentState(current_node.x, current_node.y, current_node.ambient,
                                                 current_node.carrying_object, current_node.orientation,
                                                 current_node.floor, current_node.cost, current_node.objectives)
                    cell_map[current_node] = current_node
                    # Calcular node inicial
                    new_node = self.deposit_object(new_node)
                    open_set.add(new_node)
                    cell_map[new_node] = current_node
                    # Calcular node final
                    end_node = self.calculate_closest_objective(new_node, new_node.objectives)
                    end_cost = self.calculate_to_pos(new_node, end_node[1], end_node[0])
                else:
                    if current_node.carrying_object:
                        new_node = A_Star_AgentState(current_node.x, current_node.y, current_node.ambient,
                                                     current_node.carrying_object, current_node.orientation,
                                                     current_node.floor, current_node.cost, current_node.objectives)
                        reconstructed_path.append(self.deposit_object(new_node))
                    print("Path built with cost " + str(reconstructed_path[len(reconstructed_path)-1].cost))
                    return reconstructed_path
            else:
                for next_node in self.__look_around(current_node):
                    new_node = A_Star_AgentState(current_node.x, current_node.y, current_node.ambient,
                               current_node.carrying_object, current_node.orientation,
                               current_node.floor, current_node.cost, current_node.objectives)
                    # Lógica movimento
                    # O g(n) é calculado pelas funções movimento.

                    direction = ((next_node[0] - current_node.y), (next_node[1] - current_node.x))

                    new_node = self.move(
                        self.rotate_untill_direction(new_node, obtain_direction_from_input(direction)))

                    weight = new_node.cost - current_node.cost
                    # A hash está definida como a posição guardada no state, então este genero de comparações é possivel.
                    if new_node not in open_set and new_node not in closed_set:
                        open_set.add(new_node)
                        discovered_path.append(new_node)
                        cell_map[new_node] = current_node
                    else:
                        # Buscar o elemento no open_set
                        match = next((x for x in open_set if new_node == x), None)
                        # Se não tiver sucesso, procurar no closed_set
                        if match is None:
                            # Retorna new_node como medida de segurança
                            match = next((x for x in closed_set if new_node == x), new_node)
                        new_node = match

                        if new_node.cost > current_node.cost + weight:
                            new_node.cost = current_node.cost + weight
                            cell_map[new_node] = current_node

                            if new_node in closed_set:
                                closed_set.remove(new_node)
                                open_set.add(new_node)

        print("Solution not found!")
        return []

    # BUG : Correr o algoritimo mais de que uma vez causa problemas na procura.
    def think_best_first(self):
        # Segurança
        if self.state.objectives == []:
            objectives = self.calculate_distance_per_objective()
            for objective in objectives:
                self.state.objectives.append(objective[0])

        # Visitas
        visited = []
        for y in range(0, len(self.state.ambient.w_map) - 1):
            visited.append(copy.deepcopy(self.state.ambient.w_map[y]))
        # obter o objetivo
        end_node = self.calculate_closest_objective(self.state, self.state.objectives)
        start = AgentState(self.state.x, self.state.y, self.state.ambient, self.state.carrying_object, self.state.orientation, self.state.floor, self.state.cost, self.state.objectives)
        queue = [start]
        visited[start.y][start.x] = 5
        first_run = True
        cell_map = {}
        cell_map[start] = None
        reconstructed_path = []

        while len(queue) > 0:
            current_node = None
            # A procurar pelo potencialmente mais barato
            for node in queue:
                if current_node is None or self.calculate_to_pos(node, end_node[1], end_node[0]) < self.calculate_to_pos(current_node, end_node[1], end_node[0]):
                    current_node = node
            queue.remove(current_node)

            if (current_node.y, current_node.x) == end_node:
                # Logica chegou ao objetivo
                currIt = current_node
                path_to_reverse = []
                while cell_map[currIt] is not None:
                    path_to_reverse.append(currIt)
                    currIt = cell_map[currIt]
                path_to_reverse.reverse()
                reconstructed_path += path_to_reverse
                cell_map = {}
                first_run = True
                if not current_node.carrying_object:
                    queue.clear()
                    print("Arrived at object")
                    visited = []
                    for y in range(0, len(self.state.ambient.w_map) - 1):
                        visited.append(copy.deepcopy(self.state.ambient.w_map[y]))
                    visited[current_node.y][current_node.x] = 5

                    new_state = AgentState(current_node.x, current_node.y, current_node.ambient,
                                                  current_node.carrying_object, current_node.orientation,
                                                  current_node.floor, current_node.cost, current_node.objectives)

                    new_state.objectives.remove(end_node)
                    cell_map[current_node] = None
                    # Definir o proximo objetivo como um sitio de deposito
                    end_node = self.calculate_closest_objective(new_state, new_state.ambient.end)
                    new_state = self.move(
                        self.rotate_untill_direction(self.carry_object(new_state), obtain_direction_from_input(direction)))
                    queue.append(new_state)
                    cell_map[new_state] = current_node

                elif current_node.carrying_object and len(current_node.objectives) > 0:
                    print("Deposited object")
                    queue.clear()

                    visited = []
                    for y in range(0, len(self.state.ambient.w_map) - 1):
                        visited.append(copy.deepcopy(self.state.ambient.w_map[y]))
                    visited[current_node.y][current_node.x] = 5

                    start = AgentState(current_node.x, current_node.y, current_node.ambient,
                                                  current_node.carrying_object, current_node.orientation,
                                                  current_node.floor, current_node.cost, current_node.objectives)

                    cell_map[current_node] = None
                    # Definir o proximo objetivo
                    end_node = self.calculate_closest_objective(start, start.objectives)
                    new_state = self.move(
                        self.rotate_untill_direction(self.deposit_object(start), obtain_direction_from_input(direction)))
                    queue.append(new_state)
                    cell_map[new_state] = current_node
                else:
                    print("Solution found!")
                    print("Path built with length " + str(len(reconstructed_path)))
                    return reconstructed_path
            else:
                for next_cell in self.__look_around(current_node):
                    if visited[next_cell[0]][next_cell[1]] != 5:
                            visited[next_cell[0]][next_cell[1]] = 5
                            # Calcula a direção
                            direction = ((next_cell[0] - current_node.y), (next_cell[1] - current_node.x))
                            # Roda até a direção desejada e move em relação ao estado atualmente obtido
                            new_state = AgentState(current_node.x, current_node.y, current_node.ambient,
                                                   current_node.carrying_object, current_node.orientation,
                                                   current_node.floor, current_node.cost, current_node.objectives)
                            new_state = self.move(
                                self.rotate_untill_direction(new_state, obtain_direction_from_input(direction)))
                            queue.append(new_state)
                            cell_map[new_state] = current_node
        print("Solution not found!")
        return []


    # Atuadores
    @staticmethod
    def carry_object(state):
        state.cost += 1
        if state.floor == 4:
            state.floor = 0
            state.carrying_object = True
        return state

    @staticmethod
    def deposit_object(state):
        state.cost += 1
        if state.floor == 9:
            state.carrying_object = False
        return state

    @staticmethod
    def rotate(dire, state):
        if dire == -1 or dire == 1:
            state.orientation += dire
            state.cost += 1

            if state.orientation < 0:
                state.orientation = 3
            elif state.orientation > 3:
                state.orientation = 0

            # Não existe switch(case)
            if state.orientation == 0:
                state.input = (1, 0)
            elif state.orientation == 1:
                state.input = (0, 1)  # type: ignore
            elif state.orientation == 2:
                state.input = (-1, 0)  # type: ignore
            elif state.orientation == 3:
                state.input = (0, -1)  # type: ignore
        return state

    @staticmethod
    def move(state=None):
        if state is None:
            return 0

        x = state.x + state.input[1]
        y = state.y + state.input[0]

        if state.ambient.w_map[y][x] == 0 or state.ambient.w_map[y][x] == 9 or state.ambient.w_map[y][x] == 4:
            # TODO: Visualizar isto com ferramentas debug
            # Mudar o ambiente
            state.ambient.w_map[state.y][state.x] = state.floor
            temp = state.ambient.w_map[y][x]
            # Defenir o caminho a ir com o nº agente
            state.floor = temp
            state.ambient.w_map[y][x] = 8

            # Atualizar pos
            state.cost += 2
            state.y = y
            state.x = x
        return state
