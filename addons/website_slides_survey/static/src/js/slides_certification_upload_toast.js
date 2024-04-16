flectra.define('website_slides_survey.certification_upload_toast',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');

varsessionStorage=window.sessionStorage;
varcore=require('web.core');
var_t=core._t;


publicWidget.registry.CertificationUploadToast=publicWidget.Widget.extend({
    selector:'.o_wslides_survey_certification_upload_toast',

    /**
     *@override
     */
    start:function(){
        varself=this;
        this._super.apply(this,arguments).then(function(){
            varurl=sessionStorage.getItem("survey_certification_url");
            if(url){
                self.displayNotification({
                    type:'info',
                    title:_t('Certificationcreated'),
                    message:_.str.sprintf(
                        _t('Followthislinktoaddquestionstoyourcertification.<ahref="%s">Editcertification</a>'),
                        url
                    ),
                    sticky:true,
                });
                sessionStorage.removeItem("survey_certification_url");
            }
        });
    },
});

returnpublicWidget.registry.CertificationUploadToast;

});
