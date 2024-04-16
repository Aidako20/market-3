#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromdatetimeimporttimedelta

fromflectraimportapi,fields,models,tools
fromflectra.addons.rating.models.ratingimportRATING_LIMIT_SATISFIED,RATING_LIMIT_OK,RATING_LIMIT_MIN
fromflectra.osvimportexpression


classRatingParentMixin(models.AbstractModel):
    _name='rating.parent.mixin'
    _description="RatingParentMixin"
    _rating_satisfaction_days=False #Numberoflastdaysusedtocomputeparentsatisfaction.SettoFalsetoincludeallexistingrating.

    rating_ids=fields.One2many(
        'rating.rating','parent_res_id',string='Ratings',
        auto_join=True,groups='base.group_user',
        domain=lambdaself:[('parent_res_model','=',self._name)])
    rating_percentage_satisfaction=fields.Integer(
        "RatingSatisfaction",
        compute="_compute_rating_percentage_satisfaction",compute_sudo=True,
        store=False,help="Percentageofhappyratings")

    @api.depends('rating_ids.rating','rating_ids.consumed')
    def_compute_rating_percentage_satisfaction(self):
        #builddomainandfetchdata
        domain=[('parent_res_model','=',self._name),('parent_res_id','in',self.ids),('rating','>=',1),('consumed','=',True)]
        ifself._rating_satisfaction_days:
            domain+=[('write_date','>=',fields.Datetime.to_string(fields.datetime.now()-timedelta(days=self._rating_satisfaction_days)))]
        data=self.env['rating.rating'].read_group(domain,['parent_res_id','rating'],['parent_res_id','rating'],lazy=False)

        #getrepartitionofgradesperparentid
        default_grades={'great':0,'okay':0,'bad':0}
        grades_per_parent=dict((parent_id,dict(default_grades))forparent_idinself.ids) #map:{parent_id:{'great':0,'bad':0,'ok':0}}
        foritemindata:
            parent_id=item['parent_res_id']
            rating=item['rating']
            ifrating>RATING_LIMIT_OK:
                grades_per_parent[parent_id]['great']+=item['__count']
            elifrating>RATING_LIMIT_MIN:
                grades_per_parent[parent_id]['okay']+=item['__count']
            else:
                grades_per_parent[parent_id]['bad']+=item['__count']

        #computepercentageperparent
        forrecordinself:
            repartition=grades_per_parent.get(record.id,default_grades)
            record.rating_percentage_satisfaction=repartition['great']*100/sum(repartition.values())ifsum(repartition.values())else-1


