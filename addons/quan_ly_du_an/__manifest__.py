# -*- coding: utf-8 -*-
{
    'name': 'Quản lý Dự án',
    'version': '1.0.0',
    'category': 'Project Management',
    'sequence': 10,
    'summary': 'Quản lý toàn bộ dự án, phân công nhân sự và theo dõi tiến độ',
    'description': """
        Module Quản lý Dự án
        ====================
        Module này cho phép:
        - Tạo và quản lý các dự án
        - Phân công quản lý và thành viên dự án từ danh sách nhân viên (HR)
        - Theo dõi tiến độ dự án theo công việc
        - Quản lý ngân sách dự án
        - Tích hợp với module Quản lý Nhân sự và Quản lý Công việc

        Thứ tự cài đặt:
        1. hr (có sẵn)
        2. quan_ly_cong_viec
        3. quan_ly_du_an (module này)
    """,
    'author': 'Nhóm 7 - TTDN',
    'depends': [
        'base',
        'mail',
        'nhan_su',
        'quan_ly_cong_viec',
    ],
    'data': [
        'security/du_an_security.xml',
        'security/ir.model.access.csv',
        'data/du_an_data.xml',
        'views/du_an_views.xml',
        'views/cong_viec_form_extend.xml',
        'views/hr_employee_views_extend_du_an.xml',
        'views/ai_chatbot_views.xml',
        'report/du_an_report.xml',
        'views/du_an_menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
