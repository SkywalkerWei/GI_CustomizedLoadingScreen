# GI_CustomizedLoadingScreen

依赖GIMI的 自定义原神加载界面插件

## 使用方法

0. `config.ini`中填写五行：
   - 第一行：游戏的分辨率，例如`2560, 1440`
   - 第二行：需要替换进游戏的新的加载图的文件夹的地址
   - 第三行：默认值即可，不需要更改，同级目录下不能有同名文件，否则可能闪退
   - 第四行：默认值即可，不需要更改
   - 第五行：切换模式，`crop`裁切适应游戏界面，`letterbox`扩充适应游戏界面
1. 将需要替换进游戏的`JPG`或`PNG`格式图片放进`config.ini`中设置的源文件夹
2. 确认以下文件和`GI_LoadingScreen.exe`在同级目录下：`config.ini`；`LSMod.ini`；`texconv.exe`
3. 运行`GI_LoadingScreen.exe`即可

**注意：** 每次修改源文件夹中的图片后都需要删除输出文件夹，重新运行`exe`！否则更改不会生效！

## Requirements

- 需要GIMI
- 需要电脑支持DirectX
