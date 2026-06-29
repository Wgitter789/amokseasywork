"""
时间模拟模块
功能：模拟游览时间，支持速度计算和休息功能，活动检测
"""
import pygame
import math

# 时间常量
SECONDS_PER_METER = 1 / 1.5  # 每1.5米1秒
START_HOUR = 9  # 早上9点开始
MINUTES_PER_REST = 30  # 每次休息增加30分钟

# 活动类
class Activity:
    def __init__(self, name, description, start_hour, end_hour, location_id, location_pos, trigger_distance=500, after_message=None):
        """
        初始化活动
        name: 活动名称
        description: 活动描述
        start_hour: 开始时间（小时）
        end_hour: 结束时间（小时）
        location_id: 活动地点的节点ID
        location_pos: 活动地点的坐标 (x, y)
        trigger_distance: 触发距离（米）
        after_message: 参与活动后的消息
        """
        self.name = name
        self.description = description
        self.start_time = start_hour * 60  # 转换为分钟
        self.end_time = end_hour * 60
        self.location_id = location_id
        self.location_pos = location_pos
        self.trigger_distance = trigger_distance
        self.after_message = after_message  # 参与活动后的消息
        
    def is_active(self, current_time_minutes):
        """检查活动是否在活跃时间段内"""
        return self.start_time <= current_time_minutes < self.end_time
    
    def is_nearby(self, player_pos):
        """检查玩家是否在触发距离内"""
        if player_pos is None:
            return False
        px, py = player_pos
        lx, ly = self.location_pos
        distance = math.sqrt((px - lx) ** 2 + (py - ly) ** 2)
        return distance <= self.trigger_distance


