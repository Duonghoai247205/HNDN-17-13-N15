from odoo import models, fields, api
from datetime import date


class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'ho_ten'
 
    nhan_vien_id = fields.Char("Mã nhân viên", required=True)
    ho_ten = fields.Char("Họ và tên", compute='_tinh_ho_va_ten', store=True) #Luu vao 
    
    # projects_ids = fields.Many2many('projects', string='Dự án')
    # projects_id = fields.Many2one('projects', string='Quản lý dự án')
    # taskss_ids = fields.Many2many('taskss', string='Công việc được giao')

    ngay_sinh = fields.Date("Ngày sinh")
    gioi_tinh = fields.Selection(
        selection=[
            ('nam', 'Nam'),
            ('nu', 'Nữ'),
            ('khac', "Khác"),
        ],
    string="Giới tính"
    )
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    # salary = fields.Char(string="Mức lương", help="Mức lương của nhân viên")
    image = fields.Binary("Ảnh nhân viên")
    
    lich_su_lam_viec_ids = fields.One2many('lich_su_lam_viec', inverse_name='nhan_vien_id', string='Danh sách LSLV')
    
    # chuc_vu_ids = fields.One2many('chuc_vu', inverse_name='nhan_vien_id', string='Danh sách CV')
    chuc_vu_id = fields.Many2one('chuc_vu', string='Chức vụ')
    phong_ban_id = fields.Many2one('phong_ban', string='Phòng ban')


    ho_ten_dem = fields.Char("Họ tên đệm")
    ten = fields.Char("Tên")
    
    # AI Skills Profiling
    ky_nang = fields.Text(string="Kỹ năng chính", help="Nhập các kỹ năng của bản thân (Ví dụ: Python, AI, Giao tiếp...)")

    @api.depends("ho_ten_dem", "ten")
    def _tinh_ho_va_ten(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                record.ho_ten = record.ho_ten_dem + ' ' + record.ten

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.nhan_vien_id} - {record.ho_ten}"
            result.append((record.id, name))
        return result
    