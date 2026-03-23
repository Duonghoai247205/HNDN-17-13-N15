# -*- coding: utf-8 -*-
from odoo import fields, models


class CongViecTag(models.Model):
    _name = 'cong_viec.tag'
    _description = 'Nhãn Công Việc'
    _order = 'name'

    name = fields.Char(string='Tên Nhãn', required=True, translate=True)
    color = fields.Integer(string='Màu Sắc', default=0)
    active = fields.Boolean(string='Đang Hoạt Động', default=True)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Tên nhãn đã tồn tại!'),
    ]
