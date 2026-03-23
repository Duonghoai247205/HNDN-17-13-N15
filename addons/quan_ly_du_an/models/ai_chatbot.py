# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AIChat(models.Model):
    _name = 'project.ai.chat'
    _description = 'Phiên Chatbot AI'
    _order = 'create_date desc'

    name = fields.Char(string='Tên cuộc hội thoại', default='New Chat')
    user_id = fields.Many2one('res.users', string='Người dùng', default=lambda self: self.env.user, readonly=True)
    message_ids = fields.One2many('project.ai.chat.message', 'chat_id', string='Lịch sử tin nhắn')
    user_input = fields.Text(string='Nhập câu hỏi tại đây')

    def action_send_message(self):
        self.ensure_one()
        if not self.user_input:
            raise UserError('Vui lòng nhập câu hỏi.')

        api_key = self.env['ir.config_parameter'].sudo().get_param('gemini.api_key')
        if not api_key:
            raise UserError('Chưa cấu hình Gemini API Key. Vui lòng vào Cài Đặt Chung -> Technical -> System Parameters để tạo khóa "gemini.api_key" hoặc đưa trực tiếp vào mã nguồn.')

        try:
            import google.generativeai as genai
        except ImportError:
            raise UserError('Chưa cài đặt thư viện google-generativeai. Vui lòng chờ Server cập nhật hoặc chạy lệnh cài đặt pip.')

        genai.configure(api_key=api_key.strip())
        
        # Tự động quét danh sách Model mà API Key này hỗ trợ
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not available_models:
            raise UserError('LLM Error: API Key này không được cấp quyền sử dụng bất kỳ model sinh chữ (generateContent) nào của Gemini.')

        # Ưu tiên các model phổ biến, nếu không có thì lấy model đầu tiên mà API Key hỗ trợ
        target_model = available_models[0]
        for name in ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-1.5-pro', 'models/gemini-pro', 'models/gemini-1.0-pro']:
            if name in available_models:
                target_model = name
                break

        # Khởi tạo model dựa trên kết quả quét
        model = genai.GenerativeModel(target_model.replace('models/', ''))

        # Xây dựng lịch sử chat theo chuẩn Gemini API
        history = []
        for msg in self.message_ids.sorted('id'):
            role = 'user' if msg.role == 'user' else 'model'
            history.append({
                'role': role,
                'parts': [msg.content]
            })

        # Lưu tin nhắn của người dùng vào DB ngay lập tức
        self.env['project.ai.chat.message'].create({
            'chat_id': self.id,
            'role': 'user',
            'content': self.user_input
        })

        # Gửi Request lên Gemini Cloud
        try:
            chat = model.start_chat(history=history)
            response = chat.send_message(self.user_input)
            
            # Tự đặt tên cho phiên chat lấy từ câu đầu tiên (nếu là đoạn hội thoại chưa có tên)
            if self.name == 'New Chat':
                self.name = self.user_input[:40] + '...' if len(self.user_input) > 40 else self.user_input

            # Reset khung text
            self.user_input = False 
            
            # Lưu câu trả lời của AI vào DB
            self.env['project.ai.chat.message'].create({
                'chat_id': self.id,
                'role': 'model',
                'content': response.text
            })
        except Exception as e:
            raise UserError(f"Lỗi hệ thống khi gọi Gemini API: {str(e)}")


class AIChatMessage(models.Model):
    _name = 'project.ai.chat.message'
    _description = 'Tin nhắn Chatbot AI'
    _order = 'id asc'

    chat_id = fields.Many2one('project.ai.chat', string='Phiên Chat', required=True, ondelete='cascade')
    role = fields.Selection([('user', 'Bạn'), ('model', 'AI')], string='Người gửi', required=True)
    content = fields.Text(string='Nội dung', required=True)
