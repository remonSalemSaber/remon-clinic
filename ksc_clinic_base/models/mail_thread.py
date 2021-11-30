import json
from lxml import etree

from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _get_fields(self):
        return []
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(MailThread, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                         toolbar=toolbar, submenu=submenu)
        company_fields = self._get_fields()
        if view_type == 'calendar' and company_fields:
            company_domain = [('id', '=', self.env.user.company_id.id)]
            company_data = self.env['res.company'].search_read(domain=company_domain, fields=company_fields)
            company_data = company_data and company_data[0] or {}

            doc = etree.XML(result['arch'])
            for node in doc.xpath("//calendar"):
                node.set('company_data', json.dumps(company_data))
            result['arch'] = etree.tostring(doc)
        return result
