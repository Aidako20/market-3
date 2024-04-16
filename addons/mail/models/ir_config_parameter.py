#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_
fromflectra.exceptionsimportValidationError


classIrConfigParameter(models.Model):
    _inherit='ir.config_parameter'

    @api.model_create_multi
    defcreate(self,vals_list):
        forvalsinvals_list:
            ifvals.get('key')in['mail.bounce.alias','mail.catchall.alias']:
                vals['value']=self.env['mail.alias']._clean_and_check_unique(vals.get('value'))
            elifvals.get('key')=='mail.catchall.domain.allowed':
                vals['value']=vals.get('value')andself._clean_and_check_mail_catchall_allowed_domains(vals['value'])
        returnsuper().create(vals_list)

    defwrite(self,vals):
        forparameterinself:
            if'value'invalsandparameter.keyin['mail.bounce.alias','mail.catchall.alias']andvals['value']!=parameter.value:
                vals['value']=self.env['mail.alias']._clean_and_check_unique(vals.get('value'))
            elif'value'invalsandparameter.key=='mail.catchall.domain.allowed'andvals['value']!=parameter.value:
                vals['value']=vals['value']andself._clean_and_check_mail_catchall_allowed_domains(vals['value'])
        returnsuper().write(vals)

    def_clean_and_check_mail_catchall_allowed_domains(self,value):
        """Thepurposeofthissystemparameteristoavoidthecreation
        ofrecordsfromincomingemailswithadomain!=alias_domain
        butthathaveapatternmatchinganinternalmail.alias."""
        value=[domain.strip().lower()fordomaininvalue.split(',')ifdomain.strip()]
        ifnotvalue:
            raiseValidationError(_("Valuefor`mail.catchall.domain.allowed`cannotbevalidated.\n"
                                    "Itshouldbeacommaseparatedlistofdomainse.g.example.com,example.org."))
        return",".join(value)
