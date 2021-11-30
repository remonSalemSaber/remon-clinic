
from odoo import api, fields, models, _



class AccountMove(models.Model):
    _inherit = 'account.move'

    physician_id = fields.Many2one('res.partner', string='Physician', readonly=True, states={'draft': [('readonly', False)]}) 
    
class KSCMixin(models.AbstractModel):
    _name = "ksc.mixin"
    _description = "KSC Mixin"

    def ksc_prepare_invocie_data(self, partner, product_data, inv_data):
        fiscal_position_id = self.env['account.fiscal.position'].get_fiscal_position(partner.id)
        data = {
            'partner_id': partner.id,
            'move_type': inv_data.get('move_type','out_invoice'),
            'ref': self.name,
            'invoice_origin': self.name,
            'currency_id': self.env.user.company_id.currency_id.id,
            'invoice_line_ids': self.ksc_get_invoice_lines(product_data, partner, inv_data, fiscal_position_id),
            'fiscal_position_id': fiscal_position_id,
        }
        return data

    @api.model
    def ksc_create_invoice(self, partner, product_data=[], inv_data={}):
        inv_data = self.ksc_prepare_invocie_data(partner, product_data, inv_data)
        invoice = self.env['account.move'].create(inv_data)
        invoice._onchange_partner_id()
        for line in invoice.invoice_line_ids:
            line._get_computed_name()
            line._get_computed_account()
            line._get_computed_taxes()
            line._get_computed_uom()

        invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True,recompute_tax_base_amount=True)
        return invoice

    @api.model
    def ksc_get_invoice_lines(self, product_data, partner, inv_data, fiscal_position_id):
        lines = []
        for data in product_data:
            product = data.get('product_id')
            if product:
                ksc_pricelist_id = self.env.context.get('ksc_pricelist_id')
                if not data.get('price_unit') and (partner.property_product_pricelist or ksc_pricelist_id):
                    pricelist_id = ksc_pricelist_id or partner.property_product_pricelist.id
                    price = product.with_context(pricelist=pricelist_id).price
                else:
                    price = data.get('price_unit', product.list_price)
                if inv_data.get('move_type','out_invoice') in ['out_invoice','out_refund']:
                    tax_ids = product.taxes_id
                else:
                    tax_ids = product.supplier_taxes_id

                if tax_ids:
                    if fiscal_position_id:
                        tax_ids = fiscal_position_id.map_tax(tax_ids._origin, partner=partner)
                    tax_ids = [(6, 0, tax_ids.ids)]

                lines.append((0, 0, {
                    'name': data.get('name',product.name),
                    'product_id': product.id,
                    'price_unit': price,
                    'quantity': data.get('quantity',1.0),
                    'discount': data.get('discount',0.0),
                    'product_uom_id': data.get('product_uom_id',product.uom_id.id),
                    'analytic_account_id': data.get('account_analytic_id',False),
                    'tax_ids': tax_ids,
                }))
            else:
                lines.append((0, 0, {
                    'name': data.get('name'),
                    'display_type': 'line_section',
                }))
                
        return lines

    def ksc_action_view_invoice(self, invoices):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.id
        elif self.env.context.get('ksc_open_blank_list'):
            #Allow to open invoices
            action['domain'] = [('id', 'in', invoices.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        context = {
            'default_move_type': 'out_invoice',
        }
        action['context'] = context
        return action

    @api.model
    def assign_given_lots(self, move, lot_id, lot_qty):
        MoveLine = self.env['stock.move.line']
        move_line_id = MoveLine.search([('move_id', '=', move.id),('lot_id','=',False)],limit=1)
        if move_line_id:
            move_line_id.lot_id = lot_id
            move_line_id.quantity_done = lot_qty

    def consume_material(self, source_location_id, dest_location_id, product_data):
        product = product_data['product']
        move = self.env['stock.move'].create({
            'name' : product.name,
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': product_data.get('qty',1.0),
            'date': product_data.get('date',fields.datetime.now()),
            'location_id': source_location_id,
            'location_dest_id': dest_location_id,
            'state': 'draft',
            'origin': self.name,
            'quantity_done': product_data.get('qty',1.0),
        })
        move._action_confirm()
        move._action_assign()
        if product_data.get('lot_id', False):
            lot_id = product_data.get('lot_id')
            lot_qty = product_data.get('qty',1.0)
            self.assign_given_lots(move, lot_id, lot_qty)
        if move.state == 'assigned':
            move._action_done()
        return move

