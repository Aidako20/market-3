#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels,api,fields,_
fromflectra.exceptionsimportUserError
fromdatetimeimportdatetime
fromflectra.fieldsimportDatetime,Date
fromflectra.tools.miscimportformat_date
importpytz


defctx_tz(record,field):
    res_lang=None
    ctx=record._context
    tz_name=pytz.timezone(ctx.get('tz')orrecord.env.user.tz)
    timestamp=Datetime.from_string(record[field])
    ifctx.get('lang'):
        res_lang=record.env['res.lang']._lang_get(ctx['lang'])
    ifres_lang:
        timestamp=pytz.utc.localize(timestamp,is_dst=False)
        returndatetime.strftime(timestamp.astimezone(tz_name),res_lang.date_format+''+res_lang.time_format)
    returnDatetime.context_timestamp(record,timestamp)


classResCompany(models.Model):
    _inherit='res.company'

    l10n_fr_pos_cert_sequence_id=fields.Many2one('ir.sequence')

    @api.model
    defcreate(self,vals):
        company=super(ResCompany,self).create(vals)
        #whencreatinganewfrenchcompany,createthesecurisationsequenceaswell
        ifcompany._is_accounting_unalterable():
            sequence_fields=['l10n_fr_pos_cert_sequence_id']
            company._create_secure_sequence(sequence_fields)
        returncompany

    defwrite(self,vals):
        res=super(ResCompany,self).write(vals)
        #ifcountrychangedtofr,createthesecurisationsequence
        forcompanyinself:
            ifcompany._is_accounting_unalterable():
                sequence_fields=['l10n_fr_pos_cert_sequence_id']
                company._create_secure_sequence(sequence_fields)
        returnres

    def_action_check_pos_hash_integrity(self):
        returnself.env.ref('l10n_fr_pos_cert.action_report_pos_hash_integrity').report_action(self.id)

    def_check_pos_hash_integrity(self):
        """Checksthatallpostedorinvoicedposordershavestillthesamedataaswhentheywereposted
        andraisesanerrorwiththeresult.
        """
        defbuild_order_info(order):
            entry_reference=_('(Receiptref.:%s)')
            order_reference_string=order.pos_referenceandentry_reference%order.pos_referenceor''
            return[ctx_tz(order,'date_order'),order.l10n_fr_hash,order.name,order_reference_string,ctx_tz(order,'write_date')]

        msg_alert=''
        report_dict={}
        ifself._is_accounting_unalterable():
            orders=self.env['pos.order'].search([('state','in',['paid','done','invoiced']),('company_id','=',self.id),
                                    ('l10n_fr_secure_sequence_number','!=',0)],order="l10n_fr_secure_sequence_numberASC")

            ifnotorders:
                msg_alert=(_('Thereisn\'tanyorderflaggedfordatainalterabilityyetforthecompany%s.ThismechanismonlyrunsforpointofsaleordersgeneratedaftertheinstallationofthemoduleFrance-CertificationCGI286I-3bis.-POS',self.env.company.name))
                raiseUserError(msg_alert)

            previous_hash=u''
            corrupted_orders=[]
            fororderinorders:
                iforder.l10n_fr_hash!=order._compute_hash(previous_hash=previous_hash):
                    corrupted_orders.append(order.name)
                    msg_alert=(_('Corrupteddataonpointofsaleorderwithid%s.',order.id))
                previous_hash=order.l10n_fr_hash

            orders_sorted_date=orders.sorted(lambdao:o.date_order)
            start_order_info=build_order_info(orders_sorted_date[0])
            end_order_info=build_order_info(orders_sorted_date[-1])

            report_dict.update({
                'first_order_name':start_order_info[2],
                'first_order_hash':start_order_info[1],
                'first_order_date':start_order_info[0],
                'last_order_name':end_order_info[2],
                'last_order_hash':end_order_info[1],
                'last_order_date':end_order_info[0],
            })
            corrupted_orders=','.join([oforoincorrupted_orders])
            return{
                'result':report_dictor'None',
                'msg_alert':msg_alertor'None',
                'printing_date':format_date(self.env, Date.to_string(Date.today())),
                'corrupted_orders':corrupted_ordersor'None'
            }
        else:
            raiseUserError(_('Accountingisnotunalterableforthecompany%s.Thismechanismisdesignedforcompanieswhereaccountingisunalterable.')%self.env.company.name)
