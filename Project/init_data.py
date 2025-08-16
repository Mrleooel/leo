#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化测试数据脚本
"""

from app import create_app
from models import db, Patient, Doctor, Appointment, Medicine, Prescription, User
from datetime import datetime, timedelta
import random


def init_test_data():
    """初始化测试数据"""
    app = create_app()

    with app.app_context():
        # 清空现有数据
        db.drop_all()
        db.create_all()

        # 创建管理员用户
        admin = User(
            username='admin',
            email='admin@medical.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()  # 先提交用户数据

        # 创建测试患者
        patients_data = [
            {'name': '张三', 'contact': '13800138001', 'age': 35, 'gender': '男', 'address': '北京市朝阳区'},
            {'name': '李四', 'contact': '13800138002', 'age': 28, 'gender': '女', 'address': '北京市海淀区'},
            {'name': '王五', 'contact': '13800138003', 'age': 42, 'gender': '男', 'address': '北京市西城区'},
            {'name': '赵六', 'contact': '13800138004', 'age': 31, 'gender': '女', 'address': '北京市东城区'},
            {'name': '孙七', 'contact': '13800138005', 'age': 55, 'gender': '男', 'address': '北京市丰台区'},
            {'name': '周八', 'contact': '13800138006', 'age': 26, 'gender': '女', 'address': '北京市石景山区'},
            {'name': '吴九', 'contact': '13800138007', 'age': 38, 'gender': '男', 'address': '北京市通州区'},
            {'name': '郑十', 'contact': '13800138008', 'age': 29, 'gender': '女', 'address': '北京市昌平区'},
        ]

        patients = []
        for data in patients_data:
            patient = Patient(**data)
            db.session.add(patient)
            patients.append(patient)

        # 创建测试医生
        doctors_data = [
            {'name': '李医生', 'department': '内科', 'title': '主任医师', 'phone': '13900139001',
             'email': 'li@hospital.com', 'specialization': '心血管疾病'},
            {'name': '王医生', 'department': '外科', 'title': '副主任医师', 'phone': '13900139002',
             'email': 'wang@hospital.com', 'specialization': '普外科手术'},
            {'name': '张医生', 'department': '儿科', 'title': '主治医师', 'phone': '13900139003',
             'email': 'zhang@hospital.com', 'specialization': '儿童常见病'},
            {'name': '刘医生', 'department': '妇科', 'title': '主任医师', 'phone': '13900139004',
             'email': 'liu@hospital.com', 'specialization': '妇科疾病'},
            {'name': '陈医生', 'department': '眼科', 'title': '副主任医师', 'phone': '13900139005',
             'email': 'chen@hospital.com', 'specialization': '眼科疾病'},
            {'name': '杨医生', 'department': '口腔科', 'title': '主治医师', 'phone': '13900139006',
             'email': 'yang@hospital.com', 'specialization': '口腔疾病'},
        ]

        doctors = []
        for data in doctors_data:
            doctor = Doctor(**data)
            db.session.add(doctor)
            doctors.append(doctor)

        # 先提交患者和医生数据，确保它们有ID
        db.session.commit()

        # 创建测试药品
        medicines_data = [
            {'name': '阿司匹林', 'description': '解热镇痛药', 'price': 15.50, 'stock': 200, 'category': '处方药',
             'manufacturer': '拜耳医药'},
            {'name': '布洛芬', 'description': '消炎止痛药', 'price': 12.80, 'stock': 150, 'category': '非处方药',
             'manufacturer': '中美史克'},
            {'name': '感冒灵颗粒', 'description': '感冒用药', 'price': 25.00, 'stock': 100, 'category': '非处方药',
             'manufacturer': '999药业'},
            {'name': '板蓝根颗粒', 'description': '清热解毒', 'price': 18.50, 'stock': 80, 'category': '中药',
             'manufacturer': '同仁堂'},
            {'name': '维生素C片', 'description': '维生素补充', 'price': 8.90, 'stock': 300, 'category': '非处方药',
             'manufacturer': '养生堂'},
            {'name': '钙片', 'description': '钙质补充', 'price': 45.00, 'stock': 120, 'category': '非处方药',
             'manufacturer': '汤臣倍健'},
            {'name': '降压药', 'description': '高血压治疗', 'price': 68.00, 'stock': 50, 'category': '处方药',
             'manufacturer': '诺华制药'},
            {'name': '降糖药', 'description': '糖尿病治疗', 'price': 85.50, 'stock': 40, 'category': '处方药',
             'manufacturer': '默克制药'},
        ]

        medicines = []
        for data in medicines_data:
            medicine = Medicine(**data)
            db.session.add(medicine)
            medicines.append(medicine)

        # 提交药品数据
        db.session.commit()

        # 创建测试预约
        appointments_data = []
        for i in range(30):
            patient = random.choice(patients)
            doctor = random.choice(doctors)
            date = datetime.now() + timedelta(days=random.randint(1, 30), hours=random.randint(9, 17))
            status = random.choice(['scheduled', 'completed', 'cancelled'])

            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                date=date,
                status=status,
                notes=f'测试预约 {i + 1}'
            )
            db.session.add(appointment)
            appointments_data.append(appointment)

        # 提交预约数据
        db.session.commit()

        # 创建测试处方
        for appointment in appointments_data:
            if appointment.status == 'completed':
                # 为已完成的预约创建处方
                medicine = random.choice(medicines)
                prescription = Prescription(
                    appointment_id=appointment.id,
                    medicine_id=medicine.id,
                    dosage='每日3次，每次1片',
                    quantity=random.randint(1, 3),
                    instructions='饭后服用，多喝水'
                )
                db.session.add(prescription)

        # 提交处方数据
        db.session.commit()

        print("测试数据初始化完成！")
        print(f"创建了 {len(patients)} 个患者")
        print(f"创建了 {len(doctors)} 个医生")
        print(f"创建了 {len(medicines)} 种药品")
        print(f"创建了 {len(appointments_data)} 个预约")
        print("默认管理员账户: admin / admin123")


if __name__ == '__main__':
    init_test_data()