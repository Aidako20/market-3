#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.toolsimporthtml2plaintext


classStage(models.Model):

    _name="note.stage"
    _description="NoteStage"
    _order='sequence'

    name=fields.Char('StageName',translate=True,required=True)
    sequence=fields.Integer(help="Usedtoorderthenotestages",default=1)
    user_id=fields.Many2one('res.users',string='Owner',required=True,ondelete='cascade',default=lambdaself:self.env.uid,help="Ownerofthenotestage")
    fold=fields.Boolean('FoldedbyDefault')


classTag(models.Model):

    _name="note.tag"
    _description="NoteTag"

    name=fields.Char('TagName',required=True,translate=True)
    color=fields.Integer('ColorIndex')

    _sql_constraints=[
        ('name_uniq','unique(name)',"Tagnamealreadyexists!"),
    ]


classNote(models.Model):

    _name='note.note'
    _inherit=['mail.thread','mail.activity.mixin']
    _description="Note"
    _order='sequence,iddesc'

    def_get_default_stage_id(self):
        returnself.env['note.stage'].search([('user_id','=',self.env.uid)],limit=1)

    name=fields.Text(compute='_compute_name',string='NoteSummary',store=True)
    user_id=fields.Many2one('res.users',string='Owner',default=lambdaself:self.env.uid)
    memo=fields.Html('NoteContent')
    sequence=fields.Integer('Sequence',default=0)
    stage_id=fields.Many2one('note.stage',compute='_compute_stage_id',
        inverse='_inverse_stage_id',string='Stage',default=_get_default_stage_id)
    stage_ids=fields.Many2many('note.stage','note_stage_rel','note_id','stage_id',
        string='StagesofUsers', default=_get_default_stage_id)
    open=fields.Boolean(string='Active',default=True)
    date_done=fields.Date('Datedone')
    color=fields.Integer(string='ColorIndex')
    tag_ids=fields.Many2many('note.tag','note_tags_rel','note_id','tag_id',string='Tags')
    message_partner_ids=fields.Many2many(
        comodel_name='res.partner',string='Followers(Partners)',
        compute='_get_followers',search='_search_follower_partners',
        compute_sudo=True)
    message_channel_ids=fields.Many2many(
        comodel_name='mail.channel',string='Followers(Channels)',
        compute='_get_followers',search='_search_follower_channels',
        compute_sudo=True)

    @api.depends('memo')
    def_compute_name(self):
        """Readthefirstlineofthememotodeterminethenotename"""
        fornoteinself:
            text=html2plaintext(note.memo)ifnote.memoelse''
            note.name=text.strip().replace('*','').split("\n")[0]

    def_compute_stage_id(self):
        first_user_stage=self.env['note.stage'].search([('user_id','=',self.env.uid)],limit=1)
        fornoteinself:
            forstageinnote.stage_ids.filtered(lambdastage:stage.user_id==self.env.user):
                note.stage_id=stage
            #notewithoutuser'sstage
            ifnotnote.stage_id:
                note.stage_id=first_user_stage

    def_inverse_stage_id(self):
        fornoteinself.filtered('stage_id'):
            note.stage_ids=note.stage_id+note.stage_ids.filtered(lambdastage:stage.user_id!=self.env.user)

    @api.model
    defname_create(self,name):
        returnself.create({'memo':name}).name_get()[0]

    @api.model
    defread_group(self,domain,fields,groupby,offset=0,limit=None,orderby=False,lazy=True):
        ifgroupbyandgroupby[0]=="stage_id"and(len(groupby)==1orlazy):
            stages=self.env['note.stage'].search([('user_id','=',self.env.uid)])
            ifstages:
                #iftheuserhassomestages
                result=[]
                forstageinstages:
                    #notesbystageforstagesuser
                    nb_stage_counts=self.search_count(domain+[('stage_ids','=',stage.id)])
                    result.append({
                        '__context':{'group_by':groupby[1:]},
                        '__domain':domain+[('stage_ids.id','=',stage.id)],
                        'stage_id':(stage.id,stage.name),
                        'stage_id_count':nb_stage_counts,
                        '__count':nb_stage_counts,
                        '__fold':stage.fold,
                    })
                #notewithoutuser'sstage
                nb_notes_ws=self.search_count(domain+[('stage_ids','notin',stages.ids)])
                ifnb_notes_ws:
                    #addnotetothefirstcolumnifit'sthefirststage
                    dom_not_in=('stage_ids','notin',stages.ids)
                    ifresultandresult[0]['stage_id'][0]==stages[0].id:
                        dom_in=result[0]['__domain'].pop()
                        result[0]['__domain']=domain+['|',dom_in,dom_not_in]
                        result[0]['stage_id_count']+=nb_notes_ws
                        result[0]['__count']+=nb_notes_ws
                    else:
                        #addthefirststagecolumn
                        result=[{
                            '__context':{'group_by':groupby[1:]},
                            '__domain':domain+[dom_not_in],
                            'stage_id':(stages[0].id,stages[0].name),
                            'stage_id_count':nb_notes_ws,
                            '__count':nb_notes_ws,
                            '__fold':stages[0].name,
                        }]+result
            else: #ifstage_idsisempty,getnotewithoutuser'sstage
                nb_notes_ws=self.search_count(domain)
                ifnb_notes_ws:
                    result=[{ #notesforunknownstage
                        '__context':{'group_by':groupby[1:]},
                        '__domain':domain,
                        'stage_id':False,
                        'stage_id_count':nb_notes_ws,
                        '__count':nb_notes_ws
                    }]
                else:
                    result=[]
            returnresult
        returnsuper(Note,self).read_group(domain,fields,groupby,offset=offset,limit=limit,orderby=orderby,lazy=lazy)

    defaction_close(self):
        returnself.write({'open':False,'date_done':fields.date.today()})

    defaction_open(self):
        returnself.write({'open':True})
