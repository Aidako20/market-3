
flectra.define('mass_mailing.fix.LinkDialog',function(require){
'usestrict';

constLinkDialog=require('wysiwyg.widgets.LinkDialog');

/**
 *Primaryandlinkbuttonsare"hacked"bymailingthemesscss.Wethus
 *havetofixtheirpreviewifpossible.
 */
LinkDialog.include({
    /**
     *@override
     */
    start(){
        constret=this._super(...arguments);
        if(!$(this.editable).find('.o_mail_wrapper').length){
            returnret;
        }

        this.opened().then(()=>{
            //Uglyhacktoshowtherealcolorforlinkandprimarywhich
            //dependonthemailingthemes.Note:thehackisnotenoughas
            //themailingthemechangesthosecolorsinsomeenvironment,
            //sometimes(forexample'btn-primaryinthissnippetlookslike
            //that')...we'llconsiderthisalimitationuntilamaster
            //refactoringofthosemailingthemes.
            this.__realMMColors={};
            const$previewArea=$('<div/>').addClass('o_mail_snippet_general');
            $(this.editable).find('.o_layout').append($previewArea);
            _.each(['link','primary','secondary'],type=>{
                const$el=$('<ahref="#"class="btnbtn-'+type+'"/>');
                $el.appendTo($previewArea);
                this.__realMMColors[type]={
                    'border-color':$el.css('border-top-color'),
                    'background-color':$el.css('background-color'),
                    'color':$el.css('color'),
                };
                $el.remove();

                this.$('.form-group.o_btn_preview.btn-'+type)
                    .css(_.pick(this.__realMMColors[type],'background-color','color'));
            });
            $previewArea.remove();

            this._adaptPreview();
        });

        returnret;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _adaptPreview(){
        this._super(...arguments);
        if(this.__realMMColors){
            var$preview=this.$("#link-preview");
            $preview.css('border-color','');
            $preview.css('background-color','');
            $preview.css('color','');
            _.each(['link','primary','secondary'],type=>{
                if($preview.hasClass('btn-'+type)||type==='link'&&!$preview.hasClass('btn')){
                    $preview.css(this.__realMMColors[type]);
                }
            });
        }
    },
});

});
