#-*-encoding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError

importre


classEfaktur(models.Model):
    _name="l10n_id_efaktur.efaktur.range"
    _description="AvailableE-fakturrange"

    company_id=fields.Many2one('res.company',required=True,default=lambdaself:self.env.company)
    max=fields.Char(compute='_compute_default',store=True,readonly=False)
    min=fields.Char(compute='_compute_default',store=True,readonly=False)
    available=fields.Integer(compute='_compute_available',store=True)

    @api.model
    defpop_number(self,company_id):
        range=self.search([('company_id','=',company_id)],order="minASC",limit=1)
        ifnotrange:
            returnNone

        popped=int(range.min)
        ifint(range.min)>=int(range.max):
            range.unlink()
        else:
            range.min='%013d'%(popped+1)
        returnpopped

    @api.model
    defpush_number(self,company_id,number):
        returnself.push_numbers(company_id,number,number)

    @api.model
    defpush_numbers(self,company_id,min,max):
        range_sup=self.search([('min','=','%013d'%(int(max)+1))])
        ifrange_sup:
            range_sup.min='%013d'%int(min)
            max=range_sup.max

        range_low=self.search([('max','=','%013d'%(int(max)-1))])
        ifrange_low:
            range_sup.unlink()
            range_low.max='%013d'%int(max)

        ifnotrange_supandnotrange_low:
            self.create({
                'company_id':company_id,
                'max':'%013d'%int(max),
                'min':'%013d'%int(min),
            })


    @api.constrains('min','max')
    def_constrains_min_max(self):
        forrecordinself:
            ifnotlen(record.min)==13ornotlen(record.max)==13:
                raiseValidationError(_("Thereshouldbe13digitsineachnumber."))

            ifrecord.min[:-8]!=record.max[:-8]:
                raiseValidationError(_("First5digitsshouldbesameinStartNumberandEndNumber."))

            ifint(record.min[-8:])>int(record.max[-8:]):
                raiseValidationError(_("Last8digitsofEndNumbershouldbegreaterthanthelast8digitofStartNumber"))

            if(int(record.max)-int(record.min))>10000:
                raiseValidationError(_("Thedifferencebetweenthetwonumbersmustnotbegreaterthan10.000"))

            #Thenumberofrecordsshouldalwaysbeverysmall,soitisoktosearchinloop
            ifself.search([
                '&',('id','!=',record.id),'|','|',
                '&',('min','<=',record.max),('max','>=',record.max),
                '&',('min','<=',record.min),('max','>=',record.min),
                '&',('min','>=',record.min),('max','<=',record.max),
            ]):
                raiseValidationError(_('Efakturinterleavingrangedetected'))

    @api.depends('min','max')
    def_compute_available(self):
        forrecordinself:
            record.available=1+int(record.max)-int(record.min)

    @api.depends('company_id')
    def_compute_default(self):
        forrecordinself:
            query="""
                SELECTMAX(SUBSTRING(l10n_id_tax_numberFROM4))
                FROMaccount_move
                WHEREl10n_id_tax_numberISNOTNULL
                  ANDcompany_id=%s
            """
            self.env.cr.execute(query,[record.company_id.id])
            max_used=int(self.env.cr.fetchone()[0]or0)
            max_available=int(self.env['l10n_id_efaktur.efaktur.range'].search([('company_id','=',record.company_id.id)],order='maxDESC',limit=1).max)
            record.min=record.max='%013d'%(max(max_available,max_used)+1)

    @api.onchange('min')
    def_onchange_min(self):
        min_val=re.sub(r'\D','',str(self.min))or0
        self.min='%013d'%int(min_val)
        ifnotself.maxorint(self.min)>int(self.max):
            self.max=self.min

    @api.onchange('max')
    def_onchange_max(self):
        max_val=re.sub(r'\D','',str(self.max))or0
        self.max='%013d'%int(max_val)
        ifnotself.minorint(self.min)>int(self.max):
            self.min=self.max