class TimeSimulation:
    def __init__(self):
        """初始化时间模拟器"""
        self.start_time = 9 * 60  # 初始时间（分钟，从0点开始）
        self.current_time = self.start_time  # 当前时间（分钟）
        self.is_paused = True  # 是否暂停
        self.total_distance = 0  # 累计距离（米）
        self.last_update_time = None  # 上次更新时间
        
        # 活动相关
        self.activities = []  # 活动列表
        self.active_prompts = []  # 当前需要显示的提示
        self.triggered_activities = set()  # 已触发过的活动ID（避免重复提示）
        self.after_activity_message = None  # 参与活动后的消息
        
        # 初始化默认活动：第一食堂吃饭送酸奶（11:00-13:00）
        self.setup_default_activities()
        
    def setup_default_activities(self):
        """设置默认活动"""
        # 第一食堂的节点ID是13，位置是(400, 380)
        # 需要从外部传入，这里先设置占位值
        pass
        
    def set_location_data(self, location_id, location_pos):
        """设置活动地点的数据"""
        # 第一食堂：节点13，坐标(400, 380)
        activity = Activity(
            name="第一食堂活动",
            description="吃饭送酸奶",
            start_hour=11,
            end_hour=13,
            location_id=location_id,
            location_pos=location_pos,
            trigger_distance=200,  # 200m内触发
            after_message="食堂的菜不是很好吃..."
        )
        self.activities.append(activity)
        
    def add_activity(self, name, description, start_hour, end_hour, location_id, location_pos, after_message=None):
        """添加活动"""
        activity = Activity(
            name=name,
            description=description,
            start_hour=start_hour,
            end_hour=end_hour,
            location_id=location_id,
            location_pos=location_pos,
            trigger_distance=200,
            after_message=after_message
        )
        self.activities.append(activity)
        
    def add_random_activity(self, name, descriptions, start_hour, end_hour, location_id, location_pos, trigger_distance=200, after_messages=None):
        """添加随机活动（每天随机选择一个描述和对应的消息）"""
        import random
        chosen_index = random.randint(0, len(descriptions) - 1)
        chosen_description = descriptions[chosen_index]
        chosen_message = after_messages[chosen_index] if after_messages else None
        activity = Activity(
            name=name,
            description=chosen_description,
            start_hour=start_hour,
            end_hour=end_hour,
            location_id=location_id,
            location_pos=location_pos,
            trigger_distance=trigger_distance,
            after_message=chosen_message
        )
        self.activities.append(activity)
        
    def reset(self):
        """重置时间模拟"""
        self.start_time = 9 * 60
        self.current_time = self.start_time
        self.is_paused = True
        self.total_distance = 0
        self.last_update_time = None
        self.active_prompts = []
        self.triggered_activities = set()
        self.after_activity_message = None
        
    def start(self):
        """开始/继续计时"""
        self.is_paused = False
        self.last_update_time = pygame.time.get_ticks()
        
    def pause(self):
        """暂停计时"""
        self.is_paused = True
        
    def take_rest(self):
        """稍作休息，增加30分钟"""
        self.current_time += MINUTES_PER_REST
        return MINUTES_PER_REST
        
    def add_distance(self, distance):
        """添加行驶距离，自动计算时间增加"""
        if not self.is_paused:
            self.total_distance += distance
            # 根据距离计算时间增加（秒）
            seconds_to_add = distance * SECONDS_PER_METER
            self.current_time += seconds_to_add / 60  # 转换为分钟
            
    def update(self):
        """更新当前时间（基于实际流逝的时间）"""
        if not self.is_paused and self.last_update_time is not None:
            current_ticks = pygame.time.get_ticks()
            elapsed_seconds = (current_ticks - self.last_update_time) / 1000.0
            self.current_time += elapsed_seconds / 60  # 转换为分钟
            self.last_update_time = current_ticks
            
    def check_activities(self, player_pos):
        """
        检测活动触发情况
        player_pos: 玩家当前位置 (x, y)
        返回: 需要显示的提示列表（只显示最近的活动）
        """
        self.active_prompts = []
        
        # 收集所有符合条件的活动及其距离
        nearby_activities = []
        
        for activity in self.activities:
            # 检查是否在活动时间范围内
            if not activity.is_active(self.current_time):
                continue
                
            # 检查是否已经触发过
            if id(activity) in self.triggered_activities:
                continue
                
            # 检查是否在触发距离内
            if activity.is_nearby(player_pos):
                # 计算距离
                px, py = player_pos
                lx, ly = activity.location_pos
                distance = math.sqrt((px - lx) ** 2 + (py - ly) ** 2)
                nearby_activities.append({
                    'name': activity.name,
                    'description': activity.description,
                    'activity_id': id(activity),
                    'distance': distance
                })
        
        # 只显示最近的活动
        if nearby_activities:
            # 按距离排序，取最近的
            nearby_activities.sort(key=lambda x: x['distance'])
            nearest = nearby_activities[0]
            self.active_prompts.append(nearest)
            # 标记为已触发
            self.triggered_activities.add(nearest['activity_id'])
                
        return self.active_prompts
        
    def clear_trigger(self, activity_id):
        """清除某个活动的触发状态（在继续行进后）"""
        if activity_id in self.triggered_activities:
            self.triggered_activities.remove(activity_id)
            
    def get_current_time_str(self):
        """获取当前时间字符串（HH:MM格式）"""
        total_minutes = int(self.current_time)
        hours = (total_minutes // 60) % 24
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"
    
    def get_elapsed_minutes(self):
        """获取从开始到现在经过的分钟数"""
        return max(0, int(self.current_time - self.start_time))
    
    def get_total_distance(self):
        """获取累计距离"""
        return self.total_distance
        
    def is_overnight(self):
        """检查是否超过午夜"""
        return self.current_time >= 24 * 60
    
    def get_active_activities(self):
        """获取当前时间段内的所有活动"""
        active = []
        for activity in self.activities:
            if activity.is_active(self.current_time):
                active.append(activity)
        return active


class TimePanel:
    """时间面板绘制类"""
    
    def __init__(self, screen, font, small_font):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        
        # 颜色
        self.bg_color = (255, 255, 220)  # 浅黄色
        self.border_color = (139, 90, 43)  # 棕色
        self.text_color = (80, 60, 40)
        self.button_color = (210, 180, 140)
        self.button_hover_color = (180, 140, 100)
        self.button_text_color = (60, 40, 20)
        self.activity_button_color = (100, 180, 100)  # 绿色活动按钮
        self.activity_button_hover_color = (80, 160, 80)
        
        # 活动提示颜色
        self.activity_color = (255, 100, 100)  # 红色提示
        self.activity_bg = (255, 230, 230)  # 浅红色背景
        
        # 面板位置和大小（增大）
        self.panel_x = 10
        self.panel_y = 10
        self.panel_width = 180
        self.panel_height = 130
        
        # 休息按钮（右下角）
        self.rest_button = pygame.Rect(
            self.panel_x + self.panel_width - 70, 
            self.panel_y + self.panel_height - 30, 
            60, 
            22
        )
        self.rest_button_hover = False
        
        # 参与活动按钮（休息按钮上方）
        self.join_button = pygame.Rect(
            self.panel_x + self.panel_width - 70, 
            self.panel_y + self.panel_height - 58, 
            60, 
            22
        )
        self.join_button_hover = False
        
        # 活动提示区域
        self.prompt_area_height = 0
        self.current_prompts = []
        
    def draw(self, time_sim, distance=0, player_pos=None):
        """绘制时间面板"""
        # 计算活动提示区域高度（增大）
        self.current_prompts = time_sim.active_prompts
        self.prompt_area_height = len(self.current_prompts) * 35 if self.current_prompts else 0
        
        # 活动结束后的消息区域高度
        self.after_message_height = 35 if time_sim.after_activity_message else 0
        
        total_height = self.panel_height + self.prompt_area_height + self.after_message_height
        
        # 面板背景
        pygame.draw.rect(self.screen, self.bg_color, 
                         (self.panel_x, self.panel_y, self.panel_width, total_height), 
                         border_radius=8)
        pygame.draw.rect(self.screen, self.border_color, 
                         (self.panel_x, self.panel_y, self.panel_width, total_height), 
                         2, border_radius=8)
        
        # 标题
        title = self.font.render("游览时间", True, self.text_color)
        self.screen.blit(title, (self.panel_x + 10, self.panel_y + 8))
        
        # 分隔线
        pygame.draw.line(self.screen, self.border_color, 
                        (self.panel_x + 10, self.panel_y + 35), 
                        (self.panel_x + self.panel_width - 10, self.panel_y + 35))
        
        # 当前时间
        time_str = time_sim.get_current_time_str()
        time_label = self.small_font.render("当前时间", True, self.text_color)
        self.screen.blit(time_label, (self.panel_x + 10, self.panel_y + 42))
        time_display = self.font.render(time_str, True, (0, 100, 180))
        self.screen.blit(time_display, (self.panel_x + 10, self.panel_y + 58))
        
        # 经行时间
        elapsed = time_sim.get_elapsed_minutes()
        elapsed_hours = elapsed // 60
        elapsed_mins = elapsed % 60
        elapsed_str = f"已行{elapsed_hours}时{elapsed_mins}分"
        elapsed_display = self.small_font.render(elapsed_str, True, (150, 100, 50))
        self.screen.blit(elapsed_display, (self.panel_x + 10, self.panel_y + 78))
        
        # 参与活动按钮（只在有活动提示时显示）
        if self.current_prompts:
            button_color = self.activity_button_hover_color if self.join_button_hover else self.activity_button_color
            pygame.draw.rect(self.screen, button_color, self.join_button, border_radius=5)
            pygame.draw.rect(self.screen, (0, 100, 0), self.join_button, 1, border_radius=5)
            
            join_text = self.small_font.render("参与活动", True, (255, 255, 255))
            join_rect = join_text.get_rect(center=self.join_button.center)
            self.screen.blit(join_text, join_rect)
        
        # 休息按钮
        button_color = self.button_hover_color if self.rest_button_hover else self.button_color
        pygame.draw.rect(self.screen, button_color, self.rest_button, border_radius=5)
        pygame.draw.rect(self.screen, self.border_color, self.rest_button, 1, border_radius=5)
        
        rest_text = self.small_font.render("稍作休息", True, self.button_text_color)
        rest_rect = rest_text.get_rect(center=self.rest_button.center)
        self.screen.blit(rest_text, rest_rect)
        
        # 绘制活动提示
        self.draw_activity_prompts(time_sim)
        
    def draw_activity_prompts(self, time_sim):
        """绘制活动提示和活动结束后的消息"""
        # 提示靠下一点
        prompt_y = self.panel_y + self.panel_height + 8
        
        # 绘制活动提示
        for prompt in self.current_prompts:
            # 提示背景（增大）
            pygame.draw.rect(self.screen, self.activity_bg, 
                           (self.panel_x + 5, prompt_y, self.panel_width - 10, 30), 
                           border_radius=6)
            pygame.draw.rect(self.screen, self.activity_color, 
                           (self.panel_x + 5, prompt_y, self.panel_width - 10, 30), 
                           1, border_radius=6)
            
            # 提示文字
            text = f"{prompt['name']}: {prompt['description']}"
            text_surface = self.small_font.render(text, True, self.activity_color)
            text_rect = text_surface.get_rect(center=(self.panel_x + self.panel_width // 2, prompt_y + 15))
            self.screen.blit(text_surface, text_rect)
            
            prompt_y += 35
        
        # 绘制活动结束后的消息
        if time_sim.after_activity_message:
            # 消息背景（蓝色）
            pygame.draw.rect(self.screen, (230, 230, 255), 
                           (self.panel_x + 5, prompt_y, self.panel_width - 10, 30), 
                           border_radius=6)
            pygame.draw.rect(self.screen, (100, 100, 180), 
                           (self.panel_x + 5, prompt_y, self.panel_width - 10, 30), 
                           1, border_radius=6)
            
            # 消息文字
            text_surface = self.small_font.render(time_sim.after_activity_message, True, (50, 50, 150))
            text_rect = text_surface.get_rect(center=(self.panel_x + self.panel_width // 2, prompt_y + 15))
            self.screen.blit(text_surface, text_rect)
            
    def handle_event(self, event, time_sim):
        """处理事件"""
        rest_mins = 0
        joined_activity = False
        
        if event.type == pygame.MOUSEMOTION:
            self.rest_button_hover = self.rest_button.collidepoint(event.pos)
            self.join_button_hover = self.join_button.collidepoint(event.pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rest_button.collidepoint(event.pos):
                rest_mins = time_sim.take_rest()
            elif self.join_button.collidepoint(event.pos) and self.current_prompts:
                # 参与活动：将时间推到活动结束时间
                joined_activity = self.join_activity(time_sim)
                
        return rest_mins, joined_activity
    
    def join_activity(self, time_sim):
        """参与活动，将时间推到活动结束时间"""
        if not self.current_prompts:
            return False
            
        # 找到当前活动对应的活动对象
        for activity in time_sim.activities:
            if id(activity) == self.current_prompts[0]['activity_id']:
                # 将时间设置为活动结束时间
                end_time_minutes = activity.end_time
                time_sim.current_time = end_time_minutes
                # 设置活动结束后的消息
                if activity.after_message:
                    time_sim.after_activity_message = activity.after_message
                # 清除活动触发状态
                time_sim.clear_trigger(id(activity))
                self.current_prompts = []
                return True
                
        return False
