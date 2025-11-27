import sys
import os
import shutil
import zipfile
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QPushButton, 
                             QFileDialog, QTabWidget, QTreeWidget, QTreeWidgetItem,
                             QMessageBox, QCheckBox, QGroupBox, QLineEdit,
                             QTextEdit, QSplitter, QInputDialog)  # 补全QInputDialog
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QIcon, QFont

class MCModCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project_path = ""
        # 补全版本列表的字符串
        self.mc_versions = ["1.16.5", "1.17.1", "1.18.2", "1.19.4", "1.20.1", "1.20.4", "1.20.6"]
        self.current_version = ""
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Minecraft模组开发助手")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 版本选择区域
        version_group = QGroupBox("版本选择")
        version_layout = QHBoxLayout()
        
        self.version_combo = QComboBox()
        self.version_combo.addItems(self.mc_versions)
        self.version_combo.currentTextChanged.connect(self.on_version_change)
        
        self.new_project_btn = QPushButton("新建项目")
        self.new_project_btn.clicked.connect(self.create_new_project)
        
        self.open_project_btn = QPushButton("打开项目")
        self.open_project_btn.clicked.connect(self.open_project)
        
        version_layout.addWidget(QLabel("Minecraft版本:"))
        version_layout.addWidget(self.version_combo)
        version_layout.addStretch()
        version_layout.addWidget(self.new_project_btn)
        version_layout.addWidget(self.open_project_btn)
        
        version_group.setLayout(version_layout)
        main_layout.addWidget(version_group)
        
        # 创建标签页
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # 项目结构标签页
        self.project_tab = QWidget()
        self.tabs.addTab(self.project_tab, "项目结构")
        
        # 素材管理标签页
        self.resource_tab = QWidget()
        self.tabs.addTab(self.resource_tab, "素材管理")
        
        # 设置项目结构页面
        self.setup_project_tab()
        
        # 设置素材管理页面
        self.setup_resource_tab()
        
        # 底部导出区域
        export_layout = QHBoxLayout()
        
        self.export_folder_btn = QPushButton("导出为文件夹")
        self.export_folder_btn.clicked.connect(self.export_as_folder)
        self.export_folder_btn.setEnabled(False)
        
        self.export_jar_check = QCheckBox("直接打包为JAR文件")
        
        self.export_jar_btn = QPushButton("导出为JAR")
        self.export_jar_btn.clicked.connect(self.export_as_jar)
        self.export_jar_btn.setEnabled(False)
        
        export_layout.addStretch()
        export_layout.addWidget(self.export_folder_btn)
        export_layout.addWidget(self.export_jar_check)
        export_layout.addWidget(self.export_jar_btn)
        
        main_layout.addLayout(export_layout)
        
    def setup_project_tab(self):
        layout = QHBoxLayout(self.project_tab)
        
        # 项目结构树
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabel("项目结构")
        layout.addWidget(self.project_tree)
        
        # 文件内容编辑器
        self.file_editor = QTextEdit()
        layout.addWidget(self.file_editor)
        
    def setup_resource_tab(self):
        layout = QVBoxLayout(self.resource_tab)
        
        # 原版素材预览区域
        self.resource_tree = QTreeWidget()
        self.resource_tree.setHeaderLabel("原版素材库")
        layout.addWidget(self.resource_tree)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.copy_resource_btn = QPushButton("复制到项目")
        self.copy_resource_btn.clicked.connect(self.copy_resource)
        self.copy_resource_btn.setEnabled(False)
        
        self.refresh_resource_btn = QPushButton("刷新素材库")
        self.refresh_resource_btn.clicked.connect(self.load_resources)
        
        btn_layout.addWidget(self.copy_resource_btn)
        btn_layout.addWidget(self.refresh_resource_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
    def on_version_change(self, version):
        self.current_version = version
        
    def create_new_project(self):
        # 选择项目保存位置
        project_path = QFileDialog.getExistingDirectory(self, "选择项目保存位置")
        if not project_path:
            return
            
        # 获取项目名称
        project_name, ok = QInputDialog.getText(self, "项目名称", "请输入项目名称:")
        if not ok or not project_name:
            return
            
        self.project_path = os.path.join(project_path, project_name)
        
        # 创建标准的Forge模组结构
        self.create_mod_structure()
        
        # 加载项目结构
        self.load_project_structure()
        
        # 启用导出按钮
        self.export_folder_btn.setEnabled(True)
        self.export_jar_btn.setEnabled(True)
        self.copy_resource_btn.setEnabled(True)
        
        QMessageBox.information(self, "成功", f"项目创建成功!\n位置: {self.project_path}")
        
    def create_mod_structure(self):
        # 基础目录结构
        directories = [
            "src/main/java/com/yourname/modid",
            "src/main/resources/assets/modid/textures/blocks",
            "src/main/resources/assets/modid/textures/items",
            "src/main/resources/assets/modid/models/block",
            "src/main/resources/assets/modid/models/item",
            "src/main/resources/data/modid/recipes",
            "src/main/resources/data/modid/tags/blocks",
            "src/main/resources/data/modid/tags/items"
        ]
        
        for dir_path in directories:
            full_path = os.path.join(self.project_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            
        # 创建示例文件
        self.create_example_files()
        
    def create_example_files(self):
        # 创建mods.toml
        mods_toml = f"""modLoader="javafml"
loaderVersion="[36,)"
license="MIT"
issueTrackerURL="https://github.com/yourname/modid/issues"
showAsResourcePack=false

[[mods]]
modId="modid"
version="1.0.0"
displayName="Example Mod"
authors="Your Name"
description='''
Example Mod Description
'''
"""
        self.write_file("src/main/resources/META-INF/mods.toml", mods_toml)
        
        # 创建mcmod.info
        mcmod_info = f"""[
    {{
        "modid": "modid",
        "name": "Example Mod",
        "description": "Example Mod Description",
        "version": "1.0.0",
        "mcversion": "{self.current_version}",
        "url": "https://github.com/yourname/modid",
        "updateUrl": "",
        "authorList": ["Your Name"],
        "credits": "Thanks to the Minecraft Forge team!",
        "logoFile": "",
        "screenshots": [],
        "dependencies": []
    }}
]"""
        self.write_file("src/main/resources/mcmod.info", mcmod_info)
        
        # 创建主类
        main_class = f"""package com.yourname.modid;

import net.minecraftforge.fml.common.Mod;

@Mod("modid")
public class ExampleMod {{
    public ExampleMod() {{
        // 构造函数
    }}
}}"""
        self.write_file("src/main/java/com/yourname/modid/ExampleMod.java", main_class)
        
        # 创建示例方块JSON
        block_json = """{
    "parent": "block/cube_all",
    "textures": {
        "all": "modid:block/example_block"
    }
}"""
        self.write_file("src/main/resources/assets/modid/models/block/example_block.json", block_json)
        
    def write_file(self, rel_path, content):
        full_path = os.path.join(self.project_path, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def load_project_structure(self):
        self.project_tree.clear()
        root_item = QTreeWidgetItem(self.project_tree)
        root_item.setText(0, os.path.basename(self.project_path))
        self.add_files_to_tree(root_item, self.project_path)
        
    def add_files_to_tree(self, parent_item, dir_path):
        try:
            for entry in os.listdir(dir_path):
                entry_path = os.path.join(dir_path, entry)
                
                item = QTreeWidgetItem(parent_item)
                item.setText(0, entry)
                
                if os.path.isdir(entry_path):
                    self.add_files_to_tree(item, entry_path)
                else:
                    # 存储文件路径
                    item.setData(0, Qt.UserRole, entry_path)
                    
        except PermissionError:
            pass
            
    def open_project(self):
        project_path = QFileDialog.getExistingDirectory(self, "选择项目文件夹")
        if project_path:
            self.project_path = project_path
            self.load_project_structure()
            self.export_folder_btn.setEnabled(True)
            self.export_jar_btn.setEnabled(True)
            self.copy_resource_btn.setEnabled(True)
            
    def load_resources(self):
        # 这里简化处理，实际应该从Minecraft jar文件中提取
        self.resource_tree.clear()
        
        # 创建示例素材结构
        categories = ["blocks", "items", "entities", "gui", "particles"]
        
        for category in categories:
            cat_item = QTreeWidgetItem(self.resource_tree)
            cat_item.setText(0, category)
            
            # 添加示例素材
            for i in range(5):
                res_item = QTreeWidgetItem(cat_item)
                res_item.setText(0, f"{category}_{i}.png")
                res_item.setData(0, Qt.UserRole, f"{category}/{category}_{i}.png")
                
    def copy_resource(self):
        if not self.project_path:
            QMessageBox.warning(self, "警告", "请先创建或打开项目!")
            return
            
        selected_items = self.resource_tree.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            resource_path = item.data(0, Qt.UserRole)
            if resource_path:
                # 复制到对应的项目目录
                if "blocks" in resource_path:
                    dest_dir = os.path.join(self.project_path, "src/main/resources/assets/modid/textures/blocks")
                elif "items" in resource_path:
                    dest_dir = os.path.join(self.project_path, "src/main/resources/assets/modid/textures/items")
                else:
                    dest_dir = os.path.join(self.project_path, "src/main/resources/assets/modid/textures")
                    
                os.makedirs(dest_dir, exist_ok=True)
                
                # 实际应用中应该从MC jar文件复制真实的贴图文件
                QMessageBox.information(self, "复制成功", f"素材已复制到:\n{dest_dir}")
                
    def export_as_folder(self):
        export_path = QFileDialog.getExistingDirectory(self, "选择导出位置")
        if export_path:
            dest_path = os.path.join(export_path, os.path.basename(self.project_path))
            
            # 复制整个项目
            shutil.copytree(self.project_path, dest_path, dirs_exist_ok=True)
            
            # 如果勾选了JAR选项
            if self.export_jar_check.isChecked():
                self.create_jar_file(dest_path, export_path)
                
            QMessageBox.information(self, "导出成功", f"项目已导出到:\n{dest_path}")
            
    def export_as_jar(self):
        export_path = QFileDialog.getExistingDirectory(self, "选择导出位置")
        if export_path:
            self.create_jar_file(self.project_path, export_path)
            
    def create_jar_file(self, source_path, export_path):
        jar_name = os.path.basename(source_path) + ".jar"
        jar_path = os.path.join(export_path, jar_name)
        
        # 创建JAR文件
        with zipfile.ZipFile(jar_path, 'w', zipfile.ZIP_DEFLATED) as jar:
            # 只打包src/main/resources和src/main/java内容
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # 只包含main目录下的内容
                    if "src/main/" in file_path:
                        # 计算相对路径
                        rel_path = os.path.relpath(file_path, os.path.join(source_path, "src/main"))
                        jar.write(file_path, rel_path)
                        
        QMessageBox.information(self, "JAR导出成功", f"JAR文件已创建:\n{jar_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MCModCreator()
    window.show()
    sys.exit(app.exec_())