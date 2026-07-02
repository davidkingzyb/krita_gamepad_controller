# Krita Gamepad Controller

**Krita gamepad controller. 手柄控制插件**

2026/07/02 by DKZ

### Install
[官方安装文档](https://docs.krita.org/zh_CN/user_manual/python_scripting/install_custom_python_plugin.html)    
内置 [zeth/inputs](https://github.com/zeth/inputs/tree/master) 包,直接下载zip包开箱即用.    
1. 下载zip文件
2. 解压到 pykrita
3. 复制 gamepad_controller
4. 在 Krita > Setting > config Krita > python Plugin Mananger 中启用 gamepad controller
5. 每次打开Krita 前确保手柄开启,Tools > Scripts > gamepad start 选中或使用ctrl+f5快捷键开启插件

### Keymap 
- ctrl+F5 enable 开启

- 左摇杆：HUE色相 Saturation饱和度 快选
- 右摇杆：Value明度 Saturation饱和度 快选
- 十字键: Value明度 Saturation饱和度 调整
- L1/L2: Scale 缩放
- L3: zoom to fit 自动适应画布大小
- R1: Sample 拾色器 (使用windows拾色器,暂不支持其他平台)
- R2: Erase 橡皮
- X/Y: Brush size 笔刷大小
- A/B: Brush Strength 笔刷强度
- -/+: undo/redo 重做