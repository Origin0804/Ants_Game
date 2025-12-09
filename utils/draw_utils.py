"""
绘图辅助函数 (Drawing Utilities)
"""
import pygame
import numpy as np
from config import *


def draw_world(screen, world):
    """
    绘制整个世界（背景、信息素、食物、障碍、巢穴）
    :param screen: Pygame 屏幕对象
    :param world: World 对象
    """
    # 1. 绘制背景
    screen.fill(COLOR_BACKGROUND)
    
    # 2. 绘制信息素轨迹（透明度表示浓度）
    draw_pheromones(screen, world)
    
    # 3. 绘制障碍物
    draw_obstacles(screen, world)
    
    # 4. 绘制食物
    draw_food(screen, world)
    
    # 5. 绘制巢穴
    draw_nest(screen, world)


def draw_pheromones(screen, world):
    """
    绘制信息素轨迹
    使用颜色亮度表示浓度
    """
    # 创建透明表面用于信息素渲染
    pheromone_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    
    # 遍历所有网格
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            level = world.pheromones[x, y]
            if level > 0.1:  # 只绘制可见的信息素
                # 计算透明度 (0-255)
                alpha = min(int((level / MAX_PHEROMONE) * 255), 255)
                
                # 计算屏幕位置
                screen_x = x * CELL_SIZE
                screen_y = y * CELL_SIZE
                
                # 绘制半透明方块
                color = (*COLOR_PHEROMONE, alpha)
                pygame.draw.rect(pheromone_surface, color, 
                               (screen_x, screen_y, CELL_SIZE, CELL_SIZE))
    
    # 将信息素层叠加到屏幕上
    screen.blit(pheromone_surface, (0, 0))


def draw_obstacles(screen, world):
    """绘制障碍物"""
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if world.obstacles[x, y]:
                screen_x = x * CELL_SIZE
                screen_y = y * CELL_SIZE
                pygame.draw.rect(screen, COLOR_OBSTACLE,
                               (screen_x, screen_y, CELL_SIZE, CELL_SIZE))


def draw_food(screen, world):
    """
    绘制食物
    食物量越大，显示越亮
    """
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            food_amount = world.food[x, y]
            if food_amount > 0:
                # 计算食物的大小和亮度
                size = min(FOOD_SIZE, int((food_amount / INITIAL_FOOD_AMOUNT) * FOOD_SIZE))
                size = max(2, size)  # 至少显示2像素
                
                # 计算屏幕中心位置
                center_x = x * CELL_SIZE + CELL_SIZE // 2
                center_y = y * CELL_SIZE + CELL_SIZE // 2
                
                # 绘制绿色圆点
                pygame.draw.circle(screen, COLOR_FOOD, (center_x, center_y), size)


def draw_nest(screen, world):
    """绘制巢穴"""
    center_x = world.nest_x * CELL_SIZE + CELL_SIZE // 2
    center_y = world.nest_y * CELL_SIZE + CELL_SIZE // 2
    radius = NEST_SIZE * CELL_SIZE
    
    # 绘制蓝色圆形巢穴
    pygame.draw.circle(screen, COLOR_NEST, (center_x, center_y), radius)
    
    # 绘制边框
    pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), radius, 2)


def draw_ants(screen, ants):
    """
    绘制所有蚂蚁
    :param screen: Pygame 屏幕对象
    :param ants: 蚂蚁列表
    """
    for ant in ants:
        # 根据是否携带食物选择颜色
        color = COLOR_ANT_RETURNING if ant.carrying_food else COLOR_ANT_FORAGING
        
        # 计算屏幕位置
        center_x = ant.x * CELL_SIZE + CELL_SIZE // 2
        center_y = ant.y * CELL_SIZE + CELL_SIZE // 2
        
        # 绘制蚂蚁（小圆点）
        pygame.draw.circle(screen, color, (center_x, center_y), ANT_SIZE)


def draw_ui(screen, world, fps, is_paused):
    """
    绘制 UI 信息
    :param screen: Pygame 屏幕对象
    :param world: World 对象
    :param fps: 当前 FPS
    :param is_paused: 是否暂停
    """
    font = pygame.font.Font(None, 30)
    
    # 绘制 FPS
    fps_text = font.render(f'FPS: {int(fps)}', True, COLOR_TEXT)
    screen.blit(fps_text, (UI_MARGIN, UI_MARGIN))
    
    # 绘制收集的食物总量
    food_text = font.render(f'Food Collected: {world.collected_food}', True, COLOR_TEXT)
    screen.blit(food_text, (UI_MARGIN, UI_MARGIN + UI_LINE_HEIGHT))
    
    # 如果暂停，显示暂停提示
    if is_paused:
        pause_text = font.render('PAUSED (Press SPACE to continue)', True, (255, 255, 0))
        text_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, UI_MARGIN + 10))
        screen.blit(pause_text, text_rect)


def draw_instructions(screen):
    """
    绘制操作说明（可选，首次运行时显示）
    """
    font = pygame.font.Font(None, 24)
    instructions = [
        "Controls:",
        "Left Click: Place Obstacle",
        "Right Click: Place Food",
        "SPACE: Pause/Resume",
        "R: Reset Pheromones",
        "C: Clear Map",
        "Q/ESC: Quit"
    ]
    
    y_offset = WINDOW_HEIGHT - len(instructions) * 25 - UI_MARGIN
    
    for i, line in enumerate(instructions):
        text = font.render(line, True, COLOR_TEXT)
        screen.blit(text, (WINDOW_WIDTH - 250, y_offset + i * 25))


def grid_position_from_mouse(mouse_x, mouse_y):
    """
    将鼠标屏幕坐标转换为网格坐标
    :param mouse_x: 鼠标 x 坐标
    :param mouse_y: 鼠标 y 坐标
    :return: (grid_x, grid_y) 或 None
    """
    grid_x = mouse_x // CELL_SIZE
    grid_y = mouse_y // CELL_SIZE
    
    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
        return (grid_x, grid_y)
    return None
