import copy
import random

import pygame

import agent
import warehouse

# TODO : Potencial reestrutura projeto a algum ponto.

pygame.init()
pygame.font.init()

pygame_info = pygame.display.Info()
win_w = pygame_info.current_w / 1.2
win_h = pygame_info.current_h / 1.2

win = pygame.display.set_mode((win_w, win_h))
pygame.display.set_caption("Visualização Armazem")
font = pygame.font.SysFont('freesansbold.ttf', 32)

win_x = 40
win_y = 40
run = True

# Mapa warehouse
whouse = None
# Agentes
a_list = []
path = []

dfs_analysis = []
astar_analysis = []
bfs_analysis = []
displayed_dfs = False
displayed_astar = False
displayed_bfs = False

ii = 0
last = 0
clear_screen = False

# 0 = depth first
# 1 = a_star
# 2 = best_first
search_select = 0
clear_path = True
a_colors = []

a_cost = []
# 0 = gerar normalmente(vários agentes, vários objetivos, várias saidas)
# 1 = gerar 1 agente 1 objetivo 1 saida
# 2 = gerar 1 agente vários objetivos 1 saida
whouse_gen_select = 0

while run:
    now = pygame.time.get_ticks()

    # 0 = idle
    # 1 = gerar
    # 2 = calcular
    state = 0

    done = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                state = 1
            if event.key == pygame.K_w:
                state = 2
            if event.key == pygame.K_r:
                clear_screen = True
                if path:
                    path.clear()
            if event.key == pygame.K_1:
                print("Selected depth first")
                search_select = 0
            if event.key == pygame.K_2:
                print("Selected A*")
                search_select = 1
            if event.key == pygame.K_3:
                print("Selected best first")
                search_select = 2
            if event.key == pygame.K_z:
                print("Generate normally")
                whouse_gen_select = 0
            if event.key == pygame.K_x:
                print("Generate only 1 agent 1 goal")
                whouse_gen_select = 1
            if event.key == pygame.K_c:
                print("Generate only 1 agent but various goals")
                whouse_gen_select = 2

    if state == 0:
        if clear_screen:
            print("Clearing screen")
            win.fill((0, 0, 0))
            displayed_bfs = False
            displayed_astar = False
            displayed_dfs = False
            clear_screen = False
        if path:
            if now - last >= 100:
                clear_path = True
                last = pygame.time.get_ticks()
                i = 0
                for show_path in path:
                    if ii >= len(show_path) - 1:
                        show_path.clear()
                        # TODO : Melhorar visualização para perceber a diferenca durante o caminho
                    else:
                        clear_path = False
                        pygame.draw.rect(win, (a_colors[i][0], a_colors[i][1], a_colors[i][2]),
                                         [show_path[ii].x * 10, show_path[ii].y * 10, 10, 10])
                    i += 1
                if clear_path:
                    path.clear()
                ii += 1
        # Desenhar labirinto aqui
        if whouse:
            # size_y = win_y / len(whouse.w_map)
            # size_x = win_y / len(whouse.w_map[y])
            for y in range(0, len(whouse.w_map)):
                for x in range(0, len(whouse.w_map[y])):
                    if whouse.w_map[y][x] == 1:
                        pygame.draw.rect(win, (255, 255, 255), [x * 10, y * 10, 10, 10])
                    if whouse.w_map[y][x] == 2 or whouse.w_map[y][x] == 3:
                        pygame.draw.rect(win, (255, 50, 100), [x * 10, y * 10, 10, 10])
                    if whouse.w_map[y][x] == 4:
                        pygame.draw.rect(win, (0, 0, 255), [x * 10, y * 10, 10, 10])
                    if whouse.w_map[y][x] == 8:
                        pygame.draw.rect(win, (0, 255, 0), [x * 10, y * 10, 10, 10])
                    if whouse.w_map[y][x] == 9:
                        pygame.draw.rect(win, (255, 0, 0), [x * 10, y * 10, 10, 10])
            # Texto
            DFS_text = font.render("1 = Depth first", True, (255, 255, 255), (0, 0, 0))
            BFS_text = font.render("3 = Best first search", True, (255, 255, 255), (0, 0, 0))
            ASTAR_text = font.render("2 = A* Search", True, (255, 255, 255), (0, 0, 0))
            OneAgent_text = font.render("x = Um agent, um goal", True, (255, 255, 255), (0, 0, 0))
            OneAgentManyGoals_text = font.render("c = Um agent, multiplo goals", True, (255, 255, 255), (0, 0, 0))
            Default_text = font.render("z = Geracao padrao", True, (255, 255, 255), (0, 0, 0))
            Run_text = font.render("Q = Gerar novo armazem      W = Correr pesquisa", True, (255, 255, 255), (0, 0, 0))
            win.blit(Run_text, (win_w/2, win_h/5))
            win.blit(DFS_text, (win_w / 2, win_h / 2))
            win.blit(ASTAR_text, ((win_w / 2), (win_h / 2) + 25))
            win.blit(BFS_text, ((win_w / 2), (win_h / 2) + 50))
            win.blit(OneAgent_text, ((win_w / 2) + 250, win_h / 2))
            win.blit(OneAgentManyGoals_text, ((win_w / 2) + 250, (win_h / 2) + 25))
            win.blit(Default_text, ((win_w / 2) + 250, (win_h / 2) + 50))
            # Mostrar custo de cada caminho
            if len(bfs_analysis) > 0 :
                for analysis in range(0, len(bfs_analysis)):
                    if len(bfs_analysis[analysis]) > 0:
                        bfstext = font.render("BFS Agent " + str(a_list[analysis].id) + " cost: " + str(
                            bfs_analysis[analysis][len(bfs_analysis[analysis]) - 1].cost), True, (255, 255, 255), (0, 0, 0))
                        win.blit(bfstext, (win_w / 5, (win_h / 1.5) + (analysis * 25)))
                        displayed_bfs = True
            if len(astar_analysis) > 0:
                for analysis in range(0, len(astar_analysis)):
                    if len(astar_analysis[analysis]) > 0:
                        astartext = font.render("A* Agent " + str(a_list[analysis].id) + " cost: " + str(
                            astar_analysis[analysis][len(astar_analysis[analysis]) - 1].cost), True, (255, 255, 255),
                                           (0, 0, 0))
                        win.blit(astartext, (win_w / 2.5, (win_h / 1.5) + (analysis * 25)))
                        displayed_astar = True
            if len(dfs_analysis) > 0:
                for analysis in range(0, len(dfs_analysis)):
                    if len(dfs_analysis[analysis]) > 0:
                        dfstext = font.render("DFS Agent " + str(a_list[analysis].id) + " cost: " + str(
                            dfs_analysis[analysis][len(dfs_analysis[analysis]) - 1].cost), True, (255, 255, 255), (0, 0, 0))
                        win.blit(dfstext, (win_w / 1.5, (win_h / 1.5) + (analysis * 25)))
                        displayed_dfs = True

        else:
            text = font.render("Armazem não gerado. Carregue em Q", True, (255, 255, 255), (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (500 // 2, 400 // 2)
            win.blit(text, textRect)

        pygame.display.update()

    if state == 1:
        a_list.clear()
        path.clear()

        bfs_analysis.clear()
        dfs_analysis.clear()
        astar_analysis.clear()

        a_colors.clear()
        # Criar armazem

        if whouse_gen_select == 0:
            whouse = warehouse.Warehouse()
        elif whouse_gen_select == 1:
            whouse = warehouse.Warehouse(None, 0, 0, None, None, None, (1, 1, 1))
        elif whouse_gen_select == 2:
            whouse = warehouse.Warehouse(None, 0, 0, None, None, None, (1, 10, 1))

        # Criar agentes
        for y in range(0, len(whouse.w_map)):
            for x in range(0, len(whouse.w_map[y])):
                if whouse.w_map[y][x] == 8:
                    print("Agent created at position x: " + str(x) + " y: " + str(y))
                    c = warehouse.Warehouse(whouse.w_map, whouse.x_max, whouse.y_max, whouse.objectives, whouse.end)
                    a = agent.Agent(x, y, c)
                    a_list.append(a)

        clear_screen = True
    if state == 2:
        if search_select == 0 and len(dfs_analysis) > 0:
            print("Clearing DFS")
            dfs_analysis.clear()
            displayed_dfs = False
        elif search_select == 1 and len(astar_analysis) > 0:
            print("Clearing A*")
            astar_analysis.clear()
            displayed_astar = False
        elif search_select == 2 and len(bfs_analysis) > 0:
            print("Clearing BFS")
            bfs_analysis.clear()
            displayed_bfs = False

        path.clear()
        clear_screen = True
        ii = 0
        flaaag = False
        a_ignore = {}
        a_path = {}
        # Escolher objetos e decidir quem obtem que objetos.
        while not flaaag:
            flaaag = True
            for agents in a_list:
                if agents.state in a_ignore:
                    a_path[agents.state] = agents.calculate_distance_per_objective(a_ignore[agents.state])
                else:
                    a_path[agents.state] = agents.calculate_distance_per_objective()
            # Pegar nos agentes a testar
            for compare in range(0, len(a_list)):
                for is_equal in range(compare + 1, len(a_list)):
                    compare_state = a_list[compare].state
                    is_equal_state = a_list[is_equal].state
                    # Da forma como os dados foram guardados, não foi usado o if ... in ...
                    for compare_coords in a_path[a_list[compare].state]:
                        for is_equal_coords in a_path[a_list[is_equal].state]:
                            if compare_coords[0] == is_equal_coords[0]:
                                if compare_state not in a_ignore:
                                    a_ignore[compare_state] = []
                                if is_equal_state not in a_ignore:
                                    a_ignore[is_equal_state] = []
                                if compare_coords[1] > is_equal_coords[1] and (
                                        len(a_path[compare_state]) - len(a_ignore[compare_state])) > 1:
                                    a_ignore[compare_state].append(compare_coords[0])
                                    flaaag = False
                                elif compare_coords[1] <= is_equal_coords[1] and (
                                        len(a_path[is_equal_state]) - len(a_ignore[is_equal_state])) > 1:
                                    a_ignore[is_equal_state].append(is_equal_coords[0])
                                    flaaag = False

        it = 0
        for agents in a_list:
            for paths in a_path[agents.state]:
                if paths[0] not in agents.state.objectives:
                    agents.state.objectives.append(paths[0])

            if it > len(path) - 1:
                path.append([])

            # Seleção de algoritimo
            if search_select == 0:
                print("Starting depth first")
                path[it] += agents.think_depth_first(30)
                dfs_analysis.append(copy.deepcopy(path[it]))
            elif search_select == 1:
                print("Starting A*")
                path[it] += agents.think_astar()
                astar_analysis.append(copy.deepcopy(path[it]))
            elif search_select == 2:
                print("Starting Best First")
                path[it] += agents.think_best_first()
                bfs_analysis.append(copy.deepcopy(path[it]))

            if len(a_colors) <= it:
                a_colors.append((random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)))
            print("Agent has finished searching")
            it += 1



