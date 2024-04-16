#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,tools


classProfitabilityAnalysis(models.Model):

    _name="project.profitability.report"
    _description="ProjectProfitabilityReport"
    _order='project_id,sale_line_id'
    _auto=False

    analytic_account_id=fields.Many2one('account.analytic.account',string='AnalyticAccount',readonly=True)
    project_id=fields.Many2one('project.project',string='Project',readonly=True)
    currency_id=fields.Many2one('res.currency',string='ProjectCurrency',readonly=True)
    company_id=fields.Many2one('res.company',string='ProjectCompany',readonly=True)
    user_id=fields.Many2one('res.users',string='ProjectManager',readonly=True)
    partner_id=fields.Many2one('res.partner',string='Customer',readonly=True)
    line_date=fields.Date("Date",readonly=True)
    #cost
    timesheet_unit_amount=fields.Float("TimesheetDuration",digits=(16,2),readonly=True,group_operator="sum")
    timesheet_cost=fields.Float("TimesheetCost",digits=(16,2),readonly=True,group_operator="sum")
    expense_cost=fields.Float("OtherCosts",digits=(16,2),readonly=True,group_operator="sum")
    #salerevenue
    order_confirmation_date=fields.Datetime('SalesOrderConfirmationDate',readonly=True)
    sale_line_id=fields.Many2one('sale.order.line',string='SaleOrderLine',readonly=True)
    sale_order_id=fields.Many2one('sale.order',string='SaleOrder',readonly=True)
    product_id=fields.Many2one('product.product',string='Product',readonly=True)

    amount_untaxed_to_invoice=fields.Float("UntaxedAmounttoInvoice",digits=(16,2),readonly=True,group_operator="sum")
    amount_untaxed_invoiced=fields.Float("UntaxedAmountInvoiced",digits=(16,2),readonly=True,group_operator="sum")
    expense_amount_untaxed_to_invoice=fields.Float("UntaxedAmounttoRe-invoice",digits=(16,2),readonly=True,group_operator="sum")
    expense_amount_untaxed_invoiced=fields.Float("UntaxedAmountRe-invoiced",digits=(16,2),readonly=True,group_operator="sum")
    other_revenues=fields.Float("OtherRevenues",digits=(16,2),readonly=True,group_operator="sum",
                                  help="Allrevenuesthatarenotfromtimesheetsandthatarelinkedtotheanalyticaccountoftheproject.")
    margin=fields.Float("Margin",digits=(16,2),readonly=True,group_operator="sum")

    _depends={
        'sale.order.line':[
            'order_id',
            'invoice_status',
            'price_reduce',
            'product_id',
            'qty_invoiced',
            'untaxed_amount_invoiced',
            'untaxed_amount_to_invoice',
            'currency_id',
            'company_id',
            'is_downpayment',
            'project_id',
            'task_id',
            'qty_delivered_method',
        ],
        'sale.order':[
            'date_order',
            'user_id',
            'partner_id',
            'currency_id',
            'analytic_account_id',
            'order_line',
            'invoice_status',
            'amount_untaxed',
            'currency_rate',
            'company_id',
            'project_id',
        ],
    }

    definit(self):
        tools.drop_view_if_exists(self._cr,self._table)
        query="""
            CREATEVIEW%sAS(
                SELECT
                    sub.idasid,
                    sub.project_idasproject_id,
                    sub.user_idasuser_id,
                    sub.sale_line_idassale_line_id,
                    sub.analytic_account_idasanalytic_account_id,
                    sub.partner_idaspartner_id,
                    sub.company_idascompany_id,
                    sub.currency_idascurrency_id,
                    sub.sale_order_idassale_order_id,
                    sub.order_confirmation_dateasorder_confirmation_date,
                    sub.product_idasproduct_id,
                    sub.sale_qty_delivered_methodassale_qty_delivered_method,
                    sub.expense_amount_untaxed_to_invoiceasexpense_amount_untaxed_to_invoice,
                    sub.expense_amount_untaxed_invoicedasexpense_amount_untaxed_invoiced,
                    sub.amount_untaxed_to_invoiceasamount_untaxed_to_invoice,
                    sub.amount_untaxed_invoicedasamount_untaxed_invoiced,
                    sub.timesheet_unit_amountastimesheet_unit_amount,
                    sub.timesheet_costastimesheet_cost,
                    sub.expense_costasexpense_cost,
                    sub.other_revenuesasother_revenues,
                    sub.line_dateasline_date,
                    (sub.expense_amount_untaxed_to_invoice+sub.expense_amount_untaxed_invoiced+sub.amount_untaxed_to_invoice+
                        sub.amount_untaxed_invoiced+sub.other_revenues+sub.timesheet_cost+sub.expense_cost)
                        asmargin
                FROM(
                    SELECT
                        ROW_NUMBER()OVER(ORDERBYP.id,SOL.id)ASid,
                        P.idASproject_id,
                        P.user_idASuser_id,
                        SOL.idASsale_line_id,
                        P.analytic_account_idASanalytic_account_id,
                        P.partner_idASpartner_id,
                        C.idAScompany_id,
                        C.currency_idAScurrency_id,
                        S.idASsale_order_id,
                        S.date_orderASorder_confirmation_date,
                        SOL.product_idASproduct_id,
                        SOL.qty_delivered_methodASsale_qty_delivered_method,
                        COST_SUMMARY.expense_amount_untaxed_to_invoiceASexpense_amount_untaxed_to_invoice,
                        COST_SUMMARY.expense_amount_untaxed_invoicedASexpense_amount_untaxed_invoiced,
                        COST_SUMMARY.amount_untaxed_to_invoiceASamount_untaxed_to_invoice,
                        COST_SUMMARY.amount_untaxed_invoicedASamount_untaxed_invoiced,
                        COST_SUMMARY.timesheet_unit_amountAStimesheet_unit_amount,
                        COST_SUMMARY.timesheet_costAStimesheet_cost,
                        COST_SUMMARY.expense_costASexpense_cost,
                        COST_SUMMARY.other_revenuesASother_revenues,
                        COST_SUMMARY.line_date::dateASline_date
                    FROMproject_projectP
                        JOINres_companyCONC.id=P.company_id
                        LEFTJOIN(
                            --Eachcostsandrevenueswillberetrievedindividuallybysub-requests
                            --Thisisrequiredtoabletogetthedate
                            SELECT
                                project_id,
                                analytic_account_id,
                                sale_line_id,
                                SUM(timesheet_unit_amount)AStimesheet_unit_amount,
                                SUM(timesheet_cost)AStimesheet_cost,
                                SUM(expense_cost)ASexpense_cost,
                                SUM(other_revenues)ASother_revenues,
                                SUM(expense_amount_untaxed_to_invoice)ASexpense_amount_untaxed_to_invoice,
                                SUM(expense_amount_untaxed_invoiced)ASexpense_amount_untaxed_invoiced,
                                SUM(amount_untaxed_to_invoice)ASamount_untaxed_to_invoice,
                                SUM(amount_untaxed_invoiced)ASamount_untaxed_invoiced,
                                line_dateASline_date
                            FROM(
                                --Getthetimesheetcosts
                                SELECT
                                    P.idASproject_id,
                                    P.analytic_account_idASanalytic_account_id,
                                    TS.so_lineASsale_line_id,
                                    TS.unit_amountAStimesheet_unit_amount,
                                    TS.amountAStimesheet_cost,
                                    0.0ASother_revenues,
                                    0.0ASexpense_cost,
                                    0.0ASexpense_amount_untaxed_to_invoice,
                                    0.0ASexpense_amount_untaxed_invoiced,
                                    0.0ASamount_untaxed_to_invoice,
                                    0.0ASamount_untaxed_invoiced,
                                    TS.dateASline_date
                                FROMaccount_analytic_lineTS,project_projectP
                                WHERETS.project_idISNOTNULLANDP.id=TS.project_idANDP.active='t'ANDP.allow_timesheets='t'

                                UNIONALL

                                --Gettheotherrevenues(productsthatarenotservices)
                                SELECT
                                    P.idASproject_id,
                                    P.analytic_account_idASanalytic_account_id,
                                    AAL.so_lineASsale_line_id,
                                    0.0AStimesheet_unit_amount,
                                    0.0AStimesheet_cost,
                                    AAL.amount+COALESCE(AAL_RINV.amount,0)ASother_revenues,
                                    0.0ASexpense_cost,
                                    0.0ASexpense_amount_untaxed_to_invoice,
                                    0.0ASexpense_amount_untaxed_invoiced,
                                    0.0ASamount_untaxed_to_invoice,
                                    0.0ASamount_untaxed_invoiced,
                                    AAL.dateASline_date
                                FROMproject_projectP
                                    JOINaccount_analytic_accountAAONP.analytic_account_id=AA.id
                                    JOINaccount_analytic_lineAALONAAL.account_id=AA.id
                                    LEFTJOINsale_order_line_invoice_relSOINVONSOINV.invoice_line_id=AAL.move_id
                                    LEFTJOINsale_order_lineSOLONSOINV.order_line_id=SOL.id
                                    LEFTJOINaccount_move_lineAMLONAAL.move_id=AML.id
                                                                   ANDAML.parent_state='posted'
                                                                   ANDAML.exclude_from_invoice_tab='f'
                                    --Checkifit'snotaCreditNoteforaVendorBill
                                    LEFTJOINaccount_moveRBILLONRBILL.id=AML.move_id
                                    LEFTJOINaccount_move_lineBILLLONBILLL.move_id=RBILL.reversed_entry_id
                                                                  ANDBILLL.parent_state='posted'
                                                                  ANDBILLL.exclude_from_invoice_tab='f'
                                                                  ANDBILLL.product_id=AML.product_id
                                    --Checkifit'snotanInvoicereversedbyaCreditNote
                                    LEFTJOINaccount_moveRINVONRINV.reversed_entry_id=AML.move_id
                                    LEFTJOINaccount_move_lineRINVLONRINVL.move_id=RINV.id
                                                                  ANDRINVL.parent_state='posted'
                                                                  ANDRINVL.exclude_from_invoice_tab='f'
                                                                  ANDRINVL.product_id=AML.product_id
                                    LEFTJOINaccount_analytic_lineAAL_RINVONRINVL.id=AAL_RINV.move_id
                                WHEREAAL.amount>0.0ANDAAL.project_idISNULLANDP.active='t'
                                    ANDP.allow_timesheets='t'
                                    ANDBILLL.idISNULL
                                    AND(SOL.idISNULL
                                        OR(SOL.is_expenseISNOTTRUEANDSOL.is_downpaymentISNOTTRUEANDSOL.is_serviceISNOTTRUE))

                                UNIONALL

                                --Gettheexpensecostsfromaccountanalyticline
                                SELECT
                                    P.idASproject_id,
                                    P.analytic_account_idASanalytic_account_id,
                                    AAL.so_lineASsale_line_id,
                                    0.0AStimesheet_unit_amount,
                                    0.0AStimesheet_cost,
                                    0.0ASother_revenues,
                                    AAL.amount+COALESCE(AML_RBILLL.amount,0)ASexpense_cost,
                                    0.0ASexpense_amount_untaxed_to_invoice,
                                    0.0ASexpense_amount_untaxed_invoiced,
                                    0.0ASamount_untaxed_to_invoice,
                                    0.0ASamount_untaxed_invoiced,
                                    AAL.dateASline_date
                                FROMproject_projectP
                                    JOINaccount_analytic_accountAAONP.analytic_account_id=AA.id
                                    JOINaccount_analytic_lineAALONAAL.account_id=AA.id
                                    LEFTJOINaccount_move_lineAMLONAAL.move_id=AML.id
                                                                   ANDAML.parent_state='posted'
                                                                   ANDAML.exclude_from_invoice_tab='f'
                                    --Checkifit'snotaCreditNoteforanInvoice
                                    LEFTJOINaccount_moveRINVONRINV.id=AML.move_id
                                    LEFTJOINaccount_move_lineINVLONINVL.move_id=RINV.reversed_entry_id
                                                                    ANDINVL.parent_state='posted'
                                                                    ANDINVL.exclude_from_invoice_tab='f'
                                                                    ANDINVL.product_id=AML.product_id
                                    --Checkifit'snotaBillreversedbyaCreditNote
                                    LEFTJOINaccount_moveRBILLONRBILL.reversed_entry_id=AML.move_id
                                    LEFTJOINaccount_move_lineRBILLLONRBILLL.move_id=RBILL.id
                                                                      ANDRBILLL.parent_state='posted'
                                                                      ANDRBILLL.exclude_from_invoice_tab='f'
                                                                      ANDRBILLL.product_id=AML.product_id
                                    LEFTJOINaccount_analytic_lineAML_RBILLLONRBILLL.id=AML_RBILLL.move_id
                                    --CheckiftheAALisnotrelatedtoaconsumeddownpayment(whentheSOLisfullyinvoiced-withdownpaymentdiscounted.)
                                    LEFTJOINsale_order_line_invoice_relSOINVDOWNONSOINVDOWN.invoice_line_id=AML.id
                                    LEFTJOINsale_order_lineSOLDOWNonSOINVDOWN.order_line_id=SOLDOWN.idANDSOLDOWN.is_downpayment='t'
                                WHEREAAL.amount<0.0ANDAAL.project_idISNULL
                                  ANDINVL.idISNULL
                                  ANDSOLDOWN.idISNULL
                                  ANDP.active='t'ANDP.allow_timesheets='t'

                                UNIONALL

                                --Getthefollowingvalues:expenseamountuntaxedtoinvoice/invoiced,amountuntaxedtoinvoice/invoiced
                                --Thesevalueshavetobecomputedfromalltherecordsretrievedjustabovebutgroupedbyprojectandsaleorderline
                                SELECT
                                    AMOUNT_UNTAXED.project_idASproject_id,
                                    AMOUNT_UNTAXED.analytic_account_idASanalytic_account_id,
                                    AMOUNT_UNTAXED.sale_line_idASsale_line_id,
                                    0.0AStimesheet_unit_amount,
                                    0.0AStimesheet_cost,
                                    0.0ASother_revenues,
                                    0.0ASexpense_cost,
                                    CASE
                                        WHENSOL.qty_delivered_method='analytic'THEN(SOL.untaxed_amount_to_invoice/CASECOALESCE(S.currency_rate,0)WHEN0THEN1.0ELSES.currency_rateEND)
                                        ELSE0.0
                                    ENDASexpense_amount_untaxed_to_invoice,
                                    CASE
                                        WHENSOL.qty_delivered_method='analytic'ANDSOL.invoice_status='invoiced'
                                        THEN
                                            CASE
                                                WHENT.expense_policy='sales_price'
                                                THEN(SOL.untaxed_amount_invoiced/CASECOALESCE(S.currency_rate,0)WHEN0THEN1.0ELSES.currency_rateEND)
                                                ELSE-AMOUNT_UNTAXED.expense_cost
                                            END
                                        ELSE0.0
                                    ENDASexpense_amount_untaxed_invoiced,
                                    CASE
                                        WHENSOL.qty_delivered_methodIN('timesheet','manual')THEN(SOL.untaxed_amount_to_invoice/CASECOALESCE(S.currency_rate,0)WHEN0THEN1.0ELSES.currency_rateEND)
                                        ELSE0.0
                                    ENDASamount_untaxed_to_invoice,
                                    CASE
                                        WHENSOL.qty_delivered_methodIN('timesheet','manual')THEN(SOL.untaxed_amount_invoiced/CASECOALESCE(S.currency_rate,0)WHEN0THEN1.0ELSES.currency_rateEND)
                                        ELSE0.0
                                    ENDASamount_untaxed_invoiced,
                                    S.date_orderASline_date
                                FROMproject_projectP
                                    JOINres_companyCONC.id=P.company_id
                                    LEFTJOIN(
                                        --GetsSOLlinkedtotimesheets
                                        SELECT
                                            P.idASproject_id,
                                            P.analytic_account_idASanalytic_account_id,
                                            AAL.so_lineASsale_line_id,
                                            0.0ASexpense_cost
                                        FROMaccount_analytic_lineAAL,project_projectP
                                        WHEREAAL.project_idISNOTNULLANDP.id=AAL.project_idANDP.active='t'
                                        GROUPBYP.id,AAL.so_line
                                        UNION
                                        --ServiceSOLlinkedtoaprojecttaskANDnotyettimesheeted
                                        SELECT
                                            P.idASproject_id,
                                            P.analytic_account_idASanalytic_account_id,
                                            SOL.idASsale_line_id,
                                            0.0ASexpense_cost
                                        FROMsale_order_lineSOL
                                        JOINproject_taskTONT.sale_line_id=SOL.id
                                        JOINproject_projectPONT.project_id=P.id
                                        LEFTJOINaccount_analytic_lineAALONAAL.task_id=T.id
                                        WHERESOL.is_service='t'
                                          ANDAAL.idISNULL--nottimesheeted
                                          ANDP.active='t'ANDP.allow_timesheets='t'
                                        GROUPBYP.id,SOL.id
                                        UNION
                                        --ServiceSOLlinkedtoprojectANDnotyettimesheeted
                                        SELECT
                                            P.idASproject_id,
                                            P.analytic_account_idASanalytic_account_id,
                                            SOL.idASsale_line_id,
                                            0.0ASexpense_cost
                                        FROMsale_order_lineSOL
                                        JOINproject_projectPONP.sale_line_id=SOL.id
                                        LEFTJOINaccount_analytic_lineAALONAAL.project_id=P.id
                                        LEFTJOINproject_taskTONT.sale_line_id=SOL.id
                                        WHERESOL.is_service='t'
                                          ANDAAL.idISNULL--nottimesheeted
                                          AND(T.idISNULLORT.project_id!=P.id)--notlinkedtoataskinthisproject
                                          ANDP.active='t'ANDP.allow_timesheets='t'
                                        GROUPBYP.id,SOL.id
                                        UNION
                                        --ServiceSOLlinkedtoanalyticaccountANDnotyettimesheeted
                                        SELECT
                                            P.idASproject_id,
                                            P.analytic_account_idASanalytic_account_id,
                                            SOL.idASsale_line_id,
                                            0.0ASexpense_cost
                                        FROMsale_order_lineSOL
                                        JOINsale_orderSOONSO.id=SOL.order_id
                                        JOINaccount_analytic_accountAAONAA.id=SO.analytic_account_id
                                        JOINproject_projectPONP.analytic_account_id=AA.id
                                        LEFTJOINproject_projectPSOLONPSOL.sale_line_id=SOL.id
                                        LEFTJOINproject_taskTSOLONTSOL.sale_line_id=SOL.id
                                        LEFTJOINaccount_analytic_lineAALONAAL.so_line=SOL.id
                                        WHERESOL.is_service='t'
                                          ANDAAL.idISNULL--nottimesheeted
                                          ANDTSOL.idISNULL--notlinkedtoatask
                                          ANDPSOL.idISNULL--notlinkedtoaproject
                                          ANDP.active='t'ANDP.allow_timesheets='t'
                                        GROUPBYP.id,SOL.id
                                        UNION

                                        SELECT
                                            P.idASproject_id,
                                            P.analytic_account_idASanalytic_account_id,
                                            AAL.so_lineASsale_line_id,
                                            0.0ASexpense_cost
                                        FROMproject_projectP
                                            LEFTJOINaccount_analytic_accountAAONP.analytic_account_id=AA.id
                                            LEFTJOINaccount_analytic_lineAALONAAL.account_id=AA.id
                                        WHEREAAL.amount>0.0ANDAAL.project_idISNULLANDP.active='t'ANDP.allow_timesheets='t'
                                        GROUPBYP.id,AA.id,AAL.so_line
                                        UNION
                                        SELECT
                                            P.idASproject_id,
                                            P.analytic_account_idASanalytic_account_id,
                                            AAL.so_lineASsale_line_id,
                                            SUM(AAL.amount)ASexpense_cost
                                        FROMproject_projectP
                                            LEFTJOINaccount_analytic_accountAAONP.analytic_account_id=AA.id
                                            LEFTJOINaccount_analytic_lineAALONAAL.account_id=AA.id
                                        WHEREAAL.amount<0.0ANDAAL.project_idISNULLANDP.active='t'ANDP.allow_timesheets='t'
                                        GROUPBYP.id,AA.id,AAL.so_line
                                        UNION
                                        SELECT
                                            P.idASproject_id,
                                            P.analytic_account_idASanalytic_account_id,
                                            SOLDOWN.idASsale_line_id,
                                            0.0ASexpense_cost
                                        FROMproject_projectP
                                            LEFTJOINsale_order_lineSOLONP.sale_line_id=SOL.id
                                            LEFTJOINsale_orderSOONSO.id=SOL.order_idORSO.analytic_account_id=P.analytic_account_id
                                            LEFTJOINsale_order_lineSOLDOWNONSOLDOWN.order_id=SO.idANDSOLDOWN.is_downpayment='t'
                                            LEFTJOINsale_order_line_invoice_relSOINVONSOINV.order_line_id=SOLDOWN.id
                                            LEFTJOINaccount_move_lineINVLONSOINV.invoice_line_id=INVL.id
                                                                            ANDINVL.parent_state='posted'
                                                                            ANDINVL.exclude_from_invoice_tab='f'
                                            LEFTJOINaccount_moveRINVONINVL.move_id=RINV.reversed_entry_id
                                            LEFTJOINaccount_move_lineRINVLONRINV.id=RINVL.move_id
                                                                            ANDRINVL.parent_state='posted'
                                                                            ANDRINVL.exclude_from_invoice_tab='f'
                                                                            ANDRINVL.product_id=SOLDOWN.product_id
                                            LEFTJOINaccount_analytic_lineANLIONANLI.move_id=RINVL.idANDANLI.amount<0.0
                                        WHEREANLI.idISNULL--therearenocreditnoteforthisdownpayment
                                          ANDP.active='t'ANDP.allow_timesheets='t'
                                        GROUPBYP.id,SOLDOWN.id
                                        UNION
                                        SELECT
                                            P.idASproject_id,
                                            P.analytic_account_idASanalytic_account_id,
                                            SOL.idASsale_line_id,
                                            0.0ASexpense_cost
                                        FROMsale_order_lineSOL
                                            INNERJOINproject_projectPONSOL.project_id=P.id
                                        WHEREP.active='t'ANDP.allow_timesheets='t'
                                        UNION
                                        SELECT
                                            P.idASproject_id,
                                            P.analytic_account_idASanalytic_account_id,
                                            SOL.idASsale_line_id,
                                            0.0ASexpense_cost
                                        FROMsale_order_lineSOL
                                            INNERJOINproject_taskTONSOL.task_id=T.id
                                            INNERJOINproject_projectPONP.id=T.project_id
                                        WHEREP.active='t'ANDP.allow_timesheets='t'
                                    )AMOUNT_UNTAXEDONAMOUNT_UNTAXED.project_id=P.id
                                    LEFTJOINsale_order_lineSOLONAMOUNT_UNTAXED.sale_line_id=SOL.id
                                    LEFTJOINsale_orderSONSOL.order_id=S.id
                                    LEFTJOINproduct_productPPon(SOL.product_id=PP.id)
                                    LEFTJOINproduct_templateTon(PP.product_tmpl_id=T.id)
                                    WHEREP.active='t'ANDP.analytic_account_idISNOTNULL
                            )SUB_COST_SUMMARY
                            GROUPBYproject_id,analytic_account_id,sale_line_id,line_date
                        )COST_SUMMARYONCOST_SUMMARY.project_id=P.id
                        LEFTJOINsale_order_lineSOLONCOST_SUMMARY.sale_line_id=SOL.id
                        LEFTJOINsale_orderSONSOL.order_id=S.id
                        WHEREP.active='t'ANDP.analytic_account_idISNOTNULL
                    )ASsub
            )
        """%self._table
        self._cr.execute(query)
