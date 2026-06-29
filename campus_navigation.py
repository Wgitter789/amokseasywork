# -*- coding: utf-8 -*-
import pygame
import sys
import math
import heapq
import os
import ctypes

# 导入音乐播放器模块
from music_player import MusicPlayer
from music_ui import MusicPlayerUI
from time_simulation import TimeSimulation, TimePanel

# 基础路径常量
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 节点位置（手动设置，与地图.png对应）
# 索引0是占位符，索引1-33对应DLL的1-33
locations_pos = [
    (0, 0),  # 0占位符（不对应任何顶点）
    (820, 160),  # 1八角楼
    (780, 80),  # 2办公楼
    (700, 100),  # 3实验楼
    (620, 180),  # 4教学楼
    (860, 230),  # 5学术交流中心
    (520, 140),  # 6图书馆
    (420, 260),  # 7大会堂
    (400, 80),  # 8艺术楼
    (600, 100),  # 9学术报告厅
    (300, 90),  # 10体育馆
    (320, 190),  # 11体育场
    (560, 280),  # 12隧道口
    (400, 380),  # 13第一饭堂
    (300, 280),  # 14后勤楼
    (260, 330),  # 15门诊楼
    (720, 260),  # 16第二饭堂
    (540, 420),  # 17又康超市
    (520, 500),  # 18宿舍
    (620, 540),  # 19第三饭堂
    (800, 580),  # 20中心湖公园
    (840, 640),  # 21中心体育场
    (300, 440),  # 22gogo新天地
    (460, 300),  # 23一号门
    (840, 420),  # 24二号门
    (640, 620),  # 25三号门
    (400, 440),  # 26四号门
    (460, 240),  # 27A座门
    (820, 300),  # 28行政出入口
    (620, 60),  # 29主校门
    (960, 90),  # 30 北校区
    (1030, 200),  # 31 白云山
    (920, 310),  # 32 安华汇
    (1020, 420)  # 33 万达广场
]

# 地点名称（Python内置数据）
# 索引0是占位符，索引1-33对应DLL的1-33
locations = [
    "",  # 0占位符
    "八角楼", "办公楼", "实验楼", "教学楼", "学术交流中心", "图书馆",
    "大会堂", "艺术楼", "学术报告厅", "体育馆", "体育场", "隧道口",
    "第一饭堂", "后勤楼", "门诊楼", "第二饭堂", "又康超市", "宿舍",
    "第三饭堂", "中心湖公园", "中心体育场", "gogo新天地", "一号门",
    "二号门", "三号门", "四号门", "A座门", "行政出入口", "主校门",
    "北校区", "白云山", "安华汇", "万达广场"
]

# 加载DLL
dll = None


def load_edges_from_dll():
    """从DLL获取所有边数据"""
    edge_list = []
    vertex_count = dll.GetVertexCount()
    max_vertex = len(locations_pos) - 1  # 有效顶点索引上限
    actual_count = min(vertex_count, max_vertex)
    print(f"DLL vertex count: {vertex_count}, actual usable: {actual_count}", flush=True)

    for i in range(1, actual_count + 1):
        # 获取该节点的所有邻居
        neighbors = (ctypes.c_int * vertex_count)()
        weights = (ctypes.c_int * vertex_count)()
        edge_count = dll.GetVertexEdges(i, neighbors, weights)

        for j in range(edge_count):
            neighbor = neighbors[j]
            weight = weights[j]
            # 确保边的顺序是小的在前，避免重复
            if i < neighbor:
                edge_list.append((i, neighbor, weight))
            elif neighbor < i and (neighbor, i, weight) not in edge_list:
                edge_list.append((neighbor, i, weight))

    return edge_list


# 回退用硬编码边数据
fallback_edges = [
    (1, 2, 80), (1, 4, 350), (1, 5, 30),
    (2, 3, 270), (2, 10, 600),
    (3, 4, 200), (3, 9, 150),
    (4, 6, 400), (4, 12, 200),
    (5, 28, 50),
    (6, 7, 80), (6, 9, 150), (6, 11, 200),
    (7, 8, 20), (7, 9, 150), (7, 10, 420),
    (8, 9, 150), (8, 10, 500), (8, 29, 100),
    (9, 29, 100),
    (10, 11, 400),
    (11, 27, 600),
    (12, 13, 60), (12, 16, 20), (12, 17, 220), (12, 27, 50),
    (13, 14, 50), (13, 23, 30),
    (14, 15, 20),
    (16, 24, 80),
    (17, 18, 210), (17, 19, 200), (17, 24, 100), (17, 26, 50),
    (19, 25, 10),
    (20, 21, 200), (20, 24, 900), (20, 25, 600),
    (21, 24, 1000), (21, 25, 600),
    (22, 25, 800), (22, 26, 400),
    (23, 27, 1000),
    (24, 25, 500), (24, 28, 500),
    (28, 29, 800),
    (30, 31, 100),
    (30, 32, 2000),
    (32, 33, 7200),
    (30, 33, 4800)
]

try:
    dll_path = os.path.join(os.path.dirname(__file__), "..", "campus_content.dll")
    dll = ctypes.CDLL(dll_path)
    print(f"DLL loaded from: {dll_path}", flush=True)

    map_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "地图数据.txt"))
    print(f"Loading map from: {map_file_path}", flush=True)


    class VertexInfo(ctypes.Structure):
        _fields_ = [('id', ctypes.c_int),
                    ('name', ctypes.c_char * 128),
                    ('description', ctypes.c_char * 256),
                    ('timeOfVisit', ctypes.c_int)]


    dll.LoadMap.argtypes = [ctypes.c_char_p]
    dll.LoadMap.restype = ctypes.c_int
    dll.GetVertexCount.argtypes = []
    dll.GetVertexCount.restype = ctypes.c_int
    dll.GetVertexInfo.argtypes = [ctypes.c_int, ctypes.POINTER(VertexInfo)]
    dll.GetVertexInfo.restype = ctypes.c_int
    dll.GetShortestPath.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int)]
    dll.GetShortestPath.restype = ctypes.c_int
    dll.GetTop5Hotspots.argtypes = [ctypes.POINTER(VertexInfo)]
    dll.GetTop5Hotspots.restype = ctypes.c_int
    dll.SimulateOneTrip.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int),
                                    ctypes.POINTER(ctypes.c_int)]
    dll.SimulateOneTrip.restype = ctypes.c_int
    dll.GetFloydDistance.argtypes = [ctypes.c_int, ctypes.c_int]
    dll.GetFloydDistance.restype = ctypes.c_int
    dll.ModifyRoadWeight.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
    dll.ModifyRoadWeight.restype = ctypes.c_int
    dll.AddNewRoad.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
    dll.AddNewRoad.restype = ctypes.c_int
    dll.DeleteRoad.argtypes = [ctypes.c_int, ctypes.c_int]
    dll.DeleteRoad.restype = ctypes.c_int
    dll.ResetVisitCounts.argtypes = []
    dll.ResetVisitCounts.restype = None
    dll.GetVertexEdges.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
    dll.GetVertexEdges.restype = ctypes.c_int
    dll.GetAdjMatrix.argtypes = [ctypes.POINTER(ctypes.c_int)]
    dll.GetAdjMatrix.restype = None
    dll.GetEdgeCount.argtypes = []
    dll.GetEdgeCount.restype = ctypes.c_int

    dll.LoadMap(map_file_path.encode('gbk'))

    # 从DLL动态加载边数据
    edges = load_edges_from_dll()
    print(f"Loaded {len(edges)} edges from DLL", flush=True)

except Exception as e:
    print(f"DLL load error: {e}", flush=True)
    edges = fallback_edges

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)
GREEN = (50, 200, 50)
RED = (255, 50, 50)
YELLOW = (255, 200, 50)
GRAY = (200, 200, 200)
LIGHT_BLUE = (150, 200, 255)
PURPLE = (150, 50, 200)
DARK_BLUE = (30, 50, 150)
ORANGE = (255, 150, 50)


def get_chinese_font(font_size=20):
    font_paths = [
        "msyh.ttc", "msyhbd.ttc", "msyh.ttf",  # 微软雅黑（美观圆润）
        "simhei.ttf", "simkai.ttf", "simsun.ttc",
        "STHeiti Light.ttc", "STSong.ttf", "STKaiti.ttf",
        "SourceHanSansSC-Regular.otf", "NotoSansCJKsc-Regular.otf"  # 开源美观字体
    ]

    for font_name in font_paths:
        try:
            font = pygame.font.Font(font_name, font_size)
            return font
        except:
            pass

    system_font_dirs = [
        "C:/Windows/Fonts/",
        "C:/Windows/Fonts/TrueType/",
        "/Library/Fonts/",
        "/System/Library/Fonts/",
        "/usr/share/fonts/",
    ]

    for font_dir in system_font_dirs:
        for font_name in font_paths:
            font_path = os.path.join(font_dir, font_name)
            if os.path.exists(font_path):
                try:
                    font = pygame.font.Font(font_path, font_size)
                    return font
                except:
                    pass

    return pygame.font.Font(None, font_size)


