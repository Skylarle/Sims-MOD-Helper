# -*- coding: utf-8 -*-
# Sims MOD小助手 V1.0

import os
import re
import shutil
import time
import webbrowser
import patoolib
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# =================================================================================================
# 核心逻辑区 - 我们之前写的两个脚本的主要功能被整合到了这里
# =================================================================================================

# --- “整理与分类”脚本的核心规则 ---
KEYWORD_TO_FOLDER_MAP = {
    # CAS界面相关
    'slider': 'CAS相关', 'preset': 'CAS相关', 'sculptor': 'CAS相关', 'teeth': 'CAS相关',
    'chin': 'CAS相关', 'jaw': 'CAS相关', 'nose': 'CAS相关', 'mouth': 'CAS相关',
    'ear': 'CAS相关', 'body': 'CAS相关',
    # 头发相关
    'hair': 'Hair-头发', 'hairline': 'Hairline-发际线',
    # 脸部
    'eyelash': 'Lashes-睫毛', 'lashes': 'Lashes-睫毛', 'eyebrow': 'Brows-眉毛',
    'brows': 'Brows-眉毛', 'contacts': 'Contacts-美瞳', 's-club': 'Eyes-眼珠', 'eye': 'Eyes-眼珠',
    # 皮肤相关
    'overlay': 'SkinDetail-皮肤细节', 'face mask': 'SkinDetail-皮肤细节', 'facemask': 'SkinDetail-皮肤细节',
    'face details': 'SkinDetail-皮肤细节', 'skintone': 'Skin-皮肤', 'skin': 'Skin-皮肤',
    'skindetail': 'SkinDetail-皮肤细节', 'freckles': 'SkinDetail-皮肤细节', 'mole': 'SkinDetail-皮肤细节',
    'tattoo': 'Tattoo-纹身', 'bodyhair': 'Bodyhair-体毛', 'beard': 'Beard-胡子', 'occult': 'SkinDetail-皮肤细节',
    # 化妆品
    'eyeliner': 'Makeup-化妆品', 'eyeshadow': 'Makeup-化妆品', 'lipstick': 'Makeup-化妆品',
    'lips': 'Makeup-化妆品', 'blush': 'Makeup-化妆品', 'makeup': 'Makeup-化妆品', 'contour': 'Makeup-化妆品',
    # 服装配饰
    'sneakers': 'Shoes-鞋子', 'clothing': 'Clothing-衣服', 'outfit': 'Clothing-衣服',
    'uniform': 'Clothing-衣服', 'top': 'Clothing-衣服', 'bottom': 'Clothing-衣服',
    'shoes': 'Shoes-鞋子', 'nails': 'Nails-指甲', 'acc': 'Acc-配饰',
    'accessory': 'Acc-配饰', 'jewelry': 'Acc-配饰',
    # 其他
    'pose': 'Pose-动作', 'cas': 'CAS相关', 'default': 'Default-默认替换',
}

# --- 功能函数 ---

def log_message(log_widget, message):
    """向日志窗口打印信息"""
    log_widget.config(state=tk.NORMAL)
    log_widget.insert(tk.END, message + "\n")
    log_widget.see(tk.END) # 滚动到底部
    log_widget.config(state=tk.DISABLED)
    log_widget.update() # 立即刷新界面

def open_urls_from_files(file_list, log_widget):
    """从多个txt文件中读取URL并用浏览器打开"""
    urls_to_open = []
    line_pattern = re.compile(r'https?://\S+')
    for file_path in file_list:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    match = line_pattern.search(line)
                    if match:
                        urls_to_open.append(match.group(0))
        except Exception as e:
            log_message(log_widget, f"错误:读取 {os.path.basename(file_path)} 失败: {e}")

    if not urls_to_open:
        log_message(log_widget, "错误: 未在任何文件中找到有效网址。")
        return 0
    
    log_message(log_widget, f"即将为您在浏览器中打开 {len(urls_to_open)} 个网页...")
    time.sleep(1)
    for url in urls_to_open:
        webbrowser.open_new_tab(url)
    return len(urls_to_open)

