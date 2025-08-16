from flask import render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
import plotly.graph_objs as go
import plotly.utils
import json
import os
from models import db, Patient, Doctor, Appointment, Medicine, Prescription, User
from utils.reporting import ReportGenerator
from utils.system_diagrams import generate_er_diagram, generate_appointment_activity, generate_prescription_sequence, generate_system_architecture

def init_routes(app):
    @app.route('/')
    @login_required
    def index():
        return redirect(url_for('dashboard'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                from flask_login import login_user
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('用户名或密码错误', 'error')
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        from flask_login import logout_user
        logout_user()
        return redirect(url_for('login'))

    # ==================== 处方管理 ====================
    @app.route('/prescriptions')
    @login_required
    def prescriptions():
        appointments = Appointment.query.all()
        medicines = Medicine.query.all()
        return render_template('prescriptions.html', appointments=appointments, medicines=medicines)

    @app.route('/prescriptions/add', methods=['POST'])
    @login_required
    def add_prescription():
        try:
            data = request.get_json()
            appointment_id = int(data['appointment_id'])
            medicine_id = int(data['medicine_id'])
            quantity = int(data['quantity'])

            medicine = Medicine.query.get_or_404(medicine_id)
            if medicine.stock < quantity:
                return jsonify({'success': False, 'message': '库存不足'})

            prescription = Prescription(
                appointment_id=appointment_id,
                medicine_id=medicine_id,
                quantity=quantity,
                dosage=data.get('dosage', '')
            )
            medicine.stock -= quantity
            db.session.add(prescription)
            db.session.commit()
            return jsonify({'success': True, 'message': '处方已开具并扣减库存'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'失败: {str(e)}'})

    # ==================== 患者管理 CRUD ====================
    @app.route('/patients')
    @login_required
    def patients():
        patients = Patient.query.all()
        return render_template('patients.html', patients=patients)
    
    @app.route('/patients/add', methods=['POST'])
    @login_required
    def add_patient():
        try:
            data = request.get_json()
            patient = Patient(
                name=data['name'],
                contact=data['contact'],
                age=data['age'],
                gender=data['gender'],
                address=data.get('address', ''),
                register_date=datetime.now()
            )
            db.session.add(patient)
            db.session.commit()
            return jsonify({'success': True, 'message': '患者添加成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})
    
    @app.route('/patients/edit/<int:patient_id>', methods=['POST'])
    @login_required
    def edit_patient(patient_id):
        try:
            patient = Patient.query.get_or_404(patient_id)
            data = request.get_json()
            
            patient.name = data['name']
            patient.contact = data['contact']
            patient.age = data['age']
            patient.gender = data['gender']
            patient.address = data.get('address', '')
            
            db.session.commit()
            return jsonify({'success': True, 'message': '患者信息更新成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})
    
    @app.route('/patients/delete/<int:patient_id>', methods=['POST'])
    @login_required
    def delete_patient(patient_id):
        try:
            patient = Patient.query.get_or_404(patient_id)
            db.session.delete(patient)
            db.session.commit()
            return jsonify({'success': True, 'message': '患者删除成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})
    
    # ==================== 医生管理 CRUD ====================
    @app.route('/doctors')
    @login_required
    def doctors():
        doctors = Doctor.query.all()
        return render_template('doctors.html', doctors=doctors)
    
    @app.route('/doctors/add', methods=['POST'])
    @login_required
    def add_doctor():
        try:
            data = request.get_json()
            doctor = Doctor(
                name=data['name'],
                department=data['department'],
                title=data['title'],
                phone=data.get('phone', ''),
                available=data.get('available', True)
            )
            db.session.add(doctor)
            db.session.commit()
            return jsonify({'success': True, 'message': '医生添加成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})
    
    @app.route('/doctors/edit/<int:doctor_id>', methods=['POST'])
    @login_required
    def edit_doctor(doctor_id):
        try:
            doctor = Doctor.query.get_or_404(doctor_id)
            data = request.get_json()
            
            doctor.name = data['name']
            doctor.department = data['department']
            doctor.title = data['title']
            doctor.phone = data.get('phone', '')
            doctor.available = data.get('available', True)
            
            db.session.commit()
            return jsonify({'success': True, 'message': '医生信息更新成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})
    
    @app.route('/doctors/delete/<int:doctor_id>', methods=['POST'])
    @login_required
    def delete_doctor(doctor_id):
        try:
            doctor = Doctor.query.get_or_404(doctor_id)
            db.session.delete(doctor)
            db.session.commit()
            return jsonify({'success': True, 'message': '医生删除成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})
    
    @app.route('/doctors/toggle/<int:doctor_id>', methods=['POST'])
    @login_required
    def toggle_doctor_availability(doctor_id):
        try:
            doctor = Doctor.query.get_or_404(doctor_id)
            doctor.available = not doctor.available
            db.session.commit()
            status = "可用" if doctor.available else "不可用"
            return jsonify({'success': True, 'message': f'医生状态已更新为{status}', 'available': doctor.available})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'状态更新失败: {str(e)}'})
    
    # ==================== 药品管理 CRUD ====================
    @app.route('/medicines')
    @login_required
    def medicines():
        medicines = Medicine.query.all()
        return render_template('medicines.html', medicines=medicines)
    
    @app.route('/medicines/add', methods=['POST'])
    @login_required
    def add_medicine():
        try:
            data = request.get_json()
            medicine = Medicine(
                name=data['name'],
                description=data.get('description', ''),
                price=float(data['price']),
                stock=int(data['stock']),
                category=data['category'],
                manufacturer=data.get('manufacturer', ''),
                expiry_date=datetime.strptime(data['expiry_date'], '%Y-%m-%d') if data.get('expiry_date') else None
            )
            db.session.add(medicine)
            db.session.commit()
            return jsonify({'success': True, 'message': '药品添加成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})
    
    @app.route('/medicines/edit/<int:medicine_id>', methods=['POST'])
    @login_required
    def edit_medicine(medicine_id):
        try:
            medicine = Medicine.query.get_or_404(medicine_id)
            data = request.get_json()
            
            medicine.name = data['name']
            medicine.description = data.get('description', '')
            medicine.price = float(data['price'])
            medicine.stock = int(data['stock'])
            medicine.category = data['category']
            medicine.manufacturer = data.get('manufacturer', '')
            if data.get('expiry_date'):
                medicine.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d')
            
            db.session.commit()
            return jsonify({'success': True, 'message': '药品信息更新成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})
    
    @app.route('/medicines/delete/<int:medicine_id>', methods=['POST'])
    @login_required
    def delete_medicine(medicine_id):
        try:
            medicine = Medicine.query.get_or_404(medicine_id)
            db.session.delete(medicine)
            db.session.commit()
            return jsonify({'success': True, 'message': '药品删除成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})
    
    @app.route('/medicines/stock/<int:medicine_id>', methods=['POST'])
    @login_required
    def update_medicine_stock(medicine_id):
        try:
            medicine = Medicine.query.get_or_404(medicine_id)
            data = request.get_json()
            new_stock = int(data['stock'])
            
            if new_stock < 0:
                return jsonify({'success': False, 'message': '库存不能为负数'})
            
            medicine.stock = new_stock
            db.session.commit()
            return jsonify({'success': True, 'message': '库存更新成功', 'stock': new_stock})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'库存更新失败: {str(e)}'})
    
    # ==================== 预约管理 CRUD ====================
    @app.route('/appointments')
    @login_required
    def appointments():
        appointments = Appointment.query.join(Patient).join(Doctor).all()
        patients = Patient.query.all()
        doctors = Doctor.query.filter_by(available=True).all()
        return render_template('appointments.html', 
                            appointments=appointments, 
                            patients=patients, 
                            doctors=doctors)
    
    @app.route('/appointments/add', methods=['POST'])
    @login_required
    def add_appointment():
        try:
            data = request.get_json()
            appointment = Appointment(
                patient_id=int(data['patient_id']),
                doctor_id=int(data['doctor_id']),
                date=datetime.strptime(data['date'], '%Y-%m-%d %H:%M'),
                status=data.get('status', 'scheduled'),
                notes=data.get('notes', ''),
                created_at=datetime.now()
            )
            db.session.add(appointment)
            db.session.commit()
            return jsonify({'success': True, 'message': '预约创建成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'创建失败: {str(e)}'})
    
    @app.route('/appointments/edit/<int:appointment_id>', methods=['POST'])
    @login_required
    def edit_appointment(appointment_id):
        try:
            appointment = Appointment.query.get_or_404(appointment_id)
            data = request.get_json()
            
            appointment.patient_id = int(data['patient_id'])
            appointment.doctor_id = int(data['doctor_id'])
            appointment.date = datetime.strptime(data['date'], '%Y-%m-%d %H:%M')
            appointment.status = data['status']
            appointment.notes = data.get('notes', '')
            
            db.session.commit()
            return jsonify({'success': True, 'message': '预约信息更新成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})
    
    @app.route('/appointments/delete/<int:appointment_id>', methods=['POST'])
    @login_required
    def delete_appointment(appointment_id):
        try:
            appointment = Appointment.query.get_or_404(appointment_id)
            db.session.delete(appointment)
            db.session.commit()
            return jsonify({'success': True, 'message': '预约删除成功'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})
    
    @app.route('/appointments/status/<int:appointment_id>', methods=['POST'])
    @login_required
    def update_appointment_status(appointment_id):
        try:
            appointment = Appointment.query.get_or_404(appointment_id)
            data = request.get_json()
            new_status = data['status']
            
            appointment.status = new_status
            db.session.commit()
            
            status_text = {
                'scheduled': '已预约',
                'confirmed': '已确认',
                'completed': '已完成',
                'cancelled': '已取消'
            }.get(new_status, new_status)
            
            return jsonify({'success': True, 'message': f'预约状态已更新为{status_text}', 'status': new_status})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'状态更新失败: {str(e)}'})
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/dashboard/statistics')
    @login_required
    def dashboard_statistics():
        """获取dashboard统计数据"""
        try:
            # 获取统计数据
            total_patients = Patient.query.count()
            total_doctors = Doctor.query.count()
            total_medicines = Medicine.query.count()
            
            # 获取今日预约数
            today = datetime.now().date()
            today_appointments = Appointment.query.filter(
                db.func.date(Appointment.date) == today
            ).count()
            
            return jsonify({
                'total_patients': total_patients,
                'total_doctors': total_doctors,
                'total_medicines': total_medicines,
                'today_appointments': today_appointments
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/dashboard/department_distribution')
    @login_required
    def department_distribution():
        try:
            # 优化查询：使用子查询避免N+1问题
            dept_stats = db.session.query(
                Doctor.department,
                db.func.count(Appointment.id).label('count')
            ).join(Appointment, Doctor.id == Appointment.doctor_id)\
             .group_by(Doctor.department)\
             .all()
            
            if not dept_stats:
                # 如果没有数据，返回默认数据
                dept_stats = [
                    ('内科', 0),
                    ('外科', 0),
                    ('儿科', 0),
                    ('妇科', 0),
                    ('眼科', 0),
                    ('口腔科', 0)
                ]
            
            labels = [dept[0] for dept in dept_stats]
            values = [dept[1] for dept in dept_stats]
            
            fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
            fig.update_layout(
                title='就诊科室分布',
                height=400
            )
            
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/dashboard/medicine_top10')
    @login_required
    def medicine_top10():
        try:
            # 优化查询：使用LEFT JOIN确保包含所有药品
            medicine_stats = db.session.query(
                Medicine.name,
                db.func.coalesce(db.func.sum(Prescription.quantity), 0).label('total_sold')
            ).outerjoin(Prescription, Medicine.id == Prescription.medicine_id)\
             .group_by(Medicine.id, Medicine.name)\
             .order_by(db.func.coalesce(db.func.sum(Prescription.quantity), 0).desc())\
             .limit(10)\
             .all()
            
            if not medicine_stats:
                # 如果没有数据，返回默认数据
                medicine_stats = [
                    ('阿司匹林', 0),
                    ('布洛芬', 0),
                    ('感冒灵颗粒', 0),
                    ('板蓝根颗粒', 0),
                    ('维生素C片', 0)
                ]
            
            names = [med[0] for med in medicine_stats]
            sales = [med[1] for med in medicine_stats]
            
            fig = go.Figure(data=[go.Bar(x=names, y=sales)])
            fig.update_layout(
                title='药品销量TOP10',
                xaxis_title='药品名称',
                yaxis_title='销量',
                height=400
            )
            
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/search/appointments')
    @login_required
    def search_appointments():
        patient_name = request.args.get('patient_name', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        query = Appointment.query.join(Patient)
        
        if patient_name:
            query = query.filter(Patient.name.like(f'%{patient_name}%'))
        if start_date:
            query = query.filter(Appointment.date >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(Appointment.date <= datetime.strptime(end_date, '%Y-%m-%d'))
        
        appointments = query.all()
        return jsonify([{
            'id': apt.id,
            'patient_name': apt.patient.name,
            'doctor_name': apt.doctor.name,
            'department': apt.doctor.department,
            'date': apt.date.strftime('%Y-%m-%d %H:%M'),
            'status': apt.status
        } for apt in appointments])
    
    @app.route('/search/doctors')
    @login_required
    def search_doctors():
        department = request.args.get('department', '')
        date = request.args.get('date', '')
        name = request.args.get('name', '')

        query = Doctor.query

        if name:
            query = query.filter(Doctor.name.like(f'%{name}%'))
        if department:
            query = query.filter(Doctor.department == department)
        if date:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            appointments = Appointment.query.filter(
                db.func.date(Appointment.date) == date_obj.date()
            ).with_entities(Appointment.doctor_id).all()
            doctor_ids = [apt.doctor_id for apt in appointments]
            query = query.filter(Doctor.id.in_(doctor_ids))
        
        doctors = query.all()
        return jsonify([{
            'id': doc.id,
            'name': doc.name,
            'department': doc.department,
            'title': doc.title,
            'phone': doc.phone,
            'available': doc.available
        } for doc in doctors])
    
    @app.route('/search/medicines')
    @login_required
    def search_medicines():
        category = request.args.get('category', '')
        min_stock = request.args.get('min_stock', 0)
        
        query = Medicine.query
        
        if category:
            query = query.filter(Medicine.category == category)
        if min_stock:
            query = query.filter(Medicine.stock >= int(min_stock))
        
        medicines = query.all()
        return jsonify([{
            'id': med.id,
            'name': med.name,
            'category': med.category,
            'price': float(med.price),
            'stock': med.stock,
            'expiry_date': med.expiry_date,
            'manufacturer': med.manufacturer
        } for med in medicines])
    
    @app.route('/report/medicines')
    @login_required
    def report_medicines():
        try:
            generator = ReportGenerator()
            filepath = generator.generate_medicine_sales_report()
            filename = os.path.basename(filepath)
            print(f"报表已生成: {filepath}")
            return send_file(filepath, as_attachment=True, download_name=filename)
        except Exception as e:
            print(f"报表生成失败: {str(e)}")
            flash(f'报表生成失败: {str(e)}', 'error')
            return redirect(url_for('dashboard'))

    @app.route('/report/appointments')
    @login_required
    def report_appointments():
        try:
            generator = ReportGenerator()
            filepath = generator.generate_appointment_report()
            filename = os.path.basename(filepath)
            print(f"报表已生成: {filepath}")
            return send_file(filepath, as_attachment=True, download_name=filename)
        except Exception as e:
            print(f"报表生成失败: {str(e)}")
            flash(f'报表生成失败: {str(e)}', 'error')
            return redirect(url_for('dashboard'))

    @app.route('/report/patients')
    @login_required
    def report_patients():
        try:
            generator = ReportGenerator()
            filepath = generator.generate_patient_report()
            filename = os.path.basename(filepath)
            print(f"报表已生成: {filepath}")
            return send_file(filepath, as_attachment=True, download_name=filename)
        except Exception as e:
            print(f"报表生成失败: {str(e)}")
            flash(f'报表生成失败: {str(e)}', 'error')
            return redirect(url_for('dashboard'))
    
    @app.route('/report/list')
    @login_required
    def report_list():
        """查看报表文件列表"""
        try:
            reports_folder = 'reports'
            if not os.path.exists(reports_folder):
                return jsonify({'files': [], 'message': '报表文件夹不存在'})
            
            files = []
            for filename in os.listdir(reports_folder):
                if filename.endswith('.xlsx'):
                    filepath = os.path.join(reports_folder, filename)
                    file_stat = os.stat(filepath)
                    files.append({
                        'name': filename,
                        'size': file_stat.st_size,
                        'created': datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                        'path': filepath
                    })
            
            # 按创建时间排序
            files.sort(key=lambda x: x['created'], reverse=True)
            return jsonify({'files': files})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/report/download/<filename>')
    @login_required
    def report_download(filename):
        """下载报表文件"""
        try:
            reports_folder = 'reports'
            filepath = os.path.join(reports_folder, filename)
            
            if not os.path.exists(filepath):
                flash('文件不存在', 'error')
                return redirect(url_for('dashboard'))
            
            return send_file(filepath, as_attachment=True, download_name=filename)
        except Exception as e:
            flash(f'下载失败: {str(e)}', 'error')
            return redirect(url_for('dashboard'))
    
    @app.route('/diagrams/generate')
    @login_required
    def generate_diagrams():
        """生成系统设计图"""
        try:
            results = []
            
            # 生成ER图
            result = generate_er_diagram()
            results.append(('ER图', result))
            
            # 生成预约流程活动图
            result = generate_appointment_activity()
            results.append(('预约流程活动图', result))
            
            # 生成处方开具顺序图
            result = generate_prescription_sequence()
            results.append(('处方开具顺序图', result))
            
            # 生成系统架构图
            result = generate_system_architecture()
            results.append(('系统架构图', result))
            
            # 检查生成的文件
            generated_files = []
            for file in os.listdir('.'):
                if file.endswith('.png') and any(keyword in file.lower() for keyword in ['er_diagram', 'appointment_activity', 'prescription_sequence', 'system_architecture']):
                    generated_files.append(file)
            
            return jsonify({
                'success': True,
                'results': results,
                'files': generated_files
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/diagrams/download/<filename>')
    @login_required
    def download_diagram(filename):
        """下载图表文件"""
        try:
            if not os.path.exists(filename):
                flash('文件不存在', 'error')
                return redirect(url_for('dashboard'))
            
            return send_file(filename, as_attachment=True, download_name=filename)
        except Exception as e:
            flash(f'下载失败: {str(e)}', 'error')
            return redirect(url_for('dashboard'))
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500 