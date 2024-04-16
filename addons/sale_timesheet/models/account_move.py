#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict

fromflectraimportapi,fields,models,_
fromflectra.osvimportexpression


classAccountMove(models.Model):
    _inherit="account.move"

    timesheet_ids=fields.One2many('account.analytic.line','timesheet_invoice_id',string='Timesheets',readonly=True,copy=False)
    timesheet_count=fields.Integer("Numberoftimesheets",compute='_compute_timesheet_count')

    @api.depends('timesheet_ids')
    def_compute_timesheet_count(self):
        timesheet_data=self.env['account.analytic.line'].read_group([('timesheet_invoice_id','in',self.ids)],['timesheet_invoice_id'],['timesheet_invoice_id'])
        mapped_data=dict([(t['timesheet_invoice_id'][0],t['timesheet_invoice_id_count'])fortintimesheet_data])
        forinvoiceinself:
            invoice.timesheet_count=mapped_data.get(invoice.id,0)

    defaction_view_timesheet(self):
        self.ensure_one()
        return{
            'type':'ir.actions.act_window',
            'name':_('Timesheets'),
            'domain':[('project_id','!=',False)],
            'res_model':'account.analytic.line',
            'view_id':False,
            'view_mode':'tree,form',
            'help':_("""
                <pclass="o_view_nocontent_smiling_face">
                    Recordtimesheets
                </p><p>
                    Youcanregisterandtrackyourworkingshoursbyprojectevery
                    day.Everytimespentonaprojectwillbecomeacostandcanbere-invoicedto
                    customersifrequired.
                </p>
            """),
            'limit':80,
            'context':{
                'default_project_id':self.id,
                'search_default_project_id':[self.id]
            }
        }

    def_link_timesheets_to_invoice(self,start_date=None,end_date=None):
        """Searchtimesheetsfromgivenperiodandlinkthistimesheetstotheinvoice

            Whenwecreateaninvoicefromasaleorder,weneedto
            linkthetimesheetsinthissaleordertotheinvoice.
            Then,wecanknowwhichtimesheetsareinvoicedinthesaleorder.
            :paramstart_date:thestartdateoftheperiod
            :paramend_date:theenddateoftheperiod
        """
        forlineinself.filtered(lambdai:i.move_type=='out_invoice'andi.state=='draft').invoice_line_ids:
            sale_line_delivery=line.sale_line_ids.filtered(lambdasol:sol.product_id.invoice_policy=='delivery'andsol.product_id.service_type=='timesheet')
            ifsale_line_delivery:
                domain=line._timesheet_domain_get_invoiced_lines(sale_line_delivery)
                ifstart_date:
                    domain=expression.AND([domain,[('date','>=',start_date)]])
                ifend_date:
                    domain=expression.AND([domain,[('date','<=',end_date)]])
                timesheets=self.env['account.analytic.line'].sudo().search(domain)
                timesheets.write({'timesheet_invoice_id':line.move_id.id})


classAccountMoveLine(models.Model):
    _inherit='account.move.line'

    @api.model
    def_timesheet_domain_get_invoiced_lines(self,sale_line_delivery):
        """Getthedomainforthetimesheettolinktothecreatedinvoice
            :paramsale_line_delivery:recordsetofsale.order.linetoinvoice
            :returnanormalizeddomain
        """
        return[
            ('so_line','in',sale_line_delivery.ids),
            ('project_id','!=',False),
            '|','|',
                ('timesheet_invoice_id','=',False),
                ('timesheet_invoice_id.state','=','cancel'),
                ('timesheet_invoice_id.payment_state','=','reversed')
        ]

    defunlink(self):
        move_line_read_group=self.env['account.move.line'].search_read([
            ('move_id.move_type','=','out_invoice'),
            ('move_id.state','=','draft'),
            ('sale_line_ids.product_id.invoice_policy','=','delivery'),
            ('sale_line_ids.product_id.service_type','=','timesheet'),
            ('id','in',self.ids)],
            ['move_id','sale_line_ids'])

        sale_line_ids_per_move=defaultdict(lambda:self.env['sale.order.line'])
        formove_lineinmove_line_read_group:
            sale_line_ids_per_move[move_line['move_id'][0]]+=self.env['sale.order.line'].browse(move_line['sale_line_ids'])

        timesheet_read_group=self.sudo().env['account.analytic.line'].read_group([
            ('timesheet_invoice_id.move_type','=','out_invoice'),
            ('timesheet_invoice_id.state','=','draft'),
            ('timesheet_invoice_id','in',self.move_id.ids)],
            ['timesheet_invoice_id','so_line','ids:array_agg(id)'],
            ['timesheet_invoice_id','so_line'],
            lazy=False)

        timesheet_ids=[]
        fortimesheetintimesheet_read_group:
            move_id=timesheet['timesheet_invoice_id'][0]
            iftimesheet['so_line'][0]insale_line_ids_per_move[move_id].ids:
                timesheet_ids+=timesheet['ids']

        self.sudo().env['account.analytic.line'].browse(timesheet_ids).write({'timesheet_invoice_id':False})
        returnsuper().unlink()