class SplashScreen:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.font = get_chinese_font(56)  # 主标题字体
        self.sub_font = get_chinese_font(24)
        self.button_font = get_chinese_font(28)

        # 加载背景图片（优先使用屏幕截图）
        self.background = None
        try:
            bg_path = os.path.join(BASE_DIR, "pics", "广外background.jpg")
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except:
            try:
                bg_path = os.path.join(BASE_DIR, "pics", "广外background.jpg")
                self.background = pygame.image.load(bg_path).convert()
                self.background = pygame.transform.scale(self.background, (self.width, self.height))
            except:
                self.background = None

        # 按钮状态 - 现代风格按钮尺寸，左对齐，往下移动
        self.button_rect = pygame.Rect(50, 0, 200, 50)
        self.button_rect.centery = self.height // 2 + 20
        self.button_hover = False
        self.button_click = False

        # 第二个按钮（为什么报考广外）
        self.why_button_rect = pygame.Rect(50, 0, 240, 50)
        self.why_button_rect.centery = self.height // 2 + 90
        self.why_button_hover = False
        self.why_button_click = False

        # 第三个按钮（制作人员）
        self.credits_button_rect = pygame.Rect(50, 0, 160, 50)
        self.credits_button_rect.centery = self.height // 2 + 160
        self.credits_button_hover = False
        self.credits_button_click = False

        # 音乐播放器按钮（右下角）
        self.music_button_rect = pygame.Rect(0, 0, 160, 50)
        self.music_button_rect.bottomright = (self.width - 50, self.height - 50)
        self.music_button_hover = False
        self.music_button_click = False

        # 固定标题效果
        self.alpha = 255

        # 尝试加载广外Logo
        self.logo = None
        try:
            logo_path = os.path.join(BASE_DIR, "pics", "广外Logo.jpg")
            self.logo = pygame.image.load(logo_path).convert_alpha()
            self.logo = pygame.transform.scale(self.logo, (300, 100))
        except:
            self.logo = None

        # 创建缓冲区表面用于双缓冲绘制（减少闪烁）
        self.buffer = pygame.Surface((self.width, self.height))

    def draw(self):
        # 使用缓冲区绘制（双缓冲减少闪烁）
        # 先绘制到缓冲区
        if self.background:
            self.buffer.blit(self.background, (0, 0))
        else:
            # 创建现代渐变背景（深蓝到紫色）
            for y in range(self.height):
                ratio = y / self.height
                r = int(20 + ratio * 60)
                g = int(30 + ratio * 80)
                b = int(60 + 140)
                pygame.draw.line(self.buffer, (r, g, b), (0, y), (self.width, y))

        # 绘制现代半透明遮罩
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        self.buffer.blit(overlay, (0, 0))

        # 在左侧显示广外Logo（与按钮对齐）
        if self.logo:
            logo_rect = self.logo.get_rect(topleft=(50, 30))
            self.buffer.blit(self.logo, logo_rect)

        # 绘制现代装饰元素
        self.draw_decorations_to_buffer()

        # 绘制现代风格按钮1（左对齐）
        self.draw_modern_button_to_buffer(self.button_rect, "开始导航", self.button_hover, self.button_click,
                                          primary=True)

        # 绘制现代风格按钮2（左对齐）
        self.draw_modern_button_to_buffer(self.why_button_rect, "为什么报考广外?", self.why_button_hover,
                                          self.why_button_click, primary=False)

        # 绘制现代风格按钮3（左对齐）
        self.draw_modern_button_to_buffer(self.credits_button_rect, "制作人员", self.credits_button_hover, False,
                                          primary=False)

        # 绘制音乐播放器按钮（右下角）
        self.draw_modern_button_to_buffer(self.music_button_rect, "音乐播放器", self.music_button_hover, False,
                                          primary=True)

        # 一次性将缓冲区绘制到屏幕（减少闪烁）
        self.screen.blit(self.buffer, (0, 0))
        # 注意：不在此处调用flip，由调用者控制刷新

    def draw_decorations_to_buffer(self):
        pass  # 无装饰

    def draw_modern_button_to_buffer(self, rect, text, hover, click, primary=True):
        # 透明风格UI按钮（与主界面统一）
        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # 根据hover状态设置透明度
        if hover:
            alpha = 120
            text_color = (200, 200, 200)
            stroke_color = (30, 50, 100)
        else:
            alpha = 60
            text_color = (255, 255, 255)
            stroke_color = (20, 40, 80)

        # 绘制透明边框
        pygame.draw.rect(button_surface, (255, 255, 255, alpha), button_surface.get_rect(), 2, border_radius=10)

        # 内边框效果
        inner_rect = pygame.Rect(2, 2, rect.width - 4, rect.height - 4)
        pygame.draw.rect(button_surface, (255, 255, 255, alpha // 2), inner_rect, 1, border_radius=8)

        self.buffer.blit(button_surface, rect)

        # 按钮文字 - 描边效果（中间白，边缘深蓝）
        self.draw_stroked_text_to_buffer(text, rect.center, text_color, stroke_color, self.button_font)

    def draw_stroked_text_to_buffer(self, text, center, fill_color, stroke_color, font):
        # 绘制描边文字（中间白，边缘深蓝）
        text_surface = font.render(text, True, fill_color)
        stroke_surface = font.render(text, True, stroke_color)

        # 绘制描边（8个方向）
        offsets = [(-2, -2), (-2, 0), (-2, 2),
                   (0, -2), (0, 2),
                   (2, -2), (2, 0), (2, 2)]

        x, y = center
        text_rect = text_surface.get_rect(center=(x, y))

        for dx, dy in offsets:
            self.buffer.blit(stroke_surface, (text_rect.x + dx, text_rect.y + dy))

        # 绘制填充文字（中间白色）
        self.buffer.blit(text_surface, text_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                self.button_hover = self.button_rect.collidepoint(event.pos)
                self.why_button_hover = self.why_button_rect.collidepoint(event.pos)
                self.credits_button_hover = self.credits_button_rect.collidepoint(event.pos)
                self.music_button_hover = self.music_button_rect.collidepoint(event.pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.button_rect.collidepoint(event.pos):
                    self.button_click = True
                    return "main"  # 返回主界面
                if self.why_button_rect.collidepoint(event.pos):
                    self.why_button_click = True
                    return "why"  # 返回为什么报考广外界面
                if self.credits_button_rect.collidepoint(event.pos):
                    return "credits"  # 返回制作人员界面
                if self.music_button_rect.collidepoint(event.pos):
                    return "music"  # 返回音乐播放器界面

            if event.type == pygame.MOUSEBUTTONUP:
                self.button_click = False
                self.why_button_click = False

        return None


class CampusNavigation:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        pygame.display.set_caption("广东外语外贸大学校园导航系统")

        # 使用支持中文的字体
        self.font = get_chinese_font(18)
        self.small_font = get_chinese_font(14)
        self.large_font = get_chinese_font(24)

        # 状态
        self.start_node = None
        self.end_node = None
        self.path = []
        self.selected_node = None
        self.hover_node = None
        self.back_button_hover = False

        # 当前激活的功能面板
        self.active_panel = None  # None, "info", "components", "simulation", "top5"

        # 模拟模式状态
        self.in_simulation_mode = False  # 是否处于模拟模式

        # 按钮（集中在左侧，与启动界面统一）
        self.back_button_rect = pygame.Rect(50, 340, 120, 40)

        # 新功能按钮（竖向排列）
        self.btn_info_rect = pygame.Rect(50, 395, 120, 36)
        self.btn_components_rect = pygame.Rect(50, 440, 120, 36)
        self.btn_simulation_rect = pygame.Rect(50, 485, 120, 36)
        self.btn_top5_rect = pygame.Rect(50, 530, 120, 36)
        self.btn_tour_rect = pygame.Rect(50, 580, 120, 36)  # 打卡路线
        self.btn_exchange_rect = pygame.Rect(50, 625, 120, 36)  # 换乘推荐

        self.btn_info_hover = False
        self.btn_components_hover = False
        self.btn_simulation_hover = False
        self.btn_top5_hover = False
        self.btn_tour_hover = False
        self.btn_exchange_hover = False

        # 删除道路功能按钮和状态（右下角）
        self.btn_delete_road_rect = pygame.Rect(0, 0, 120, 36)
        self.btn_delete_road_rect.bottomright = (self.screen_width - 50, self.screen_height - 120)
        self.btn_delete_road_hover = False
        self.in_delete_road_mode = False  # 是否处于删除道路模式
        self.delete_road_node1 = None  # 删除道路选择的第一个节点
        self.delete_road_node2 = None  # 删除道路选择的第二个节点

        # 添加道路功能按钮和状态（右下角）
        self.btn_add_road_rect = pygame.Rect(0, 0, 120, 36)
        self.btn_add_road_rect.bottomright = (self.screen_width - 50, self.screen_height - 75)
        self.btn_add_road_hover = False
        self.in_add_road_mode = False  # 是否处于添加道路模式
        self.add_road_node1 = None  # 添加道路选择的第一个节点
        self.add_road_node2 = None  # 添加道路选择的第二个节点
        self.add_road_distance = ""  # 添加道路的距离输入
        self.add_road_input_active = False  # 距离输入框是否激活

        # 游览模拟状态
        self.simulation_path = []
        self.simulation_distance = 0  # 单次模拟距离
        self.simulation_index = 0
        self.simulation_timer = 0

        # 历史模拟记录
        self.simulation_history = []  # 存储多次模拟记录，每个记录包含{path, distance, end_node}
        self.total_distance = 0  # 累计路径长度

        # 连通分量结果
        self.components_result = []

        # 存储地点信息
        self.selected_location_info = None

        # 时间模拟
        self.time_sim = TimeSimulation()
        self.time_panel = TimePanel(screen, self.font, self.small_font)

        # 设置活动地点数据
        # 第一食堂（节点13，坐标400,380）：11:00-13:00 吃饭送酸奶
        self.time_sim.set_location_data(13, locations_pos[13])
        # 艺术楼（节点8，坐标400,80）：19:00-21:00 歌唱比赛演出
        self.time_sim.add_activity("艺术楼活动", "歌唱比赛演出", 19, 21, 8, locations_pos[8], "高雅人士欣赏后很满意")
        # gogo新天地（节点22，坐标300,440）：18:00-22:00 随机活动，触发距离500m
        self.time_sim.add_random_activity("gogo新天地活动",
                                          ["《洛克王国》线下活动", "《原神x脆脆鲨》联动活动"],
                                          18, 22, 22, locations_pos[22], 500,
                                          ["参与活动得到了迪莫挂件和其他精灵周边",
                                           "谁不想急头白脸的边炫脆脆鲨边启动原神呢"])

        # 当前玩家位置（用于活动检测）
        self.player_pos = None
        self.transfer_message = ""  # 换乘提示文本

    def dijkstra(self, start, end):
        # 使用Python实现Dijkstra算法
        # 根据 edges 中实际最大顶点编号动态分配邻接表大小
        max_vertex = max(max(u, v) for u, v, w in edges) + 1 if edges else 30
        graph = [[] for _ in range(max_vertex)]
        for u, v, w in edges:
            graph[u].append((v, w))
            graph[v].append((u, w))

        # Dijkstra算法
        import heapq
        INF = float('inf')
        dist = [INF] * max_vertex
        prev = [-1] * max_vertex
        dist[start] = 0
        heap = [(0, start)]

        while heap:
            d, u = heapq.heappop(heap)
            if u == end:
                break
            if d > dist[u]:
                continue
            for v, w in graph[u]:
                if dist[v] > dist[u] + w:
                    dist[v] = dist[u] + w
                    prev[v] = u
                    heapq.heappush(heap, (dist[v], v))

        # 重构路径
        path_list = []
        if dist[end] != INF:
            curr = end
            while curr != -1:
                path_list.append(curr)
                curr = prev[curr]
            path_list.reverse()

        return path_list, dist[end]

    def calculate_path_distance(self, path):
        # 计算路径总距离
        total = 0
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            for w1, v1, weight in edges:
                if (w1 == u and v1 == v) or (w1 == v and v1 == u):
                    total += weight
                    break
        return total

    def find_connected_components(self):
        """使用DFS查找连通分量"""
        max_vertex = max(max(u, v) for u, v, w in edges) + 1 if edges else 30
        visited = [False] * max_vertex
        components = []

        def dfs(node, component):
            visited[node] = True
            component.append(node)
            for neighbor, _ in graph[node]:
                if not visited[neighbor]:
                    dfs(neighbor, component)

        # 构建邻接表
        graph = [[] for _ in range(max_vertex)]
        for u, v, w in edges:
            graph[u].append((v, w))
            graph[v].append((u, w))

        for i in range(1, max_vertex):
            if not visited[i]:
                component = []
                dfs(i, component)
                if component:
                    components.append(sorted(component))

        return components

    def get_location_info(self, node_id):
        """从DLL获取地点详细信息"""
        if dll is None:
            return None

        info = VertexInfo()
        # Python索引是0-based，DLL也是0-based，直接传递
        if dll.GetVertexInfo(node_id, ctypes.byref(info)) == 1:
            return {
                'id': info.id,
                'name': info.name.decode('gbk', errors='ignore'),
                'description': info.description.decode('gbk', errors='ignore'),
                'visits': info.timeOfVisit
            }
        return None

    # 推荐路线
    def plan_tour(self, start_node):

        if start_node is None or start_node < 1 or start_node > len(locations) - 1:
            return [], 0

        unvisited = set(range(1, len(locations)))  # 1~33
        unvisited.remove(start_node)
        tour_path = [start_node]
        total_dist = 0
        current = start_node

        while unvisited:
            # 找出当前节点到所有未访问节点的最短距离，选择最近的一个
            nearest = None
            min_dist = float('inf')
            for v in unvisited:
                path, dist = self.dijkstra(current, v)
                if dist < min_dist:
                    min_dist = dist
                    nearest = v
            if nearest is None:  # 无法到达（图不连通）
                break
            # 记录距离和路径
            total_dist += min_dist
            tour_path.append(nearest)
            unvisited.remove(nearest)
            current = nearest

        return tour_path, total_dist

    # 换乘
    def disconnected_tour(self):
        """
        分析所有连通分量，为每个分量生成内部游览路线并计算总距离，
        同时给出分量间换乘提示。
        返回一个字典：{
            'component_count': int,
            'components': [ [节点列表], ... ],
            'component_distances': [ 每个分量的内部游览距离, ... ],
            'total_distance': int
        }
        """
        # 1. 用DFS找连通分量
        visited = [False] * len(locations)
        components = []

        def dfs(node, comp):
            visited[node] = True
            comp.append(node)
            # 遍历邻接边（基于edges）
            for u, v2, w in edges:
                if u == node and not visited[v2]:
                    dfs(v2, comp)
                elif v2 == node and not visited[u]:
                    dfs(u, comp)

        for i in range(1, len(locations)):
            if not visited[i]:
                comp = []
                dfs(i, comp)
                components.append(sorted(comp))

        # 2. 对每个分量，计算内部"打卡路线"（从分量内第一个点出发，贪心走遍分量内所有点）
        component_distances = []
        for comp in components:
            if len(comp) == 1:
                component_distances.append(0)
                continue
            # 从第一个点出发
            start = comp[0]
            unvisited = set(comp)
            unvisited.remove(start)
            current = start
            dist_sum = 0
            while unvisited:
                nearest = None
                min_d = float('inf')
                for v in unvisited:
                    _, d = self.dijkstra(current, v)
                    if d < min_d:
                        min_d = d
                        nearest = v
                if nearest is None:
                    break
                dist_sum += min_d
                unvisited.remove(nearest)
                current = nearest
            component_distances.append(dist_sum)

        total_distance = sum(component_distances)

        return {
            'component_count': len(components),
            'components': components,
            'component_distances': component_distances,
            'total_distance': total_distance
        }

    def run_simulation(self, start, end):
        """运行游览模拟"""
        try:
            if dll is None:
                print("DLL not loaded", flush=True)
                return [], 0

            # Python索引是0-based，DLL内部vertex数组也是0-based（根据用户反馈）
            # 所以直接传递Python索引，不需要+1转换
            dll_start = start
            dll_end = end
            print(f"\n=== 游览模拟 ===", flush=True)
            print(f"Python索引: start={start}, end={end}", flush=True)
            print(f"DLL索引: start={dll_start}, end={dll_end}", flush=True)

            # 使用Python端的Dijkstra算法计算最短路径（已验证正确）
            path, distance = self.dijkstra(start, end)

            if path:
                print(f"路径: {' -> '.join([locations[i] for i in path])}", flush=True)
                print(f"距离: {distance} 米", flush=True)

                # 调用DLL的SimulateOneTrip更新访问次数
                # 直接传递Python索引（0-based）给DLL
                path_len = ctypes.c_int()
                dll_path = (ctypes.c_int * 100)()

                # 记录调用前的访问次数
                info_before = self.get_location_info(end)  # 使用Python索引
                print(f"调用前 - 终点[{end}] {info_before['name']} 的访问次数: {info_before['visits']}", flush=True)

                dll.SimulateOneTrip(dll_start, dll_end, dll_path, ctypes.byref(path_len))

                # 记录调用后的访问次数
                info_after = self.get_location_info(end)  # 使用Python索引
                print(f"调用后 - 终点[{end}] {info_after['name']} 的访问次数: {info_after['visits']}", flush=True)

                return path, distance
            return [], 0
        except Exception as e:
            print(f"Simulation error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return [], 0

    def run_and_record_simulation(self):
        """运行模拟并记录结果"""
        path, _ = self.run_simulation(self.start_node, self.end_node)
        if path:
            self.simulation_path = path
            # 在Python端计算路径距离
            self.simulation_distance = self.calculate_path_distance(path)
            # 添加到历史记录
            self.simulation_history.append({
                'path': path,
                'distance': self.simulation_distance,
                'end_node': self.end_node
            })
            # 更新累计距离
            self.total_distance += self.simulation_distance
            # 更新时间模拟器的距离
            self.time_sim.add_distance(self.simulation_distance)

    def get_top5_hotspots(self):
        """获取访问次数Top5"""
        if dll is None:
            print("DLL not loaded for get_top5_hotspots", flush=True)
            return []

        try:
            hotspots = (VertexInfo * 5)()
            result_code = dll.GetTop5Hotspots(hotspots)
            print(f"GetTop5Hotspots result (count): {result_code}", flush=True)

            result = []
            for i in range(result_code):  # 使用实际返回的数量，而不是固定5个
                print(f"Hotspot {i}: id={hotspots[i].id}, name={hotspots[i].name}, visits={hotspots[i].timeOfVisit}",
                      flush=True)
                if hotspots[i].id > 0:
                    result.append({
                        'id': hotspots[i].id - 1,  # 转换为0-based索引
                        'name': hotspots[i].name.decode('gbk', errors='ignore'),
                        'visits': hotspots[i].timeOfVisit
                    })
            return result
        except Exception as e:
            print(f"get_top5_hotspots error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return []

    def delete_road(self, node1, node2):
        """删除道路：调用DLL并更新edges列表"""
        global edges

        if dll is None:
            print("DLL not loaded for delete_road", flush=True)
            return False

        try:
            print(f"\n=== 删除道路 ===", flush=True)
            print(f"节点1: {node1} ({locations[node1]})", flush=True)
            print(f"节点2: {node2} ({locations[node2]})", flush=True)

            # 调用DLL的DeleteRoad函数
            result = dll.DeleteRoad(node1, node2)
            print(f"DLL DeleteRoad result: {result}", flush=True)

            if result == 1:
                # 成功删除，更新本地edges列表
                # 从edges列表中移除该边
                edges_to_remove = []
                for u, v, w in edges:
                    if (u == node1 and v == node2) or (u == node2 and v == node1):
                        edges_to_remove.append((u, v, w))

                for edge in edges_to_remove:
                    edges.remove(edge)
                    print(f"从本地edges列表中移除边: {edge}", flush=True)

                print(f"成功删除道路 {node1}-{node2}", flush=True)
                print(f"当前edges列表长度: {len(edges)}", flush=True)
                return True
            else:
                print(f"删除失败，可能不存在该道路", flush=True)
                return False

        except Exception as e:
            print(f"delete_road error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return False

    def add_road(self, node1, node2, distance):
        """添加道路：调用DLL并更新edges列表"""
        global edges

        if dll is None:
            print("DLL not loaded for add_road", flush=True)
            return False

        try:
            print(f"\n=== 添加道路 ===", flush=True)
            print(f"节点1: {node1} ({locations[node1]})", flush=True)
            print(f"节点2: {node2} ({locations[node2]})", flush=True)
            print(f"距离: {distance}", flush=True)

            # 调用DLL的AddNewRoad函数
            result = dll.AddNewRoad(node1, node2, distance)
            print(f"DLL AddNewRoad result: {result}", flush=True)

            if result == 1:
                # 成功添加，更新本地edges列表
                # 确保边的顺序是小的在前，避免重复
                u, v = (node1, node2) if node1 < node2 else (node2, node1)
                new_edge = (u, v, distance)

                # 检查是否已存在该边
                exists = False
                for edge in edges:
                    if (edge[0] == u and edge[1] == v) or (edge[0] == v and edge[1] == u):
                        exists = True
                        break

                if not exists:
                    edges.append(new_edge)
                    print(f"添加新边到本地edges列表: {new_edge}", flush=True)
                    print(f"当前edges列表长度: {len(edges)}", flush=True)
                    return True
                else:
                    print(f"该道路已存在，无需重复添加", flush=True)
                    return False
            else:
                print(f"D添加失败，可能参数错误", flush=True)
                return False

        except Exception as e:
            print(f"add_road error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return False

    def draw_feature_buttons(self):
        """绘制功能按钮"""
        # 地点信息按钮
        self.draw_modern_ui_button(self.btn_info_rect, "地点信息", hover=self.btn_info_hover)

        # 连通分量按钮
        self.draw_modern_ui_button(self.btn_components_rect, "连通分量", hover=self.btn_components_hover)

        # 游览模拟按钮
        self.draw_modern_ui_button(self.btn_simulation_rect, "游览模拟", hover=self.btn_simulation_hover)

        # Top5按钮
        self.draw_modern_ui_button(self.btn_top5_rect, "访问Top5", hover=self.btn_top5_hover)

        # 打卡路线按钮
        self.draw_modern_ui_button(self.btn_tour_rect, "打卡路线", hover=self.btn_tour_hover)

        # 换乘推荐按钮
        self.draw_modern_ui_button(self.btn_exchange_rect, "换乘推荐", hover=self.btn_exchange_hover)

        # 删除道路按钮
        self.draw_modern_ui_button(self.btn_delete_road_rect, "删除道路", hover=self.btn_delete_road_hover)

        # 添加道路按钮
        self.draw_modern_ui_button(self.btn_add_road_rect, "添加道路", hover=self.btn_add_road_hover)

    def draw_info_panel(self, info, x, y):
        """绘制地点信息面板"""
        if info is None:
            return y

        panel_width = 300
        panel_height = 180
        pygame.draw.rect(self.screen, WHITE, (x, y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(self.screen, BLUE, (x, y, panel_width, panel_height), 2, border_radius=10)

        title = self.font.render("地点信息", True, DARK_BLUE)
        self.screen.blit(title, (x + 10, y + 10))
        pygame.draw.line(self.screen, BLUE, (x + 10, y + 35), (x + panel_width - 10, y + 35))

        name_text = f"名称: {info['name']}"
        id_text = f"编号: {info['id']}"
        visits_text = f"访问次数: {info['visits']}"

        self.screen.blit(self.small_font.render(name_text, True, BLACK), (x + 15, y + 45))
        self.screen.blit(self.small_font.render(id_text, True, BLACK), (x + 15, y + 70))
        self.screen.blit(self.small_font.render(visits_text, True, BLACK), (x + 15, y + 95))

        # 描述（换行显示）
        desc = info['description']
        if desc:
            desc_lines = []
            words = ""
            for char in desc:
                if self.small_font.size(words + char)[0] > panel_width - 30:
                    desc_lines.append(words)
                    words = char
                else:
                    words += char
            if words:
                desc_lines.append(words)

            line_y = y + 120
            for line in desc_lines[:3]:
                if line_y < y + panel_height - 10:
                    self.screen.blit(self.small_font.render(line, True, GRAY), (x + 15, line_y))
                    line_y += 18

        return y + panel_height + 10

    def draw_components_panel(self, x, y):
        """绘制连通分量分析面板"""
        components = self.find_connected_components()

        panel_width = 300
        panel_height = 50 + len(components) * 35 + 20
        pygame.draw.rect(self.screen, WHITE, (x, y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(self.screen, GREEN, (x, y, panel_width, panel_height), 2, border_radius=10)

        title = self.font.render("连通分量分析", True, DARK_BLUE)
        self.screen.blit(title, (x + 10, y + 10))
        pygame.draw.line(self.screen, GREEN, (x + 10, y + 35), (x + panel_width - 10, y + 35))

        info_text = f"共 {len(components)} 个连通分量"
        self.screen.blit(self.small_font.render(info_text, True, BLACK), (x + 15, y + 45))

        line_y = y + 70
        for i, comp in enumerate(components):
            nodes_str = ", ".join([locations[n] for n in comp])
            text = f"分量{i + 1}: {nodes_str}"
            # 简化显示
            short_text = text[:25] + "..." if len(text) > 25 else text
            self.screen.blit(self.small_font.render(short_text, True, BLUE), (x + 15, line_y))
            line_y += 22

        return y + panel_height + 10

    def draw_simulation_panel(self, x, y):
        """绘制游览模拟面板"""
        # 根据内容调整面板高度
        panel_width = 300
        panel_height = 180 + len(self.simulation_history) * 30

        pygame.draw.rect(self.screen, WHITE, (x, y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(self.screen, PURPLE, (x, y, panel_width, panel_height), 2, border_radius=10)

        # 标题和模式状态
        title = self.font.render("游览模拟", True, DARK_BLUE)
        self.screen.blit(title, (x + 10, y + 10))

        # 模式状态指示器
        mode_text = "模拟中" if self.in_simulation_mode else "已关闭"
        mode_color = GREEN if self.in_simulation_mode else RED
        mode_label = self.small_font.render(f"模式: {mode_text}", True, mode_color)
        self.screen.blit(mode_label, (x + 150, y + 12))

        pygame.draw.line(self.screen, PURPLE, (x + 10, y + 35), (x + panel_width - 10, y + 35))

        current_y = y + 45

        # 显示当前模拟结果
        if self.simulation_path:
            path_names = " → ".join([locations[i] for i in self.simulation_path])
            path_text = f"当前路径: {path_names[:25]}..."
            self.screen.blit(self.small_font.render(path_text, True, BLACK), (x + 15, current_y))
            current_y += 22

            dist_text = f"本次距离: {self.simulation_distance} 米"
            self.screen.blit(self.small_font.render(dist_text, True, PURPLE), (x + 15, current_y))
            current_y += 22
        else:
            tip_text = "请选择起点和终点" if self.in_simulation_mode else "点击按钮开启模拟模式"
            self.screen.blit(self.small_font.render(tip_text, True, GRAY), (x + 15, current_y))
            current_y += 22

        # 显示累计统计
        total_text = f"累计距离: {self.total_distance} 米"
        self.screen.blit(self.small_font.render(total_text, True, BLUE), (x + 15, current_y))

        # 清空按钮
        clear_button = pygame.Rect(x + panel_width - 80, current_y - 5, 70, 22)
        pygame.draw.rect(self.screen, RED, clear_button, border_radius=5)
        clear_text = self.small_font.render("清空", True, WHITE)
        self.screen.blit(clear_text, (x + panel_width - 55, current_y))
        self.clear_button_rect = clear_button  # 保存按钮位置供点击检测

        current_y += 28

        # 显示历史记录
        if self.simulation_history:
            history_title = self.font.render("历史记录", True, DARK_BLUE)
            self.screen.blit(history_title, (x + 15, current_y))
            current_y += 18

            for i, record in enumerate(reversed(self.simulation_history[-5:])):  # 只显示最近5条
                end_name = locations[record['end_node']]
                record_text = f"→ {end_name} ({record['distance']}米)"
                self.screen.blit(self.small_font.render(record_text, True, GRAY), (x + 20, current_y))
                current_y += 20

        return current_y + 10

    def draw_top5_panel(self, x, y):
        """绘制Top5访问次数面板"""
        hotspots = self.get_top5_hotspots()

        panel_width = 300
        panel_height = 180
        pygame.draw.rect(self.screen, WHITE, (x, y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(self.screen, ORANGE, (x, y, panel_width, panel_height), 2, border_radius=10)

        title = self.font.render("访问次数Top5", True, DARK_BLUE)
        self.screen.blit(title, (x + 10, y + 10))
        pygame.draw.line(self.screen, ORANGE, (x + 10, y + 35), (x + panel_width - 10, y + 35))

        if hotspots:
            line_y = y + 50
            # 使用数字序号而不是emoji，避免显示方块
            for i, spot in enumerate(hotspots):
                text = f"{i + 1}. {spot['name']}: {spot['visits']}次"
                self.screen.blit(self.small_font.render(text, True, BLACK), (x + 15, line_y))
                line_y += 25
        else:
            self.screen.blit(self.small_font.render("暂无数据", True, GRAY), (x + 15, y + 50))

        return y + panel_height + 10

    def draw_gradient_background(self):
        # 从上到下的渐变
        for y in range(self.screen_height):
            r = 245 - y // 50
            g = 248 - y // 50
            b = 252 - y // 50
            if r < 200: r = 200
            if g < 200: g = 200
            if b < 220: b = 220
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))

        # 绘制网格
        grid_size = 50
        for x in range(0, self.screen_width, grid_size):
            pygame.draw.line(self.screen, (220, 230, 245), (x, 0), (x, self.screen_height))
        for y in range(0, self.screen_height, grid_size):
            pygame.draw.line(self.screen, (220, 230, 245), (0, y), (self.screen_width, y))

    def draw_title_bar(self):
        # 现代风格标题栏
        # 渐变背景
        bar_height = 50
        for y in range(bar_height):
            ratio = y / bar_height
            r = int(66 * (1 - ratio * 0.2))
            g = int(153 * (1 - ratio * 0.2))
            b = int(225 * (1 - ratio * 0.2))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))

        # 标题栏底部阴影
        shadow_surface = pygame.Surface((self.screen_width, 5), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 30), shadow_surface.get_rect())
        self.screen.blit(shadow_surface, (0, bar_height))

        # 现代标题文字
        title_text = self.large_font.render("GDUFS Campus Navigator", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, bar_height // 2))
        self.screen.blit(title_text, title_rect)

        # 现代装饰图标
        # 定位图标
        icon_size = 20
        icon_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        pygame.draw.circle(icon_surface, (255, 193, 7), (icon_size // 2, icon_size // 2), icon_size // 2 - 2)
        pygame.draw.circle(icon_surface, (255, 255, 255), (icon_size // 2, icon_size // 2), icon_size // 4)
        self.screen.blit(icon_surface, (20, bar_height // 2 - icon_size // 2))

    def draw_edges(self):
        max_vertex = len(locations_pos) - 1  # 最大有效索引
        for u, v, w in edges:
            # 跳过超出 locations_pos 范围的顶点
            if u > max_vertex or v > max_vertex:
                continue
            x1, y1 = locations_pos[u]
            x2, y2 = locations_pos[v]

            is_path = False
            for i in range(len(self.path) - 1):
                if (self.path[i] == u and self.path[i + 1] == v) or \
                        (self.path[i] == v and self.path[i + 1] == u):
                    is_path = True
                    break

            if is_path:
                color = RED
                width = 4
            else:
                color = (150, 170, 200)
                width = 2

            # 绘制渐变线条
            self.draw_gradient_line(x1, y1, x2, y2, color, width)

            # 绘制距离标签（非路径边）
            if not is_path:
                mid_x = (x1 + x2) // 2
                mid_y = (y1 + y2) // 2
                # 标签背景
                pygame.draw.rect(self.screen, WHITE, (mid_x - 15, mid_y - 12, 30, 20), border_radius=5)
                pygame.draw.rect(self.screen, GRAY, (mid_x - 15, mid_y - 12, 30, 20), 1, border_radius=5)
                text = self.small_font.render(str(w), True, DARK_BLUE)
                self.screen.blit(text, (mid_x - 8, mid_y - 10))

    def draw_gradient_line(self, x1, y1, x2, y2, color, width):
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx * dx + dy * dy)
        steps = int(length / 5)

        for i in range(steps):
            t = i / steps
            x = int(x1 + dx * t)
            y = int(y1 + dy * t)
            alpha = int(150 + 105 * t)
            pygame.draw.circle(self.screen, (color[0], color[1], color[2], alpha), (x, y), width)

    def draw_path(self):
        max_vertex = len(locations_pos) - 1
        for i in range(len(self.path) - 1):
            u = self.path[i]
            v = self.path[i + 1]
            if u > max_vertex or v > max_vertex:
                continue
            x1, y1 = locations_pos[u]
            x2, y2 = locations_pos[v]

            pygame.draw.line(self.screen, RED, (x1, y1), (x2, y2), 4)
            pygame.draw.line(self.screen, (255, 150, 150), (x1, y1), (x2, y2), 2)

            # 箭头
            angle = math.atan2(y2 - y1, x2 - x1)
            arrow_size = 12
            pygame.draw.polygon(self.screen, RED, [
                (x2 - arrow_size * math.cos(angle - 0.4), y2 - arrow_size * math.sin(angle - 0.4)),
                (x2, y2),
                (x2 - arrow_size * math.cos(angle + 0.4), y2 - arrow_size * math.sin(angle + 0.4))
            ])

    def draw_nodes(self):
        for i, (x, y) in enumerate(locations_pos):
            # 删除道路模式下的选中节点显示特殊颜色
            if self.in_delete_road_mode and i == self.delete_road_node1:
                color = (255, 0, 255)  # 紫色，表示删除道路选中的第一个节点
                radius = 18
            elif self.in_delete_road_mode and i == self.delete_road_node2:
                color = (255, 0, 255)  # 紫色，表示删除道路选中的第二个节点
                radius = 18
            # 添加道路模式下的选中节点显示特殊颜色
            elif self.in_add_road_mode and i == self.add_road_node1:
                color = (0, 255, 255)  # 青色，表示添加道路选中的第一个节点
                radius = 18
            elif self.in_add_road_mode and i == self.add_road_node2:
                color = (0, 255, 255)  # 青色，表示添加道路选中的第二个节点
                radius = 18
            elif i == self.selected_node:
                color = YELLOW
                radius = 18
            elif i == self.hover_node:
                color = LIGHT_BLUE
                radius = 14
            elif i == self.start_node:
                color = GREEN
                radius = 14
            elif i == self.end_node:
                color = RED
                radius = 14
            else:
                color = BLUE
                radius = 12

            # 节点光晕效果
            glow_radius = radius + 6
            for r in range(glow_radius, radius, -2):
                alpha = int(25 * (1 - (r - radius) / 6))
                pygame.draw.circle(self.screen, (color[0], color[1], color[2], alpha), (x, y), r)

            # 节点主体
            pygame.draw.circle(self.screen, color, (x, y), radius)
            pygame.draw.circle(self.screen, BLACK, (x, y), radius, 2)

            # 节点编号
            num_text = self.small_font.render(str(i), True, BLACK)
            self.screen.blit(num_text, (x - 5, y - 5))

            # 节点名称（带背景框）
            name_text = self.font.render(locations[i], True, BLACK)
            text_width = name_text.get_width()
            pygame.draw.rect(self.screen, WHITE,
                             (x - text_width // 2 - 5, y + radius + 8, text_width + 10, 22),
                             border_radius=5)
            pygame.draw.rect(self.screen, GRAY,
                             (x - text_width // 2 - 5, y + radius + 8, text_width + 10, 22),
                             1, border_radius=5)
            text_rect = name_text.get_rect(center=(x, y + radius + 19))
            self.screen.blit(name_text, text_rect)

    def draw_modern_button(self, rect, text, hover, click, primary=True):
        # 透明风格UI按钮（与启动界面统一）
        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # 根据hover状态设置透明度
        if hover:
            alpha = 120
            text_color = (200, 200, 200)
            stroke_color = (30, 50, 100)
        else:
            alpha = 60
            text_color = (255, 255, 255)
            stroke_color = (20, 40, 80)

        # 绘制透明边框
        pygame.draw.rect(button_surface, (255, 255, 255, alpha), button_surface.get_rect(), 2, border_radius=10)

        # 内边框效果
        inner_rect = pygame.Rect(2, 2, rect.width - 4, rect.height - 4)
        pygame.draw.rect(button_surface, (255, 255, 255, alpha // 2), inner_rect, 1, border_radius=8)

        self.screen.blit(button_surface, rect)

        # 按钮文字 - 描边效果（中间白，边缘深蓝）
        self.draw_stroked_text(text, rect.center, text_color, stroke_color, self.font)

    def draw_modern_ui_button(self, rect, text, primary=True, hover=False):
        # 透明风格UI按钮
        # 按钮主体 - 完全透明，只有边框
        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # 根据hover状态设置透明度
        if hover:
            alpha = 120
            text_color = (200, 200, 200)
            stroke_color = (30, 50, 100)
        else:
            alpha = 60
            text_color = (255, 255, 255)
            stroke_color = (20, 40, 80)

        # 绘制透明边框
        pygame.draw.rect(button_surface, (255, 255, 255, alpha), button_surface.get_rect(), 2, border_radius=10)

        # 内边框效果
        inner_rect = pygame.Rect(2, 2, rect.width - 4, rect.height - 4)
        pygame.draw.rect(button_surface, (255, 255, 255, alpha // 2), inner_rect, 1, border_radius=8)

        self.screen.blit(button_surface, rect)

        # 按钮文字 - 描边效果（中间白，边缘深蓝）
        self.draw_stroked_text(text, rect.center, text_color, stroke_color, self.font)

    def draw_stroked_text(self, text, center, fill_color, stroke_color, font):
        # 绘制描边文字（中间白，边缘深蓝）
        text_surface = font.render(text, True, fill_color)
        stroke_surface = font.render(text, True, stroke_color)

        # 绘制描边（8个方向）
        offsets = [(-2, -2), (-2, 0), (-2, 2),
                   (0, -2), (0, 2),
                   (2, -2), (2, 0), (2, 2)]

        x, y = center
        text_rect = text_surface.get_rect(center=(x, y))

        for dx, dy in offsets:
            self.screen.blit(stroke_surface, (text_rect.x + dx, text_rect.y + dy))

        # 绘制填充文字（中间白色）
        self.screen.blit(text_surface, text_rect)

    #推荐路线
    def draw_tour_panel(self, x, y):
        """绘制打卡路线推荐面板"""
        # 如果没有选择起点，提示
        if self.start_node is None:
            panel_width, panel_height = 300, 100
            pygame.draw.rect(self.screen, WHITE, (x, y, panel_width, panel_height), border_radius=10)
            pygame.draw.rect(self.screen, BLUE, (x, y, panel_width, panel_height), 2, border_radius=10)
            tip = self.font.render("请先选择起点", True, DARK_BLUE)
            self.screen.blit(tip, (x + 20, y + 40))
            return

        tour_path, total_dist = self.plan_tour(self.start_node)
        if not tour_path:
            panel_width, panel_height = 300, 100
            pygame.draw.rect(self.screen, WHITE, (x, y, panel_width, panel_height), border_radius=10)
            pygame.draw.rect(self.screen, BLUE, (x, y, panel_width, panel_height), 2, border_radius=10)
            tip = self.font.render("无法规划路线", True, RED)
            self.screen.blit(tip, (x + 20, y + 40))
            return

        # 计算面板高度（按行数）
        lines = len(tour_path) + 3  # 标题 + 总距离 + 路径行
        panel_height = 50 + lines * 22
        panel_width = 300
        pygame.draw.rect(self.screen, WHITE, (x, y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(self.screen, BLUE, (x, y, panel_width, panel_height), 2, border_radius=10)

        title = self.font.render("校园打卡路线", True, DARK_BLUE)
        self.screen.blit(title, (x + 10, y + 10))
        pygame.draw.line(self.screen, BLUE, (x + 10, y + 35), (x + panel_width - 10, y + 35))

        current_y = y + 45
        # 显示总距离
        dist_text = f"总距离: {total_dist} 米"
        self.screen.blit(self.small_font.render(dist_text, True, PURPLE), (x + 15, current_y))
        current_y += 22

        # 显示路径（换行）
        path_names = [locations[i] for i in tour_path]
        line = ""
        for name in path_names:
            if len(line) + len(name) > 18:
                self.screen.blit(self.small_font.render(line, True, BLACK), (x + 15, current_y))
                current_y += 20
                line = name
            else:
                if line:
                    line += " → "
                line += name
        if line:
            self.screen.blit(self.small_font.render(line, True, BLACK), (x + 15, current_y))

    #换乘
    def draw_exchange_panel(self, x, y):
        """绘制换乘后路线推荐面板"""
        result = self.disconnected_tour()
        comp_count = result['component_count']
        components = result['components']
        comp_dists = result['component_distances']
        total = result['total_distance']

        # 计算面板高度
        lines = 3 + sum(len(comp) for comp in components) + comp_count
        panel_height = 50 + lines * 20
        panel_width = 300
        pygame.draw.rect(self.screen, WHITE, (x, y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(self.screen, GREEN, (x, y, panel_width, panel_height), 2, border_radius=10)

        title = self.font.render("换乘后路线推荐", True, DARK_BLUE)
        self.screen.blit(title, (x + 10, y + 10))
        pygame.draw.line(self.screen, GREEN, (x + 10, y + 35), (x + panel_width - 10, y + 35))

        current_y = y + 45
        info_text = f"共有 {comp_count} 个连通分量"
        self.screen.blit(self.small_font.render(info_text, True, BLACK), (x + 15, current_y))
        current_y += 22

        for i, comp in enumerate(components):
            nodes_str = ", ".join([locations[n] for n in comp])
            text = f"分量{i + 1}: {nodes_str[:20]}..."
            self.screen.blit(self.small_font.render(text, True, BLUE), (x + 15, current_y))
            current_y += 18
            dist_str = f"  内部游览距离: {comp_dists[i]} 米"
            self.screen.blit(self.small_font.render(dist_str, True, GRAY), (x + 20, current_y))
            current_y += 20
            if i < comp_count - 1:
                self.screen.blit(self.small_font.render("  ↓ 换乘 ↓", True, ORANGE), (x + 20, current_y))
                current_y += 20

        total_text = f"总游览距离: {total} 米"
        self.screen.blit(self.small_font.render(total_text, True, PURPLE), (x + 15, current_y))

    def draw_delete_road_panel(self, x, y):
        """绘制删除道路面板"""
        panel_width = 300
        panel_height = 150
        pygame.draw.rect(self.screen, WHITE, (x, y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(self.screen, RED, (x, y, panel_width, panel_height), 2, border_radius=10)

        title = self.font.render("删除道路", True, DARK_BLUE)
        self.screen.blit(title, (x + 10, y + 10))
        pygame.draw.line(self.screen, RED, (x + 10, y + 35), (x + panel_width - 10, y + 35))

        current_y = y + 45

        # 显示操作提示
        mode_text = "模式: 删除道路中" if self.in_delete_road_mode else "模式: 已关闭"
        mode_color = GREEN if self.in_delete_road_mode else RED
        mode_label = self.small_font.render(mode_text, True, mode_color)
        self.screen.blit(mode_label, (x + 15, current_y))
        current_y += 25

        # 显示节点选择状态
        if self.delete_road_node1 is None:
            tip1 = "请点击选择第一个节点"
            self.screen.blit(self.small_font.render(tip1, True, BLACK), (x + 15, current_y))
        else:
            node1_text = f"已选择: {locations[self.delete_road_node1]}"
            self.screen.blit(self.small_font.render(node1_text, True, BLUE), (x + 15, current_y))

        current_y += 25

        if self.delete_road_node1 is not None and self.delete_road_node2 is None:
            tip2 = "请点击选择第二个节点"
            self.screen.blit(self.small_font.render(tip2, True, BLACK), (x + 15, current_y))
        elif self.delete_road_node2 is not None:
            node2_text = f"已选择: {locations[self.delete_road_node2]}"
            self.screen.blit(self.small_font.render(node2_text, True, BLUE), (x + 15, current_y))

        current_y += 25

        # 操作说明
        tips = self.small_font.render("点击同一节点可取消选择", True, GRAY)
        self.screen.blit(tips, (x + 15, current_y))

    def draw_add_road_panel(self, x, y):
        """绘制添加道路面板"""
        panel_width = 300
        panel_height = 200
        pygame.draw.rect(self.screen, WHITE, (x, y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(self.screen, GREEN, (x, y, panel_width, panel_height), 2, border_radius=10)

        title = self.font.render("添加道路", True, DARK_BLUE)
        self.screen.blit(title, (x + 10, y + 10))
        pygame.draw.line(self.screen, GREEN, (x + 10, y + 35), (x + panel_width - 10, y + 35))

        current_y = y + 45

        # 显示操作提示
        mode_text = "模式: 添加道路中" if self.in_add_road_mode else "模式: 已关闭"
        mode_color = GREEN if self.in_add_road_mode else RED
        mode_label = self.small_font.render(mode_text, True, mode_color)
        self.screen.blit(mode_label, (x + 15, current_y))
        current_y += 25

        # 显示节点选择状态
        if self.add_road_node1 is None:
            tip1 = "请点击选择第一个节点"
            self.screen.blit(self.small_font.render(tip1, True, BLACK), (x + 15, current_y))
        else:
            node1_text = f"节点1: {locations[self.add_road_node1]}"
            self.screen.blit(self.small_font.render(node1_text, True, BLUE), (x + 15, current_y))

        current_y += 25

        if self.add_road_node1 is not None and self.add_road_node2 is None:
            tip2 = "请点击选择第二个节点"
            self.screen.blit(self.small_font.render(tip2, True, BLACK), (x + 15, current_y))
        elif self.add_road_node2 is not None:
            node2_text = f"节点2: {locations[self.add_road_node2]}"
            self.screen.blit(self.small_font.render(node2_text, True, BLUE), (x + 15, current_y))

        current_y += 25

        # 显示距离输入框
        if self.add_road_node1 is not None and self.add_road_node2 is not None:
            # 输入框提示
            input_label = self.small_font.render("距离(米):", True, BLACK)
            self.screen.blit(input_label, (x + 15, current_y))

            # 输入框
            input_rect = pygame.Rect(x + 15, current_y + 22, 270, 30)
            pygame.draw.rect(self.screen, (240, 240, 240), input_rect, border_radius=5)
            pygame.draw.rect(self.screen, BLUE, input_rect, 2, border_radius=5)

            # 输入框内容
            distance_text = self.add_road_distance if self.add_road_distance else "输入数字后回车"
            distance_color = BLACK if self.add_road_distance else GRAY
            text_surface = self.font.render(distance_text, True, distance_color)
            self.screen.blit(text_surface, (x + 20, current_y + 27))

            # 保存输入框位置用于点击检测
            self.add_road_input_rect = input_rect

            current_y += 60

            # 操作提示
            tip3 = "数字键输入，退格键删除，回车确认"
            self.screen.blit(self.small_font.render(tip3, True, GRAY), (x + 15, current_y))

    def draw_panel(self):
        # 无框导航信息
        y = 50

        # 面板标题
        title_text = self.font.render("导航信息", True, WHITE)
        self.screen.blit(title_text, (20, y))
        pygame.draw.line(self.screen, (200, 200, 255), (20, y + 22), (150, y + 22))
        y += 30

        # 起点信息
        if self.start_node is not None:
            pygame.draw.circle(self.screen, GREEN, (20, y + 8), 6)
            text = f"起点: {locations[self.start_node]}"
            self.screen.blit(self.font.render(text, True, BLACK), (35, y))
        else:
            pygame.draw.circle(self.screen, GRAY, (20, y + 8), 6)
            self.screen.blit(self.font.render("起点: 未选择", True, GRAY), (35, y))
        y += 25

        # 终点信息
        if self.end_node is not None:
            pygame.draw.circle(self.screen, RED, (20, y + 8), 6)
            text = f"终点: {locations[self.end_node]}"
            self.screen.blit(self.font.render(text, True, BLACK), (35, y))
        else:
            pygame.draw.circle(self.screen, GRAY, (20, y + 8), 6)
            self.screen.blit(self.font.render("终点: 未选择", True, GRAY), (35, y))
        y += 30

        # 路径信息
        if self.path:
            self.screen.blit(self.font.render("路径长度:", True, BLACK), (20, y))
            y += 20
            text = f"{self.path_distance} 米"
            self.screen.blit(self.font.render(text, True, PURPLE), (35, y))
            y += 20

            self.screen.blit(self.font.render("途经节点:", True, BLACK), (20, y))
            y += 18
            path_names = [locations[i] for i in self.path]
            current_line = ""
            for name in path_names:
                if len(current_line) + len(name) > 18:
                    self.screen.blit(self.small_font.render(current_line, True, BLUE), (35, y))
                    y += 16
                    current_line = name
                else:
                    if current_line:
                        current_line += " → "
                    current_line += name
            if current_line:
                self.screen.blit(self.small_font.render(current_line, True, BLUE), (35, y))
        elif self.transfer_message:
            # 显示换乘提示（红色醒目）
            self.screen.blit(self.font.render(self.transfer_message, True, RED), (20, y))
            y += 25
        else:
            self.screen.blit(self.font.render("请选择起点和终点", True, GRAY), (20, y))
            y += 20


        # 返回主界面按钮 - 统一使用draw_modern_button
        self.draw_modern_button(self.back_button_rect, "返回主界面", self.back_button_hover, False, primary=False)

        # 操作提示面板
        tips_rect = pygame.Rect(10, self.screen_height - 90, 220, 70)
        pygame.draw.rect(self.screen, WHITE, tips_rect, border_radius=10)
        pygame.draw.rect(self.screen, GRAY, tips_rect, 1, border_radius=10)

        tips_title = self.font.render("操作提示", True, DARK_BLUE)
        self.screen.blit(tips_title, (20, self.screen_height - 75))

        tip1 = self.small_font.render("左键: 设置起点/终点", True, BLACK)
        tip2 = self.small_font.render("右键: 清除选择", True, BLACK)
        tip3 = self.small_font.render("R键: 重置", True, BLACK)

        self.screen.blit(tip1, (20, self.screen_height - 55))
        self.screen.blit(tip2, (20, self.screen_height - 38))
        self.screen.blit(tip3, (20, self.screen_height - 21))

    def get_node_at_pos(self, pos):
        for i, (x, y) in enumerate(locations_pos):
            dx = pos[0] - x
            dy = pos[1] - y
            if dx * dx + dy * dy <= 30 * 30:
                return i
        return None

    def draw(self):
        # 更新时间模拟
        self.time_sim.update()

        # 绘制渐变背景
        self.draw_gradient_background()

        # 绘制所有边
        self.draw_edges()

        # 绘制路径
        if self.path:
            self.draw_path()

        # 绘制所有节点
        self.draw_nodes()

        # 绘制信息面板
        self.draw_panel()

        # 绘制功能按钮
        self.draw_feature_buttons()

        # 根据激活的面板绘制额外信息
        if self.active_panel == "info" and self.selected_location_info:
            self.draw_info_panel(self.selected_location_info, self.screen_width - 320, 60)
        elif self.active_panel == "components":
            self.draw_components_panel(self.screen_width - 320, 60)
        elif self.active_panel == "simulation":
            self.draw_simulation_panel(self.screen_width - 320, 60)
        elif self.active_panel == "top5":
            self.draw_top5_panel(self.screen_width - 320, 60)
        elif self.active_panel == "tour":
            self.draw_tour_panel(self.screen_width - 320, 60)
        elif self.active_panel == "exchange":
            self.draw_exchange_panel(self.screen_width - 320, 60)
        elif self.active_panel == "delete_road":
            self.draw_delete_road_panel(self.screen_width - 320, 60)
        elif self.active_panel == "add_road":
            self.draw_add_road_panel(self.screen_width - 320, 60)

        # 绘制标题栏
        self.draw_title_bar()

        # 绘制时间面板
        self.time_panel.draw(self.time_sim, self.total_distance)

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                self.hover_node = self.get_node_at_pos(event.pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                node = self.get_node_at_pos(event.pos)

                if event.button == 1:
                    if node is not None:
                        if self.start_node is None:
                            self.start_node = node
                            self.end_node = None
                            self.path = []
                            self.path_distance = 0
                        elif self.end_node is None and node != self.start_node:
                            self.end_node = node
                            self.path, self.path_distance = self.dijkstra(self.start_node, self.end_node)
                        else:
                            self.start_node = node
                            self.end_node = None
                            self.path = []
                            self.path_distance = 0

                if event.button == 3:
                    if node is not None:
                        if node == self.start_node:
                            self.start_node = None
                        elif node == self.end_node:
                            self.end_node = None
                        self.path = []

    def handle_events_with_return(self):
        result = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                self.hover_node = self.get_node_at_pos(event.pos)
                # 检查按钮hover状态
                self.back_button_hover = self.back_button_rect.collidepoint(event.pos)
                self.btn_info_hover = self.btn_info_rect.collidepoint(event.pos)
                self.btn_components_hover = self.btn_components_rect.collidepoint(event.pos)
                self.btn_simulation_hover = self.btn_simulation_rect.collidepoint(event.pos)
                self.btn_top5_hover = self.btn_top5_rect.collidepoint(event.pos)
                self.btn_tour_hover = self.btn_tour_rect.collidepoint(event.pos)
                self.btn_exchange_hover = self.btn_exchange_rect.collidepoint(event.pos)
                self.btn_delete_road_hover = self.btn_delete_road_rect.collidepoint(event.pos)
                self.btn_add_road_hover = self.btn_add_road_rect.collidepoint(event.pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                # 检查按钮点击（优先检查）
                if self.back_button_rect.collidepoint(event.pos):
                    return "splash"

                # 检查功能按钮点击
                if self.btn_info_rect.collidepoint(event.pos):
                    self.active_panel = "info" if self.active_panel != "info" else None
                elif self.btn_components_rect.collidepoint(event.pos):
                    self.active_panel = "components" if self.active_panel != "components" else None
                elif self.btn_simulation_rect.collidepoint(event.pos):
                    # 切换模拟模式
                    self.in_simulation_mode = not self.in_simulation_mode
                    if self.in_simulation_mode:
                        self.active_panel = "simulation"
                        self.time_sim.start()  # 开始时间模拟
                        # 如果已经有起点和终点，立即运行一次模拟
                        if self.start_node is not None and self.end_node is not None:
                            self.run_and_record_simulation()
                    else:
                        # 退出模拟模式，清空当前模拟结果
                        self.simulation_path = []
                        self.simulation_distance = 0
                        self.time_sim.pause()  # 暂停时间模拟
                elif self.btn_top5_rect.collidepoint(event.pos):
                    self.active_panel = "top5" if self.active_panel != "top5" else None




                elif self.btn_tour_rect.collidepoint(event.pos):
                    # 点击打卡路线按钮：如果已打开则关闭，否则打开
                    self.active_panel = "tour" if self.active_panel != "tour" else None
                    # 如果有起点，自动计算打卡路线；没有起点就提示
                    if self.start_node is None:
                        print("请先选择起点")
                elif self.btn_exchange_rect.collidepoint(event.pos):
                    self.active_panel = "exchange" if self.active_panel != "exchange" else None
                elif self.btn_delete_road_rect.collidepoint(event.pos):
                    # 切换删除道路模式（退出添加道路模式）
                    # 先退出添加道路模式
                    if self.in_add_road_mode:
                        self.in_add_road_mode = False
                        self.add_road_node1 = None
                        self.add_road_node2 = None
                        self.add_road_distance = ""
                        print("退出添加道路模式", flush=True)

                    # 切换删除道路模式
                    self.in_delete_road_mode = not self.in_delete_road_mode
                    if self.in_delete_road_mode:
                        self.active_panel = "delete_road"
                        # 清空之前的选择
                        self.delete_road_node1 = None
                        self.delete_road_node2 = None
                        print("进入删除道路模式，请依次选择两个节点", flush=True)
                    else:
                        self.active_panel = None
                        self.delete_road_node1 = None
                        self.delete_road_node2 = None
                        print("退出删除道路模式", flush=True)
                elif self.btn_add_road_rect.collidepoint(event.pos):
                    # 切换添加道路模式（退出删除道路模式）
                    # 先退出删除道路模式
                    if self.in_delete_road_mode:
                        self.in_delete_road_mode = False
                        self.delete_road_node1 = None
                        self.delete_road_node2 = None
                        print("退出删除道路模式", flush=True)

                    # 切换添加道路模式
                    self.in_add_road_mode = not self.in_add_road_mode
                    if self.in_add_road_mode:
                        self.active_panel = "add_road"
                        # 清空之前的选择
                        self.add_road_node1 = None
                        self.add_road_node2 = None
                        self.add_road_distance = ""
                        self.add_road_input_active = False
                        print("进入添加道路模式，请依次选择两个节点并输入距离", flush=True)
                    else:
                        self.active_panel = None
                        self.add_road_node1 = None
                        self.add_road_node2 = None
                        self.add_road_distance = ""
                        self.add_road_input_active = False
                        print("退出添加道路模式", flush=True)

                # 检查时间面板的休息按钮点击
                rest_mins, joined_activity = self.time_panel.handle_event(event, self.time_sim)
                if rest_mins > 0:
                    print(f"休息增加 {rest_mins} 分钟，当前时间: {self.time_sim.get_current_time_str()}", flush=True)
                if joined_activity:
                    print(f"参与活动，时间已更新为: {self.time_sim.get_current_time_str()}", flush=True)

                # 检查清空按钮点击
                if hasattr(self, 'clear_button_rect') and self.clear_button_rect.collidepoint(event.pos):
                    self.total_distance = 0
                    self.simulation_history = []
                    self.simulation_path = []
                    self.simulation_distance = 0

                # 检查节点点击
                node = self.get_node_at_pos(event.pos)
                if node is not None:
                    # 更新玩家位置
                    self.player_pos = locations_pos[node]

                    # 如果在删除道路模式，优先处理删除道路的节点选择
                    if self.in_delete_road_mode and event.button == 1:
                        # 选择第一个节点
                        if self.delete_road_node1 is None:
                            self.delete_road_node1 = node
                            print(f"已选择第一个节点: {node} ({locations[node]})", flush=True)
                        # 选择第二个节点
                        elif self.delete_road_node2 is None and node != self.delete_road_node1:
                            self.delete_road_node2 = node
                            print(f"已选择第二个节点: {node} ({locations[node]})", flush=True)

                            # 执行删除道路
                            if self.delete_road(self.delete_road_node1, self.delete_road_node2):
                                print("道路删除成功！", flush=True)
                            else:
                                print("道路删除失败，请检查该道路是否存在", flush=True)

                            # 清空选择，准备下一次删除
                            self.delete_road_node1 = None
                            self.delete_road_node2 = None
                        # 如果点击了已选中的第一个节点，取消选择
                        elif node == self.delete_road_node1:
                            self.delete_road_node1 = None
                            print("取消选择第一个节点", flush=True)
                    # 如果在添加道路模式，优先处理添加道路的节点选择
                    elif self.in_add_road_mode and event.button == 1:
                        # 选择第一个节点
                        if self.add_road_node1 is None:
                            self.add_road_node1 = node
                            print(f"已选择第一个节点: {node} ({locations[node]})", flush=True)
                        # 选择第二个节点
                        elif self.add_road_node2 is None and node != self.add_road_node1:
                            self.add_road_node2 = node
                            print(f"已选择第二个节点: {node} ({locations[node]})", flush=True)
                            print("请在面板中输入距离并回车确认", flush=True)
                        # 如果点击了已选中的第一个节点，取消选择
                        elif node == self.add_road_node1:
                            self.add_road_node1 = None
                            self.add_road_node2 = None
                            self.add_road_distance = ""
                            print("取消选择，重新开始", flush=True)
                    # 否则执行正常的导航功能
                    elif event.button == 1:
                        # 更新选中节点的信息
                        self.selected_node = node
                        self.selected_location_info = self.get_location_info(node)

                        if self.start_node is None:
                            self.start_node = node
                            self.end_node = None
                            self.path = []
                            self.path_distance = 0




                        elif self.end_node is None and node != self.start_node:
                            self.end_node = node
                            self.path, self.path_distance = self.dijkstra(self.start_node, self.end_node)
                            if not self.path:
                                # 不可达，设置换乘提示
                                self.transfer_message = ("换乘提示：可通过大学城专线3换乘")
                                self.path_distance = None  # 避免显示错误的距离
                            else:
                                self.transfer_message = ""
                            # 模拟模式相关
                            if self.in_simulation_mode:
                                self.run_and_record_simulation()
                                if self.player_pos:
                                    self.time_sim.check_activities(self.player_pos)



                        else:
                            self.start_node = node
                            self.end_node = None
                            self.path = []
                            self.path_distance = 0
                            # 清除活动触发状态（继续行进）
                            if self.time_sim.active_prompts:
                                for prompt in self.time_sim.active_prompts:
                                    self.time_sim.clear_trigger(prompt['activity_id'])
                                self.time_sim.active_prompts = []
                            # 清除活动结束后的消息（继续行进）
                            self.time_sim.after_activity_message = None
                    elif event.button == 3:
                        if node == self.start_node:
                            self.start_node = None
                        elif node == self.end_node:
                            self.end_node = None
                        self.path = []

            if event.type == pygame.KEYDOWN:
                # 添加道路模式的键盘输入处理
                if self.in_add_road_mode and self.add_road_node1 is not None and self.add_road_node2 is not None:
                    # 数字输入
                    if event.key >= pygame.K_0 and event.key <= pygame.K_9:
                        self.add_road_distance += chr(event.key)
                    # 退格键删除
                    elif event.key == pygame.K_BACKSPACE:
                        self.add_road_distance = self.add_road_distance[:-1]
                    # 回车键确认添加
                    elif event.key == pygame.K_RETURN and self.add_road_distance:
                        try:
                            distance = int(self.add_road_distance)
                            if distance > 0:
                                # 执行添加道路
                                if self.add_road(self.add_road_node1, self.add_road_node2, distance):
                                    print(f"道路添加成功！距离: {distance}米", flush=True)
                                else:
                                    print("道路添加失败", flush=True)
                                # 清空选择，准备下一次添加
                                self.add_road_node1 = None
                                self.add_road_node2 = None
                                self.add_road_distance = ""
                            else:
                                print("距离必须大于0", flush=True)
                        except ValueError:
                            print("请输入有效的数字", flush=True)

                # R键重置导航
                if event.key == pygame.K_r:
                    self.start_node = None
                    self.end_node = None
                    self.path = []
                    self.selected_node = None
                    self.selected_location_info = None
                    self.simulation_path = []

        return result

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.handle_events()
            self.draw()
            clock.tick(30)


class WhyGDUFS:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.font = get_chinese_font(20)
        self.title_font = get_chinese_font(32)

        # 加载背景图片
        self.background = None
        try:
            bg_path = os.path.join(BASE_DIR, "pics", "广外background.jpg")
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except:
            try:
                bg_path = os.path.join(BASE_DIR, "pics", "广外background.jpg")
                self.background = pygame.image.load(bg_path).convert()
                self.background = pygame.transform.scale(self.background, (self.width, self.height))
            except:
                self.background = None

        # 返回按钮（左对齐，与其他界面统一）
        self.back_button_rect = pygame.Rect(50, 20, 140, 40)
        self.back_button_hover = False

        # 文本内容
        self.text_lines = [
            "报考广外的理由，可以这样看。",
            "",
            "首先是你绕不开的\"百万闸机\"，刷脸进出，排面拉满，四年下来有种天天进甲级写字楼的错觉，",
            "学校在管理上是真舍得花钱，安全感很实在。更出名的是它\"CPU大学\"的绰号，",
            "翻译过来就是铺天盖地的课堂展示。每门课都要上台讲，从磕磕巴巴讲到面不改色，",
            "表达能力、逻辑思维就是这么硬生生磨出来的，到了职场就知道这是真本事。",
            "",
            "抛开这些，广外官网招生章程上那几句\"国际化特色鲜明的高水平大学\"",
            "\"华南地区外语语种最多的大学\"，还真不是虚的。地处广州，一线城市的资源和机会不用多说，",
            "广交会和各种涉外实习就在家门口，跟官网上说的\"外语+专业\"深度融合完全对得上。",
            "就业有底气，语言和经贸是看家本领，校友遍布大湾区外贸圈和跨国企业，薪酬排名常年不低。",
            "专业方面，外语类不用讲，商务、法律、金融全带着国际味儿，",
            "而且不少都是国家级一流本科专业建设点，很对市场的胃口。",
            "再加上校园风气务实，不飘着，大家目标明确，就是奔着好工作、好出路去。",
            "",
            "被闸机守着，被无数Pre练着，在广州这座城市里耳濡目染，",
            "四年后你会发现自己已经能写会说、敢闯敢秀，",
            "手上拿着的是一张实实在在的职场入场券。"
        ]

    def draw_stroked_text(self, text, center, fill_color, stroke_color, font):
        text_surface = font.render(text, True, fill_color)
        stroke_surface = font.render(text, True, stroke_color)
        offsets = [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)]
        x, y = center
        text_rect = text_surface.get_rect(center=(x, y))
        for dx, dy in offsets:
            self.screen.blit(stroke_surface, (text_rect.x + dx, text_rect.y + dy))
        self.screen.blit(text_surface, text_rect)

    def draw_modern_button(self, rect, text, hover):
        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        if hover:
            alpha = 120
            text_color = (200, 200, 200)
            stroke_color = (30, 50, 100)
        else:
            alpha = 60
            text_color = (255, 255, 255)
            stroke_color = (20, 40, 80)
        pygame.draw.rect(button_surface, (255, 255, 255, alpha), button_surface.get_rect(), 2, border_radius=10)
        inner_rect = pygame.Rect(2, 2, rect.width - 4, rect.height - 4)
        pygame.draw.rect(button_surface, (255, 255, 255, alpha // 2), inner_rect, 1, border_radius=8)
        self.screen.blit(button_surface, rect)
        self.draw_stroked_text(text, rect.center, text_color, stroke_color, self.font)

    def draw(self):
        # 绘制背景
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            for i in range(self.height):
                color = (30 + i // 4, 50 + i // 4, 150 + i // 3)
                pygame.draw.line(self.screen, color, (0, i), (self.width, i))

        # 绘制轻微半透明遮罩（让文字更清晰）
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 50))  # 减少遮罩透明度，让背景更亮
        self.screen.blit(overlay, (0, 0))

        # 绘制标题
        title_text = self.title_font.render("为什么报考广外", True, WHITE)
        title_rect = title_text.get_rect(center=(self.width // 2, 60))
        self.screen.blit(title_text, title_rect)

        pygame.draw.line(self.screen, (100, 150, 255),
                         (self.width // 2 - 150, 85),
                         (self.width // 2 + 150, 85), 2)

        # 绘制文本
        y = 120
        for line in self.text_lines:
            text = self.font.render(line, True, (230, 240, 255))
            self.screen.blit(text, (60, y))
            y += 28

        # 绘制返回按钮（统一使用draw_modern_button）
        self.draw_modern_button(self.back_button_rect, "返回主界面", self.back_button_hover)

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                self.back_button_hover = self.back_button_rect.collidepoint(event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.back_button_rect.collidepoint(event.pos):
                    return True
        return False

    def run(self):
        clock = pygame.time.Clock()
        while True:
            if self.handle_events():
                return
            self.draw()
            clock.tick(30)


class Credits:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.font = get_chinese_font(24)
        self.title_font = get_chinese_font(36)

        # 加载背景图片
        self.background = None
        try:
            bg_path = os.path.join(BASE_DIR, "pics", "广外background.jpg")
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except:
            try:
                bg_path = os.path.join(BASE_DIR, "pics", "广外background.jpg")
                self.background = pygame.image.load(bg_path).convert()
                self.background = pygame.transform.scale(self.background, (self.width, self.height))
            except:
                self.background = None

        # 返回按钮（左对齐，与其他界面统一）
        self.back_button_rect = pygame.Rect(50, 20, 140, 40)
        self.back_button_hover = False

        # 文本内容
        self.text_lines = [
            "刘予溪：四类基本功能、主程序的实现",
            "",
            "吴敏仪：校园抽象图设计，部分额外功能以及报告和视频整理",
            "",
            "武泽宇——GUI的实现"
        ]

    def draw_stroked_text(self, text, center, fill_color, stroke_color, font):
        text_surface = font.render(text, True, fill_color)
        stroke_surface = font.render(text, True, stroke_color)
        offsets = [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)]
        x, y = center
        text_rect = text_surface.get_rect(center=(x, y))
        for dx, dy in offsets:
            self.screen.blit(stroke_surface, (text_rect.x + dx, text_rect.y + dy))
        self.screen.blit(text_surface, text_rect)

    def draw_modern_button(self, rect, text, hover):
        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        if hover:
            alpha = 120
            text_color = (200, 200, 200)
            stroke_color = (30, 50, 100)
        else:
            alpha = 60
            text_color = (255, 255, 255)
            stroke_color = (20, 40, 80)
        pygame.draw.rect(button_surface, (255, 255, 255, alpha), button_surface.get_rect(), 2, border_radius=10)
        inner_rect = pygame.Rect(2, 2, rect.width - 4, rect.height - 4)
        pygame.draw.rect(button_surface, (255, 255, 255, alpha // 2), inner_rect, 1, border_radius=8)
        self.screen.blit(button_surface, rect)
        self.draw_stroked_text(text, rect.center, text_color, stroke_color, self.font)

    def draw(self):
        # 绘制背景
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            for i in range(self.height):
                color = (30 + i // 4, 50 + i // 4, 150 + i // 3)
                pygame.draw.line(self.screen, color, (0, i), (self.width, i))

        # 绘制轻微半透明遮罩
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 50))
        self.screen.blit(overlay, (0, 0))

        # 绘制标题
        title_text = self.title_font.render("制作人员", True, WHITE)
        title_rect = title_text.get_rect(center=(self.width // 2, 60))
        self.screen.blit(title_text, title_rect)

        pygame.draw.line(self.screen, (100, 150, 255),
                         (self.width // 2 - 100, 95),
                         (self.width // 2 + 100, 95), 2)

        # 绘制文本
        y = 160
        for line in self.text_lines:
            text = self.font.render(line, True, (230, 240, 255))
            self.screen.blit(text, (self.width // 2 - 200, y))
            y += 40

        # 绘制返回按钮
        self.draw_modern_button(self.back_button_rect, "返回主界面", self.back_button_hover)

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                self.back_button_hover = self.back_button_rect.collidepoint(event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.back_button_rect.collidepoint(event.pos):
                    return True
        return False

    def run(self):
        clock = pygame.time.Clock()
        while True:
            if self.handle_events():
                return
            self.draw()
            clock.tick(30)


def show_startup_screen(screen):
    """显示启动过场动画：白底黑字居中显示标题和署名，带渐变淡出效果"""
    width, height = screen.get_size()
    title_font = get_chinese_font(32)
    name_font = get_chinese_font(48)
    clock = pygame.time.Clock()

    # 白底背景
    screen.fill((255, 255, 255))

    # 居中显示标题（上方）
    title_text = title_font.render("广东外语外贸大学校园导航系统", True, (0, 0, 0))
    title_rect = title_text.get_rect(center=(width // 2, height // 2 - 50))
    screen.blit(title_text, title_rect)

    # 居中显示署名（下方）
    name_text = name_font.render("Made by 计算机类2507——group 2", True, (0, 0, 0))
    name_rect = name_text.get_rect(center=(width // 2, height // 2 + 20))
    screen.blit(name_text, name_rect)

    pygame.display.flip()

    # 等待1秒
    pygame.time.wait(1000)

    # 渐变淡出效果（1秒内从完全不透明到完全透明）
    for alpha in range(0, 256, 5):
        fade_surface = pygame.Surface((width, height))
        fade_surface.fill((255, 255, 255))
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)


def main():
    pygame.init()
    # 调整窗口大小（扩大一圈，给地图留边距）
    # 使用DOUBLEBUF和HWSURFACE启用硬件加速双缓冲，减少闪烁
    screen = pygame.display.set_mode((1100, 750), pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("广东外语外贸大学校园导航系统")

    # 显示启动过场动画
    show_startup_screen(screen)

    # 初始化音乐播放器（单例模式，自动播放第一首）
    music_player = MusicPlayer()
    music_player.init_pygame_mixer()
    if music_player.songs:
        music_player.play(0)  # 自动播放第一首

    # 显示启动界面
    splash = SplashScreen(screen)
    clock = pygame.time.Clock()

    while True:
        result = splash.handle_events()
        if result == "main":
            break
        elif result == "why":
            why = WhyGDUFS(screen)
            why.run()
            continue
        elif result == "credits":
            credits = Credits(screen)
            credits.run()
            continue
        elif result == "music":
            # 显示音乐播放器界面（从启动界面进入）
            try:
                music_ui = MusicPlayerUI(screen, music_player)  # 传入共享的music_player
                running = True
                while running:
                    splash.draw()
                    music_ui.draw()
                    pygame.display.flip()

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        # 处理右键退出（不停止音乐，继续播放）
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                            running = False
                            break
                        # 左键点击事件
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            music_ui.handle_events(event.pos, event)
            except Exception as e:
                print(f"Music UI Error: {e}", flush=True)
                import traceback
                traceback.print_exc()
            continue
        splash.draw()
        pygame.display.flip()
        clock.tick(30)

    # 进入主界面（传入共享的screen对象）
    app = CampusNavigation(screen)
    while True:
        result = app.handle_events_with_return()
        if result == "why":
            why = WhyGDUFS(screen)
            why.run()
            continue
        elif result == "splash":
            while True:
                result2 = splash.handle_events()
                if result2 == "main":
                    break
                elif result2 == "why":
                    why = WhyGDUFS(screen)
                    why.run()
                    continue
                elif result2 == "music":
                    # 显示音乐播放器界面（从启动界面进入）
                    try:
                        music_ui = MusicPlayerUI(screen, music_player)  # 传入共享的music_player
                        running = True
                        while running:
                            splash.draw()
                            music_ui.draw()
                            pygame.display.flip()

                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                # 处理右键退出（不停止音乐，继续播放）
                                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                                    running = False
                                    break
                                # 左键点击事件
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    music_ui.handle_events(event.pos, event)
                    except Exception as e:
                        print(f"Music UI Error: {e}", flush=True)
                        import traceback
                        traceback.print_exc()
                    continue
                splash.draw()
                pygame.display.flip()
                clock.tick(30)
            continue
        app.draw()
        clock.tick(30)


if __name__ == "__main__":
    main()
