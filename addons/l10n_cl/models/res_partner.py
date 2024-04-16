#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importstdnum
fromflectraimport_,api,fields,models
fromflectra.exceptionsimportUserError,ValidationError


classResPartner(models.Model):
    _name='res.partner'
    _inherit='res.partner'

    _sii_taxpayer_types=[
        ('1',_('VATAffected(1stCategory)')),
        ('2',_('FeesReceiptIssuer(2ndcategory)')),
        ('3',_('EndConsumer')),
        ('4',_('Foreigner')),
    ]

    l10n_cl_sii_taxpayer_type=fields.Selection(
        _sii_taxpayer_types,'TaxpayerType',index=True,
        help='1-VATAffected(1stCategory)(Mostofthecases)\n'
             '2-FeesReceiptIssuer(Appliestosupplierswhoissuefeesreceipt)\n'
             '3-Endconsumer(onlyreceipts)\n'
             '4-Foreigner')

    @api.model
    def_commercial_fields(self):
        returnsuper()._commercial_fields()+['l10n_cl_sii_taxpayer_type']

    def_format_vat_cl(self,values):
        identification_types=[self.env.ref('l10n_latam_base.it_vat').id,self.env.ref('l10n_cl.it_RUT').id,
                                self.env.ref('l10n_cl.it_RUN').id]
        country=self.env["res.country"].browse(values.get('country_id'))
        identification_type=self.env['l10n_latam.identification.type'].browse(
            values.get('l10n_latam_identification_type_id')
        )
        partner_country_is_chile=country.code=="CL"oridentification_type.country_id.code=="CL"
        ifpartner_country_is_chileand\
                values.get('l10n_latam_identification_type_id')inidentification_typesandvalues.get('vat'):
            returnstdnum.util.get_cc_module('cl','vat').format(values['vat']).replace('.','').replace(
                'CL','').upper()
        else:
            returnvalues['vat']

    def_format_dotted_vat_cl(self,vat):
        vat_l=vat.split('-')
        n_vat,n_dv=vat_l[0],vat_l[1]
        return'%s-%s'%(format(int(n_vat),',d').replace(',','.'),n_dv)

    @api.model
    defcreate(self,values):
        ifvalues.get('vat'):
            values['vat']=self._format_vat_cl(values)
        returnsuper().create(values)

    defwrite(self,values):
        ifany(fieldinvaluesforfieldin['vat','l10n_latam_identification_type_id','country_id']):
            forrecordinself:
                vat_values={
                    'vat':values.get('vat',record.vat),
                    'l10n_latam_identification_type_id':values.get(
                        'l10n_latam_identification_type_id',record.l10n_latam_identification_type_id.id),
                    'country_id':values.get('country_id',record.country_id.id)
                }
                values['vat']=self._format_vat_cl(vat_values)
        returnsuper().write(values)
