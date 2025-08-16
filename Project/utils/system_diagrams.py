#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统设计图生成模块
使用diagrams库生成各种系统设计图
"""

import os
import sys

# 确保能正确导入diagrams库
try:
    from diagrams import Diagram, Cluster
    from diagrams.generic.database import SQL
    from diagrams.generic.storage import Storage
    from diagrams.onprem.client import Client
    from diagrams.programming.framework import Flask
    from diagrams.programming.language import Python
except ImportError as e:
    print(f"导入diagrams库失败: {e}")
    print("请确保已安装diagrams库: pip install diagrams")
    sys.exit(1)


def generate_er_diagram():
    """生成ER图，展示5张表的关系"""
    try:
        with Diagram("医疗平台ER图", show=False, direction="TB", filename="er_diagram"):
            # 定义节点
            patient = SQL("患者表\n(Patient)")
            doctor = SQL("医生表\n(Doctor)")
            appointment = SQL("预约表\n(Appointment)")
            medicine = SQL("药品表\n(Medicine)")
            prescription = SQL("处方表\n(Prescription)")

            # 定义关系
            patient >> appointment
            doctor >> appointment
            appointment >> prescription
            medicine >> prescription

        return "ER图生成完成，文件保存为: er_diagram.png"
    except Exception as e:
        return f"ER图生成失败: {str(e)}"


def generate_appointment_activity():
    """生成预约流程活动图"""
    try:
        with Diagram("预约流程活动图", show=False, direction="LR", filename="appointment_activity"):
            # 定义活动节点
            start = Client("开始")
            register = Storage("患者注册")
            search = Storage("查找医生")
            book = Storage("预约挂号")
            confirm = Storage("确认预约")
            visit = Storage("就诊")
            end = Client("结束")

            # 定义流程
            start >> register >> search >> book >> confirm >> visit >> end

        return "预约流程活动图生成完成，文件保存为: appointment_activity.png"
    except Exception as e:
        return f"预约流程活动图生成失败: {str(e)}"


def generate_prescription_sequence():
    """生成处方开具顺序图"""
    try:
        with Diagram("处方开具顺序图", show=False, direction="TB", filename="prescription_sequence"):
            with Cluster("医疗流程"):
                patient = Client("患者")
                doctor = Flask("医生")
                pharmacy = Storage("药房")
                system = SQL("系统")

                # 定义交互顺序
                patient >> doctor
                doctor >> system
                system >> pharmacy
                pharmacy >> patient

        return "处方开具顺序图生成完成，文件保存为: prescription_sequence.png"
    except Exception as e:
        return f"处方开具顺序图生成失败: {str(e)}"


def generate_system_architecture():
    """生成系统架构图"""
    try:
        with Diagram("医疗平台系统架构", show=False, direction="TB", filename="system_architecture"):
            with Cluster("前端"):
                web = Client("Web客户端")
                mobile = Client("移动端")

            with Cluster("后端服务"):
                flask = Flask("Flask应用")
                api = Python("API服务")

            with Cluster("数据层"):
                db = SQL("数据库")
                cache = Storage("缓存")

            # 连接关系
            web >> flask
            mobile >> flask
            flask >> api
            api >> db
            api >> cache

        return "系统架构图生成完成，文件保存为: system_architecture.png"
    except Exception as e:
        return f"系统架构图生成失败: {str(e)}"


def generate_all_diagrams():
    """生成所有图表"""
    results = []
    
    print("开始生成系统设计图...")
    
    # 生成ER图
    print("1. 生成ER图...")
    result = generate_er_diagram()
    results.append(result)
    print(result)
    
    # 生成预约流程活动图
    print("2. 生成预约流程活动图...")
    result = generate_appointment_activity()
    results.append(result)
    print(result)
    
    # 生成处方开具顺序图
    print("3. 生成处方开具顺序图...")
    result = generate_prescription_sequence()
    results.append(result)
    print(result)
    
    # 生成系统架构图
    print("4. 生成系统架构图...")
    result = generate_system_architecture()
    results.append(result)
    print(result)
    
    print("\n所有图表生成完成！")
    print("生成的文件保存在当前目录:")
    for file in os.listdir('.'):
        if file.endswith('.png') and 'diagram' in file.lower():
            print(f"  - {file}")
    
    return results


if __name__ == "__main__":
    # 生成所有图表
    generate_all_diagrams() 