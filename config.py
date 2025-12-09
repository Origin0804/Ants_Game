"""
全局配置参数 (Global Configuration Parameters)
"""

# 屏幕设置 (Screen Settings)
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
GRID_WIDTH = 80
GRID_HEIGHT = 60
CELL_SIZE = min(WINDOW_WIDTH // GRID_WIDTH, WINDOW_HEIGHT // GRID_HEIGHT)
FPS = 30

# 蚂蚁参数 (Ant Parameters)
ANT_COUNT = 50
ANT_SPEED = 1  # 每帧移动的格子数
SENSOR_RANGE = 2  # 感知范围 (3x3 或 5x5)
ANT_SIZE = 3  # 绘制大小

# 信息素参数 (Pheromone Parameters)
EVAPORATION_RATE = 0.98  # 信息素挥发速率 (0.95-0.99)
PHEROMONE_DEPOSIT = 100  # 蚂蚁每步释放的信息素量
PHEROMONE_INFLUENCE = 2.0  # 信息素对决策的影响权重
MAX_PHEROMONE = 1000  # 最大信息素浓度

# 食物参数 (Food Parameters)
INITIAL_FOOD_AMOUNT = 100  # 每个食物源的初始量
FOOD_PICKUP_AMOUNT = 1  # 每次拾取的食物量
FOOD_SIZE = 5  # 绘制大小

# 环境参数 (Environment Parameters)
NEST_POSITION = (GRID_WIDTH // 2, GRID_HEIGHT // 2)  # 巢穴位置 (中心)
NEST_SIZE = 5  # 巢穴半径

# 颜色定义 (Color Definitions)
COLOR_BACKGROUND = (20, 20, 20)  # 深灰色背景
COLOR_NEST = (0, 100, 255)  # 蓝色巢穴
COLOR_FOOD = (0, 255, 0)  # 绿色食物
COLOR_OBSTACLE = (200, 200, 200)  # 灰色障碍
COLOR_ANT_FORAGING = (255, 50, 50)  # 红色蚂蚁 (寻找食物)
COLOR_ANT_RETURNING = (255, 200, 0)  # 黄色蚂蚁 (回巢)
COLOR_PHEROMONE = (100, 255, 100)  # 绿色信息素轨迹
COLOR_TEXT = (255, 255, 255)  # 白色文字

# UI 参数 (UI Parameters)
UI_MARGIN = 10
UI_LINE_HEIGHT = 25
