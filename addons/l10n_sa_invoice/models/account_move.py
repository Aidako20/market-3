#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.toolsimportfloat_repr


classAccountMove(models.Model):
    _inherit='account.move'

    l10n_sa_delivery_date=fields.Date(string='DeliveryDate',default=fields.Date.context_today,copy=False,
                                        readonly=True,states={'draft':[('readonly',False)]},
                                        help="Incaseofmultipledeliveries,youshouldtakethedateofthelatestone.")
    l10n_sa_show_delivery_date=fields.Boolean(compute='_compute_show_delivery_date')
    l10n_sa_qr_code_str=fields.Char(string='ZatkaQRCode',compute='_compute_qr_code_str')
    l10n_sa_confirmation_datetime=fields.Datetime(string='ConfirmationDate',readonly=True,copy=False)

    @api.depends('country_code','move_type')
    def_compute_show_delivery_date(self):
        formoveinself:
            move.l10n_sa_show_delivery_date=move.country_code=='SA'andmove.move_typein('out_invoice','out_refund')

    @api.depends('amount_total_signed','amount_tax_signed','l10n_sa_confirmation_datetime','company_id','company_id.vat')
    def_compute_qr_code_str(self):
        """GeneratetheqrcodeforSaudie-invoicing.Specsareavailableatthefollowinglinkatpage23
        https://zatca.gov.sa/ar/E-Invoicing/SystemsDevelopers/Documents/20210528_ZATCA_Electronic_Invoice_Security_Features_Implementation_Standards_vShared.pdf
        """
        defget_qr_encoding(tag,field):
            company_name_byte_array=field.encode()
            company_name_tag_encoding=tag.to_bytes(length=1,byteorder='big')
            company_name_length_encoding=len(company_name_byte_array).to_bytes(length=1,byteorder='big')
            returncompany_name_tag_encoding+company_name_length_encoding+company_name_byte_array

        forrecordinself:
            qr_code_str=''
            ifrecord.l10n_sa_confirmation_datetimeandrecord.company_id.vat:
                seller_name_enc=get_qr_encoding(1,record.company_id.display_name)
                company_vat_enc=get_qr_encoding(2,record.company_id.vat)
                time_sa=fields.Datetime.context_timestamp(self.with_context(tz='Asia/Riyadh'),record.l10n_sa_confirmation_datetime)
                timestamp_enc=get_qr_encoding(3,time_sa.isoformat())
                invoice_total_enc=get_qr_encoding(4,float_repr(abs(record.amount_total_signed),2))
                total_vat_enc=get_qr_encoding(5,float_repr(abs(record.amount_tax_signed),2))

                str_to_encode=seller_name_enc+company_vat_enc+timestamp_enc+invoice_total_enc+total_vat_enc
                qr_code_str=base64.b64encode(str_to_encode).decode()
            record.l10n_sa_qr_code_str=qr_code_str

    def_post(self,soft=True):
        res=super()._post(soft)
        forrecordinself:
            ifrecord.country_code=='SA'andrecord.move_typein('out_invoice','out_refund'):
                ifnotrecord.l10n_sa_show_delivery_date:
                    raiseUserError(_('DeliveryDatecannotbeempty'))
                self.write({
                    'l10n_sa_confirmation_datetime':fields.Datetime.now()
                })
        returnres
