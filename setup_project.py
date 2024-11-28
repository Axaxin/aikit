import os

# 创建目录结构
directories = ['utils', 'routes', 'models', 'static', 'templates']
for directory in directories:
    os.makedirs(directory, exist_ok=True)

print("Project structure created successfully!")
