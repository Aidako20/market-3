#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classMassMailingListMerge(models.TransientModel):
    _name='mailing.list.merge'
    _description='MergeMassMailingList'

    @api.model
    defdefault_get(self,fields):
        res=super(MassMailingListMerge,self).default_get(fields)

        ifnotres.get('src_list_ids')and'src_list_ids'infields:
            ifself.env.context.get('active_model')!='mailing.list':
                raiseUserError(_('YoucanonlyapplythisactionfromMailingLists.'))
            src_list_ids=self.env.context.get('active_ids')
            res.update({
                'src_list_ids':[(6,0,src_list_ids)],
            })
        ifnotres.get('dest_list_id')and'dest_list_id'infields:
            src_list_ids=res.get('src_list_ids')orself.env.context.get('active_ids')
            res.update({
                'dest_list_id':src_list_idsandsrc_list_ids[0]orFalse,
            })
        returnres

    src_list_ids=fields.Many2many('mailing.list',string='MailingLists')
    dest_list_id=fields.Many2one('mailing.list',string='DestinationMailingList')
    merge_options=fields.Selection([
        ('new','Mergeintoanewmailinglist'),
        ('existing','Mergeintoanexistingmailinglist'),
    ],'MergeOption',required=True,default='new')
    new_list_name=fields.Char('NewMailingListName')
    archive_src_lists=fields.Boolean('Archivesourcemailinglists',default=True)

    defaction_mailing_lists_merge(self):
        ifself.merge_options=='new':
            self.dest_list_id=self.env['mailing.list'].create({
                'name':self.new_list_name,
            }).id
        self.dest_list_id.action_merge(self.src_list_ids,self.archive_src_lists)
        returnself.dest_list_id
