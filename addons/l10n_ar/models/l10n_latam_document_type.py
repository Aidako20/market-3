fromflectraimportmodels,api,fields,_
fromflectra.exceptionsimportUserError


classL10nLatamDocumentType(models.Model):

    _inherit='l10n_latam.document.type'

    l10n_ar_letter=fields.Selection(
        selection='_get_l10n_ar_letters',
        string='Letters',
        help='LettersdefinedbytheAFIPthatcanbeusedtoidentifythe'
        'documentspresentedtothegovernmentandthatdependsonthe'
        'operationtype,theresponsibilityofboththeissuerandthe'
        'receptorofthedocument')
    purchase_aliquots=fields.Selection(
        [('not_zero','NotZero'),('zero','Zero')],help='Raiseanerrorifavendorbillismissencoded."NotZero"'
        'meanstheVATtaxesarerequiredfortheinvoicesrelatedtothisdocumenttype,andthosewith"Zero"means'
        'thatonly"VATNotApplicable"taxisallowed.')

    def_get_l10n_ar_letters(self):
        """Returnthelistofvaluesoftheselectionfield."""
        return[
            ('A','A'),
            ('B','B'),
            ('C','C'),
            ('E','E'),
            ('M','M'),
            ('T','T'),
            ('R','R'),
            ('X','X'),
            ('I','I'), #usedformappingofimports
        ]
    def_filter_taxes_included(self,taxes):
        """Inargentinaweincludetaxesdependingondocumentletter"""
        self.ensure_one()
        ifself.country_id.code=="AR"andself.l10n_ar_letterin['B','C','X','R']:
            returntaxes.filtered(lambdax:x.tax_group_id.l10n_ar_vat_afip_code)
        returnsuper()._filter_taxes_included(taxes)

    def_format_document_number(self,document_number):
        """MakevalidationofImportDispatchNumber
          *makingvalidationsonthedocument_number.Ifitiswrongitshouldraiseanexception
          *formatthedocument_numberagainstapatternandreturnit
        """
        self.ensure_one()
        ifself.country_id.code!="AR":
            returnsuper()._format_document_number(document_number)

        ifnotdocument_number:
            returnFalse

        msg="'%s'"+_("isnotavalidvaluefor")+"'%s'.<br/>%s"

        ifnotself.code:
            returndocument_number

        #ImportDispatchNumberValidator
        ifself.codein['66','67']:
            iflen(document_number)!=16:
                raiseUserError(msg%(document_number,self.name,_('ThenumberofimportDispatchmustbe16characters')))
            returndocument_number

        #InvoiceNumberValidator(ForEg:123-123)
        failed=False
        args=document_number.split('-')
        iflen(args)!=2:
            failed=True
        else:
            pos,number=args
            iflen(pos)>5ornotpos.isdigit():
                failed=True
            eliflen(number)>8ornotnumber.isdigit():
                failed=True
            document_number='{:>05s}-{:>08s}'.format(pos,number)
        iffailed:
            raiseUserError(msg%(document_number,self.name,_(
                'Thedocumentnumbermustbeenteredwithadash(-)andamaximumof5charactersforthefirstpart'
                'and8forthesecond.Thefollowingareexamplesofvalidnumbers:\n*1-1\n*0001-00000001'
                '\n*00001-00000001')))

        returndocument_number
