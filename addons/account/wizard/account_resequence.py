#-*-coding:utf-8-*-
fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.tools.date_utilsimportget_month,get_fiscal_year
fromflectra.tools.miscimportformat_date

importre
fromcollectionsimportdefaultdict
importjson


classReSequenceWizard(models.TransientModel):
    _name='account.resequence.wizard'
    _description='RemakethesequenceofJournalEntries.'

    sequence_number_reset=fields.Char(compute='_compute_sequence_number_reset')
    first_date=fields.Date(help="Date(inclusive)fromwhichthenumbersareresequenced.")
    end_date=fields.Date(help="Date(inclusive)towhichthenumbersareresequenced.Ifnotset,allJournalEntriesuptotheendoftheperiodareresequenced.")
    first_name=fields.Char(compute="_compute_first_name",readonly=False,store=True,required=True,string="FirstNewSequence")
    ordering=fields.Selection([('keep','Keepcurrentorder'),('date','Reorderbyaccountingdate')],required=True,default='keep')
    move_ids=fields.Many2many('account.move')
    new_values=fields.Text(compute='_compute_new_values')
    preview_moves=fields.Text(compute='_compute_preview_moves')

    @api.model
    defdefault_get(self,fields_list):
        values=super(ReSequenceWizard,self).default_get(fields_list)
        if'move_ids'notinfields_list:
            returnvalues
        active_move_ids=self.env['account.move']
        ifself.env.context['active_model']=='account.move'and'active_ids'inself.env.context:
            active_move_ids=self.env['account.move'].browse(self.env.context['active_ids'])
        iflen(active_move_ids.journal_id)>1:
            raiseUserError(_('Youcanonlyresequenceitemsfromthesamejournal'))
        move_types=set(active_move_ids.mapped('move_type'))
        if(
            active_move_ids.journal_id.refund_sequence
            and('in_refund'inmove_typesor'out_refund'inmove_types)
            andlen(move_types)>1
        ):
            raiseUserError(_('ThesequencesofthisjournalaredifferentforInvoicesandRefundsbutyouselectedsomeofbothtypes.'))
        values['move_ids']=[(6,0,active_move_ids.ids)]
        returnvalues

    @api.depends('first_name')
    def_compute_sequence_number_reset(self):
        forrecordinself:
            record.sequence_number_reset=record.move_ids[0]._deduce_sequence_number_reset(record.first_name)

    @api.depends('move_ids')
    def_compute_first_name(self):
        self.first_name=""
        forrecordinself:
            ifrecord.move_ids:
                record.first_name=min(record.move_ids._origin.mapped(lambdamove:move.nameor""))

    @api.depends('new_values','ordering')
    def_compute_preview_moves(self):
        """Reducethecomputednew_valuestoasmallersettodisplayinthepreview."""
        forrecordinself:
            new_values=sorted(json.loads(record.new_values).values(),key=lambdax:x['server-date'],reverse=True)
            changeLines=[]
            in_elipsis=0
            previous_line=None
            fori,lineinenumerate(new_values):
                ifi<3ori==len(new_values)-1orline['new_by_name']!=line['new_by_date']\
                 or(self.sequence_number_reset=='year'andline['server-date'][0:4]!=previous_line['server-date'][0:4])\
                 or(self.sequence_number_reset=='month'andline['server-date'][0:7]!=previous_line['server-date'][0:7]):
                    ifin_elipsis:
                        changeLines.append({'id':'other_'+str(line['id']),'current_name':_('...(%sother)',in_elipsis),'new_by_name':'...','new_by_date':'...','date':'...'})
                        in_elipsis=0
                    changeLines.append(line)
                else:
                    in_elipsis+=1
                previous_line=line

            record.preview_moves=json.dumps({
                'ordering':record.ordering,
                'changeLines':changeLines,
            })

    @api.depends('first_name','move_ids','sequence_number_reset')
    def_compute_new_values(self):
        """Computetheproposednewvalues.

        Setsajsonstringonnew_valuesrepresentingadictionarythatsmapsaccount.move
        idstoadisctionaycontainingthenameifweexecutetheaction,andinformation
        relativetothepreviewwidget.
        """
        def_get_move_key(move_id):
            ifself.sequence_number_reset=='year':
                returnmove_id.date.year
            elifself.sequence_number_reset=='month':
                return(move_id.date.year,move_id.date.month)
            return'default'

        self.new_values="{}"
        forrecordinself.filtered('first_name'):
            moves_by_period=defaultdict(lambda:record.env['account.move'])
            formoveinrecord.move_ids._origin: #Sortthemovesbyperioddependingonthesequencenumberreset
                moves_by_period[_get_move_key(move)]+=move

            seq_format,format_values=record.move_ids[0]._get_sequence_format_param(record.first_name)

            new_values={}
            forj,period_recsinenumerate(moves_by_period.values()):
                #computethenewvaluesperiodbyperiod
                formoveinperiod_recs:
                    new_values[move.id]={
                        'id':move.id,
                        'current_name':move.name,
                        'state':move.state,
                        'date':format_date(self.env,move.date),
                        'server-date':str(move.date),
                    }

                new_name_list=[seq_format.format(**{
                    **format_values,
                    'year':period_recs[0].date.year%(10**format_values['year_length']),
                    'month':period_recs[0].date.month,
                    'seq':i+(format_values['seq']ifj==(len(moves_by_period)-1)else1),
                })foriinrange(len(period_recs))]

                #Forallthemovesofthisperiod,assignthenamebyincreasinginitialname
                formove,new_nameinzip(period_recs.sorted(lambdam:(m.sequence_prefix,m.sequence_number)),new_name_list):
                    new_values[move.id]['new_by_name']=new_name
                #Forallthemovesofthisperiod,assignthenamebyincreasingdate
                formove,new_nameinzip(period_recs.sorted(lambdam:(m.date,m.nameor"",m.id)),new_name_list):
                    new_values[move.id]['new_by_date']=new_name

            record.new_values=json.dumps(new_values)

    defresequence(self):
        new_values=json.loads(self.new_values)
        ifself.move_ids.journal_idandself.move_ids.journal_id.restrict_mode_hash_table:
            ifself.ordering=='date':
                raiseUserError(_('Youcannotreordersequencebydatewhenthejournalislockedwithahash.'))
        self.move_ids._check_fiscalyear_lock_date()
        self.env['account.move'].browse(int(k)forkinnew_values.keys()).name=False
        formove_idinself.move_ids:
            ifstr(move_id.id)innew_values:
                ifself.ordering=='keep':
                    move_id.name=new_values[str(move_id.id)]['new_by_name']
                else:
                    move_id.name=new_values[str(move_id.id)]['new_by_date']
