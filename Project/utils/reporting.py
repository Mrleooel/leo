import pandas as pd
import os
from datetime import datetime
from models import db, Medicine, Prescription, Appointment, Doctor, Patient

class ReportGenerator:
    """报表生成器"""
    
    def __init__(self, reports_folder='reports'):
        self.reports_folder = reports_folder
        os.makedirs(reports_folder, exist_ok=True)
    
    def generate_medicine_sales_report(self):
        """生成药品销售报表"""
        try:
            # 查询药品销售数据
            query = db.session.query(
                Medicine.name,
                Medicine.category,
                Medicine.price,
                Medicine.stock,
                db.func.coalesce(db.func.sum(Prescription.quantity), 0).label('total_sold'),
                db.func.coalesce(db.func.sum(Prescription.quantity * Medicine.price), 0).label('total_revenue')
            ).outerjoin(Prescription, Medicine.id == Prescription.medicine_id)\
             .group_by(Medicine.id, Medicine.name, Medicine.category, Medicine.price, Medicine.stock)
            
            # 将查询结果转换为DataFrame
            results = query.all()
            data = []
            for result in results:
                data.append({
                    '药品名称': result.name,
                    '类别': result.category,
                    '单价': float(result.price),
                    '库存': result.stock,
                    '销量': result.total_sold,
                    '销售额': float(result.total_revenue)
                })
            
            df = pd.DataFrame(data)
            
            # 生成Excel文件
            filename = f"medicine_sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join(self.reports_folder, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # 销售报表
                df.to_excel(writer, sheet_name='药品销售报表', index=False)
                
                # 库存报表
                stock_df = df[['药品名称', '类别', '库存', '单价']].copy()
                stock_df['库存价值'] = stock_df['库存'] * stock_df['单价']
                stock_df.to_excel(writer, sheet_name='库存报表', index=False)
                
                # 销售统计
                summary_data = {
                    '统计项': ['总药品数', '总库存', '总销售额', '平均单价'],
                    '数值': [
                        len(df),
                        df['库存'].sum(),
                        df['销售额'].sum(),
                        df['单价'].mean()
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='统计摘要', index=False)
            
            return filepath
        except Exception as e:
            print(f"生成药品销售报表时出错: {str(e)}")
            raise
    
    def generate_appointment_report(self, start_date=None, end_date=None):
        """生成预约报表"""
        try:
            query = db.session.query(
                Appointment.id,
                Patient.name.label('patient_name'),
                Doctor.name.label('doctor_name'),
                Doctor.department,
                Appointment.date,
                Appointment.status,
                Appointment.notes
            ).join(Patient).join(Doctor)
            
            if start_date:
                query = query.filter(Appointment.date >= start_date)
            if end_date:
                query = query.filter(Appointment.date <= end_date)
            
            # 将查询结果转换为DataFrame
            results = query.all()
            data = []
            for result in results:
                data.append({
                    '预约ID': result.id,
                    '患者姓名': result.patient_name,
                    '医生姓名': result.doctor_name,
                    '科室': result.department,
                    '预约时间': result.date.strftime('%Y-%m-%d %H:%M'),
                    '状态': result.status,
                    '备注': result.notes or ''
                })
            
            df = pd.DataFrame(data)
            
            filename = f"appointment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join(self.reports_folder, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='预约报表', index=False)
                
                # 按科室统计
                if not df.empty:
                    dept_stats = df.groupby('科室').size().reset_index(name='预约数量')
                    dept_stats.to_excel(writer, sheet_name='科室统计', index=False)
                    
                    # 按状态统计
                    status_stats = df.groupby('状态').size().reset_index(name='数量')
                    status_stats.to_excel(writer, sheet_name='状态统计', index=False)
            
            return filepath
        except Exception as e:
            print(f"生成预约报表时出错: {str(e)}")
            raise
    
    def generate_patient_report(self):
        """生成患者报表"""
        try:
            query = db.session.query(
                Patient.id,
                Patient.name,
                Patient.age,
                Patient.gender,
                Patient.register_date,
                db.func.count(Appointment.id).label('appointment_count')
            ).outerjoin(Appointment)\
             .group_by(Patient.id, Patient.name, Patient.age, Patient.gender, Patient.register_date)
            
            # 将查询结果转换为DataFrame
            results = query.all()
            data = []
            for result in results:
                data.append({
                    '患者ID': result.id,
                    '姓名': result.name,
                    '年龄': result.age,
                    '性别': result.gender,
                    '注册日期': result.register_date.strftime('%Y-%m-%d'),
                    '预约次数': result.appointment_count
                })
            
            df = pd.DataFrame(data)
            
            filename = f"patient_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = os.path.join(self.reports_folder, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='患者报表', index=False)
                
                # 年龄分布
                if not df.empty:
                    age_stats = df.groupby(pd.cut(df['年龄'], bins=[0, 18, 30, 50, 70, 100])).size()
                    age_stats.to_excel(writer, sheet_name='年龄分布')
                    
                    # 性别分布
                    gender_stats = df.groupby('性别').size().reset_index(name='数量')
                    gender_stats.to_excel(writer, sheet_name='性别分布', index=False)
            
            return filepath
        except Exception as e:
            print(f"生成患者报表时出错: {str(e)}")
            raise 