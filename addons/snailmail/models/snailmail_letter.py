#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importre
importbase64
importio

fromPyPDF2importPdfFileReader,PdfFileMerger,PdfFileWriter
fromreportlab.platypusimportFrame,Paragraph,KeepInFrame
fromreportlab.lib.unitsimportmm
fromreportlab.lib.pagesizesimportA4
fromreportlab.lib.stylesimportgetSampleStyleSheet
fromreportlab.pdfgen.canvasimportCanvas

fromflectraimportfields,models,api,_
fromflectra.addons.iap.toolsimportiap_tools
fromflectra.exceptionsimportAccessError,UserError
fromflectra.tools.safe_evalimportsafe_eval

DEFAULT_ENDPOINT='https://iap-snailmail.flectrahq.com'
PRINT_ENDPOINT='/iap/snailmail/1/print'
DEFAULT_TIMEOUT=30

ERROR_CODES=[
    'MISSING_REQUIRED_FIELDS',
    'CREDIT_ERROR',
    'TRIAL_ERROR',
    'NO_PRICE_AVAILABLE',
    'FORMAT_ERROR',
    'UNKNOWN_ERROR',
]


classSnailmailLetter(models.Model):
    _name='snailmail.letter'
    _description='SnailmailLetter'

    user_id=fields.Many2one('res.users','Sentby')
    model=fields.Char('Model',required=True)
    res_id=fields.Integer('DocumentID',required=True)
    partner_id=fields.Many2one('res.partner',string='Recipient',required=True)
    company_id=fields.Many2one('res.company',string='Company',required=True,readonly=True,
        default=lambdaself:self.env.company.id)
    report_template=fields.Many2one('ir.actions.report','Optionalreporttoprintandattach')

    attachment_id=fields.Many2one('ir.attachment',string='Attachment',ondelete='cascade')
    attachment_datas=fields.Binary('Document',related='attachment_id.datas')
    attachment_fname=fields.Char('AttachmentFilename',related='attachment_id.name')
    color=fields.Boolean(string='Color',default=lambdaself:self.env.company.snailmail_color)
    cover=fields.Boolean(string='CoverPage',default=lambdaself:self.env.company.snailmail_cover)
    duplex=fields.Boolean(string='Bothside',default=lambdaself:self.env.company.snailmail_duplex)
    state=fields.Selection([
        ('pending','InQueue'),
        ('sent','Sent'),
        ('error','Error'),
        ('canceled','Canceled')
        ],'Status',readonly=True,copy=False,default='pending',required=True,
        help="Whenaletteriscreated,thestatusis'Pending'.\n"
             "Iftheletteriscorrectlysent,thestatusgoesin'Sent',\n"
             "Ifnot,itwillgotinstate'Error'andtheerrormessagewillbedisplayedinthefield'ErrorMessage'.")
    error_code=fields.Selection([(err_code,err_code)forerr_codeinERROR_CODES],string="Error")
    info_msg=fields.Char('Information')
    display_name=fields.Char('DisplayName',compute="_compute_display_name")

    reference=fields.Char(string='RelatedRecord',compute='_compute_reference',readonly=True,store=False)

    message_id=fields.Many2one('mail.message',string="SnailmailStatusMessage")
    notification_ids=fields.One2many('mail.notification','letter_id',"Notifications")

    street=fields.Char('Street')
    street2=fields.Char('Street2')
    zip=fields.Char('Zip')
    city=fields.Char('City')
    state_id=fields.Many2one("res.country.state",string='State')
    country_id=fields.Many2one('res.country',string='Country')

    @api.depends('reference','partner_id')
    def_compute_display_name(self):
        forletterinself:
            ifletter.attachment_id:
                letter.display_name="%s-%s"%(letter.attachment_id.name,letter.partner_id.name)
            else:
                letter.display_name=letter.partner_id.name

    @api.depends('model','res_id')
    def_compute_reference(self):
        forresinself:
            res.reference="%s,%s"%(res.model,res.res_id)

    @api.model
    defcreate(self,vals):
        msg_id=self.env[vals['model']].browse(vals['res_id']).message_post(
            body=_("LettersentbypostwithSnailmail"),
            message_type='snailmail'
        )

        partner_id=self.env['res.partner'].browse(vals['partner_id'])
        vals.update({
            'message_id':msg_id.id,
            'street':partner_id.street,
            'street2':partner_id.street2,
            'zip':partner_id.zip,
            'city':partner_id.city,
            'state_id':partner_id.state_id.id,
            'country_id':partner_id.country_id.id,
        })
        letter=super(SnailmailLetter,self).create(vals)

        self.env['mail.notification'].sudo().create({
            'mail_message_id':msg_id.id,
            'res_partner_id':partner_id.id,
            'notification_type':'snail',
            'letter_id':letter.id,
            'is_read':True, #discardInboxnotification
            'notification_status':'ready',
        })

        letter.attachment_id.check('read')
        returnletter

    defwrite(self,vals):
        res=super().write(vals)
        if'attachment_id'invals:
            self.attachment_id.check('read')
        returnres

    def_fetch_attachment(self):
        """
        Thismethodwillcheckifwehaveanyexistentattachementmatchingthemodel
        andres_idsandcreatethemifnotfound.
        """
        self.ensure_one()
        obj=self.env[self.model].browse(self.res_id)
        ifnotself.attachment_id:
            report=self.report_template
            ifnotreport:
                report_name=self.env.context.get('report_name')
                report=self.env['ir.actions.report']._get_report_from_name(report_name)
                ifnotreport:
                    returnFalse
                else:
                    self.write({'report_template':report.id})
                #report=self.env.ref('account.account_invoices')
            ifreport.print_report_name:
                report_name=safe_eval(report.print_report_name,{'object':obj})
            elifreport.attachment:
                report_name=safe_eval(report.attachment,{'object':obj})
            else:
                report_name='Document'
            filename="%s.%s"%(report_name,"pdf")
            paperformat=report.get_paperformat()
            if(paperformat.format=='custom'andpaperformat.page_width!=210andpaperformat.page_height!=297)orpaperformat.format!='A4':
                raiseUserError(_("PleaseuseanA4Paperformat."))
            pdf_bin,unused_filetype=report.with_context(snailmail_layout=notself.cover,lang='en_US')._render_qweb_pdf(self.res_id)
            pdf_bin=self._overwrite_margins(pdf_bin)
            ifself.cover:
                pdf_bin=self._append_cover_page(pdf_bin)
            attachment=self.env['ir.attachment'].create({
                'name':filename,
                'datas':base64.b64encode(pdf_bin),
                'res_model':'snailmail.letter',
                'res_id':self.id,
                'type':'binary', #overridedefault_typefromcontext,possiblymeantforanothermodel!
            })
            self.write({'attachment_id':attachment.id})

        returnself.attachment_id

    def_count_pages_pdf(self,bin_pdf):
        """Countthenumberofpagesofthegivenpdffile.
            :parambin_pdf:binarycontentofthepdffile
        """
        pages=0
        formatchinre.compile(b"/Count\s+(\d+)").finditer(bin_pdf):
            pages=int(match.group(1))
        returnpages

    def_snailmail_create(self,route):
        """
        Createadictionnaryobjecttosendtosnailmailserver.

        :return:Dictintheform:
        {
            account_token:string,   //IAPAccounttokenoftheuser
            documents:[{
                pages:int,
                pdf_bin:pdffile
                res_id:int(client-sideres_id),
                res_model:char(client-sideres_model),
                address:{
                    name:char,
                    street:char,
                    street2:char(OPTIONAL),
                    zip:int,
                    city:char,
                    state:char(statecode(OPTIONAL)),
                    country_code:char(countrycode)
                }
                return_address:{
                    name:char,
                    street:char,
                    street2:char(OPTIONAL),
                    zip:int,
                    city:char,at
                    state:char(statecode(OPTIONAL)),
                    country_code:char(countrycode)
                }
            }],
            options:{
                color:boolean(trueifcolor,falseifblack-white),
                duplex:boolean(trueifduplex,falseotherwise),
                currency_name:char
            }
        }
        """
        account_token=self.env['iap.account'].get('snailmail').account_token
        dbuuid=self.env['ir.config_parameter'].sudo().get_param('database.uuid')
        documents=[]

        batch=len(self)>1
        forletterinself:
            recipient_name=letter.partner_id.nameorletter.partner_id.parent_idandletter.partner_id.parent_id.name
            ifnotrecipient_name:
                letter.write({
                    'info_msg':_('Invalidrecipientname.'),
                    'state':'error',
                    'error_code':'MISSING_REQUIRED_FIELDS'
                    })
                continue
            document={
                #genericinformationstosend
                'letter_id':letter.id,
                'res_model':letter.model,
                'res_id':letter.res_id,
                'contact_address':letter.partner_id.with_context(snailmail_layout=True,show_address=True).name_get()[0][1],
                'address':{
                    'name':recipient_name,
                    'street':letter.partner_id.street,
                    'street2':letter.partner_id.street2,
                    'zip':letter.partner_id.zip,
                    'state':letter.partner_id.state_id.codeifletter.partner_id.state_idelseFalse,
                    'city':letter.partner_id.city,
                    'country_code':letter.partner_id.country_id.code
                },
                'return_address':{
                    'name':letter.company_id.partner_id.name,
                    'street':letter.company_id.partner_id.street,
                    'street2':letter.company_id.partner_id.street2,
                    'zip':letter.company_id.partner_id.zip,
                    'state':letter.company_id.partner_id.state_id.codeifletter.company_id.partner_id.state_idelseFalse,
                    'city':letter.company_id.partner_id.city,
                    'country_code':letter.company_id.partner_id.country_id.code,
                }
            }
            #Specifictoeachcase:
            #Ifweareestimatingtheprice:1object=1page
            #Ifweareprinting->attachthepdf
            ifroute=='estimate':
                document.update(pages=1)
            else:
                #addingtheweblogofromthecompanyforfuturepossiblecustomization
                document.update({
                    'company_logo':letter.company_id.logo_webandletter.company_id.logo_web.decode('utf-8')orFalse,
                })
                attachment=letter._fetch_attachment()
                ifattachment:
                    document.update({
                        'pdf_bin':route=='print'andattachment.datas.decode('utf-8'),
                        'pages':route=='estimate'andself._count_pages_pdf(base64.b64decode(attachment.datas)),
                    })
                else:
                    letter.write({
                        'info_msg':'Theattachmentcouldnotbegenerated.',
                        'state':'error',
                        'error_code':'UNKNOWN_ERROR'
                    })
                    continue
                ifletter.company_id.external_report_layout_id==self.env.ref('l10n_de.external_layout_din5008',False):
                    document.update({
                        'rightaddress':0,
                    })
            documents.append(document)

        return{
            'account_token':account_token,
            'dbuuid':dbuuid,
            'documents':documents,
            'options':{
                'color':selfandself[0].color,
                'cover':selfandself[0].cover,
                'duplex':selfandself[0].duplex,
                'currency_name':'EUR',
            },
            #thiswillnotraisetheInsufficientCreditErrorwhichisthebehaviourwewantfornow
            'batch':True,
        }

    def_get_error_message(self,error):
        iferror=='CREDIT_ERROR':
            link=self.env['iap.account'].get_credits_url(service_name='snailmail')
            return_('Youdon\'thaveenoughcreditstoperformthisoperation.<br>Pleasegotoyour<ahref=%starget="new">iapaccount</a>.',link)
        iferror=='TRIAL_ERROR':
            link=self.env['iap.account'].get_credits_url(service_name='snailmail',trial=True)
            return_('Youdon\'thaveanIAPaccountregisteredforthisservice.<br>Pleasegoto<ahref=%starget="new">iap.flectrahq.com</a>toclaimyourfreecredits.',link)
        iferror=='NO_PRICE_AVAILABLE':
            return_('ThecountryofthepartnerisnotcoveredbySnailmail.')
        iferror=='MISSING_REQUIRED_FIELDS':
            return_('Oneormorerequiredfieldsareempty.')
        iferror=='FORMAT_ERROR':
            return_('Theattachmentofthelettercouldnotbesent.Pleasecheckitscontentandcontactthesupportiftheproblempersists.')
        else:
            return_('Anunknownerrorhappened.Pleasecontactthesupport.')
        returnerror

    def_get_failure_type(self,error):
        iferror=='CREDIT_ERROR':
            return'sn_credit'
        iferror=='TRIAL_ERROR':
            return'sn_trial'
        iferror=='NO_PRICE_AVAILABLE':
            return'sn_price'
        iferror=='MISSING_REQUIRED_FIELDS':
            return'sn_fields'
        iferror=='FORMAT_ERROR':
            return'sn_format'
        else:
            return'sn_error'

    def_snailmail_print(self,immediate=True):
        valid_address_letters=self.filtered(lambdal:l._is_valid_address(l))
        invalid_address_letters=self-valid_address_letters
        invalid_address_letters._snailmail_print_invalid_address()
        ifvalid_address_lettersandimmediate:
            forletterinvalid_address_letters:
                letter._snailmail_print_valid_address()
                self.env.cr.commit()

    def_snailmail_print_invalid_address(self):
        error='MISSING_REQUIRED_FIELDS'
        error_message=_("Theaddressoftherecipientisnotcomplete")
        self.write({
            'state':'error',
            'error_code':error,
            'info_msg':error_message,
        })
        self.notification_ids.sudo().write({
            'notification_status':'exception',
            'failure_type':self._get_failure_type(error),
            'failure_reason':error_message,
        })
        self.message_id._notify_message_notification_update()

    def_snailmail_print_valid_address(self):
        """
        getresponse
        {
            'request_code':RESPONSE_OK,#becausewereceive200ifgoodorfail
            'total_cost':total_cost,
            'credit_error':credit_error,
            'request':{
                'documents':documents,
                'options':options
                }
            }
        }
        """
        endpoint=self.env['ir.config_parameter'].sudo().get_param('snailmail.endpoint',DEFAULT_ENDPOINT)
        timeout=int(self.env['ir.config_parameter'].sudo().get_param('snailmail.timeout',DEFAULT_TIMEOUT))
        params=self._snailmail_create('print')
        try:
            response=iap_tools.iap_jsonrpc(endpoint+PRINT_ENDPOINT,params=params,timeout=timeout)
        exceptAccessErrorasae:
            fordocinparams['documents']:
                letter=self.browse(doc['letter_id'])
                letter.state='error'
                letter.error_code='UNKNOWN_ERROR'
            raiseae
        fordocinresponse['request']['documents']:
            ifdoc.get('sent')andresponse['request_code']==200:
                note=_('Thedocumentwascorrectlysentbypost.<br>Thetrackingidis%s',doc['send_id'])
                letter_data={'info_msg':note,'state':'sent','error_code':False}
                notification_data={
                    'notification_status':'sent',
                    'failure_type':False,
                    'failure_reason':False,
                }
            else:
                error=doc['error']ifresponse['request_code']==200elseresponse['reason']

                note=_('Anerroroccuredwhensendingthedocumentbypost.<br>Error:%s',self._get_error_message(error))
                letter_data={
                    'info_msg':note,
                    'state':'error',
                    'error_code':erroriferrorinERROR_CODESelse'UNKNOWN_ERROR'
                }
                notification_data={
                    'notification_status':'exception',
                    'failure_type':self._get_failure_type(error),
                    'failure_reason':note,
                }

            letter=self.browse(doc['letter_id'])
            letter.write(letter_data)
            letter.notification_ids.sudo().write(notification_data)
        self.message_id._notify_message_notification_update()

    defsnailmail_print(self):
        self.write({'state':'pending'})
        self.notification_ids.sudo().write({
            'notification_status':'ready',
            'failure_type':False,
            'failure_reason':False,
        })
        self.message_id._notify_message_notification_update()
        iflen(self)==1:
            self._snailmail_print()

    defcancel(self):
        self.write({'state':'canceled','error_code':False})
        self.notification_ids.sudo().write({
            'notification_status':'canceled',
        })
        self.message_id._notify_message_notification_update()

    @api.model
    def_snailmail_cron(self,autocommit=True):
        letters_send=self.search([
            '|',
            ('state','=','pending'),
            '&',
            ('state','=','error'),
            ('error_code','in',['TRIAL_ERROR','CREDIT_ERROR','MISSING_REQUIRED_FIELDS'])
        ])
        forletterinletters_send:
            letter._snailmail_print()
            ifletter.error_code=='CREDIT_ERROR':
                break #avoidspam
            #Commitaftereverylettersenttoavoidtosenditagainincaseofarollback
            ifautocommit:
                self.env.cr.commit()

    @api.model
    def_is_valid_address(self,record):
        record.ensure_one()
        required_keys=['street','city','zip','country_id']
        returnall(record[key]forkeyinrequired_keys)

    def_append_cover_page(self,invoice_bin:bytes):
        address_split=self.partner_id.with_context(show_address=True,lang='en_US')._get_name().split('\n')
        address_split[0]=self.partner_id.nameorself.partner_id.parent_idandself.partner_id.parent_id.nameoraddress_split[0]
        address='<br/>'.join(address_split)
        address_x=118*mm
        address_y=60*mm
        frame_width=85.5*mm
        frame_height=25.5*mm

        cover_buf=io.BytesIO()
        canvas=Canvas(cover_buf,pagesize=A4)
        styles=getSampleStyleSheet()

        frame=Frame(address_x,A4[1]-address_y-frame_height,frame_width,frame_height)
        story=[Paragraph(address,styles['Normal'])]
        address_inframe=KeepInFrame(0,0,story)
        frame.addFromList([address_inframe],canvas)
        canvas.save()
        cover_buf.seek(0)

        invoice=PdfFileReader(io.BytesIO(invoice_bin))
        cover_bin=io.BytesIO(cover_buf.getvalue())
        cover_file=PdfFileReader(cover_bin)
        merger=PdfFileMerger()

        merger.append(cover_file,import_bookmarks=False)
        merger.append(invoice,import_bookmarks=False)

        out_buff=io.BytesIO()
        merger.write(out_buff)
        returnout_buff.getvalue()

    def_overwrite_margins(self,invoice_bin:bytes):
        """
        Fillthemarginswithwhiteforvalidationpurposes.
        """
        pdf_buf=io.BytesIO()
        canvas=Canvas(pdf_buf,pagesize=A4)
        canvas.setFillColorRGB(255,255,255)
        page_width=A4[0]
        page_height=A4[1]

        #HorizontalMargin
        hmargin_width=page_width
        hmargin_height=5*mm

        #VerticalMargin
        vmargin_width=5*mm
        vmargin_height=page_height

        #Bottomleftsquare
        sq_width=15*mm

        #Drawthehorizontalmargins
        canvas.rect(0,0,hmargin_width,hmargin_height,stroke=0,fill=1)
        canvas.rect(0,page_height,hmargin_width,-hmargin_height,stroke=0,fill=1)

        #Drawtheverticalmargins
        canvas.rect(0,0,vmargin_width,vmargin_height,stroke=0,fill=1)
        canvas.rect(page_width,0,-vmargin_width,vmargin_height,stroke=0,fill=1)

        #Drawthebottomleftwhitesquare
        canvas.rect(0,0,sq_width,sq_width,stroke=0,fill=1)
        canvas.save()
        pdf_buf.seek(0)

        new_pdf=PdfFileReader(pdf_buf)
        curr_pdf=PdfFileReader(io.BytesIO(invoice_bin))
        out=PdfFileWriter()
        forpageincurr_pdf.pages:
            page.mergePage(new_pdf.getPage(0))
            out.addPage(page)
        out_stream=io.BytesIO()
        out.write(out_stream)
        out_bin=out_stream.getvalue()
        out_stream.close()
        returnout_bin
