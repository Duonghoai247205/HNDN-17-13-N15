# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CongViecExtDuAn(models.Model):
    """
    Mở rộng model cong_viec.task để thêm liên kết với Dự Án.
    Pattern này giống hr_timesheet mở rộng project.task.
    """
    _inherit = 'cong_viec.task'

    # ==================== Liên kết với Dự Án ====================
    project_id = fields.Many2one(
        'project.du_an',
        string='Dự Án',
        tracking=True,
        ondelete='restrict',
        help='Dự án mà công việc này thuộc về'
    )
    project_manager_id = fields.Many2one(
        'nhan_vien',
        string='Quản Lý Dự Án',
        related='project_id.manager_id',
        store=True,
        readonly=True
    )
    project_state = fields.Selection(
        related='project_id.state',
        string='Trạng Thái Dự Án',
        store=True,
        readonly=True
    )

    # ==================== Validation kết hợp 3 module ====================
    @api.constrains('project_id', 'employee_id')
    def _check_employee_in_project(self):
        """
        Đảm bảo nhân viên được giao việc phải là thành viên của dự án.
        Đây là điểm tích hợp quan trọng giữa 3 module:
        HR (nhân viên) ←→ Dự Án (thành viên) ←→ Công Việc (phân công)
        """
        for rec in self:
            if rec.project_id and rec.employee_id:
                project = rec.project_id
                # Tất cả nhân viên hợp lệ: thành viên + quản lý dự án
                all_members = project.member_ids | project.manager_id
                if rec.employee_id not in all_members:
                    raise ValidationError(
                        _('Nhân viên "%s" không thuộc dự án "%s"!\n'
                          'Vui lòng thêm nhân viên vào danh sách thành viên dự án trước.')
                        % (rec.employee_id.ho_ten, project.name)
                    )
