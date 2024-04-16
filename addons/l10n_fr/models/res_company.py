#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api,_


classResCompany(models.Model):
    _inherit='res.company'

    l10n_fr_closing_sequence_id=fields.Many2one('ir.sequence','Sequencetousetobuildsaleclosings',readonly=True)
    siret=fields.Char(related='partner_id.siret',string='SIRET',size=14,readonly=False)
    ape=fields.Char(string='APE')

    @api.model
    def_get_unalterable_country(self):
        return['FR','MF','MQ','NC','PF','RE','GF','GP','TF']#ThesecodescorrespondtoFranceandDOM-TOM.

    def_is_vat_french(self):
        returnself.vatandself.vat.startswith('FR')andlen(self.vat)==13

    def_is_accounting_unalterable(self):
        ifnotself.vatandnotself.country_id:
            returnFalse
        returnself.country_idandself.country_id.codeinself._get_unalterable_country()

    @api.model
    defcreate(self,vals):
        company=super(ResCompany,self).create(vals)
        #whencreatinganewfrenchcompany,createthesecurisationsequenceaswell
        ifcompany._is_accounting_unalterable():
            sequence_fields=['l10n_fr_closing_sequence_id']
            company._create_secure_sequence(sequence_fields)
        returncompany

    defwrite(self,vals):
        res=super(ResCompany,self).write(vals)
        #ifcountrychangedtofr,createthesecurisationsequence
        forcompanyinself:
            ifcompany._is_accounting_unalterable():
                sequence_fields=['l10n_fr_closing_sequence_id']
                company._create_secure_sequence(sequence_fields)
        returnres

    def_create_secure_sequence(self,sequence_fields):
        """Thisfunctioncreatesano_gapsequenceoneachcompanyinselfthatwillensure
        auniquenumberisgiventoallpostedaccount.moveinsuchawaythatwecanalways
        findthepreviousmoveofajournalentryonaspecificjournal.
        """
        forcompanyinself:
            vals_write={}
            forseq_fieldinsequence_fields:
                ifnotcompany[seq_field]:
                    vals={
                        'name':_('Securisationof%s-%s')%(seq_field,company.name),
                        'code':'FRSECURE%s-%s'%(company.id,seq_field),
                        'implementation':'no_gap',
                        'prefix':'',
                        'suffix':'',
                        'padding':0,
                        'company_id':company.id}
                    seq=self.env['ir.sequence'].create(vals)
                    vals_write[seq_field]=seq.id
            ifvals_write:
                company.write(vals_write)
