# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class NhanVienCongViec(models.Model):
    """
    Mở rộng model nhan_vien để thêm thống kê công việc.
    Đây là điểm tích hợp giữa module Nhân Sự và Công Việc:
    - Nhân viên có thể xem danh sách công việc được giao
    - Tính điểm hiệu quả trung bình (KPI) từ kết quả công việc
    """
    _inherit = 'nhan_vien'

    # ==================== Liên kết ngược từ cong_viec.task ====================
    task_ids = fields.One2many(
        'cong_viec.task',
        'employee_id',
        string='Công Việc Được Giao',
        help='Danh sách công việc đã được giao cho nhân viên'
    )
    task_count = fields.Integer(
        string='Tổng Công Việc',
        compute='_compute_task_stats',
        help='Tổng số công việc được giao'
    )
    task_done_count = fields.Integer(
        string='Công Việc Hoàn Thành',
        compute='_compute_task_stats',
        help='Số công việc đã hoàn thành'
    )
    performance_avg = fields.Float(
        string='Hiệu Quả TB (%)',
        compute='_compute_task_stats',
        help='Điểm hiệu quả trung bình tính từ các công việc đã hoàn thành và được đánh giá'
    )

    @api.depends('task_ids', 'task_ids.state', 'task_ids.performance_score')
    def _compute_task_stats(self):
        for rec in self:
            tasks = rec.task_ids
            rec.task_count = len(tasks)
            done_tasks = tasks.filtered(lambda t: t.state == 'done')
            rec.task_done_count = len(done_tasks)
            # Tính điểm hiệu quả trung bình từ CV hoàn thành và có đánh giá
            scored = done_tasks.filtered(lambda t: t.performance_score)
            if scored:
                total = sum(int(t.performance_score) for t in scored)
                rec.performance_avg = (total / len(scored)) * 20  # scale 1-5 → 0-100%
            else:
                rec.performance_avg = 0.0

    def action_view_tasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Công Việc của %s') % self.ho_ten,
            'res_model': 'cong_viec.task',
            'view_mode': 'list,form,kanban',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }
