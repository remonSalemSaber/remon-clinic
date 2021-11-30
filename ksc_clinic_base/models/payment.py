from odoo import _, api, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Account Payment'

    domain_journal_ids = fields.Many2many('account.journal',compute='_compute_domain_journal_ids')
    
    @api.depends('amount','payment_type','journal_id')
    def _compute_domain_journal_ids(self):
        for rec in self:
            rec.domain_journal_ids = rec.get_journal_ids()

    def get_journal_domain(self):
        return [('type','in',['bank','cash'])]

    def get_journal_ids(self):
        domain = self.get_journal_domain()
        return self.env['account.journal'].search(domain)