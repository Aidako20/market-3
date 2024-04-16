/**
 *ThisfileallowsintroducingnewJSmoduleswithoutcontaminatingotherfiles.
 *ThisisusefulwhenbugfixingrequiresaddingsuchJSmodulesinstable
 *versionsofFlectra.Anymodulethatisdefinedinthisfileshouldbeisolated
 *initsownfileinmaster.
 */
flectra.define('hr_holidays/static/src/bugfix/bugfix.js',function(require){
'usestrict';

});

//FIXMEmovemeinhr_holidays/static/src/models/partner/partner.js
flectra.define('hr_holidays/static/src/models/partner/partner.js',function(require){
'usestrict';

const{
    registerClassPatchModel,
    registerFieldPatchModel,
    registerInstancePatchModel,
}=require('mail/static/src/model/model_core.js');
const{attr,one2one}=require('mail/static/src/model/model_field.js');
const{clear}=require('mail/static/src/model/model_field_command.js');

const{str_to_datetime}=require('web.time');

registerClassPatchModel('mail.partner','hr_holidays/static/src/models/partner/partner.js',{
    /**
     *@override
     */
    convertData(data){
        constdata2=this._super(data);
        if('out_of_office_date_end'indata){
            data2.outOfOfficeDateEnd=data.out_of_office_date_end?data.out_of_office_date_end:clear();
        }
        returndata2;
    },
});

registerInstancePatchModel('mail.partner','hr_holidays/static/src/models/partner/partner.js',{
    /**
     *@private
     */
    _computeOutOfOfficeText(){
        if(!this.outOfOfficeDateEnd){
            returnclear();
        }
        if(!this.env.messaging.locale.language){
            returnclear();
        }
        constcurrentDate=newDate();
        constdate=str_to_datetime(this.outOfOfficeDateEnd);
        constoptions={day:'numeric',month:'short'};
        if(currentDate.getFullYear()!==date.getFullYear()){
            options.year='numeric';
        }
        letlocaleCode=this.env.messaging.locale.language.replace(/_/g,'-');
        if(localeCode=="sr@latin"){
            localeCode="sr-Latn-RS";
        }
        constformattedDate=date.toLocaleDateString(localeCode,options);
        return_.str.sprintf(this.env._t("Outofofficeuntil%s"),formattedDate);
    },

});

registerFieldPatchModel('mail.partner','hr/static/src/models/partner/partner.js',{
    /**
     *Servesascomputedependency.
     */
    locale:one2one('mail.locale',{
        related:'messaging.locale',
    }),
    /**
     *Dateofendoftheoutofofficeperiodofthepartnerasstring.
     *StringisexpectedtouseFlectra'sdatetimestringformat
     *(examples:'2011-12-0115:12:35.832'or'2011-12-0115:12:35').
     */
    outOfOfficeDateEnd:attr(),
    /**
     *Textshownwhenpartnerisoutofoffice.
     */
    outOfOfficeText:attr({
        compute:'_computeOutOfOfficeText',
        dependencies:[
            'locale',
            'outOfOfficeDateEnd',
        ],
    }),
});

});
