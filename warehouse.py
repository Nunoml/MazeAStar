import random


class Warehouse:

    def __init__(self, warehouse=None, x_max=0, y_max=0, objectives=None, end=None, start=None, startArgs=None):
        if end is None:
            end = []
        if start is None:
            start = []
        if objectives is None:
            objectives = []
        if warehouse and x_max is not None and y_max is not None:
            self.w_map = warehouse
            self.x_max = x_max
            self.y_max = y_max
            self.objectives = objectives
            self.end = end
            self.start = start
        else:
            self.start = []
            self.objectives = []
            self.end = []
            if startArgs is not None:
                self.w_map = self.generate_warehouse(startArgs[0], startArgs[1], startArgs[2])
            else:
                self.w_map = self.generate_warehouse()

    def generate_warehouse(self, max_agents=-1, max_goals=10, max_exits=-1):
        # Step 1: Gerar a dimensão do armazem
        random.seed()
        self.x_max = random.randint(10, 40)
        self.y_max = random.randint(10, 40)

        # Inicializar lista, fazendo desta forma cria um novo elemento na lista por espaço
        warehouse_map = [[]]
        for y in range(0, self.y_max):
            warehouse_map.append([])
            for x in range(0, self.x_max):
                warehouse_map[y].append(0)

        # Gerando paredes.
        for y in range(self.y_max):
            for x in range(self.x_max):
                if y == 0 or y == self.y_max - 1:
                    warehouse_map[y][x] = 1
                if x == 0 or x == self.x_max - 1:
                    warehouse_map[y][x] = 1

        # Gerar prateleiras

        for y in range(2, self.y_max - 2, 3):
            for x in range(2, self.x_max - 2):
                # Escrever regras para geração
                # Decidir se gerar
                # Se gerar, escolher tamanho e verificar por colisões com outros obstaculos
                # Aplicar a prateleira

                # Verificar se a pos atual tem espaço livre
                if warehouse_map[y][x] == 0 and (warehouse_map[y][x + 1] == 0 and warehouse_map[y][x - 1] == 0) and (
                        warehouse_map[y + 1][x] == 0 and warehouse_map[y - 1][x] == 0):

                    # Decidir tamanho
                    sizeMax = (self.x_max - 2) - x
                    if sizeMax > 2:
                        if sizeMax > 5:
                            size = random.randint(2, sizeMax)
                        else:
                            size = sizeMax

                        temp_map = warehouse_map
                        generate = True
                        # Verificar colisão
                        for i in range(x, x + size):
                            if temp_map[y][i] != 0:
                                generate = False
                            else:
                                temp_map[y][i] = 2

                        # Aplicar
                        if generate:
                            warehouse_map = temp_map

        obstacle_gen = 0

        # Gerar obstaculos
        for y in range(2, self.y_max - 2):
            for x in range(2, self.x_max - 2):
                # Escrever regra de geração
                if warehouse_map[y][x] == 0:
                    generate = random.randint(0, 100)
                    if generate <= 10:
                        obstacle_gen += 1
                        warehouse_map[y][x] = 3

        # Gerar objetivo(Obter este objeto antes de partir para o final)
        goalgen = True
        goals_to_gen = random.randint(1, max_goals)
        count = 0
        while goalgen:
            # Gerar os pontos iniciais
            xGoal = random.randint(1, self.x_max - 1)
            yGoal = random.randint(1, self.y_max - 1)

            # Escrever condições aqui
            if warehouse_map[yGoal][xGoal] == 2:
                warehouse_map[yGoal][xGoal] = 4
                count += 1
                self.objectives.append((yGoal, xGoal))
                if count >= goals_to_gen:
                    goalgen = False

        # Gerando ponto de inicio e final
        if max_agents > 0 and goals_to_gen >= max_agents:
            agents_gen = random.randint(1, max_agents)
        else:
            agents_gen = random.randint(1, goals_to_gen)
        agents_it = agents_gen
        not_generated = True
        while not_generated:
            # Gerar os pontos iniciais
            xStart = random.randint(1, self.x_max - 1)
            yStart = random.randint(1, self.y_max - 1)
            if warehouse_map[yStart][xStart] == 0:
                self.start.append((yStart, xStart))
                warehouse_map[yStart][xStart] = 8
                agents_it -= 1
                if agents_it <= 0:
                    not_generated = False

        if max_exits > 0 and max_exits <= agents_gen:
            end_gen = random.randint(1, max_exits)
        else:
            end_gen = random.randint(1, agents_gen)
        not_generated = True
        while not_generated:
            xEnd = random.randint(1, self.x_max - 1)
            yEnd = random.randint(1, self.y_max - 1)
            if warehouse_map[yEnd][xEnd] == 0:
                self.end.append((yEnd, xEnd))
                warehouse_map[yEnd][xEnd] = 9
                end_gen -= 1
                if end_gen <= 0:
                    not_generated = False

        return warehouse_map

    def __str__(self):
        returnstr = ""
        for y in self.w_map:
            for x in y:
                returnstr += (str(x) + " ")
            returnstr += "\n"
        return returnstr
