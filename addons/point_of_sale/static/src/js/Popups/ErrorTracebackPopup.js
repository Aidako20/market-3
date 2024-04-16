flectra.define('point_of_sale.ErrorTracebackPopup',function(require){
    'usestrict';

    constErrorPopup=require('point_of_sale.ErrorPopup');
    constRegistries=require('point_of_sale.Registries');

    //formerlyErrorTracebackPopupWidget
    classErrorTracebackPopupextendsErrorPopup{
        gettracebackUrl(){
            constblob=newBlob([this.props.body]);
            constURL=window.URL||window.webkitURL;
            returnURL.createObjectURL(blob);
        }
        gettracebackFilename(){
            return`${this.env._t('error')}${moment().format('YYYY-MM-DD-HH-mm-ss')}.txt`;
        }
        emailTraceback(){
            constaddress=this.env.pos.company.email;
            constsubject=this.env._t('IMPORTANT:BugReportFromFlectraPointOfSale');
            window.open(
                'mailto:'+
                    address+
                    '?subject='+
                    (subject?window.encodeURIComponent(subject):'')+
                    '&body='+
                    (this.props.body?window.encodeURIComponent(this.props.body):'')
            );
        }
    }
    ErrorTracebackPopup.template='ErrorTracebackPopup';
    ErrorTracebackPopup.defaultProps={
        confirmText:'Ok',
        cancelText:'Cancel',
        title:'ErrorwithTraceback',
        body:'',
        exitButtonIsShown:false,
        exitButtonText:'ExitPos',
        exitButtonTrigger:'close-pos'
    };

    Registries.Component.add(ErrorTracebackPopup);

    returnErrorTracebackPopup;
});
