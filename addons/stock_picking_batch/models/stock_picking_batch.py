#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.tools.float_utilsimportfloat_compare,float_is_zero,float_round

classStockPickingBatch(models.Model):
    _inherit=['mail.thread','mail.activity.mixin']
    _name="stock.picking.batch"
    _description="BatchTransfer"
    _order="namedesc"

    name=fields.Char(
        string='BatchTransfer',default='New',
        copy=False,required=True,readonly=True,
        help='Nameofthebatchtransfer')
    user_id=fields.Many2one(
        'res.users',string='Responsible',tracking=True,check_company=True,
        readonly=True,states={'draft':[('readonly',False)],'in_progress':[('readonly',False)]},
        help='Personresponsibleforthisbatchtransfer')
    company_id=fields.Many2one(
        'res.company',string="Company",required=True,readonly=True,
        index=True,default=lambdaself:self.env.company)
    picking_ids=fields.One2many(
        'stock.picking','batch_id',string='Transfers',readonly=True,
        domain="[('id','in',allowed_picking_ids)]",check_company=True,
        states={'draft':[('readonly',False)],'in_progress':[('readonly',False)]},
        help='Listoftransfersassociatedtothisbatch')
    show_check_availability=fields.Boolean(
        compute='_compute_move_ids',
        help='Technicalfieldusedtocomputewhetherthecheckavailabilitybuttonshouldbeshown.')
    allowed_picking_ids=fields.One2many('stock.picking',compute='_compute_allowed_picking_ids')
    move_ids=fields.One2many(
        'stock.move',string="Stockmoves",compute='_compute_move_ids')
    move_line_ids=fields.One2many(
        'stock.move.line',string='Stockmovelines',
        compute='_compute_move_ids',inverse='_set_move_line_ids',readonly=True,
        states={'draft':[('readonly',False)],'in_progress':[('readonly',False)]})
    state=fields.Selection([
        ('draft','Draft'),
        ('in_progress','Inprogress'),
        ('done','Done'),
        ('cancel','Cancelled')],default='draft',
        store=True,compute='_compute_state',
        copy=False,tracking=True,required=True,readonly=True)
    picking_type_id=fields.Many2one(
        'stock.picking.type','OperationType',check_company=True,copy=False,
        readonly=True,states={'draft':[('readonly',False)]})
    scheduled_date=fields.Datetime(
        'ScheduledDate',copy=False,store=True,readonly=False,compute="_compute_scheduled_date",
        states={'done':[('readonly',True)],'cancel':[('readonly',True)]},
        help="""Scheduleddateforthetransferstobeprocessed.
              -Ifmanuallysetthenscheduleddateforalltransfersinbatchwillautomaticallyupdatetothisdate.
              -Ifnotmanuallychangedandtransfersareadded/removed/updatedthenthiswillbetheirearliestscheduleddate
                butthisscheduleddatewillnotbesetforalltransfersinbatch.""")

    @api.depends('company_id','picking_type_id','state')
    def_compute_allowed_picking_ids(self):
        allowed_picking_states=['waiting','confirmed','assigned']
        cancelled_batchs=self.env['stock.picking.batch'].search_read(
            [('state','=','cancel')],['id']
        )
        cancelled_batch_ids=[batch['id']forbatchincancelled_batchs]

        forbatchinself:
            domain_states=list(allowed_picking_states)
            #Allowstoadddraftpickingsonlyifbatchisindraftaswell.
            ifbatch.state=='draft':
                domain_states.append('draft')
            domain=[
                ('company_id','=',batch.company_id.id),
                ('immediate_transfer','=',False),
                ('state','in',domain_states),
                '|',
                '|',
                ('batch_id','=',False),
                ('batch_id','=',batch.id),
                ('batch_id','in',cancelled_batch_ids),
            ]
            ifbatch.picking_type_id:
                domain+=[('picking_type_id','=',batch.picking_type_id.id)]
            batch.allowed_picking_ids=self.env['stock.picking'].search(domain)

    @api.depends('picking_ids','picking_ids.move_line_ids','picking_ids.move_lines','picking_ids.move_lines.state')
    def_compute_move_ids(self):
        forbatchinself:
            batch.move_ids=batch.picking_ids.move_lines
            batch.move_line_ids=batch.picking_ids.move_line_ids
            batch.show_check_availability=any(m.statenotin['assigned','done']forminbatch.move_ids)

    @api.depends('picking_ids','picking_ids.state')
    def_compute_state(self):
        batchs=self.filtered(lambdabatch:batch.statenotin['cancel','done'])
        forbatchinbatchs:
            ifnotbatch.picking_ids:
                continue
            #Cancelsautomaticallythebatchpickingifallitstransfersarecancelled.
            ifall(picking.state=='cancel'forpickinginbatch.picking_ids):
                batch.state='cancel'
            #Batchpickingismarkedasdoneifallitsnotcanceledtransfersaredone.
            elifall(picking.statein['cancel','done']forpickinginbatch.picking_ids):
                batch.state='done'

    @api.depends('picking_ids','picking_ids.scheduled_date')
    def_compute_scheduled_date(self):
        forrecinself:
            rec.scheduled_date=min(rec.picking_ids.filtered('scheduled_date').mapped('scheduled_date'),default=False)

    @api.onchange('scheduled_date')
    defonchange_scheduled_date(self):
        ifself.scheduled_date:
            self.picking_ids.scheduled_date=self.scheduled_date

    def_set_move_line_ids(self):
        new_move_lines=self[0].move_line_ids
        forpickinginself.picking_ids:
            old_move_lines=picking.move_line_ids
            picking.move_line_ids=new_move_lines.filtered(lambdaml:ml.picking_id.id==picking.id)
            move_lines_to_unlink=old_move_lines-new_move_lines
            ifmove_lines_to_unlink:
                move_lines_to_unlink.unlink()

    #-------------------------------------------------------------------------
    #CRUD
    #-------------------------------------------------------------------------
    @api.model
    defcreate(self,vals):
        ifvals.get('name','/')=='/':
            vals['name']=self.env['ir.sequence'].next_by_code('picking.batch')or'/'
        returnsuper().create(vals)

    defwrite(self,vals):
        res=super().write(vals)
        ifvals.get('picking_type_id'):
            self._sanity_check()
        ifvals.get('picking_ids'):
            batch_without_picking_type=self.filtered(lambdabatch:notbatch.picking_type_id)
            ifbatch_without_picking_type:
                picking=self.picking_idsandself.picking_ids[0]
                batch_without_picking_type.picking_type_id=picking.picking_type_id.id
        returnres

    defunlink(self):
        ifany(batch.state!='draft'forbatchinself):
            raiseUserError(_("Youcanonlydeletedraftbatchtransfers."))
        returnsuper().unlink()

    defonchange(self,values,field_name,field_onchange):
        """OverrideonchangetoNOTtoupdateallscheduled_dateonpickingswhen
        scheduled_dateonbatchisupdatedbythechangeofscheduled_dateonpickings.
        """
        result=super().onchange(values,field_name,field_onchange)
        iffield_name=='picking_ids'and'value'inresult:
            forlineinresult['value'].get('picking_ids',[]):
                ifline[0]<2and'scheduled_date'inline[2]:
                    delline[2]['scheduled_date']
        returnresult

    #-------------------------------------------------------------------------
    #Actionmethods
    #-------------------------------------------------------------------------
    defaction_confirm(self):
        """Sanitychecks,confirmthepickingsandmarkthebatchasconfirmed."""
        self.ensure_one()
        ifnotself.picking_ids:
            raiseUserError(_("Youhavetosetsomepickingstobatch."))
        self.picking_ids.action_confirm()
        self._check_company()
        self.state='in_progress'
        returnTrue

    defaction_cancel(self):
        self.ensure_one()
        self.state='cancel'
        returnTrue

    defaction_print(self):
        self.ensure_one()
        returnself.env.ref('stock_picking_batch.action_report_picking_batch').report_action(self)

    defaction_done(self):
        self.ensure_one()
        self._check_company()
        pickings=self.mapped('picking_ids').filtered(lambdapicking:picking.statenotin('cancel','done'))
        ifany(picking.statenotin('assigned','confirmed')forpickinginpickings):
            raiseUserError(_('Sometransfersarestillwaitingforgoods.Pleasecheckorforcetheiravailabilitybeforesettingthisbatchtodone.'))

        empty_pickings=set()
        forpickinginpickings:
            ifall(float_is_zero(line.qty_done,precision_rounding=line.product_uom_id.rounding)forlineinpicking.move_line_idsifline.statenotin('done','cancel')):
                empty_pickings.add(picking.id)
            picking.message_post(
                body="<b>%s:</b>%s<ahref=#id=%s&view_type=form&model=stock.picking.batch>%s</a>"%(
                    _("Transferredby"),
                    _("BatchTransfer"),
                    picking.batch_id.id,
                    picking.batch_id.name))

        iflen(empty_pickings)==len(pickings):
            returnpickings.button_validate()
        else:
            res=pickings.with_context(skip_immediate=True).button_validate()
            ifempty_pickingsandres.get('context'):
                res['context']['pickings_to_detach']=list(empty_pickings)
            returnres

    defaction_assign(self):
        self.ensure_one()
        self.picking_ids.action_assign()

    defaction_put_in_pack(self):
        """Actiontoputmovelineswith'Done'quantitiesintoanewpack
        Thismethodfollowssamelogictostock.picking.
        """
        self.ensure_one()
        ifself.statenotin('done','cancel'):
            picking_move_lines=self.move_line_ids

            move_line_ids=picking_move_lines.filtered(lambdaml:
                float_compare(ml.qty_done,0.0,precision_rounding=ml.product_uom_id.rounding)>0
                andnotml.result_package_id
            )
            ifnotmove_line_ids:
                move_line_ids=picking_move_lines.filtered(lambdaml:float_compare(ml.product_uom_qty,0.0,
                                     precision_rounding=ml.product_uom_id.rounding)>0andfloat_compare(ml.qty_done,0.0,
                                     precision_rounding=ml.product_uom_id.rounding)==0)
            ifmove_line_ids:
                res=move_line_ids.picking_id[0]._pre_put_in_pack_hook(move_line_ids)
                ifnotres:
                    res=move_line_ids.picking_id[0]._put_in_pack(move_line_ids,False)
                returnres
            else:
                raiseUserError(_("Pleaseadd'Done'quantitiestothebatchpickingtocreateanewpack."))

    #-------------------------------------------------------------------------
    #Miscellaneous
    #-------------------------------------------------------------------------
    def_sanity_check(self):
        forbatchinself:
            ifnotbatch.picking_ids<=batch.allowed_picking_ids:
                erroneous_pickings=batch.picking_ids-batch.allowed_picking_ids
                raiseUserError(_(
                    "Thefollowingtransferscannotbeaddedtobatchtransfer%s."
                    "Pleasechecktheirstatesandoperationtypes,iftheyaren'timmediate"
                    "transfersorifthey'renotalreadypartofanotherbatchtransfer.\n\n"
                    "Incompatibilities:%s",batch.name,','.join(erroneous_pickings.mapped('name'))))

    def_track_subtype(self,init_values):
        if'state'ininit_values:
            returnself.env.ref('stock_picking_batch.mt_batch_state')
        returnsuper()._track_subtype(init_values)

