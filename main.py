"""
主程序 (Main Program) - 蚁群仿真模拟器
包含游戏循环、事件处理和渲染
"""
import pygame
import sys
from config import *
from entity.world import World
from entity.ant import Ant
from utils.draw_utils import *


class AntSimulation:
    """蚁群仿真主类"""
    
    def __init__(self):
        """初始化游戏"""
        # 初始化 Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🐜 Ant Colony Simulation")
        self.clock = pygame.time.Clock()
        
        # 创建世界
        self.world = World()
        
        # 创建蚂蚁群（在巢穴周围随机生成）
        self.ants = []
        for i in range(ANT_COUNT):
            # 在巢穴附近随机生成
            x = int(self.world.nest_x + (hash(str(i)) % 10 - 5))
            y = int(self.world.nest_y + (hash(str(i * 7)) % 10 - 5))
            x = max(0, min(GRID_WIDTH - 1, x))
            y = max(0, min(GRID_HEIGHT - 1, y))
            self.ants.append(Ant(x, y))
        
        # 游戏状态
        self.running = True
        self.paused = False
        self.mouse_dragging = False
        self.current_fps = 0
        
        # 添加一些初始食物源
        self._place_initial_food()
    
    def _place_initial_food(self):
        """放置初始食物源"""
        # 在四个角落附近放置食物
        food_positions = [
            (10, 10),
            (GRID_WIDTH - 10, 10),
            (10, GRID_HEIGHT - 10),
            (GRID_WIDTH - 10, GRID_HEIGHT - 10)
        ]
        
        for x, y in food_positions:
            self.world.add_food(x, y, INITIAL_FOOD_AMOUNT)
    
    def handle_events(self):
        """处理用户输入事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keypress(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_dragging:
                    self._handle_mouse_drag(event.pos)
    
    def _handle_keypress(self, key):
        """处理键盘按键"""
        if key == pygame.K_SPACE:
            # 暂停/继续
            self.paused = not self.paused
        
        elif key == pygame.K_r:
            # 重置信息素
            self.world.clear_pheromones()
        
        elif key == pygame.K_c:
            # 清空地图
            self.world.clear_map()
        
        elif key == pygame.K_q or key == pygame.K_ESCAPE:
            # 退出
            self.running = False
    
    def _handle_mouse_down(self, event):
        """处理鼠标按下"""
        grid_pos = grid_position_from_mouse(event.pos[0], event.pos[1])
        
        if grid_pos:
            x, y = grid_pos
            
            if event.button == 1:  # 左键 - 放置障碍物
                self.world.add_obstacle(x, y)
                self.mouse_dragging = True
            
            elif event.button == 3:  # 右键 - 放置食物
                self.world.add_food(x, y, INITIAL_FOOD_AMOUNT)
    
    def _handle_mouse_drag(self, pos):
        """处理鼠标拖动（连续放置障碍物）"""
        grid_pos = grid_position_from_mouse(pos[0], pos[1])
        
        if grid_pos:
            x, y = grid_pos
            self.world.add_obstacle(x, y)
    
    def update(self):
        """更新游戏状态"""
        if not self.paused:
            # 更新所有蚂蚁
            for ant in self.ants:
                ant.update(self.world)
            
            # 信息素挥发
            self.world.evaporate_pheromones()
    
    def render(self):
        """渲染画面"""
        # 绘制世界
        draw_world(self.screen, self.world)
        
        # 绘制蚂蚁
        draw_ants(self.screen, self.ants)
        
        # 绘制 UI
        draw_ui(self.screen, self.world, self.current_fps, self.paused)
        
        # 绘制操作说明
        draw_instructions(self.screen)
        
        # 更新显示
        pygame.display.flip()
    
    def run(self):
        """主游戏循环"""
        while self.running:
            # 处理事件
            self.handle_events()
            
            # 更新游戏状态
            self.update()
            
            # 渲染画面
            self.render()
            
            # 控制帧率
            self.clock.tick(FPS)
            self.current_fps = self.clock.get_fps()
        
        # 退出
        pygame.quit()
        sys.exit()


def main():
    """程序入口"""
    simulation = AntSimulation()
    simulation.run()


if __name__ == "__main__":
    main()
