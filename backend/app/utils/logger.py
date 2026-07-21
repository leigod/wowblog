import logging
import os
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
import time
import gzip
import shutil

class DateRotatingFileHandler(RotatingFileHandler):
    # 单个日志文件最大大小，默认2M
    LOG_FILE_MAX_SIZE = 2*1024*1024
    # 定义基础日志目录
    BASE_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    
    def __init__(self, base_log_dir, log_name, max_bytes=LOG_FILE_MAX_SIZE, backup_count=0):
        """
        自定义日志处理器，按年月创建目录，按日创建文件，超过大小后创建带时间戳的新文件
        
        :param base_log_dir: 基础日志目录
        :param log_name: 日志名称前缀
        :param max_bytes: 单个日志文件最大字节数
        :param backup_count: 保留的备份文件数量
        """
        self.base_log_dir = base_log_dir
        self.log_name = log_name
        self.current_date = datetime.now().strftime('%d')
        self.current_month_dir = datetime.now().strftime('%Y%m')
        
        # 确保基础日志目录存在
        os.makedirs(base_log_dir, exist_ok=True)
        
        # 获取当前日志文件路径
        log_file_path = self._get_log_file_path()
        
        # 初始化父类
        super().__init__(log_file_path, maxBytes=max_bytes, backupCount=backup_count)
    
    def _get_log_file_path(self):
        """获取当前日志文件的路径"""
        # 创建年月目录
        month_dir = os.path.join(self.base_log_dir, self.current_month_dir)
        os.makedirs(month_dir, exist_ok=True)
        
        # 基本文件名格式：日期.log
        base_filename = os.path.join(month_dir, f"{self.current_date}.log")
        
        # 检查是否存在该文件，如果存在且大小超过阈值，创建新文件
        if os.path.exists(base_filename):
            file_size = os.path.getsize(base_filename)
            # 如果文件大小小于阈值，直接返回原文件名
            if file_size < self.maxBytes:
                return base_filename
            
        # 返回带时间戳的新文件名格式：日期-时间戳.log
        timestamp = int(time.time())
        return os.path.join(month_dir, f"{self.current_date}-{timestamp}.log")
    
    def emit(self, record):
        """重写emit方法，在写入前检查日期和文件大小"""
        # 获取当前日期
        now = datetime.now()
        current_date = now.strftime('%d')
        current_month_dir = now.strftime('%Y%m')
        
        # 如果日期变更或年月变更，更新日志文件路径
        if current_date != self.current_date or current_month_dir != self.current_month_dir:
            self.current_date = current_date
            self.current_month_dir = current_month_dir
            
            # 关闭当前文件并打开新文件
            self.baseFilename = self._get_log_file_path()
            if self.stream:
                self.stream.close()
                self.stream = None
            self._open()
        
        # 检查文件大小，如果超过阈值，创建新文件
        if os.path.exists(self.baseFilename):
            file_size = os.path.getsize(self.baseFilename)
            if file_size >= self.maxBytes:
                # 创建新文件
                self.baseFilename = self._get_log_file_path()
                if self.stream:
                    self.stream.close()
                    self.stream = None
                self._open()
        
        # 调用父类emit方法写入日志
        super().emit(record)



# 创建一个日志格式化器
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 配置根日志记录器
def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """设置并返回一个自定义的日志记录器"""
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 检查是否已经添加过处理器，避免重复添加
    if not logger.handlers:
        # 创建自定义的日期轮转文件处理器
        file_handler = DateRotatingFileHandler(
            base_log_dir=DateRotatingFileHandler.BASE_LOG_DIR,
            log_name=name,
            max_bytes=DateRotatingFileHandler.LOG_FILE_MAX_SIZE,  # 2MB
            backup_count=100  # 保留大量备份文件，实际会按日期和大小管理
        )
        file_handler.setFormatter(formatter)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # 添加处理器到记录器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# 创建不同模块的日志记录器
app_logger = setup_logger("app", logging.INFO)
api_logger = setup_logger("api", logging.INFO)
security_logger = setup_logger("security", logging.WARNING)
upload_logger = setup_logger("upload", logging.INFO)
exception_logger = setup_logger("exception", logging.ERROR)


# 日志清理策略：定期删除过旧的日志文件
def cleanup_old_logs(log_dir, days_to_keep=90):
    """删除超过指定天数的日志文件"""
    now = datetime.now()
    cutoff = now - timedelta(days=days_to_keep)
    
    for root, dirs, files in os.walk(log_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if file_mtime < cutoff:
                os.remove(file_path)


# 日志压缩
def compress_old_logs(log_dir, days_to_keep=30):
    """压缩并归档旧日志文件"""
    now = datetime.now()
    cutoff = now - timedelta(days=days_to_keep)
    
    for root, dirs, files in os.walk(log_dir):
        for file in files:
            if file.endswith('.log') and not file.endswith('.gz'):
                file_path = os.path.join(root, file)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_mtime < cutoff:
                    with open(file_path, 'rb') as f_in:
                        with gzip.open(f'{file_path}.gz', 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    os.remove(file_path)