def organize_downloads(downloads_dir, mods_dir, log_widget):
    """整理下载文件夹里的新文件"""
    log_message(log_widget, "【步骤 ②】开始整理下载...")
    dest_folder_name = 'AA-待整理'
    destination_path = os.path.join(mods_dir, dest_folder_name)
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
    
    files_after = set(os.listdir(downloads_dir))
    new_files = files_after - app.files_before_download # app.files_before_download 是全局变量
    
    if not new_files:
        log_message(log_widget, "未检测到任何新下载的文件。")
        return
        
    log_message(log_widget, f"检测到 {len(new_files)} 个新文件，开始处理：")
    for filename in new_files:
        if filename.endswith(('.crdownload', '.tmp', '.part')):
            continue
        
        source_filepath = os.path.join(downloads_dir, filename)
        moved_filepath = os.path.join(destination_path, filename)

        try:
            shutil.move(source_filepath, moved_filepath)
            log_message(log_widget, f"  -> '{filename}' 已移动到 {dest_folder_name}")

            if moved_filepath.lower().endswith(('.zip', '.rar', '.7z')):
                log_message(log_widget, f"    -> 正在解压: {filename}...")
                patoolib.extract_archive(moved_filepath, outdir=destination_path, verbosity=-1)
                log_message(log_widget, "    -> 解压成功！")
                os.remove(moved_filepath)
                log_message(log_widget, f"    -> 已删除原始压缩包: {filename}")
        except Exception as e:
            log_message(log_widget, f"处理 '{filename}' 时出错: {e}")

def sort_organized_files(mods_dir, log_widget):
    """对“待整理”文件夹里的文件进行智能分类"""
    log_message(log_widget, "【步骤 ③】开始智能分类...")
    source_folder_name = 'AA-待整理'
    source_dir = os.path.join(mods_dir, source_folder_name)
    
    if not os.path.isdir(source_dir):
        log_message(log_widget, f"错误: 文件夹 '{source_folder_name}' 不存在。")
        return

    items_in_source = os.listdir(source_dir)
    if not items_in_source:
        log_message(log_widget, "待整理文件夹是空的，无需分类。")
        return

    moved_count = 0
    for item_name in items_in_source:
        item_path = os.path.join(source_dir, item_name)
        item_name_lower = item_name.lower()
        moved = False

        for keyword, dest_folder_name in KEYWORD_TO_FOLDER_MAP.items():
            if keyword in item_name_lower:
                dest_dir = os.path.join(mods_dir, dest_folder_name)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                
                dest_path = os.path.join(dest_dir, item_name)
                if os.path.exists(dest_path):
                    name, ext = os.path.splitext(item_name)
                    dest_path = os.path.join(dest_dir, f"{name}_duplicate_{int(time.time())}{ext}")

                try:
                    shutil.move(item_path, dest_path)
                    log_message(log_widget, f"'{item_name}' -> 已移动到 '{dest_folder_name}' (关键词: {keyword})")
                    moved = True
                    moved_count += 1
                    break
                except Exception as e:
                    log_message(log_widget, f"移动 '{item_name}' 时出错: {e}")
                    moved = True
                    break
        
        if not moved:
            log_message(log_widget, f"'{item_name}' -> 未找到匹配关键词，保留在原地。")
    
    log_message(log_widget, f"分类完毕！成功移动 {moved_count} 项。")


# =================================================================================================
# GUI 界面区 - 使用Tkinter创建我们的程序窗口
# =================================================================================================

class ModHelperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sims MOD小助手 V1.0")
        self.root.geometry("700x650") # 设置窗口大小

        # 全局变量，用于存储路径和状态
        self.mods_dir = tk.StringVar()
        self.downloads_dir = tk.StringVar()
        self.txt_files = []
        self.files_before_download = set()

        # --- 1. 路径设置区 ---
        path_frame = tk.LabelFrame(root, text=" 路径设置 ", padx=10, pady=10)
        path_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(path_frame, text="MODS文件夹路径:").grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(path_frame, textvariable=self.mods_dir, width=70).grid(row=0, column=1, sticky="ew")
        tk.Button(path_frame, text="浏览...", command=self.select_mods_dir).grid(row=0, column=2, padx=5)

        tk.Label(path_frame, text="下载文件夹路径:").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(path_frame, textvariable=self.downloads_dir, width=70).grid(row=1, column=1, sticky="ew")
        tk.Button(path_frame, text="浏览...", command=self.select_downloads_dir).grid(row=1, column=2, padx=5)
        
        path_frame.grid_columnconfigure(1, weight=1)

        # --- 2. 下载流程区 ---
        download_frame = tk.LabelFrame(root, text=" 下载与整理流程 ", padx=10, pady=10)
        download_frame.pack(padx=10, pady=10, fill="x")

        # CC列表文件显示区域
        self.txt_listbox = tk.Listbox(download_frame, height=5)
        self.txt_listbox.pack(padx=5, pady=5, fill="x", expand=True)

        # 按钮们
        btn_frame = tk.Frame(download_frame)
        btn_frame.pack(fill="x", pady=5)
        
        tk.Button(btn_frame, text="添加CC列表(.txt)", command=self.add_txt_files).pack(side="left", padx=5)
        tk.Button(btn_frame, text="清空列表", command=self.clear_txt_list).pack(side="left", padx=5)
        
        # 流程按钮
        self.btn_step1 = tk.Button(download_frame, text="① 开始下载 (打开网页)", command=self.run_step1, bg="#c1e1c1", font=('Helvetica', 10, 'bold'))
        self.btn_step1.pack(fill="x", pady=5)
        
        self.btn_step2 = tk.Button(download_frame, text="② 整理下载 (移动与解压)", command=self.run_step2, state="disabled")
        self.btn_step2.pack(fill="x", pady=5)
        
        self.btn_step3 = tk.Button(download_frame, text="③ 智能分类", command=self.run_step3, state="disabled")
        self.btn_step3.pack(fill="x", pady=5)

        # --- 3. 日志显示区 ---
        log_frame = tk.LabelFrame(root, text=" 日志 ", padx=10, pady=10)
        log_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED, height=10)
        self.log_text.pack(fill="both", expand=True)

    # --- GUI按钮对应的功能函数 ---
    def select_mods_dir(self):
        dir_path = filedialog.askdirectory(title="请选择你的Mods文件夹")
        if dir_path:
            self.mods_dir.set(dir_path)
            log_message(self.log_text, f"已设置Mods文件夹: {dir_path}")

    def select_downloads_dir(self):
        dir_path = filedialog.askdirectory(title="请选择你的浏览器默认下载文件夹")
        if dir_path:
            self.downloads_dir.set(dir_path)
            log_message(self.log_text, f"已设置下载文件夹: {dir_path}")

    def add_txt_files(self):
        files = filedialog.askopenfilenames(title="请选择一个或多个CC列表txt文件", filetypes=[("Text files", "*.txt")])
        if files:
            for file in files:
                if file not in self.txt_files:
                    self.txt_files.append(file)
                    self.txt_listbox.insert(tk.END, os.path.basename(file))
            log_message(self.log_text, f"已添加 {len(files)} 个txt文件。")

    def clear_txt_list(self):
        self.txt_files.clear()
        self.txt_listbox.delete(0, tk.END)
        log_message(self.log_text, "已清空txt文件列表。")

    def run_step1(self):
        # 检查路径和文件是否已选择
        if not self.mods_dir.get() or not self.downloads_dir.get():
            messagebox.showerror("错误", "请先设置好Mods和下载文件夹的路径！")
            return
        if not self.txt_files:
            messagebox.showerror("错误", "请先添加至少一个CC列表txt文件！")
            return
        
        # 提醒用户清理下载文件夹
        if not messagebox.askokcancel("操作确认", "即将开始下载流程。\n\n为确保整理准确，请先手动清理您的“下载”文件夹。\n\n清理完毕后，请点击“确定”继续。"):
            return

        # 记录下载前状态
        self.files_before_download = set(os.listdir(self.downloads_dir.get()))
        log_message(self.log_text, "【步骤 ①】开始下载...")
        log_message(self.log_text, "已记录当前下载文件夹状态。")
        
        # 执行功能
        opened_count = open_urls_from_files(self.txt_files, self.log_text)
        if opened_count > 0:
            log_message(self.log_text, f"所有网页已打开。请在浏览器中手动下载所有文件。")
            log_message(self.log_text, "下载完成后，请点击【步骤 ②】按钮继续。")
            # 更新按钮状态
            self.btn_step1.config(state="disabled")
            self.btn_step2.config(state="normal", bg="#c1e1c1")
            self.btn_step3.config(state="disabled", bg="SystemButtonFace")
    
    def run_step2(self):
        if not messagebox.askokcancel("操作确认", "请确认您已在浏览器中下载完所有文件。\n\n点击“确定”将开始整理。"):
            return
            
        organize_downloads(self.downloads_dir.get(), self.mods_dir.get(), self.log_text)
        log_message(self.log_text, "整理完毕！现在可以点击【步骤 ③】进行智能分类。")
        
        # 更新按钮状态
        self.btn_step2.config(state="disabled", bg="SystemButtonFace")
        self.btn_step3.config(state="normal", bg="#c1e1c1")

    def run_step3(self):
        sort_organized_files(self.mods_dir.get(), self.log_text)
        log_message(self.log_text, "========================================")
        log_message(self.log_text, "所有流程已完成！可以关闭程序或开始新一轮下载。")
        
        # 重置流程，允许新一轮下载
        self.btn_step1.config(state="normal", bg="#c1e1c1")
        self.btn_step2.config(state="disabled", bg="SystemButtonFace")
        self.btn_step3.config(state="disabled", bg="SystemButtonFace")
        self.clear_txt_list()
        

if __name__ == "__main__":
    root = tk.Tk()
    app = ModHelperApp(root)
    root.mainloop()