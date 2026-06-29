# -*- coding: utf-8 -*-
import pygame
import os
from music_player import MusicPlayer

def get_chinese_font(size):
    """获取中文字体"""
    font_paths = [
        "msyh.ttc", "msyhbd.ttc", "msyh.ttf",  # 微软雅黑
        "simhei.ttf", "simkai.ttf", "simsun.ttc", 
        "STHeiti Light.ttc", "STSong.ttf", "STKaiti.ttf",
        "SourceHanSansSC-Regular.otf", "NotoSansCJKsc-Regular.otf"
    ]
    
    for font_name in font_paths:
        try:
            font = pygame.font.Font(font_name, size)
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
                    font = pygame.font.Font(font_path, size)
                    return font
                except:
                    pass
    
    return pygame.font.Font(None, size)

class MusicPlayerUI:
    def __init__(self, screen, music_player=None):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.font = get_chinese_font(20)
        self.small_font = get_chinese_font(16)
        
        # 音乐播放器实例（单例模式）
        if music_player is None:
            self.music_player = MusicPlayer()
        else:
            self.music_player = music_player
        
        # UI元素位置
        self.window_rect = pygame.Rect(200, 150, 500, 400)
        
        # 按钮矩形
        self.play_button_rect = pygame.Rect(self.window_rect.centerx - 40, self.window_rect.bottom - 80, 80, 40)
        self.pause_button_rect = pygame.Rect(self.window_rect.centerx + 50, self.window_rect.bottom - 80, 80, 40)
        self.mute_button_rect = pygame.Rect(self.window_rect.right - 50, self.window_rect.bottom - 30, 40, 25)
        
        # 音量滑块
        self.volume_slider_rect = pygame.Rect(self.window_rect.left + 50, self.window_rect.bottom - 30, 200, 20)
        self.volume_handle_rect = pygame.Rect(0, 0, 15, 25)
        
        # 歌曲列表区域
        self.song_list_rect = pygame.Rect(self.window_rect.left + 20, self.window_rect.top + 60, self.window_rect.width - 40, 200)
        
        # 选中的歌曲索引
        self.selected_song = -1
        
        # 更新音量滑块位置
        self.update_volume_handle()
    
    def update_volume_handle(self):
        """更新音量滑块位置"""
        volume = self.music_player.get_volume()
        x = self.volume_slider_rect.left + (self.volume_slider_rect.width * volume // 100) - 7
        self.volume_handle_rect.topleft = (x, self.volume_slider_rect.top - 2)
    
    def draw_stroked_text(self, text, center, fill_color, stroke_color, font, surface):
        """绘制描边文字"""
        text_surface = font.render(text, True, fill_color)
        stroke_surface = font.render(text, True, stroke_color)
        offsets = [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)]
        x, y = center
        text_rect = text_surface.get_rect(center=(x, y))
        for dx, dy in offsets:
            surface.blit(stroke_surface, (text_rect.x + dx, text_rect.y + dy))
        surface.blit(text_surface, text_rect)
    
    def draw_modern_button(self, rect, text, hover, surface):
        """绘制现代风格按钮"""
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
        surface.blit(button_surface, rect)
        self.draw_stroked_text(text, rect.center, text_color, stroke_color, self.font, surface)
    
    def draw(self):
        """绘制音乐播放器界面 - 直接在screen上绘制"""
        # 绘制半透明背景窗口（带圆角）
        bg_surface = pygame.Surface((self.window_rect.width, self.window_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (30, 30, 50, 220), bg_surface.get_rect(), border_radius=15)
        self.screen.blit(bg_surface, self.window_rect.topleft)
        
        # 绘制边框
        pygame.draw.rect(self.screen, (100, 100, 150), self.window_rect, 2, border_radius=15)
        
        # 绘制标题
        title_text = self.font.render("音乐播放器", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.window_rect.centerx, self.window_rect.top + 25))
        self.screen.blit(title_text, title_rect)
        
        # 绘制歌曲列表
        songs = self.music_player.get_song_list()
        if songs:
            for i, song in enumerate(songs):
                y = self.song_list_rect.top + i * 30
                song_rect = pygame.Rect(self.song_list_rect.left, y, self.song_list_rect.width, 25)
                
                # 选中的歌曲高亮
                if i == self.selected_song or (i == self.music_player.current_index and self.music_player.is_playing):
                    highlight_surface = pygame.Surface((song_rect.width, song_rect.height), pygame.SRCALPHA)
                    highlight_surface.fill((100, 150, 200, 100))
                    self.screen.blit(highlight_surface, song_rect.topleft)
                
                song_text = self.small_font.render(song, True, (255, 255, 255))
                self.screen.blit(song_text, (song_rect.left + 10, song_rect.top + 3))
        else:
            no_music_text = self.small_font.render("暂无音乐文件", True, (150, 150, 150))
            no_music_rect = no_music_text.get_rect(center=self.song_list_rect.center)
            self.screen.blit(no_music_text, no_music_rect)
        
        # 绘制音量滑块背景
        pygame.draw.rect(self.screen, (80, 80, 100), self.volume_slider_rect, border_radius=10)
        
        # 绘制音量滑块填充
        fill_width = self.volume_slider_rect.width * self.music_player.get_volume() // 100
        fill_rect = pygame.Rect(self.volume_slider_rect.left, self.volume_slider_rect.top, fill_width, self.volume_slider_rect.height)
        pygame.draw.rect(self.screen, (100, 150, 200), fill_rect, border_radius=10)
        
        # 绘制音量滑块手柄
        pygame.draw.rect(self.screen, (255, 255, 255), self.volume_handle_rect, border_radius=5)
        
        # 绘制音量数值
        volume_text = self.small_font.render(str(self.music_player.get_volume()), True, (255, 255, 255))
        volume_rect = volume_text.get_rect(left=self.volume_slider_rect.right + 10, centery=self.volume_slider_rect.centery)
        self.screen.blit(volume_text, volume_rect)
        
        # 绘制静音按钮
        mute_text = self.small_font.render("静音" if not self.music_player.is_muted() else "取消", True, (255, 255, 255))
        pygame.draw.rect(self.screen, (80, 80, 100), self.mute_button_rect, border_radius=5)
        mute_text_rect = mute_text.get_rect(center=self.mute_button_rect.center)
        self.screen.blit(mute_text, mute_text_rect)
        
        # 绘制控制按钮
        self.draw_modern_button(self.play_button_rect, "播放", False, self.screen)
        self.draw_modern_button(self.pause_button_rect, "暂停", False, self.screen)
        
        # 绘制当前播放状态
        if self.music_player.is_playing:
            current_text = self.small_font.render(f"正在播放: {self.music_player.get_current_song_name()}", True, (100, 200, 100))
        else:
            current_text = self.small_font.render(f"当前歌曲: {self.music_player.get_current_song_name()}", True, (150, 150, 150))
        current_rect = current_text.get_rect(center=(self.window_rect.centerx, self.window_rect.bottom - 100))
        self.screen.blit(current_text, current_rect)
    
    def handle_events(self, mouse_pos, event):
        """处理事件 - 右键退出音乐界面"""
        # 右键退出
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.music_player.stop()
            return "close"
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 歌曲列表点击
            songs = self.music_player.get_song_list()
            for i, _ in enumerate(songs):
                y = self.song_list_rect.top + i * 30
                song_rect = pygame.Rect(self.song_list_rect.left, y, self.song_list_rect.width, 25)
                if song_rect.collidepoint(mouse_pos):
                    self.selected_song = i
                    # 先初始化mixer
                    if not self.music_player.initialized:
                        self.music_player.init_pygame_mixer()
                    self.music_player.play(i)
                    return None
            
            # 播放按钮
            if self.play_button_rect.collidepoint(mouse_pos):
                if not self.music_player.is_playing:
                    # 先初始化mixer
                    if not self.music_player.initialized:
                        self.music_player.init_pygame_mixer()
                    if self.music_player.current_song:
                        self.music_player.resume()
                    else:
                        self.music_player.play()
                return None
            
            # 暂停按钮
            if self.pause_button_rect.collidepoint(mouse_pos):
                self.music_player.pause()
                return None
            
            # 静音按钮
            if self.mute_button_rect.collidepoint(mouse_pos):
                self.music_player.toggle_mute()
                return None
            
            # 音量滑块
            if self.volume_slider_rect.collidepoint(mouse_pos):
                x = mouse_pos[0] - self.volume_slider_rect.left
                volume = int((x / self.volume_slider_rect.width) * 100)
                self.music_player.set_volume(volume)
                self.update_volume_handle()
                return None
        
        # 音量滑块拖动
        if event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:
                if self.volume_slider_rect.collidepoint(mouse_pos):
                    x = mouse_pos[0] - self.volume_slider_rect.left
                    volume = int((x / self.volume_slider_rect.width) * 100)
                    self.music_player.set_volume(volume)
                    self.update_volume_handle()
        
        return None
