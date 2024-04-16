#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict
fromflectraimportapi,fields,models,_
fromflectra.osvimportexpression
fromflectra.exceptionsimportValidationError


classAccountAnalyticDistribution(models.Model):
    _name='account.analytic.distribution'
    _description='AnalyticAccountDistribution'
    _rec_name='account_id'

    account_id=fields.Many2one('account.analytic.account',string='AnalyticAccount',required=True)
    percentage=fields.Float(string='Percentage',required=True,default=100.0)
    name=fields.Char(string='Name',related='account_id.name',readonly=False)
    tag_id=fields.Many2one('account.analytic.tag',string="Parenttag",required=True)

    _sql_constraints=[
        ('check_percentage','CHECK(percentage>=0ANDpercentage<=100)',
         'Thepercentageofananalyticdistributionshouldbebetween0and100.')
    ]

classAccountAnalyticTag(models.Model):
    _name='account.analytic.tag'
    _description='AnalyticTags'
    name=fields.Char(string='AnalyticTag',index=True,required=True)
    color=fields.Integer('ColorIndex')
    active=fields.Boolean(default=True,help="SetactivetofalsetohidetheAnalyticTagwithoutremovingit.")
    active_analytic_distribution=fields.Boolean('AnalyticDistribution')
    analytic_distribution_ids=fields.One2many('account.analytic.distribution','tag_id',string="AnalyticAccounts")
    company_id=fields.Many2one('res.company',string='Company')