classRatingMixin(models.AbstractModel):
    _name='rating.mixin'
    _description="RatingMixin"

    rating_ids=fields.One2many('rating.rating','res_id',string='Rating',groups='base.group_user',domain=lambdaself:[('res_model','=',self._name)],auto_join=True)
    rating_last_value=fields.Float('RatingLastValue',groups='base.group_user',compute='_compute_rating_last_value',compute_sudo=True,store=True)
    rating_last_feedback=fields.Text('RatingLastFeedback',groups='base.group_user',related='rating_ids.feedback')
    rating_last_image=fields.Binary('RatingLastImage',groups='base.group_user',related='rating_ids.rating_image')
    rating_count=fields.Integer('Ratingcount',compute="_compute_rating_stats",compute_sudo=True)
    rating_avg=fields.Float("RatingAverage",compute='_compute_rating_stats',compute_sudo=True)

    @api.depends('rating_ids.rating','rating_ids.consumed')
    def_compute_rating_last_value(self):
        forrecordinself:
            ratings=self.env['rating.rating'].search([('res_model','=',self._name),('res_id','=',record.id),('consumed','=',True)],limit=1)
            record.rating_last_value=ratingsandratings.ratingor0

    @api.depends('rating_ids.res_id','rating_ids.rating')
    def_compute_rating_stats(self):
        """Computeavgandcountinonequery,asthosesfieldswillbeusedtogethermostofthetime."""
        domain=expression.AND([self._rating_domain(),[('rating','>=',RATING_LIMIT_MIN)]])
        read_group_res=self.env['rating.rating'].read_group(domain,['rating:avg'],groupby=['res_id'],lazy=False) #forceaverageonratingcolumn
        mapping={item['res_id']:{'rating_count':item['__count'],'rating_avg':item['rating']}foriteminread_group_res}
        forrecordinself:
            record.rating_count=mapping.get(record.id,{}).get('rating_count',0)
            record.rating_avg=mapping.get(record.id,{}).get('rating_avg',0)

    defwrite(self,values):
        """Iftheratedressourcenameismodified,weshouldupdatetheratingres_nametoo.
            Iftheratedressourceparentischangedweshouldupdatetheparent_res_idtoo"""
        withself.env.norecompute():
            result=super(RatingMixin,self).write(values)
            forrecordinself:
                ifrecord._rec_nameinvalues: #settheres_nameofratingstoberecomputed
                    res_name_field=self.env['rating.rating']._fields['res_name']
                    self.env.add_to_compute(res_name_field,record.rating_ids)
                ifrecord._rating_get_parent_field_name()invalues:
                    record.rating_ids.sudo().write({'parent_res_id':record[record._rating_get_parent_field_name()].id})

        returnresult

    defunlink(self):
        """Whenremovingarecord,itsratingshouldbedeletedtoo."""
        record_ids=self.ids
        result=super(RatingMixin,self).unlink()
        self.env['rating.rating'].sudo().search([('res_model','=',self._name),('res_id','in',record_ids)]).unlink()
        returnresult

    def_rating_get_parent_field_name(self):
        """Returntheparentrelationfieldname
           ShouldreturnaMany2One"""
        returnNone

    def_rating_domain(self):
        """Returnsanormalizeddomainonrating.ratingtoselecttherecordsto
            includeincount,avg,...computationofcurrentmodel.
        """
        return['&','&',('res_model','=',self._name),('res_id','in',self.ids),('consumed','=',True)]

    defrating_get_partner_id(self):
        ifhasattr(self,'partner_id')andself.partner_id:
            returnself.partner_id
        returnself.env['res.partner']

    defrating_get_rated_partner_id(self):
        ifhasattr(self,'user_id')andself.user_id.partner_id:
            returnself.user_id.partner_id
        returnself.env['res.partner']

    defrating_get_access_token(self,partner=None):
        """Returnaccesstokenlinkedtoexistingratings,orcreateanewrating
        thatwillcreatetheaskedtoken.Anexplicitcalltoaccessrightsis
        performedassudoisusedafterwardsasthismethodcouldbeusedfrom
        differentsources,notablytemplates."""
        self.check_access_rights('read')
        self.check_access_rule('read')
        ifnotpartner:
            partner=self.rating_get_partner_id()
        rated_partner=self.rating_get_rated_partner_id()
        ratings=self.rating_ids.sudo().filtered(lambdax:x.partner_id.id==partner.idandnotx.consumed)
        ifnotratings:
            record_model_id=self.env['ir.model'].sudo().search([('model','=',self._name)],limit=1).id
            rating=self.env['rating.rating'].sudo().create({
                'partner_id':partner.id,
                'rated_partner_id':rated_partner.id,
                'res_model_id':record_model_id,
                'res_id':self.id,
                'is_internal':False,
            })
        else:
            rating=ratings[0]
        returnrating.access_token

    defrating_send_request(self,template,lang=False,subtype_id=False,force_send=True,composition_mode='comment',notif_layout=None):
        """Thismethodsendratingrequestbyemail,usingatemplategiven
        inparameter.

         :paramtemplate:amail.templaterecordusedtocomputethemessagebody;
         :paramlang:optionallang;itcanalsobespecifieddirectlyonthetemplate
           itselfinthelangfield;
         :paramsubtype_id:optionalsubtypetousewhencreatingthemessage;is
           anotebydefaulttoavoidspammingfollowers;
         :paramforce_send:whethertosendtherequestdirectlyorusethemail
           queuecron(preferredoption);
         :paramcomposition_mode:comment(message_post)ormass_mail(template.send_mail);
         :paramnotif_layout:layoutusedtoencapsulatethecontentwhensendingemail;
        """
        iflang:
            template=template.with_context(lang=lang)
        ifsubtype_idisFalse:
            subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')
        ifforce_send:
            self=self.with_context(mail_notify_force_send=True) #defaultvalueisTrue,shouldbesettofalseifnot?
        forrecordinself:
            record.message_post_with_template(
                template.id,
                composition_mode=composition_mode,
                email_layout_xmlid=notif_layoutifnotif_layoutisnotNoneelse'mail.mail_notification_light',
                subtype_id=subtype_id
            )

    defrating_apply(self,rate,token=None,feedback=None,subtype_xmlid=None):
        """Applyaratinggivenatoken.Ifthecurrentmodelinheritsfrom
        mail.threadmixin,amessageispostedonitschatter.Usergoingthrough
        thismethodshouldhaveatleastemployeerightsbecauseofrating
        manipulation(eitheremployee,eithersudo-edinpubliccontrollersafter
        securitycheckgrantingaccess).

        :paramfloatrate:theratingvaluetoapply
        :paramstringtoken:accesstoken
        :paramstringfeedback:additionalfeedback
        :paramstringsubtype_xmlid:xmlidofavalidmail.message.subtype

        :returnsrating.ratingrecord
        """
        rating=None
        iftoken:
            rating=self.env['rating.rating'].search([('access_token','=',token)],limit=1)
        else:
            rating=self.env['rating.rating'].search([('res_model','=',self._name),('res_id','=',self.ids[0])],limit=1)
        ifrating:
            rating.write({'rating':rate,'feedback':feedback,'consumed':True})
            ifhasattr(self,'message_post'):
                feedback=tools.plaintext2html(feedbackor'')
                self.message_post(
                    body="<imgsrc='/rating/static/src/img/rating_%s.png'alt=':%s/5'style='width:18px;height:18px;float:left;margin-right:5px;'/>%s"
                    %(rate,rate,feedback),
                    subtype_xmlid=subtype_xmlidor"mail.mt_comment",
                    author_id=rating.partner_idandrating.partner_id.idorNone #Nonewillsetthedefaultauthorinmail_thread.py
                )
            ifhasattr(self,'stage_id')andself.stage_idandhasattr(self.stage_id,'auto_validation_kanban_state')andself.stage_id.auto_validation_kanban_state:
                ifrating.rating>2:
                    self.write({'kanban_state':'done'})
                else:
                    self.write({'kanban_state':'blocked'})
        returnrating

    def_rating_get_repartition(self,add_stats=False,domain=None):
        """gettherepatitionofratinggradeforthegivenres_ids.
            :paramadd_stats:flagtoaddstattotheresult
            :typeadd_stats:boolean
            :paramdomain:optionalextradomainoftheratingtoinclude/excludeinrepartition
            :returndictionnary
                ifnotadd_stats,thedictislike
                    -keyistheratingvalue(integer)
                    -valueisthenumberofobject(res_model,res_id)havingthevalue
                otherwise,keyisthevalueoftheinformation(string):eitherstatname(avg,total,...)or'repartition'
                containingthesamedictifadd_statswasFalse.
        """
        base_domain=expression.AND([self._rating_domain(),[('rating','>=',1)]])
        ifdomain:
            base_domain+=domain
        data=self.env['rating.rating'].read_group(base_domain,['rating'],['rating','res_id'])
        #initdictwithallposibleratevalue,except0(novaluefortherating)
        values=dict.fromkeys(range(1,6),0)
        values.update((d['rating'],d['rating_count'])fordindata)
        #addotherstats
        ifadd_stats:
            rating_number=sum(values.values())
            result={
                'repartition':values,
                'avg':sum(float(key*values[key])forkeyinvalues)/rating_numberifrating_number>0else0,
                'total':sum(it['rating_count']foritindata),
            }
            returnresult
        returnvalues

    defrating_get_grades(self,domain=None):
        """gettherepatitionofratinggradeforthegivenres_ids.
            :paramdomain:optionaldomainoftheratingtoinclude/excludeingradescomputation
            :returndictionnarywherethekeyisthegrade(great,okay,bad),andthevalue,thenumberofobject(res_model,res_id)havingthegrade
                    thegradearecomputeas   0-30%:Bad
                                                31-69%:Okay
                                                70-100%:Great
        """
        data=self._rating_get_repartition(domain=domain)
        res=dict.fromkeys(['great','okay','bad'],0)
        forkeyindata:
            ifkey>=RATING_LIMIT_SATISFIED:
                res['great']+=data[key]
            elifkey>=RATING_LIMIT_OK:
                res['okay']+=data[key]
            else:
                res['bad']+=data[key]
        returnres

    defrating_get_stats(self,domain=None):
        """getthestatisticsoftheratingrepatition
            :paramdomain:optionaldomainoftheratingtoinclude/excludeinstatisticcomputation
            :returndictionnarywhere
                -keyisthenameoftheinformation(statname)
                -valueisstatisticvalue:'percent'containstherepartitioninpercentage,'avg'istheaveragerate
                  and'total'isthenumberofrating
        """
        data=self._rating_get_repartition(domain=domain,add_stats=True)
        result={
            'avg':data['avg'],
            'total':data['total'],
            'percent':dict.fromkeys(range(1,6),0),
        }
        forrateindata['repartition']:
            result['percent'][rate]=(data['repartition'][rate]*100)/data['total']ifdata['total']>0else0
        returnresult
