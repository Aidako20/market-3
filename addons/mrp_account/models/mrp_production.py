#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromastimportliteral_eval

fromflectraimportapi,fields,models
fromflectra.toolsimportfloat_is_zero


classMrpProductionWorkcenterLineTime(models.Model):
    _inherit='mrp.workcenter.productivity'

    cost_already_recorded=fields.Boolean('CostRecorded',help="Technicalfieldautomaticallycheckedwhenaongoingproductionpostsjournalentriesforitscosts.Thisway,wecanrecordoneproduction'scostmultipletimesandonlyconsidernewentriesintheworkcenterstimelines.")


classMrpProduction(models.Model):
    _inherit='mrp.production'

    extra_cost=fields.Float(copy=False,help='Extracostperproducedunit')
    show_valuation=fields.Boolean(compute='_compute_show_valuation')

    def_compute_show_valuation(self):
        fororderinself:
            order.show_valuation=any(m.state=='done'forminorder.move_finished_ids)

    def_cal_price(self,consumed_moves):
        """Setapriceunitonthefinishedmoveaccordingto`consumed_moves`.
        """
        super(MrpProduction,self)._cal_price(consumed_moves)
        work_center_cost=0
        finished_move=self.move_finished_ids.filtered(lambdax:x.product_id==self.product_idandx.statenotin('done','cancel')andx.quantity_done>0)
        iffinished_move:
            finished_move.ensure_one()
            forwork_orderinself.workorder_ids:
                time_lines=work_order.time_ids.filtered(lambdax:x.date_endandnotx.cost_already_recorded)
                duration=sum(time_lines.mapped('duration'))
                time_lines.write({'cost_already_recorded':True})
                work_center_cost+=(duration/60.0)*work_order.workcenter_id.costs_hour
            iffinished_move.product_id.cost_methodin('fifo','average'):
                qty_done=finished_move.product_uom._compute_quantity(finished_move.quantity_done,finished_move.product_id.uom_id)
                extra_cost=self.extra_cost*qty_done
                finished_move.price_unit=(sum([-m.stock_valuation_layer_ids.valueforminconsumed_moves.sudo()])+work_center_cost+extra_cost)/qty_done
        returnTrue

    def_prepare_wc_analytic_line(self,wc_line):
        wc=wc_line.workcenter_id
        hours=wc_line.duration/60.0
        value=hours*wc.costs_hour
        account=wc.costs_hour_account_id.id
        return{
            'name':wc_line.name+'(H)',
            'amount':-value,
            'account_id':account,
            'ref':wc.code,
            'unit_amount':hours,
            'company_id':self.company_id.id,
        }

    def_costs_generate(self):
        """Calculatestotalcostsattheendoftheproduction.
        """
        self.ensure_one()
        AccountAnalyticLine=self.env['account.analytic.line'].sudo()
        forwc_lineinself.workorder_ids.filtered('workcenter_id.costs_hour_account_id'):
            vals=self._prepare_wc_analytic_line(wc_line)
            precision_rounding=(wc_line.workcenter_id.costs_hour_account_id.currency_idorself.company_id.currency_id).rounding
            ifnotfloat_is_zero(vals.get('amount',0.0),precision_rounding=precision_rounding):
                #weuseSUPERUSER_IDaswedonotguaranteeanmrpuser
                #hasaccesstoaccountanalyticlinesbutstillshouldbe
                #abletoproduceorders
                AccountAnalyticLine.create(vals)

    def_get_backorder_mo_vals(self):
        res=super()._get_backorder_mo_vals()
        res['extra_cost']=self.extra_cost
        returnres

    defbutton_mark_done(self):
        res=super(MrpProduction,self).button_mark_done()
        fororderinself:
            iforder.state!='done':
                continue
            order._costs_generate()
        returnres

    defaction_view_stock_valuation_layers(self):
        self.ensure_one()
        domain=[('id','in',(self.move_raw_ids+self.move_finished_ids+self.scrap_ids.move_id).stock_valuation_layer_ids.ids)]
        action=self.env["ir.actions.actions"]._for_xml_id("stock_account.stock_valuation_layer_action")
        context=literal_eval(action['context'])
        context.update(self.env.context)
        context['no_at_date']=True
        context['search_default_group_by_product_id']=False
        returndict(action,domain=domain,context=context)
