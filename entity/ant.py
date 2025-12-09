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
    
    # 障碍物规避参数
    STUCK_THRESHOLD = 5  # 检测到卡住所需的步数
    EXPLORATION_STEPS = 20  # 探索模式持续的步数
    PERPENDICULAR_THRESHOLD = 0.5  # 判断垂直方向的点积阈值
    
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
        # 用于检测是否卡住
        self.stuck_counter = 0
        self.last_positions = []
        self.exploration_direction = None  # 当前探索的方向索引
        self.exploration_steps = 0  # 持续探索的剩余步数
        
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
        # 1. 先尝试拾取当前位置的食物
        if world.pickup_food(self.x, self.y):
            self.carrying_food = True
            # 反转方向开始回巢
            self.direction_index = (self.direction_index + 4) % 8
            return
        
        # 2. 检测周围是否有食物
        food_positions, pheromone_data = world.get_sensor_data(self.x, self.y)
        
        if food_positions:
            # 移动到最近的食物
            target = min(food_positions, key=lambda pos: self._distance(pos[0], pos[1]))
            self._move_towards(target[0], target[1], world)
        else:
            # 3. 没有食物，尝试跟随信息素
            if random.random() < 0.8:  # 80% 的概率跟随信息素
                best_direction = self._choose_direction_by_pheromone(pheromone_data, world)
                if best_direction is not None:
                    self.direction_index = best_direction
            
            # 4. 按当前方向移动（带随机扰动）
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
        """朝向目标移动，带有障碍物规避"""
        # 记录当前位置用于检测是否卡住
        self.last_positions.append((self.x, self.y))
        if len(self.last_positions) > 8:
            self.last_positions.pop(0)
        
        # 检测是否卡住（在同一小范围内循环）
        is_stuck = False
        if len(self.last_positions) >= 5:
            unique_positions = set(self.last_positions)
            if len(unique_positions) <= 2:  # 在2个位置之间来回移动
                is_stuck = True
                self.stuck_counter += 1
            else:
                self.stuck_counter = max(0, self.stuck_counter - 1)
        
        dx = target_x - self.x
        dy = target_y - self.y
        
        # 如果处于探索模式，继续沿着墙走
        if self.exploration_steps > 0:
            self.exploration_steps -= 1
            # 尝试沿探索方向移动
            if self.exploration_direction is not None:
                dir_x, dir_y = self.DIRECTIONS[self.exploration_direction]
                new_x = self.x + dir_x
                new_y = self.y + dir_y
                
                if world.is_valid_position(new_x, new_y):
                    # 可以继续沿这个方向探索
                    self.direction_index = self.exploration_direction
                    if self._move_forward(world):
                        return
                
                # 如果原方向被堵，尝试相邻的方向
                for offset in [-1, 1, -2, 2]:
                    test_dir = (self.exploration_direction + offset) % 8
                    self.direction_index = test_dir
                    if self._move_forward(world):
                        self.exploration_direction = test_dir
                        return
            
            # 探索失败，退出探索模式
            self.exploration_steps = 0
            self.exploration_direction = None
        
        # 找到所有可行的方向
        valid_moves = []
        
        for i, (dir_x, dir_y) in enumerate(self.DIRECTIONS):
            new_x = self.x + dir_x
            new_y = self.y + dir_y
            
            if world.is_valid_position(new_x, new_y):
                # 计算到目标的曼哈顿距离
                dist = abs(new_x - target_x) + abs(new_y - target_y)
                
                # 计算这个方向与目标方向的关系
                if dx != 0 or dy != 0:
                    target_length = math.sqrt(dx * dx + dy * dy)
                    dot_product = (dir_x * dx + dir_y * dy) / target_length
                else:
                    dot_product = 0
                
                valid_moves.append({
                    'direction': i,
                    'distance': dist,
                    'x': new_x,
                    'y': new_y,
                    'dot_product': dot_product,
                    'dir_x': dir_x,
                    'dir_y': dir_y
                })
        
        if not valid_moves:
            return  # 完全被困，无法移动
        
        # 如果卡住了，进入墙壁跟随模式
        if is_stuck and self.stuck_counter > self.STUCK_THRESHOLD:
            # 选择一个垂直于目标方向的探索方向
            # 找到所有垂直方向（dot_product 接近 0）
            perpendicular = [m for m in valid_moves if abs(m['dot_product']) < self.PERPENDICULAR_THRESHOLD]
            
            if perpendicular:
                # 随机选择一个垂直方向探索（可能是任何与目标方向接近垂直的方向）
                perpendicular.sort(key=lambda m: m['distance'])
                chosen = perpendicular[random.randint(0, min(1, len(perpendicular)-1))]
                
                # 进入探索模式：沿着这个方向走一段距离
                self.exploration_direction = chosen['direction']
                self.exploration_steps = self.EXPLORATION_STEPS
                self.stuck_counter = 0
                
                self.direction_index = chosen['direction']
                self._move_forward(world)
                return
            
            # 如果没有垂直方向，尝试任何未访问的方向
            unvisited = [m for m in valid_moves 
                        if (m['x'], m['y']) not in self.last_positions[-5:]]
            if unvisited:
                chosen = random.choice(unvisited)
                self.exploration_direction = chosen['direction']
                self.exploration_steps = self.EXPLORATION_STEPS
                self.stuck_counter = 0
                
                self.direction_index = chosen['direction']
                self._move_forward(world)
                return
        
        # 正常模式：贪心选择最接近目标的方向
        valid_moves.sort(key=lambda m: m['distance'])
        self.direction_index = valid_moves[0]['direction']
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
