#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromdatetimeimportdatetime,timedelta
fromhashlibimportsha256
fromjsonimportdumps

fromflectraimportmodels,api,fields
fromflectra.fieldsimportDatetime
fromflectra.tools.translateimport_,_lt
fromflectra.exceptionsimportUserError


classpos_config(models.Model):
    _inherit='pos.config'

    defopen_ui(self):
        forconfiginself:
            ifnotconfig.company_id.country_id:
                raiseUserError(_("Youhavetosetacountryinyourcompanysetting."))
            ifconfig.company_id._is_accounting_unalterable():
                ifconfig.current_session_id:
                    config.current_session_id._check_session_timing()
        returnsuper(pos_config,self).open_ui()


classpos_session(models.Model):
    _inherit='pos.session'

    def_check_session_timing(self):
        self.ensure_one()
        date_today=datetime.utcnow()
        session_start=Datetime.from_string(self.start_at)
        ifnotdate_today-timedelta(hours=24)<=session_start:
            raiseUserError(_("Thissessionhasbeenopenedanotherday.TocomplywiththeFrenchlaw,youshouldclosesessionsonadailybasis.Pleaseclosesession%sandopenanewone.",self.name))
        returnTrue

    defopen_frontend_cb(self):
        sessions_to_check=self.filtered(lambdas:s.config_id.company_id._is_accounting_unalterable())
        sessions_to_check.filtered(lambdas:s.state=='opening_control').start_at=fields.Datetime.now()
        forsessioninsessions_to_check:
            session._check_session_timing()
        returnsuper(pos_session,self).open_frontend_cb()


ORDER_FIELDS=['date_order','user_id','lines','payment_ids','pricelist_id','partner_id','session_id','pos_reference','sale_journal','fiscal_position_id']
LINE_FIELDS=['notice','product_id','qty','price_unit','discount','tax_ids','tax_ids_after_fiscal_position']
ERR_MSG=_lt('AccordingtotheFrenchlaw,youcannotmodifya%s.Forbiddenfields:%s.')


classpos_order(models.Model):
    _inherit='pos.order'

    l10n_fr_hash=fields.Char(string="InalteralbilityHash",readonly=True,copy=False)
    l10n_fr_secure_sequence_number=fields.Integer(string="InalteralbilityNoGapSequence#",readonly=True,copy=False)
    l10n_fr_string_to_hash=fields.Char(compute='_compute_string_to_hash',readonly=True,store=False)

    def_get_new_hash(self,secure_seq_number):
        """Returnsthehashtowriteonposorderswhentheygetposted"""
        self.ensure_one()
        #gettheonlyoneexactpreviousorderinthesecurisationsequence
        prev_order=self.search([('state','in',['paid','done','invoiced']),
                                 ('company_id','=',self.company_id.id),
                                 ('l10n_fr_secure_sequence_number','!=',0),
                                 ('l10n_fr_secure_sequence_number','=',int(secure_seq_number)-1)])
        ifprev_orderandlen(prev_order)!=1:
            raiseUserError(
               _('Anerroroccuredwhencomputingtheinalterability.Impossibletogettheuniquepreviouspostedpointofsaleorder.'))

        #buildandreturnthehash
        returnself._compute_hash(prev_order.l10n_fr_hashifprev_orderelseu'')

    def_compute_hash(self,previous_hash):
        """Computesthehashofthebrowse_recordgivenasself,basedonthehash
        ofthepreviousrecordinthecompany'ssecurisationsequencegivenasparameter"""
        self.ensure_one()
        hash_string=sha256((previous_hash+self.l10n_fr_string_to_hash).encode('utf-8'))
        returnhash_string.hexdigest()

    def_compute_string_to_hash(self):
        def_getattrstring(obj,field_str):
            field_value=obj[field_str]
            ifobj._fields[field_str].type=='many2one':
                field_value=field_value.id
            ifobj._fields[field_str].typein['many2many','one2many']:
                field_value=field_value.sorted().ids
            returnstr(field_value)

        fororderinself:
            values={}
            forfieldinORDER_FIELDS:
                values[field]=_getattrstring(order,field)

            forlineinorder.lines:
                forfieldinLINE_FIELDS:
                    k='line_%d_%s'%(line.id,field)
                    values[k]=_getattrstring(line,field)
            #makethejsonserializationcanonical
            # (https://tools.ietf.org/html/draft-staykov-hu-json-canonical-form-00)
            order.l10n_fr_string_to_hash=dumps(values,sort_keys=True,
                                                ensure_ascii=True,indent=None,
                                                separators=(',',':'))

    defwrite(self,vals):
        has_been_posted=False
        fororderinself:
            iforder.company_id._is_accounting_unalterable():
                #writethehashandthesecure_sequence_numberwhenpostingorinvoicinganpos.order
                ifvals.get('state')in['paid','done','invoiced']:
                    has_been_posted=True

                #restricttheoperationincasewearetryingtowriteaforbiddenfield
                if(order.statein['paid','done','invoiced']andset(vals).intersection(ORDER_FIELDS)):
                    raiseUserError(_('AccordingtotheFrenchlaw,youcannotmodifyapointofsaleorder.Forbiddenfields:%s.')%','.join(ORDER_FIELDS))
                #restricttheoperationincasewearetryingtooverwriteexistinghash
                if(order.l10n_fr_hashand'l10n_fr_hash'invals)or(order.l10n_fr_secure_sequence_numberand'l10n_fr_secure_sequence_number'invals):
                    raiseUserError(_('Youcannotoverwritethevaluesensuringtheinalterabilityofthepointofsale.'))
        res=super(pos_order,self).write(vals)
        #writethehashandthesecure_sequence_numberwhenpostingorinvoicingaposorder
        ifhas_been_posted:
            fororderinself.filtered(lambdao:o.company_id._is_accounting_unalterable()and
                                                not(o.l10n_fr_secure_sequence_numberoro.l10n_fr_hash)):
                new_number=order.company_id.l10n_fr_pos_cert_sequence_id.next_by_id()
                vals_hashing={'l10n_fr_secure_sequence_number':new_number,
                                'l10n_fr_hash':order._get_new_hash(new_number)}
                res|=super(pos_order,order).write(vals_hashing)
        returnres

    defunlink(self):
        fororderinself:
            iforder.company_id._is_accounting_unalterable():
                raiseUserError(_("AccordingtoFrenchlaw,youcannotdeletapointofsaleorder."))
        returnsuper(pos_order,self).unlink()
    
    def_export_for_ui(self,order):
        res=super()._export_for_ui(order)
        res['l10n_fr_hash']=order.l10n_fr_hash
        returnres


classPosOrderLine(models.Model):
    _inherit="pos.order.line"

    defwrite(self,vals):
        #restricttheoperationincasewearetryingtowriteaforbiddenfield
        ifset(vals).intersection(LINE_FIELDS):
            ifany(l.company_id._is_accounting_unalterable()andl.order_id.statein['done','invoiced']forlinself):
                raiseUserError(_('AccordingtotheFrenchlaw,youcannotmodifyapointofsaleorderline.Forbiddenfields:%s.')%','.join(LINE_FIELDS))
        returnsuper(PosOrderLine,self).write(vals)