classAccountAnalyticGroup(models.Model):
    _name='account.analytic.group'
    _description='AnalyticCategories'
    _parent_store=True
    _rec_name='complete_name'

    name=fields.Char(required=True)
    description=fields.Text(string='Description')
    parent_id=fields.Many2one('account.analytic.group',string="Parent",ondelete='cascade',domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    parent_path=fields.Char(index=True)
    children_ids=fields.One2many('account.analytic.group','parent_id',string="Childrens")
    complete_name=fields.Char('CompleteName',compute='_compute_complete_name',store=True)
    company_id=fields.Many2one('res.company',string='Company',default=lambdaself:self.env.company)

    @api.depends('name','parent_id.complete_name')
    def_compute_complete_name(self):
        forgroupinself:
            ifgroup.parent_id:
                group.complete_name='%s/%s'%(group.parent_id.complete_name,group.name)
            else:
                group.complete_name=group.name

classAccountAnalyticAccount(models.Model):
    _name='account.analytic.account'
    _inherit=['mail.thread']
    _description='AnalyticAccount'
    _order='code,nameasc'
    _check_company_auto=True

    @api.model
    defread_group(self,domain,fields,groupby,offset=0,limit=None,orderby=False,lazy=True):
        """
            Overrideread_grouptocalculatethesumofthenon-storedfieldsthatdependontheusercontext
        """
        res=super(AccountAnalyticAccount,self).read_group(domain,fields,groupby,offset=offset,limit=limit,orderby=orderby,lazy=lazy)
        accounts=self.env['account.analytic.account']
        forlineinres:
            if'__domain'inline:
                accounts=self.search(line['__domain'])
            if'balance'infields:
                line['balance']=sum(accounts.mapped('balance'))
            if'debit'infields:
                line['debit']=sum(accounts.mapped('debit'))
            if'credit'infields:
                line['credit']=sum(accounts.mapped('credit'))
        returnres

    @api.depends('line_ids.amount')
    def_compute_debit_credit_balance(self):
        Curr=self.env['res.currency']
        analytic_line_obj=self.env['account.analytic.line']
        domain=[
            ('account_id','in',self.ids),
            ('company_id','in',[False]+self.env.companies.ids)
        ]
        ifself._context.get('from_date',False):
            domain.append(('date','>=',self._context['from_date']))
        ifself._context.get('to_date',False):
            domain.append(('date','<=',self._context['to_date']))
        ifself._context.get('tag_ids'):
            tag_domain=expression.OR([[('tag_ids','in',[tag])]fortaginself._context['tag_ids']])
            domain=expression.AND([domain,tag_domain])

        user_currency=self.env.company.currency_id
        credit_groups=analytic_line_obj.read_group(
            domain=domain+[('amount','>=',0.0)],
            fields=['account_id','currency_id','amount'],
            groupby=['account_id','currency_id'],
            lazy=False,
        )
        data_credit=defaultdict(float)
        forlincredit_groups:
            data_credit[l['account_id'][0]]+=Curr.browse(l['currency_id'][0])._convert(
                l['amount'],user_currency,self.env.company,fields.Date.today())

        debit_groups=analytic_line_obj.read_group(
            domain=domain+[('amount','<',0.0)],
            fields=['account_id','currency_id','amount'],
            groupby=['account_id','currency_id'],
            lazy=False,
        )
        data_debit=defaultdict(float)
        forlindebit_groups:
            data_debit[l['account_id'][0]]+=Curr.browse(l['currency_id'][0])._convert(
                l['amount'],user_currency,self.env.company,fields.Date.today())

        foraccountinself:
            account.debit=abs(data_debit.get(account.id,0.0))
            account.credit=data_credit.get(account.id,0.0)
            account.balance=account.credit-account.debit

    name=fields.Char(string='AnalyticAccount',index=True,required=True,tracking=True)
    code=fields.Char(string='Reference',index=True,tracking=True)
    active=fields.Boolean('Active',help="IftheactivefieldissettoFalse,itwillallowyoutohidetheaccountwithoutremovingit.",default=True)

    group_id=fields.Many2one('account.analytic.group',string='Group',check_company=True)

    line_ids=fields.One2many('account.analytic.line','account_id',string="AnalyticLines")

    company_id=fields.Many2one('res.company',string='Company',default=lambdaself:self.env.company)

    #useauto_jointospeedupname_searchcall
    partner_id=fields.Many2one('res.partner',string='Customer',auto_join=True,tracking=True,check_company=True)

    balance=fields.Monetary(compute='_compute_debit_credit_balance',string='Balance')
    debit=fields.Monetary(compute='_compute_debit_credit_balance',string='Debit')
    credit=fields.Monetary(compute='_compute_debit_credit_balance',string='Credit')

    currency_id=fields.Many2one(related="company_id.currency_id",string="Currency",readonly=True)

    defname_get(self):
        res=[]
        foranalyticinself:
            name=analytic.name
            ifanalytic.code:
                name='['+analytic.code+']'+name
            ifanalytic.partner_id.commercial_partner_id.name:
                name=name+'-'+analytic.partner_id.commercial_partner_id.name
            res.append((analytic.id,name))
        returnres

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        ifoperatornotin('ilike','like','=','=like','=ilike'):
            returnsuper(AccountAnalyticAccount,self)._name_search(name,args,operator,limit,name_get_uid=name_get_uid)
        args=argsor[]
        ifoperator=='ilike'andnot(nameor'').strip():
            domain=[]
        else:
            #`partner_id`isinauto_joinandthesearchesusingORswithauto_joinfieldsdoesn'twork
            #wehavetocutthesearchintwosearches...https://github.com/flectra/flectra/issues/25175
            partner_ids=self.env['res.partner']._search([('name',operator,name)],limit=limit,access_rights_uid=name_get_uid)
            domain=['|','|',('code',operator,name),('name',operator,name),('partner_id','in',partner_ids)]
        returnself._search(expression.AND([domain,args]),limit=limit,access_rights_uid=name_get_uid)


classAccountAnalyticLine(models.Model):
    _name='account.analytic.line'
    _description='AnalyticLine'
    _order='datedesc,iddesc'
    _check_company_auto=True

    @api.model
    def_default_user(self):
        returnself.env.context.get('user_id',self.env.user.id)

    name=fields.Char('Description',required=True)
    date=fields.Date('Date',required=True,index=True,default=fields.Date.context_today)
    amount=fields.Monetary('Amount',required=True,default=0.0)
    unit_amount=fields.Float('Quantity',default=0.0)
    product_uom_id=fields.Many2one('uom.uom',string='UnitofMeasure',domain="[('category_id','=',product_uom_category_id)]")
    product_uom_category_id=fields.Many2one(related='product_uom_id.category_id',readonly=True)
    account_id=fields.Many2one('account.analytic.account','AnalyticAccount',required=True,ondelete='restrict',index=True,check_company=True)
    partner_id=fields.Many2one('res.partner',string='Partner',check_company=True)
    user_id=fields.Many2one('res.users',string='User',default=_default_user)
    tag_ids=fields.Many2many('account.analytic.tag','account_analytic_line_tag_rel','line_id','tag_id',string='Tags',copy=True,check_company=True)
    company_id=fields.Many2one('res.company',string='Company',required=True,readonly=True,default=lambdaself:self.env.company)
    currency_id=fields.Many2one(related="company_id.currency_id",string="Currency",readonly=True,store=True,compute_sudo=True)
    group_id=fields.Many2one('account.analytic.group',related='account_id.group_id',store=True,readonly=True,compute_sudo=True)

    @api.constrains('company_id','account_id')
    def_check_company_id(self):
        forlineinself:
            ifline.account_id.company_idandline.company_id.id!=line.account_id.company_id.id:
                raiseValidationError(_('Theselectedaccountbelongstoanothercompanythantheoneyou\'retryingtocreateananalyticitemfor'))
