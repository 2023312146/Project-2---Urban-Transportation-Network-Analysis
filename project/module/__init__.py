import os

def get_data_path(filename):
    """
    获取数据文件的相对路径
    
    Args:
        filename (str): 数据文件名
        
    Returns:
        str: 数据文件的完整路径
    """
    # 获取当前文件所在目录的父目录（project目录）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录
    project_root = os.path.dirname(current_dir)
    # 构建数据文件路径
    return os.path.join(project_root, "data", filename)
