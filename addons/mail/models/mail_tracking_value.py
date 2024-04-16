#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime

fromflectraimportapi,fields,models


classMailTracking(models.Model):
    _name='mail.tracking.value'
    _description='MailTrackingValue'
    _rec_name='field'
    _order='tracking_sequenceasc'

    field=fields.Many2one('ir.model.fields',required=True,readonly=1,ondelete='cascade')
    field_desc=fields.Char('FieldDescription',required=True,readonly=1)
    field_type=fields.Char('FieldType')
    field_groups=fields.Char(compute='_compute_field_groups')

    old_value_integer=fields.Integer('OldValueInteger',readonly=1)
    old_value_float=fields.Float('OldValueFloat',readonly=1)
    old_value_monetary=fields.Float('OldValueMonetary',readonly=1)
    old_value_char=fields.Char('OldValueChar',readonly=1)
    old_value_text=fields.Text('OldValueText',readonly=1)
    old_value_datetime=fields.Datetime('OldValueDateTime',readonly=1)

    new_value_integer=fields.Integer('NewValueInteger',readonly=1)
    new_value_float=fields.Float('NewValueFloat',readonly=1)
    new_value_monetary=fields.Float('NewValueMonetary',readonly=1)
    new_value_char=fields.Char('NewValueChar',readonly=1)
    new_value_text=fields.Text('NewValueText',readonly=1)
    new_value_datetime=fields.Datetime('NewValueDatetime',readonly=1)

    mail_message_id=fields.Many2one('mail.message','MessageID',required=True,index=True,ondelete='cascade')

    tracking_sequence=fields.Integer('Trackingfieldsequence',readonly=1,default=100)

    def_compute_field_groups(self):
        fortrackinginself:
            model=self.env[tracking.mail_message_id.model]
            field=model._fields.get(tracking.field.name)
            tracking.field_groups=field.groupsiffieldelse'base.group_system'

    @api.model
    defcreate_tracking_values(self,initial_value,new_value,col_name,col_info,tracking_sequence,model_name):
        tracked=True

        field=self.env['ir.model.fields']._get(model_name,col_name)
        ifnotfield:
            return

        values={'field':field.id,'field_desc':col_info['string'],'field_type':col_info['type'],'tracking_sequence':tracking_sequence}

        ifcol_info['type']in['integer','float','char','text','datetime','monetary']:
            values.update({
                'old_value_%s'%col_info['type']:initial_value,
                'new_value_%s'%col_info['type']:new_value
            })
        elifcol_info['type']=='date':
            values.update({
                'old_value_datetime':initial_valueandfields.Datetime.to_string(datetime.combine(fields.Date.from_string(initial_value),datetime.min.time()))orFalse,
                'new_value_datetime':new_valueandfields.Datetime.to_string(datetime.combine(fields.Date.from_string(new_value),datetime.min.time()))orFalse,
            })
        elifcol_info['type']=='boolean':
            values.update({
                'old_value_integer':initial_value,
                'new_value_integer':new_value
            })
        elifcol_info['type']=='selection':
            values.update({
                'old_value_char':initial_valueanddict(col_info['selection']).get(initial_value,initial_value)or'',
                'new_value_char':new_valueanddict(col_info['selection'])[new_value]or''
            })
        elifcol_info['type']=='many2one':
            values.update({
                'old_value_integer':initial_valueandinitial_value.idor0,
                'new_value_integer':new_valueandnew_value.idor0,
                'old_value_char':initial_valueandinitial_value.sudo().name_get()[0][1]or'',
                'new_value_char':new_valueandnew_value.sudo().name_get()[0][1]or''
            })
        else:
            tracked=False

        iftracked:
            returnvalues
        return{}

    defget_display_value(self,type):
        asserttypein('new','old')
        result=[]
        forrecordinself:
            ifrecord.field_typein['integer','float','char','text','monetary']:
                result.append(getattr(record,'%s_value_%s'%(type,record.field_type)))
            elifrecord.field_type=='datetime':
                ifrecord['%s_value_datetime'%type]:
                    new_datetime=getattr(record,'%s_value_datetime'%type)
                    result.append('%sZ'%new_datetime)
                else:
                    result.append(record['%s_value_datetime'%type])
            elifrecord.field_type=='date':
                ifrecord['%s_value_datetime'%type]:
                    new_date=record['%s_value_datetime'%type]
                    result.append(fields.Date.to_string(new_date))
                else:
                    result.append(record['%s_value_datetime'%type])
            elifrecord.field_type=='boolean':
                result.append(bool(record['%s_value_integer'%type]))
            else:
                result.append(record['%s_value_char'%type])
        returnresult

    defget_old_display_value(self):
        #grep:#old_value_integer|old_value_datetime|old_value_char
        returnself.get_display_value('old')

    defget_new_display_value(self):
        #grep:#new_value_integer|new_value_datetime|new_value_char
        returnself.get_display_value('new')
