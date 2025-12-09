"""
蚂蚁类 (Ant Class) - 管理蚂蚁个体的行为逻辑
"""
import random
import math
from config import *


class Ant:
    """
    蚂蚁个体类，实现寻找食物和回巢的行为逻辑
    """
    
    # 8个移动方向 (上下左右 + 4个斜角)
    DIRECTIONS = [
        (-1, 0), (1, 0), (0, -1), (0, 1),  # 左、右、上、下
        (-1, -1), (-1, 1), (1, -1), (1, 1)  # 四个斜角
    ]
    
    def __init__(self, x, y):
        """
        初始化蚂蚁
        :param x: 初始 x 坐标
        :param y: 初始 y 坐标
        """
        self.x = x
        self.y = y
        self.carrying_food = False
        self.direction_index = random.randint(0, len(self.DIRECTIONS) - 1)
        
    def update(self, world):
        """
        更新蚂蚁状态（每帧调用）
        :param world: World 对象
        """
        if self.carrying_food:
            self._return_to_nest(world)
        else:
            self._forage_for_food(world)
    
    def _forage_for_food(self, world):
        """寻找食物模式"""
        # 1. 检测周围是否有食物
        food_positions, pheromone_data = world.get_sensor_data(self.x, self.y)
        
        if food_positions:
            # 移动到最近的食物
            target = min(food_positions, key=lambda pos: self._distance(pos[0], pos[1]))
            self._move_towards(target[0], target[1], world)
            
            # 尝试拾取食物
            if (self.x, self.y) == target:
                if world.pickup_food(self.x, self.y):
                    self.carrying_food = True
                    # 反转方向开始回巢
                    self.direction_index = (self.direction_index + 4) % 8
        else:
            # 2. 没有食物，尝试跟随信息素
            if random.random() < 0.8:  # 80% 的概率跟随信息素
                best_direction = self._choose_direction_by_pheromone(pheromone_data, world)
                if best_direction is not None:
                    self.direction_index = best_direction
            
            # 3. 按当前方向移动（带随机扰动）
            self._move_with_randomness(world)
    
    def _return_to_nest(self, world):
        """回巢模式"""
        # 释放信息素
        world.deposit_pheromone(self.x, self.y)
        
        # 检查是否到达巢穴
        if world.is_nest(self.x, self.y):
            self.carrying_food = False
            world.deposit_food_at_nest()
            # 反转方向继续寻找食物
            self.direction_index = (self.direction_index + 4) % 8
        else:
            # 朝向巢穴移动
            self._move_towards(world.nest_x, world.nest_y, world)
    
    def _move_towards(self, target_x, target_y, world):
        """朝向目标移动"""
        dx = target_x - self.x
        dy = target_y - self.y
        
        # 找到最接近目标方向的可行方向
        best_direction = None
        best_score = float('inf')
        
        for i, (dir_x, dir_y) in enumerate(self.DIRECTIONS):
            new_x = self.x + dir_x
            new_y = self.y + dir_y
            
            if world.is_valid_position(new_x, new_y):
                # 计算距离目标的距离
                dist = abs(new_x - target_x) + abs(new_y - target_y)
                if dist < best_score:
                    best_score = dist
                    best_direction = i
        
        if best_direction is not None:
            self.direction_index = best_direction
            self._move_forward(world)
    
    def _move_with_randomness(self, world):
        """带随机扰动的移动"""
        # 20% 概率随机改变方向
        if random.random() < 0.2:
            self.direction_index = random.randint(0, len(self.DIRECTIONS) - 1)
        
        # 尝试前进
        if not self._move_forward(world):
            # 如果被阻挡，随机选择新方向
            for _ in range(8):
                self.direction_index = random.randint(0, len(self.DIRECTIONS) - 1)
                if self._move_forward(world):
                    break
    
    def _move_forward(self, world):
        """
        按当前方向前进一步
        返回是否成功移动
        """
        dx, dy = self.DIRECTIONS[self.direction_index]
        new_x = self.x + dx
        new_y = self.y + dy
        
        if world.is_valid_position(new_x, new_y):
            self.x = new_x
            self.y = new_y
            return True
        return False
    
    def _choose_direction_by_pheromone(self, pheromone_data, world):
        """
        基于信息素浓度概率选择方向
        返回方向索引或 None
        """
        # 过滤出可行的邻居格子
        valid_moves = []
        
        for i, (dx, dy) in enumerate(self.DIRECTIONS):
            new_x = self.x + dx
            new_y = self.y + dy
            
            if world.is_valid_position(new_x, new_y):
                # 查找该位置的信息素浓度
                pheromone_level = world.get_pheromone(new_x, new_y)
                if pheromone_level > 0:
                    valid_moves.append({
                        'direction': i,
                        'pheromone': pheromone_level
                    })
        
        if not valid_moves:
            return None
        
        # 使用轮盘赌算法选择方向（概率正比于信息素浓度）
        total_pheromone = sum(move['pheromone'] ** PHEROMONE_INFLUENCE for move in valid_moves)
        
        if total_pheromone == 0:
            return None
        
        rand_value = random.uniform(0, total_pheromone)
        cumulative = 0
        
        for move in valid_moves:
            cumulative += move['pheromone'] ** PHEROMONE_INFLUENCE
            if cumulative >= rand_value:
                return move['direction']
        
        return valid_moves[-1]['direction']
    
    def _distance(self, x, y):
        """计算到指定位置的距离"""
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)
