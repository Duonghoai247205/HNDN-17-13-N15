# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class NhanVienThanhVien(models.Model):
    """
    Mở rộng model nhan_vien để thêm thống kê dự án.
    Đây là điểm tích hợp giữa module Nhân Sự và Dự Án:
    - Nhân viên có thể xem danh sách dự án tham gia và quản lý
    """
    _inherit = 'nhan_vien'

    # ==================== Liên kết ngược từ project.du_an ====================
    du_an_ids = fields.Many2many(
        'project.du_an',
        'project_du_an_employee_rel',
        'employee_id',
        'du_an_id',
        string='Dự Án Tham Gia',
        help='Các dự án mà nhân viên đang là thành viên'
    )
    du_an_quan_ly_ids = fields.One2many(
        'project.du_an',
        'manager_id',
        string='Dự Án Quản Lý',
        help='Các dự án mà nhân viên đang là quản lý'
    )
    du_an_count = fields.Integer(
        string='Số Dự Án',
        compute='_compute_du_an_count',
        help='Tổng số dự án tham gia và quản lý'
    )

    @api.depends('du_an_ids', 'du_an_quan_ly_ids')
    def _compute_du_an_count(self):
        for rec in self:
            all_projects = rec.du_an_ids | rec.du_an_quan_ly_ids
            rec.du_an_count = len(all_projects)

    def action_view_du_an(self):
        self.ensure_one()
        all_projects = self.du_an_ids | self.du_an_quan_ly_ids
        return {
            'type': 'ir.actions.act_window',
            'name': _('Dự Án của %s') % self.ho_ten,
            'res_model': 'project.du_an',
            'view_mode': 'list,form,kanban',
            'domain': [('id', 'in', all_projects.ids)],
        }

    # ==================== AI Recommendation System ====================
    def action_ai_recommend_tasks(self):
        self.ensure_one()
        if not self.ky_nang:
            return {
                'type': 'ir.actions.client', 
                'tag': 'display_notification', 
                'params': {'title': 'Chú ý', 'message': 'Vui lòng điền Kỹ năng của bạn ở tab Kỹ Năng & Kinh Nghiệm trước khi dùng AI!', 'type': 'warning'}
            }
            
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
        except ImportError:
            return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {'title': 'Lỗi', 'message': 'Chưa cài đặt scikit-learn trên Server!', 'type': 'danger'}}

        # Lấy tất cả Tasks đang 'todo'
        tasks = self.env['cong_viec.task'].search([('state', '=', 'todo')])
        if not tasks:
            return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {'title': 'Thông báo', 'message': 'Không có công việc nào đang cần làm trên hệ thống!', 'type': 'info'}}

        # Trích xuất dữ liệu Text
        task_docs = []
        for t in tasks:
            desc = t.description or ""
            task_docs.append(t.name + " " + desc)

        documents = [self.ky_nang] + task_docs
        
        # Chạy thuật toán AI TF-IDF
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(documents)
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        
        sim_scores = list(enumerate(cosine_sim[0]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Chỉ lấy những task có điểm > 0 (tối đa lấy 5 task)
        top_indices = [i[0] for i in sim_scores if i[1] > 0][:5]
        
        if not top_indices:
            return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {'title': 'AI Không tìm thấy', 'message': 'Không có công việc nào khớp với kỹ năng của bạn!', 'type': 'info'}}
            
        recommended_task_ids = [tasks[i].id for i in top_indices]

        return {
            'type': 'ir.actions.act_window',
            'name': _('AI Đề xuất Công việc cho %s') % self.ho_ten,
            'res_model': 'cong_viec.task',
            'view_mode': 'tree,form,kanban',
            'domain': [('id', 'in', recommended_task_ids)],
        }
        
    def action_ai_recommend_projects(self):
        self.ensure_one()
        if not self.ky_nang:
            return {
                'type': 'ir.actions.client', 
                'tag': 'display_notification', 
                'params': {'title': 'Chú ý', 'message': 'Vui lòng điền Kỹ năng của bạn ở tab Kỹ Năng & Kinh Nghiệm trước khi dùng AI!', 'type': 'warning'}
            }
            
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
        except ImportError:
            return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {'title': 'Lỗi', 'message': 'Chưa cài đặt scikit-learn trên Server!', 'type': 'danger'}}

        projects = self.env['project.du_an'].search([('state', 'in', ['draft', 'in_progress'])])
        if not projects:
            return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {'title': 'Thông báo', 'message': 'Không có dự án mở nào trên hệ thống!', 'type': 'info'}}

        proj_docs = []
        for p in projects:
            desc = p.description or ""
            proj_docs.append(p.name + " " + desc)

        documents = [self.ky_nang] + proj_docs
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(documents)
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        
        sim_scores = list(enumerate(cosine_sim[0]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        top_indices = [i[0] for i in sim_scores if i[1] > 0][:5]
        
        if not top_indices:
            return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {'title': 'AI Không tìm thấy', 'message': 'Không có dự án nào khớp với kỹ năng của bạn!', 'type': 'info'}}
            
        recommended_proj_ids = [projects[i].id for i in top_indices]

        return {
            'type': 'ir.actions.act_window',
            'name': _('AI Đề xuất Dự án cho %s') % self.ho_ten,
            'res_model': 'project.du_an',
            'view_mode': 'tree,form,kanban',
            'domain': [('id', 'in', recommended_proj_ids)],
        }
