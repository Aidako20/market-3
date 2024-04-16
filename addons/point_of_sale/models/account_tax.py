#-*-coding:utf-8-*-

fromflectraimport_,api,models
fromflectra.exceptionsimportUserError
fromflectra.toolsimportsplit_every


classAccountTax(models.Model):
    _inherit='account.tax'

    defwrite(self,vals):
        forbidden_fields={
            'amount_type','amount','type_tax_use','tax_group_id','price_include',
            'include_base_amount'
        }
        ifforbidden_fields&set(vals.keys()):
            lines=self.env['pos.order.line'].sudo().search([
                ('order_id.session_id.state','!=','closed')
            ])
            self_ids=set(self.ids)
            forlines_chunkinmap(self.env['pos.order.line'].sudo().browse,split_every(100000,lines.ids)):
                ifany(tidinself_idsfortsinlines_chunk.read(['tax_ids'])fortidints['tax_ids']):
                    raiseUserError(_(
                        'ItisforbiddentomodifyataxusedinaPOSordernotposted.'
                        'YoumustclosethePOSsessionsbeforemodifyingthetax.'
                    ))
                lines_chunk.invalidate_cache(['tax_ids'],lines_chunk.ids)
        returnsuper(AccountTax,self).write(vals)

    defget_real_tax_amount(self):
        tax_list=[]
        fortaxinself:
            tax_repartition_lines=tax.invoice_repartition_line_ids.filtered(lambdax:x.repartition_type=='tax')
            total_factor=sum(tax_repartition_lines.mapped('factor'))
            real_amount=tax.amount*total_factor
            tax_list.append({'id':tax.id,'amount':real_amount})
        returntax_list
