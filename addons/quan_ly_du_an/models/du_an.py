# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date


class DuAn(models.Model):
    _name = 'project.du_an'
    _description = 'Dự Án'
    _order = 'date_start desc, name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ==================== Thông tin cơ bản ====================
    name = fields.Char(
        string='Tên Dự Án',
        required=True,
        tracking=True,
        help='Tên của dự án'
    )
    code = fields.Char(
        string='Mã Dự Án',
        required=True,
        copy=False,
        tracking=True,
        help='Mã định danh duy nhất của dự án'
    )
    description = fields.Text(
        string='Mô Tả',
        help='Mô tả chi tiết về dự án'
    )
    color = fields.Integer(string='Màu Sắc', default=0)
    active = fields.Boolean(string='Đang Hoạt Động', default=True)

    # ==================== Trạng thái ====================
    state = fields.Selection([
        ('draft', 'Khởi Thảo'),
        ('confirmed', 'Đã Xác Nhận'),
        ('in_progress', 'Đang Thực Hiện'),
        ('done', 'Hoàn Thành'),
        ('cancelled', 'Đã Hủy'),
    ], string='Trạng Thái', default='draft', tracking=True, required=True)

    priority = fields.Selection([
        ('0', 'Bình Thường'),
        ('1', 'Quan Trọng'),
        ('2', 'Rất Quan Trọng'),
        ('3', 'Khẩn Cấp'),
    ], string='Độ Ưu Tiên', default='0')

    # ==================== Thời gian ====================
    date_start = fields.Date(
        string='Ngày Bắt Đầu',
        required=True,
        tracking=True,
        default=fields.Date.today
    )
    date_end = fields.Date(
        string='Ngày Kết Thúc',
        required=True,
        tracking=True
    )
    duration = fields.Integer(
        string='Thời Gian (ngày)',
        compute='_compute_duration',
        store=True
    )
    is_overdue = fields.Boolean(
        string='Quá Hạn',
        compute='_compute_is_overdue',
        store=True
    )

    # ==================== Nhân sự (liên kết với module HR) ====================
    manager_id = fields.Many2one(
        'nhan_vien',
        string='Quản Lý Dự Án',
        required=True,
        tracking=True,
        help='Nhân viên quản lý chịu trách nhiệm dự án'
    )
    department_id = fields.Many2one(
        'phong_ban',
        string='Phòng Ban',
        related='manager_id.phong_ban_id',
        store=True,
        readonly=True,
        help='Phòng ban của quản lý dự án'
    )
    member_ids = fields.Many2many(
        'nhan_vien',
        'project_du_an_employee_rel',
        'du_an_id',
        'employee_id',
        string='Thành Viên Dự Án',
        help='Danh sách nhân viên tham gia dự án'
    )
    member_count = fields.Integer(
        string='Số Thành Viên',
        compute='_compute_member_count',
        store=True
    )

    # ==================== Ngân sách ====================
    budget = fields.Float(
        string='Ngân Sách (VNĐ)',
        default=0.0,
        help='Tổng ngân sách phân bổ cho dự án'
    )
    actual_cost = fields.Float(
        string='Chi Phí Thực Tế (VNĐ)',
        default=0.0,
        tracking=True
    )
    budget_remaining = fields.Float(
        string='Ngân Sách Còn Lại (VNĐ)',
        compute='_compute_budget_remaining',
        store=True
    )

    # ==================== Công việc (liên kết với module Công việc) ====================
    task_ids = fields.One2many(
        'cong_viec.task',
        'project_id',
        string='Danh Sách Công Việc'
    )
    task_count = fields.Integer(
        string='Tổng Công Việc',
        compute='_compute_task_stats',
        store=True
    )
    task_done_count = fields.Integer(
        string='Công Việc Hoàn Thành',
        compute='_compute_task_stats',
        store=True
    )
    completion_rate = fields.Float(
        string='Tỷ Lệ Hoàn Thành (%)',
        compute='_compute_task_stats',
        store=True
    )

    # ==================== Ghi chú ====================
    notes = fields.Html(string='Ghi Chú', help='Ghi chú thêm về dự án')

    # ==================== Constraints ====================
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Mã dự án đã tồn tại! Vui lòng nhập mã khác.'),
    ]

    # ==================== Compute Methods ====================
    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                delta = rec.date_end - rec.date_start
                rec.duration = delta.days
            else:
                rec.duration = 0

    @api.depends('date_end', 'state')
    def _compute_is_overdue(self):
        today = date.today()
        for rec in self:
            rec.is_overdue = (
                rec.date_end and
                rec.date_end < today and
                rec.state not in ('done', 'cancelled')
            )

    @api.depends('member_ids')
    def _compute_member_count(self):
        for rec in self:
            rec.member_count = len(rec.member_ids)

    @api.depends('budget', 'actual_cost')
    def _compute_budget_remaining(self):
        for rec in self:
            rec.budget_remaining = rec.budget - rec.actual_cost

    @api.depends('task_ids', 'task_ids.state')
    def _compute_task_stats(self):
        for rec in self:
            tasks = rec.task_ids
            rec.task_count = len(tasks)
            done_tasks = tasks.filtered(lambda t: t.state == 'done')
            rec.task_done_count = len(done_tasks)
            if rec.task_count > 0:
                rec.completion_rate = (rec.task_done_count / rec.task_count) * 100
            else:
                rec.completion_rate = 0.0

    # ==================== Validation ====================
    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_end < rec.date_start:
                raise ValidationError(_('Ngày kết thúc phải sau ngày bắt đầu!'))

    @api.constrains('budget')
    def _check_budget(self):
        for rec in self:
            if rec.budget < 0:
                raise ValidationError(_('Ngân sách không thể âm!'))

    # ==================== Auto-generate code ====================
    @api.model
    def create(self, vals):
        if not vals.get('code') or vals.get('code') == '/':
            vals['code'] = self.env['ir.sequence'].next_by_code('project.du_an') or '/'
        return super().create(vals)

    # ==================== Action Methods ====================
    def action_confirm(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'confirmed'

    def action_start(self):
        for rec in self:
            if rec.state == 'confirmed':
                rec.state = 'in_progress'

    def action_done(self):
        for rec in self:
            if rec.state == 'in_progress':
                rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            if rec.state not in ('done',):
                rec.state = 'cancelled'

    def action_reset_draft(self):
        for rec in self:
            if rec.state == 'cancelled':
                rec.state = 'draft'

    def action_view_tasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Công Việc - %s') % self.name,
            'res_model': 'cong_viec.task',
            'view_mode': 'list,form,kanban',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_members(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Thành Viên - %s') % self.name,
            'res_model': 'nhan_vien',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.member_ids.ids)],
        }

    # ==================== Name Get ====================
    def name_get(self):
        result = []
        for rec in self:
            name = '[%s] %s' % (rec.code, rec.name) if rec.code else rec.name
            result.append((rec.id, name))
        return result
