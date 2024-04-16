#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools


classMrpRoutingWorkcenter(models.Model):
    _name='mrp.routing.workcenter'
    _description='WorkCenterUsage'
    _order='sequence,id'
    _check_company_auto=True

    name=fields.Char('Operation',required=True)
    workcenter_id=fields.Many2one('mrp.workcenter','WorkCenter',required=True,check_company=True)
    sequence=fields.Integer(
        'Sequence',default=100,
        help="GivesthesequenceorderwhendisplayingalistofroutingWorkCenters.")
    bom_id=fields.Many2one(
        'mrp.bom','BillofMaterial',check_company=True,
        index=True,ondelete='cascade',
        help="TheBillofMaterialthisoperationislinkedto")
    company_id=fields.Many2one(
        'res.company','Company',default=lambdaself:self.env.company)
    worksheet_type=fields.Selection([
        ('pdf','PDF'),('google_slide','GoogleSlide'),('text','Text')],
        string="WorkSheet",default="text",
        help="DefinesifyouwanttouseaPDForaGoogleSlideasworksheet."
    )
    note=fields.Text('Description',help="Textworksheetdescription")
    worksheet=fields.Binary('PDF')
    worksheet_google_slide=fields.Char('GoogleSlide',help="PastetheurlofyourGoogleSlide.Makesuretheaccesstothedocumentispublic.")
    time_mode=fields.Selection([
        ('auto','Computebasedontrackedtime'),
        ('manual','Setdurationmanually')],string='DurationComputation',
        default='manual')
    time_mode_batch=fields.Integer('Basedon',default=10)
    time_cycle_manual=fields.Float(
        'ManualDuration',default=60,
        help="Timeinminutes:"
        "-Inmanualmode,timeused"
        "-Inautomaticmode,supposedfirsttimewhentherearen'tanyworkordersyet")
    time_cycle=fields.Float('Duration',compute="_compute_time_cycle")
    workorder_count=fields.Integer("#WorkOrders",compute="_compute_workorder_count")
    workorder_ids=fields.One2many('mrp.workorder','operation_id',string="WorkOrders")

    @api.depends('time_cycle_manual','time_mode','workorder_ids')
    def_compute_time_cycle(self):
        manual_ops=self.filtered(lambdaoperation:operation.time_mode=='manual')
        foroperationinmanual_ops:
            operation.time_cycle=operation.time_cycle_manual
        foroperationinself-manual_ops:
            data=self.env['mrp.workorder'].search([
                ('operation_id','=',operation.id),
                ('qty_produced','>',0),
                ('state','=','done')],
                limit=operation.time_mode_batch,
                order="date_finisheddesc")
            #Tocomputethetime_cycle,wecantakethetotaldurationofpreviousoperations
            #butforthequantity,wewilltakeinconsiderationtheqty_producedlikeifthecapacitywas1.
            #Soproducing50in00:10withcapacity2,forthetime_cycle,weassumeitis25in00:10
            #Whenrecomputingtheexpectedduration,thecapacityisusedagaintodividetheqtytoproduce
            #sothatifweneed50withcapacity2,itwillcomputetheexpectedof25whichis00:10
            total_duration=0 #Canbe0sinceit'snotaninvaliddurationforBoM
            cycle_number=0 #Never0unlessinfiniteitem['workcenter_id'].capacity
            foritemindata:
                total_duration+=item['duration']
                cycle_number+=tools.float_round((item['qty_produced']/item['workcenter_id'].capacityor1.0),precision_digits=0,rounding_method='UP')
            ifcycle_number:
                operation.time_cycle=total_duration/cycle_number
            else:
                operation.time_cycle=operation.time_cycle_manual

    def_compute_workorder_count(self):
        data=self.env['mrp.workorder'].read_group([
            ('operation_id','in',self.ids),
            ('state','=','done')],['operation_id'],['operation_id'])
        count_data=dict((item['operation_id'][0],item['operation_id_count'])foritemindata)
        foroperationinself:
            operation.workorder_count=count_data.get(operation.id,0)

    def_get_comparison_values(self):
        ifnotself:
            returnFalse
        self.ensure_one()
        returntuple(self[key]forkeyin ('name','company_id','workcenter_id','time_mode','time_cycle_manual'))

    defwrite(self,values):
        if'bom_id'invalues:
            filtered_lines=self.bom_id.bom_line_ids.filtered(lambdaline:line.operation_id==self)
            filtered_lines.operation_id=False
        returnsuper().write(values)
