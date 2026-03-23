# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date


class CongViec(models.Model):
    """
    Model quản lý công việc cụ thể.
    - Tích hợp với module Nhân Sự (hr): giao việc cho nhân viên, phòng ban tự động
    - Tích hợp với module Dự Án: trường project_id được thêm bởi quan_ly_du_an
    """
    _name = 'cong_viec.task'
    _description = 'Công Việc'
    _order = 'date_deadline asc, priority desc, name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ==================== Thông tin cơ bản ====================
    name = fields.Char(
        string='Tên Công Việc',
        required=True,
        tracking=True,
        help='Tên mô tả ngắn gọn của công việc'
    )
    code = fields.Char(
        string='Mã Công Việc',
        required=True,
        copy=False,
        tracking=True,
        default='/'
    )
    description = fields.Text(
        string='Mô Tả Chi Tiết',
        help='Mô tả đầy đủ nội dung và yêu cầu công việc'
    )
    active = fields.Boolean(string='Đang Hoạt Động', default=True)
    color = fields.Integer(string='Màu Sắc', default=0)
    sequence = fields.Integer(string='Thứ Tự', default=10)

    # ==================== Trạng thái ====================
    state = fields.Selection([
        ('todo', 'Cần Làm'),
        ('in_progress', 'Đang Thực Hiện'),
        ('review', 'Đang Kiểm Tra'),
        ('done', 'Hoàn Thành'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='todo', tracking=True, required=True,
       group_expand='_expand_states')

    priority = fields.Selection([
        ('0', 'Thấp'),
        ('1', 'Bình Thường'),
        ('2', 'Cao'),
        ('3', 'Khẩn Cấp'),
    ], string='Độ Ưu Tiên', default='1', tracking=True)

    tag_ids = fields.Many2many(
        'cong_viec.tag',
        string='Nhãn',
        help='Nhãn phân loại công việc'
    )

    # ==================== Thời gian ====================
    date_start = fields.Date(
        string='Ngày Bắt Đầu',
        default=fields.Date.today,
        tracking=True
    )
    date_deadline = fields.Date(
        string='Hạn Hoàn Thành',
        tracking=True
    )
    date_done = fields.Datetime(
        string='Ngày Hoàn Thành Thực Tế',
        readonly=True
    )
    duration_planned = fields.Float(
        string='Thời Gian Dự Kiến (giờ)',
        default=0.0,
        help='Số giờ công dự kiến để hoàn thành'
    )
    duration_actual = fields.Float(
        string='Thời Gian Thực Tế (giờ)',
        default=0.0,
        tracking=True,
        help='Số giờ công thực tế đã thực hiện'
    )
    is_overdue = fields.Boolean(
        string='Quá Hạn',
        compute='_compute_is_overdue',
        store=True
    )

    # ==================== Nhân sự (tích hợp module HR) ====================
    employee_id = fields.Many2one(
        'nhan_vien',
        string='Nhân Viên Phụ Trách',
        required=True,
        tracking=True,
        help='Nhân viên chịu trách nhiệm thực hiện công việc'
    )
    reviewer_id = fields.Many2one(
        'nhan_vien',
        string='Người Kiểm Tra',
        tracking=True,
        help='Nhân viên kiểm tra và nghiệm thu kết quả'
    )
    department_id = fields.Many2one(
        'phong_ban',
        string='Phòng Ban',
        related='employee_id.phong_ban_id',
        store=True,
        readonly=True
    )
    job_id = fields.Many2one(
        'chuc_vu',
        string='Chức Vụ',
        related='employee_id.chuc_vu_id',
        store=True,
        readonly=True
    )

    # ==================== Kết quả & đánh giá KPI ====================
    result = fields.Text(
        string='Kết Quả Thực Hiện',
        help='Mô tả kết quả và sản phẩm bàn giao của công việc'
    )
    performance_score = fields.Selection([
        ('1', 'Không Đạt (< 50%)'),
        ('2', 'Cần Cải Thiện (50-69%)'),
        ('3', 'Đạt (70-84%)'),
        ('4', 'Tốt (85-94%)'),
        ('5', 'Xuất Sắc (95-100%)'),
    ], string='Đánh Giá Hiệu Quả', tracking=True,
       help='Đánh giá hiệu quả hoàn thành công việc - dùng để đánh giá KPI nhân sự')
    notes = fields.Html(string='Ghi Chú', help='Ghi chú bổ sung')
    progress = fields.Integer(
        string='Tiến Độ (%)',
        default=0,
        tracking=True,
        help='Phần trăm hoàn thành công việc (0-100)'
    )

    # ==================== SQL Constraints ====================
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Mã công việc đã tồn tại!'),
        ('progress_range', 'check(progress >= 0 AND progress <= 100)',
         'Tiến độ phải từ 0 đến 100!'),
    ]

    # ==================== Compute Methods ====================
    @api.depends('date_deadline', 'state')
    def _compute_is_overdue(self):
        today = date.today()
        for rec in self:
            rec.is_overdue = (
                rec.date_deadline and
                rec.date_deadline < today and
                rec.state not in ('done', 'cancelled')
            )

    @api.model
    def _expand_states(self, states, domain, order):
        return [key for key, _ in self._fields['state'].selection]

    # ==================== Validation ====================
    @api.constrains('date_start', 'date_deadline')
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_deadline and rec.date_deadline < rec.date_start:
                raise ValidationError(_('Hạn hoàn thành phải sau ngày bắt đầu!'))

    # ==================== Auto-generate code & AI History ====================
    @api.model
    def create(self, vals):
        if not vals.get('code') or vals.get('code') == '/':
            vals['code'] = self.env['ir.sequence'].next_by_code('cong_viec.task') or '/'
            
        record = super().create(vals)
        
        # Nếu vừa tạo mới đã để trạng thái 'done' (ít khi xảy ra nhưng có thể)
        if record.state == 'done' and record.employee_id:
            phong_ban_id = record.employee_id.phong_ban_id.id
            if not phong_ban_id:
                fallback_pb = self.env['phong_ban'].search([], limit=1)
                phong_ban_id = fallback_pb.id if fallback_pb else False
            
            if phong_ban_id:
                self.env['lich_su_lam_viec'].create({
                    'ten_cong_viec': record.name,
                    'nhan_vien_id': record.employee_id.id,
                    'ma_phong_ban': phong_ban_id,
                })
                
        return record

    def write(self, vals):
        # Lưu trữ danh sách các task CHƯA 'done' trước khi write
        tasks_not_done = self.filtered(lambda t: t.state != 'done')
        
        res = super(CongViec, self).write(vals)
        
        if vals.get('state') == 'done':
            # Chỉ ghi nhận lịch sử cho những task từ trạng thái khác chuyển sang 'done'
            for rec in tasks_not_done:
                if rec.employee_id:
                    phong_ban_id = rec.employee_id.phong_ban_id.id
                    if not phong_ban_id:
                        fallback_pb = self.env['phong_ban'].search([], limit=1)
                        phong_ban_id = fallback_pb.id if fallback_pb else False
                        
                    if phong_ban_id:
                        self.env['lich_su_lam_viec'].create({
                            'ten_cong_viec': rec.name,
                            'nhan_vien_id': rec.employee_id.id,
                            'ma_phong_ban': phong_ban_id,
                        })
        return res

    # ==================== State Transitions ====================
    def action_start(self):
        for rec in self:
            if rec.state == 'todo':
                rec.write({'state': 'in_progress', 'progress': 10})

    def action_review(self):
        for rec in self:
            if rec.state == 'in_progress':
                rec.write({'state': 'review', 'progress': 90})

    def action_done(self):
        for rec in self:
            if rec.state in ('in_progress', 'review'):
                rec.write({
                    'state': 'done',
                    'progress': 100,
                    'date_done': fields.Datetime.now(),
                })

    def action_cancel(self):
        for rec in self:
            if rec.state not in ('done',):
                rec.write({'state': 'cancelled'})

    def action_reset_todo(self):
        for rec in self:
            if rec.state == 'cancelled':
                rec.write({'state': 'todo', 'progress': 0, 'date_done': False})

    # ==================== Name Get ====================
    def name_get(self):
        result = []
        for rec in self:
            name = '[%s] %s' % (rec.code, rec.name) if rec.code and rec.code != '/' else rec.name
            result.append((rec.id, name))
        return result
