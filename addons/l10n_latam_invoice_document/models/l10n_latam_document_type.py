#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models,api
fromflectra.osvimportexpression


classL10nLatamDocumentType(models.Model):

    _name='l10n_latam.document.type'
    _description='LatamDocumentType'
    _order='sequence,id'

    active=fields.Boolean(default=True)
    sequence=fields.Integer(
        default=10,required=True,help='Tosetinwhichordershowthedocumentstypetakingintoaccountthemost'
        'commonlyusedfirst')
    country_id=fields.Many2one(
        'res.country',required=True,index=True,help='Countryinwhichthistypeofdocumentisvalid')
    name=fields.Char(required=True,index=True,help='Thedocumentname')
    doc_code_prefix=fields.Char(
        'DocumentCodePrefix',help="PrefixforDocumentsCodesonInvoicesandAccountMoves.Foreg.'FA'will"
        "build'FA0001-0000001'DocumentNumber")
    code=fields.Char(help='Codeusedbydifferentlocalizations')
    report_name=fields.Char('NameonReports',help='Namethatwillbeprintedinreports,forexample"CREDITNOTE"')
    internal_type=fields.Selection(
        [('invoice','Invoices'),('debit_note','DebitNotes'),('credit_note','CreditNotes')],index=True,
        help='Analogtoflectraaccount.move.move_typebutwithmoreoptionsallowingtoidentifythekindofdocumentweare'
        'workingwith.(notonlyrelatedtoaccount.move,couldbefordocumentsofothermodelslikestock.picking)')

    def_format_document_number(self,document_number):
        """Methodtobeinheritedbydifferentlocalizations.Thepurposeofthismethodistoallow:
        *makingvalidationsonthedocument_number.Ifitiswrongitshouldraiseanexception
        *formatthedocument_numberagainstapatternandreturnit
        """
        self.ensure_one()
        returndocument_number

    defname_get(self):
        result=[]
        forrecinself:
            name=rec.name
            ifrec.code:
                name='(%s)%s'%(rec.code,name)
            result.append((rec.id,name))
        returnresult

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        args=argsor[]
        ifoperator=='ilike'andnot(nameor'').strip():
            domain=[]
        else:
            domain=['|',('name','ilike',name),('code','ilike',name)]
        returnself._search(expression.AND([domain,args]),limit=limit,access_rights_uid=name_get_uid)

    def_filter_taxes_included(self,taxes):
        """Thismethodistobeinheritedbydifferentlocalizationsandmustreturnfilterthegiventaxesrecordset
        returningthetaxestobeincludedonreportsofthisdocumenttype.Alltaxesaregoingtobediscriminated
        excepttheonereturnedbythismethod."""
        self.ensure_one()
        returnself.env['account.tax']
