#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.account_edi.tests.commonimportAccountEdiTestCommon
fromcontextlibimportcontextmanager
fromunittest.mockimportpatch
importbase64

#TODOforthetesttowork,weneedacharttemplate(COA)butwedon'thaveanyanddon'twanttoadddependency(createemptycoa?)


def_generate_mocked_needs_web_services(needs_web_services):
    returnlambdaedi_format:needs_web_services


def_generate_mocked_support_batching(support_batching):
    returnlambdaedi_format,move,state,company:support_batching


def_mocked_get_batch_key(edi_format,move,state):
    return()


def_mocked_check_move_configuration_success(edi_format,move):
    return[]


def_mocked_check_move_configuration_fail(edi_format,move):
    return['Fakeerror(mocked)']


def_mocked_post(edi_format,invoices,test_mode):
    res={}
    forinvoiceininvoices:
        attachment=edi_format.env['ir.attachment'].create({
            'name':'mock_simple.xml',
            'datas':base64.encodebytes(b"<?xmlversion='1.0'encoding='UTF-8'?><Invoice/>"),
            'mimetype':'application/xml'
        })
        res[invoice]={'attachment':attachment}
    returnres


def_mocked_post_two_steps(edi_format,invoices,test_mode):
    #Forthistest,weusethefieldreftoknowifthefirststepisalreadydoneornot.
    #Typically,atechnicalfieldforthereferenceoftheuploadtotheweb-servicewill
    #besavedontheinvoice.
    invoices_no_ref=invoices.filtered(lambdai:noti.ref)
    iflen(invoices_no_ref)==len(invoices): #firststep
        invoices_no_ref.ref='test_ref'
        return{invoice:{}forinvoiceininvoices}
    eliflen(invoices_no_ref)==0: #secondstep
        res={}
        forinvoiceininvoices:
            attachment=edi_format.env['ir.attachment'].create({
                'name':'mock_simple.xml',
                'datas':base64.encodebytes(b"<?xmlversion='1.0'encoding='UTF-8'?><Invoice/>"),
                'mimetype':'application/xml'
            })
            res[invoice]={'attachment':attachment}
        returnres
    else:
        raiseValueError('wronguseof"_mocked_post_two_steps"')


def_mocked_cancel_success(edi_format,invoices,test_mode):
    return{invoice:{'success':True}forinvoiceininvoices}


def_mocked_cancel_failed(edi_format,invoices,test_mode):
    return{invoice:{'error':'Fakederror(mocked)'}forinvoiceininvoices}


classAccountEdiExtendedTestCommon(AccountEdiTestCommon):

    @contextmanager
    defmock_edi(self,
                 _is_required_for_invoice_method=lambdaedi_format,invoice:True,
                 _is_required_for_payment_method=lambdaedi_format,invoice:True,
                 _support_batching_method=_generate_mocked_support_batching(False),
                 _get_batch_key_method=_mocked_get_batch_key,
                 _needs_web_services_method=_generate_mocked_needs_web_services(False),
                 _check_move_configuration_method=_mocked_check_move_configuration_success,
                 _post_invoice_edi_method=_mocked_post,
                 _cancel_invoice_edi_method=_mocked_cancel_success,
                 _post_payment_edi_method=_mocked_post,
                 _cancel_payment_edi_method=_mocked_cancel_success,
                 ):

        try:
            withpatch('flectra.addons.account_edi.models.account_edi_format.AccountEdiFormat._is_required_for_invoice',
                       new=_is_required_for_invoice_method),\
                 patch('flectra.addons.account_edi.models.account_edi_format.AccountEdiFormat._is_required_for_payment',
                       new=_is_required_for_payment_method),\
                 patch('flectra.addons.account_edi.models.account_edi_format.AccountEdiFormat._needs_web_services',
                       new=_needs_web_services_method),\
                 patch('flectra.addons.account_edi.models.account_edi_format.AccountEdiFormat._support_batching',
                       new=_support_batching_method),\
                 patch('flectra.addons.account_edi.models.account_edi_format.AccountEdiFormat._get_batch_key',
                       new=_get_batch_key_method),\
                 patch('flectra.addons.account_edi.models.account_edi_format.AccountEdiFormat._check_move_configuration',
                       new=_check_move_configuration_method),\
                 patch('flectra.addons.account_edi.models.account_edi_format.AccountEdiFormat._post_invoice_edi',
                       new=_post_invoice_edi_method),\
                 patch('flectra.addons.account_edi.models.account_edi_format.AccountEdiFormat._cancel_invoice_edi',
                       new=_cancel_invoice_edi_method),\
                 patch('flectra.addons.account_edi.models.account_edi_format.AccountEdiFormat._post_payment_edi',
                       new=_post_payment_edi_method),\
                 patch('flectra.addons.account_edi.models.account_edi_format.AccountEdiFormat._cancel_payment_edi',
                       new=_cancel_payment_edi_method):

                yield
        finally:
            pass
