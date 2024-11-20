from PyInstaller import __main__ as pyi

params = [
    "-F",
    "-w", # 不显示控制台窗口
    "--add-data",
    "static:static",
    "--clean",
    "--noconfirm",
    "main.py",
    "--icon=static/uiflow.ico",
    "--name",
    "uiflow",
]

pyi.run(params)