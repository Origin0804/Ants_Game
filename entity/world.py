"""
世界类 (World Class) - 管理地图网格、信息素、食物和障碍物
"""
import numpy as np
from config import *


class World:
    """
    环境/地图类，管理网格状态、信息素和环境对象
    """
    
    def __init__(self):
        """初始化世界环境"""
        # 使用 NumPy 数组存储网格状态
        self.pheromones = np.zeros((GRID_WIDTH, GRID_HEIGHT), dtype=np.float32)
        self.food = np.zeros((GRID_WIDTH, GRID_HEIGHT), dtype=np.int32)
        self.obstacles = np.zeros((GRID_WIDTH, GRID_HEIGHT), dtype=np.bool_)
        
        # 巢穴位置标记
        self.nest_x, self.nest_y = NEST_POSITION
        
        # 统计数据
        self.collected_food = 0
        
    def is_nest(self, x, y):
        """判断位置是否在巢穴范围内"""
        dx = x - self.nest_x
        dy = y - self.nest_y
        return (dx * dx + dy * dy) <= (NEST_SIZE * NEST_SIZE)
    
    def is_valid_position(self, x, y):
        """判断位置是否有效（不越界且不是障碍物）"""
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return False
        return not self.obstacles[x, y]
    
    def add_food(self, x, y, amount=INITIAL_FOOD_AMOUNT):
        """在指定位置添加食物"""
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            self.food[x, y] = amount
    
    def add_obstacle(self, x, y):
        """在指定位置添加障碍物"""
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            # 不能在巢穴范围内放置障碍
            if not self.is_nest(x, y):
                self.obstacles[x, y] = True
    
    def remove_obstacle(self, x, y):
        """移除指定位置的障碍物"""
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            self.obstacles[x, y] = False
    
    def pickup_food(self, x, y):
        """从指定位置拾取食物，返回是否成功"""
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            if self.food[x, y] > 0:
                self.food[x, y] -= FOOD_PICKUP_AMOUNT
                return True
        return False
    
    def deposit_pheromone(self, x, y, amount=PHEROMONE_DEPOSIT):
        """在指定位置释放信息素"""
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            self.pheromones[x, y] = min(self.pheromones[x, y] + amount, MAX_PHEROMONE)
    
    def get_pheromone(self, x, y):
        """获取指定位置的信息素浓度"""
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            return self.pheromones[x, y]
        return 0
    
    def evaporate_pheromones(self):
        """信息素挥发（全局更新）"""
        self.pheromones *= EVAPORATION_RATE
        # 清理极小值以提高性能
        self.pheromones[self.pheromones < 0.1] = 0
    
    def clear_pheromones(self):
        """清除所有信息素"""
        self.pheromones.fill(0)
    
    def clear_map(self):
        """清空地图（清除所有障碍和食物）"""
        self.food.fill(0)
        self.obstacles.fill(False)
    
    def deposit_food_at_nest(self):
        """在巢穴存放食物"""
        self.collected_food += FOOD_PICKUP_AMOUNT
    
    def get_sensor_data(self, x, y, sensor_range=SENSOR_RANGE):
        """
        获取指定位置周围的感知数据
        返回: (食物位置列表, 信息素数据)
        """
        food_positions = []
        pheromone_data = []
        
        for dx in range(-sensor_range, sensor_range + 1):
            for dy in range(-sensor_range, sensor_range + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    # 检测食物
                    if self.food[nx, ny] > 0:
                        food_positions.append((nx, ny))
                    # 记录信息素
                    pheromone_data.append({
                        'pos': (nx, ny),
                        'level': self.pheromones[nx, ny]
                    })
        
        return food_positions, pheromone_data
