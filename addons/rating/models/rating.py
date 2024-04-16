#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64
importuuid

fromflectraimportapi,fields,models

fromflectra.modules.moduleimportget_resource_path

RATING_LIMIT_SATISFIED=5
RATING_LIMIT_OK=3
RATING_LIMIT_MIN=1


classRating(models.Model):
    _name="rating.rating"
    _description="Rating"
    _order='write_datedesc'
    _rec_name='res_name'
    _sql_constraints=[
        ('rating_range','check(rating>=0andrating<=5)','Ratingshouldbebetween0and5'),
    ]

    @api.depends('res_model','res_id')
    def_compute_res_name(self):
        forratinginself:
            name=self.env[rating.res_model].sudo().browse(rating.res_id).name_get()
            rating.res_name=nameandname[0][1]or('%s/%s')%(rating.res_model,rating.res_id)

    @api.model
    def_default_access_token(self):
        returnuuid.uuid4().hex

    @api.model
    def_selection_target_model(self):
        return[(model.model,model.name)formodelinself.env['ir.model'].search([])]

    create_date=fields.Datetime(string="Submittedon")
    res_name=fields.Char(string='Resourcename',compute='_compute_res_name',store=True,help="Thenameoftheratedresource.")
    res_model_id=fields.Many2one('ir.model','RelatedDocumentModel',index=True,ondelete='cascade',help='Modelofthefollowedresource')
    res_model=fields.Char(string='DocumentModel',related='res_model_id.model',store=True,index=True,readonly=True)
    res_id=fields.Integer(string='Document',required=True,help="Identifieroftheratedobject",index=True)
    resource_ref=fields.Reference(
        string='ResourceRef',selection='_selection_target_model',
        compute='_compute_resource_ref',readonly=True)
    parent_res_name=fields.Char('ParentDocumentName',compute='_compute_parent_res_name',store=True)
    parent_res_model_id=fields.Many2one('ir.model','ParentRelatedDocumentModel',index=True,ondelete='cascade')
    parent_res_model=fields.Char('ParentDocumentModel',store=True,related='parent_res_model_id.model',index=True,readonly=False)
    parent_res_id=fields.Integer('ParentDocument',index=True)
    parent_ref=fields.Reference(
        string='ParentRef',selection='_selection_target_model',
        compute='_compute_parent_ref',readonly=True)
    rated_partner_id=fields.Many2one('res.partner',string="RatedOperator",help="Owneroftheratedresource")
    partner_id=fields.Many2one('res.partner',string='Customer',help="Authoroftherating")
    rating=fields.Float(string="RatingValue",group_operator="avg",default=0,help="Ratingvalue:0=Unhappy,5=Happy")
    rating_image=fields.Binary('Image',compute='_compute_rating_image')
    rating_text=fields.Selection([
        ('satisfied','Satisfied'),
        ('not_satisfied','Notsatisfied'),
        ('highly_dissatisfied','Highlydissatisfied'),
        ('no_rating','NoRatingyet')],string='Rating',store=True,compute='_compute_rating_text',readonly=True)
    feedback=fields.Text('Comment',help="Reasonoftherating")
    message_id=fields.Many2one(
        'mail.message',string="Message",
        index=True,ondelete='cascade',
        help="Associatedmessagewhenpostingareview.Mainlyusedinwebsiteaddons.")
    is_internal=fields.Boolean('VisibleInternallyOnly',readonly=False,related='message_id.is_internal',store=True)
    access_token=fields.Char('SecurityToken',default=_default_access_token,help="Accesstokentosettheratingofthevalue")
    consumed=fields.Boolean(string="FilledRating",help="Enablediftheratinghasbeenfilled.")

    @api.depends('res_model','res_id')
    def_compute_resource_ref(self):
        forratinginself:
            ifrating.res_modelandrating.res_modelinself.env:
                rating.resource_ref='%s,%s'%(rating.res_model,rating.res_idor0)
            else:
                rating.resource_ref=None

    @api.depends('parent_res_model','parent_res_id')
    def_compute_parent_ref(self):
        forratinginself:
            ifrating.parent_res_modelandrating.parent_res_modelinself.env:
                rating.parent_ref='%s,%s'%(rating.parent_res_model,rating.parent_res_idor0)
            else:
                rating.parent_ref=None

    @api.depends('parent_res_model','parent_res_id')
    def_compute_parent_res_name(self):
        forratinginself:
            name=False
            ifrating.parent_res_modelandrating.parent_res_id:
                name=self.env[rating.parent_res_model].sudo().browse(rating.parent_res_id).name_get()
                name=nameandname[0][1]or('%s/%s')%(rating.parent_res_model,rating.parent_res_id)
            rating.parent_res_name=name

    def_get_rating_image_filename(self):
        self.ensure_one()
        ifself.rating>=RATING_LIMIT_SATISFIED:
            rating_int=5
        elifself.rating>=RATING_LIMIT_OK:
            rating_int=3
        elifself.rating>=RATING_LIMIT_MIN:
            rating_int=1
        else:
            rating_int=0
        return'rating_%s.png'%rating_int

    def_compute_rating_image(self):
        forratinginself:
            try:
                image_path=get_resource_path('rating','static/src/img',rating._get_rating_image_filename())
                rating.rating_image=base64.b64encode(open(image_path,'rb').read())ifimage_pathelseFalse
            except(IOError,OSError):
                rating.rating_image=False

    @api.depends('rating')
    def_compute_rating_text(self):
        forratinginself:
            ifrating.rating>=RATING_LIMIT_SATISFIED:
                rating.rating_text='satisfied'
            elifrating.rating>=RATING_LIMIT_OK:
                rating.rating_text='not_satisfied'
            elifrating.rating>=RATING_LIMIT_MIN:
                rating.rating_text='highly_dissatisfied'
            else:
                rating.rating_text='no_rating'

    @api.model
    defcreate(self,values):
        ifvalues.get('res_model_id')andvalues.get('res_id'):
            values.update(self._find_parent_data(values))
        returnsuper(Rating,self).create(values)

    defwrite(self,values):
        ifvalues.get('res_model_id')andvalues.get('res_id'):
            values.update(self._find_parent_data(values))
        returnsuper(Rating,self).write(values)

    defunlink(self):
        #OPW-2181568:Deletethechattermessagetoo
        self.env['mail.message'].search([('rating_ids','in',self.ids)]).unlink()
        returnsuper(Rating,self).unlink()

    def_find_parent_data(self,values):
        """Determinetheparentres_model/res_id,basedonthevaluestocreateorwrite"""
        current_model_name=self.env['ir.model'].sudo().browse(values['res_model_id']).model
        current_record=self.env[current_model_name].browse(values['res_id'])
        data={
            'parent_res_model_id':False,
            'parent_res_id':False,
        }
        ifhasattr(current_record,'_rating_get_parent_field_name'):
            current_record_parent=current_record._rating_get_parent_field_name()
            ifcurrent_record_parent:
                parent_res_model=getattr(current_record,current_record_parent)
                data['parent_res_model_id']=self.env['ir.model']._get(parent_res_model._name).id
                data['parent_res_id']=parent_res_model.id
        returndata

    defreset(self):
        forrecordinself:
            record.write({
                'rating':0,
                'access_token':record._default_access_token(),
                'feedback':False,
                'consumed':False,
            })

    defaction_open_rated_object(self):
        self.ensure_one()
        return{
            'type':'ir.actions.act_window',
            'res_model':self.res_model,
            'res_id':self.res_id,
            'views':[[False,'form']]
        }
