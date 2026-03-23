# -*- coding: utf-8 -*-
{
    'name': 'Quản lý Công việc',
    'version': '1.0.0',
    'category': 'Project Management',
    'sequence': 11,
    'summary': 'Giao việc cho nhân viên, theo dõi tiến độ và đánh giá hiệu quả nhân sự',
    'description': """
        Module Quản lý Công việc
        ========================
        Module này cho phép:
        - Tạo và giao công việc cho nhân viên (tích hợp module Nhân sự)
        - Theo dõi tiến độ thực hiện từng công việc theo luồng 5 bước
        - Quản lý thời hạn và cảnh báo công việc quá hạn
        - Đánh giá hiệu quả hoàn thành công việc (performance_score)
        - Phân loại công việc bằng nhãn
        - Xem báo cáo hiệu quả nhân sự từ kết quả công việc

        Ghi chú: Trường Dự Án (project_id) sẽ được bổ sung khi cài
        thêm module quan_ly_du_an.

        Phụ thuộc:
        - hr (Quản lý Nhân sự): lấy danh sách nhân viên, phòng ban
    """,
    'author': 'Nhóm 7 - TTDN',
    'depends': [
        'base',
        'mail',
        'nhan_su',
    ],
    'data': [
        'security/cong_viec_security.xml',
        'security/ir.model.access.csv',
        'data/cong_viec_data.xml',
        'views/cong_viec_views.xml',
        'views/hr_employee_views_extend.xml',
        'report/cong_viec_report.xml',
        'views/cong_viec_menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
