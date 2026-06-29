# -*- coding: utf-8 -*-
import pygame
import os

class MusicPlayer:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.initialized = False
            self.current_song = None
            self.volume = 50  # 0-100
            self.is_playing = False
            self.muted = False
            self.songs = []
            self.current_index = 0
            self._initialized = True
        
    def init_pygame_mixer(self):
        """初始化pygame音频 mixer"""
        if not self.initialized:
            try:
                # 尝试使用不同的参数初始化
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
                print("pygame.mixer initialized successfully", flush=True)
                self.initialized = True
                self.load_songs()
                print(f"Loaded {len(self.songs)} songs", flush=True)
            except Exception as e:
                print(f"Failed to initialize pygame mixer: {e}", flush=True)
                import traceback
                traceback.print_exc()
                self.initialized = False
    
    def load_songs(self):
        """加载music文件夹中的所有MP3文件"""
        music_dir = os.path.join(os.path.dirname(__file__), '..', 'music')
        if os.path.exists(music_dir):
            for filename in os.listdir(music_dir):
                if filename.endswith('.mp3'):
                    self.songs.append(os.path.join(music_dir, filename))
    
    def get_song_list(self):
        """获取所有可用歌曲列表"""
        return [os.path.basename(song) for song in self.songs]
    
    def play(self, song_index=None):
        """播放音乐"""
        self.init_pygame_mixer()
        
        if song_index is not None:
            if 0 <= song_index < len(self.songs):
                self.current_index = song_index
                self.current_song = self.songs[song_index]
            else:
                return False
        elif not self.current_song and self.songs:
            self.current_index = 0
            self.current_song = self.songs[0]
        
        if not self.current_song:
            return False
        
        try:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.set_volume(self.volume / 100.0)
            pygame.mixer.music.play(-1)  # -1表示循环播放
            self.is_playing = True
            return True
        except Exception as e:
            print(f"播放音乐失败: {e}")
            return False
    
    def pause(self):
        """暂停播放"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
    
    def resume(self):
        """恢复播放"""
        if not self.is_playing:
            pygame.mixer.music.unpause()
            self.is_playing = True
    
    def stop(self):
        """停止播放"""
        pygame.mixer.music.stop()
        self.is_playing = False
    
    def set_volume(self, volume):
        """设置音量（0-100）"""
        self.volume = max(0, min(100, volume))
        if not self.muted:
            pygame.mixer.music.set_volume(self.volume / 100.0)
    
    def toggle_mute(self):
        """切换静音状态"""
        self.muted = not self.muted
        if self.muted:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.volume / 100.0)
    
    def next_song(self):
        """下一首"""
        if len(self.songs) > 1:
            self.current_index = (self.current_index + 1) % len(self.songs)
            return self.play(self.current_index)
        return False
    
    def prev_song(self):
        """上一首"""
        if len(self.songs) > 1:
            self.current_index = (self.current_index - 1) % len(self.songs)
            return self.play(self.current_index)
        return False
    
    def get_current_song_name(self):
        """获取当前播放歌曲名称"""
        if self.current_song:
            return os.path.basename(self.current_song)
        return ""
    
    def is_muted(self):
        """是否静音"""
        return self.muted
    
    def get_volume(self):
        """获取当前音量"""
        return self.volume
