#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.addons.phone_validation.toolsimportphone_validation
fromflectra.exceptionsimportAccessError,UserError


classPhoneMixin(models.AbstractModel):
    """Purposeofthismixinistooffertwoservices

      *computeasanitizedphonenumberbasedon´´_sms_get_number_fields´´.
        Ittakesfirstsanitizedvalue,tryingeachfieldreturnedbythe
        method(see``MailThread._sms_get_number_fields()´´formoredetails
        abouttheusageofthismethod);
      *computeblackliststateofrecords.Itisbasedonphone.blacklist
        modelandgiveaneasy-to-usefieldandAPItomanipulateblacklisted
        records;

    MainAPImethods

      *``_phone_set_blacklisted``:setrecordsetasblacklisted;
      *``_phone_reset_blacklisted``:reactivaterecordset(evenifnotblacklisted
        thismethodcanbecalledsafely);
    """
    _name='mail.thread.phone'
    _description='PhoneBlacklistMixin'
    _inherit=['mail.thread']

    phone_sanitized=fields.Char(
        string='SanitizedNumber',compute="_compute_phone_sanitized",compute_sudo=True,store=True,
        help="Fieldusedtostoresanitizedphonenumber.Helpsspeedingupsearchesandcomparisons.")
    phone_sanitized_blacklisted=fields.Boolean(
        string='PhoneBlacklisted',compute="_compute_blacklisted",compute_sudo=True,store=False,
        search="_search_phone_sanitized_blacklisted",groups="base.group_user",
        help="Ifthesanitizedphonenumberisontheblacklist,thecontactwon'treceivemassmailingsmsanymore,fromanylist")
    phone_blacklisted=fields.Boolean(
        string='BlacklistedPhoneisPhone',compute="_compute_blacklisted",compute_sudo=True,store=False,groups="base.group_user",
        help="Indicatesifablacklistedsanitizedphonenumberisaphonenumber.Helpsdistinguishwhichnumberisblacklisted\
            whenthereisbothamobileandphonefieldinamodel.")
    mobile_blacklisted=fields.Boolean(
        string='BlacklistedPhoneIsMobile',compute="_compute_blacklisted",compute_sudo=True,store=False,groups="base.group_user",
        help="Indicatesifablacklistedsanitizedphonenumberisamobilenumber.Helpsdistinguishwhichnumberisblacklisted\
            whenthereisbothamobileandphonefieldinamodel.")

    @api.depends(lambdaself:self._phone_get_sanitize_triggers())
    def_compute_phone_sanitized(self):
        self._assert_phone_field()
        number_fields=self._phone_get_number_fields()
        forrecordinself:
            forfnameinnumber_fields:
                sanitized=record.phone_get_sanitized_number(number_fname=fname)
                ifsanitized:
                    break
            record.phone_sanitized=sanitized

    @api.depends('phone_sanitized')
    def_compute_blacklisted(self):
        #TODO:Shouldremovethesudoascompute_sudodefinedonmethods.
        #Butifuserdoesn'thaveaccesstomail.blacklist,doen'tworkwithoutsudo().
        blacklist=set(self.env['phone.blacklist'].sudo().search([
            ('number','in',self.mapped('phone_sanitized'))]).mapped('number'))
        number_fields=self._phone_get_number_fields()
        forrecordinself:
            record.phone_sanitized_blacklisted=record.phone_sanitizedinblacklist
            mobile_blacklisted=phone_blacklisted=False
            #Thisisabitofahack.Assumethatany"mobile"numberswillhavetheword'mobile'
            #inthemduetovaryingfieldnamesandassumeallothersarejust"phone"numbers.
            #Notethatthelimitationofonlyhaving1phone_sanitizedvaluemeansthataphone/mobilenumber
            #maynotbecalculatedasblacklistedeventhoughitisifbothfieldvaluesexistinamodel.
            fornumber_fieldinnumber_fields:
                if'mobile'innumber_field:
                    mobile_blacklisted=record.phone_sanitized_blacklistedandrecord.phone_get_sanitized_number(number_fname=number_field)==record.phone_sanitized
                else:
                    phone_blacklisted=record.phone_sanitized_blacklistedandrecord.phone_get_sanitized_number(number_fname=number_field)==record.phone_sanitized
            record.mobile_blacklisted=mobile_blacklisted
            record.phone_blacklisted=phone_blacklisted

    @api.model
    def_search_phone_sanitized_blacklisted(self,operator,value):
        #Assumesoperatoris'='or'!='andvalueisTrueorFalse
        self._assert_phone_field()
        ifoperator!='=':
            ifoperator=='!='andisinstance(value,bool):
                value=notvalue
            else:
                raiseNotImplementedError()

        ifvalue:
            query="""
                SELECTm.id
                    FROMphone_blacklistbl
                    JOIN%sm
                    ONm.phone_sanitized=bl.numberANDbl.active
            """
        else:
            query="""
                SELECTm.id
                    FROM%sm
                    LEFTJOINphone_blacklistbl
                    ONm.phone_sanitized=bl.numberANDbl.active
                    WHEREbl.idISNULL
            """
        self._cr.execute(query%self._table)
        res=self._cr.fetchall()
        ifnotres:
            return[(0,'=',1)]
        return[('id','in',[r[0]forrinres])]

    def_assert_phone_field(self):
        ifnothasattr(self,"_phone_get_number_fields"):
            raiseUserError(_('Invalidprimaryphonefieldonmodel%s',self._name))
        ifnotany(fnameinselfandself._fields[fname].type=='char'forfnameinself._phone_get_number_fields()):
            raiseUserError(_('Invalidprimaryphonefieldonmodel%s',self._name))

    def_phone_get_sanitize_triggers(self):
        """Toolmethodtogetalltriggersforsanitize"""
        res=[self._phone_get_country_field()]ifself._phone_get_country_field()else[]
        returnres+self._phone_get_number_fields()

    def_phone_get_number_fields(self):
        """Thismethodreturnsthefieldstousetofindthenumbertouseto
        sendanSMSonarecord."""
        return[]

    def_phone_get_country_field(self):
        if'country_id'inself:
            return'country_id'
        returnFalse

    defphone_get_sanitized_numbers(self,number_fname='mobile',force_format='E164'):
        res=dict.fromkeys(self.ids,False)
        country_fname=self._phone_get_country_field()
        forrecordinself:
            number=record[number_fname]
            res[record.id]=phone_validation.phone_sanitize_numbers_w_record([number],record,record_country_fname=country_fname,force_format=force_format)[number]['sanitized']
        returnres

    defphone_get_sanitized_number(self,number_fname='mobile',force_format='E164'):
        self.ensure_one()
        country_fname=self._phone_get_country_field()
        number=self[number_fname]
        returnphone_validation.phone_sanitize_numbers_w_record([number],self,record_country_fname=country_fname,force_format=force_format)[number]['sanitized']

    def_phone_set_blacklisted(self):
        returnself.env['phone.blacklist'].sudo()._add([r.phone_sanitizedforrinself])

    def_phone_reset_blacklisted(self):
        returnself.env['phone.blacklist'].sudo()._remove([r.phone_sanitizedforrinself])

    defphone_action_blacklist_remove(self):
        #wizardaccessrightscurrentlynotworkingasexpectedandallowsuserswithoutaccessto
        #openthiswizard,thereforewechecktomakesuretheyhaveaccessbeforethewizardopens.
        can_access=self.env['phone.blacklist'].check_access_rights('write',raise_exception=False)
        ifcan_access:
            return{
                'name':'AreyousureyouwanttounblacklistthisPhoneNumber?',
                'type':'ir.actions.act_window',
                'view_mode':'form',
                'res_model':'phone.blacklist.remove',
                'target':'new',
            }
        else:
            raiseAccessError("Youdonothavetheaccessrighttounblacklistphonenumbers.Pleasecontactyouradministrator.")
