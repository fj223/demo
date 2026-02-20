# 课程表查询系统

一个基于 Flask 的课程表查询与导出工具，支持从 Excel 文件读取课程数据，按教师/班级查看课程表，并支持导出为 PDF 格式。

## 功能特点

- 📅 从 Excel 文件读取课程表数据
- 🔍 按教师/班级筛选查看课程
- 📤 支持上传自定义课程表文件
- 📄 导出课程表为 PDF 格式
- 🌐 Web 界面，操作简单

## 技术栈

- **后端**: Python Flask
- **数据处理**: Pandas, OpenPyXL
- **PDF生成**: pdfkit + wkhtmltopdf

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/fj223/demo.git
cd demo
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 安装 wkhtmltopdf（PDF 导出必需）

#### Windows 安装步骤：

1. **下载 wkhtmltopdf**

   访问 [wkhtmltopdf 官网](https://wkhtmltopdf.org/downloads.html) 下载 Windows 版本安装包

2. **安装到指定目录**

   将 wkhtmltopdf 安装到 `D:\wkhtmltopdf` 目录（安装时可自定义路径）

3. **添加系统环境变量**

   - 右键点击 **此电脑** → **属性** → **高级系统设置**
   - 点击 **环境变量**
   - 在 **系统变量** 中找到 `Path`，点击 **编辑**
   - 点击 **新建**，添加路径：`D:\wkhtmltopdf\bin`
   - 点击 **确定** 保存

4. **验证安装**

   打开新的命令行窗口，运行：

   ```bash
   wkhtmltopdf --version
   ```

   如果显示版本号，则安装成功。

## 使用方法

### 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

### 访问应用

在浏览器中打开 http://localhost:5000

### 操作说明

1. **查看课程表**: 从下拉菜单选择教师/班级，点击查询
2. **上传课程表**: 点击上传按钮，选择符合格式的 Excel 文件
3. **导出 PDF**: 在课程表页面点击导出 PDF 按钮

## Excel 文件格式要求

Excel 文件需包含以下列：

| 列名 | 说明 |
|------|------|
| Day | 星期几（如 ПОНЕДЕЛЬНИК, ВТОРНИК 等） |
| Time | 时间段（如 1-2, 3-4 等） |
| 其他列 | 各班级/教师的课程信息 |

建议将数据放在名为 `for_app` 的工作表中。

## Docker 部署

```bash
# 构建镜像
docker build -t timetable-app .

# 运行容器
docker run -d -p 5000:5000 --name timetable timetable-app
```

## 项目结构

```
demo/
├── app.py                 # Flask 主程序
├── requirements.txt       # Python 依赖
├── Dockerfile            # Docker 配置
├── templates/            # HTML 模板
│   ├── index.html
│   └── schedule.html
└── *.xlsx                # 课程表数据文件
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| PORT | 服务端口 | 5000 |
| WKHTMLTOPDF_PATH | wkhtmltopdf 可执行文件路径 | 系统 PATH 中查找 |

## 许可证

MIT License
