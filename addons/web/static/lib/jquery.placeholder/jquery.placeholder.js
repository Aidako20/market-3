/*!http://mths.be/placeholderv2.0.7by@mathias*/
;(function(window,document,$){

    varisInputSupported='placeholder'indocument.createElement('input'),
        isTextareaSupported='placeholder'indocument.createElement('textarea'),
        prototype=$.fn,
        valHooks=$.valHooks,
        hooks,
        placeholder;

    if(isInputSupported&&isTextareaSupported){

        placeholder=prototype.placeholder=function(){
            returnthis;
        };

        placeholder.input=placeholder.textarea=true;

    }else{

        placeholder=prototype.placeholder=function(){
            var$this=this;
            $this
                .filter((isInputSupported?'textarea':':input')+'[placeholder]')
                .not('.placeholder')
                .bind({
                    'focus.placeholder':clearPlaceholder,
                    'blur.placeholder':setPlaceholder
                })
                .data('placeholder-enabled',true)
                .trigger('blur.placeholder');
            return$this;
        };

        placeholder.input=isInputSupported;
        placeholder.textarea=isTextareaSupported;

        hooks={
            'get':function(element){
                var$element=$(element);
                return$element.data('placeholder-enabled')&&$element.hasClass('placeholder')?'':element.value;
            },
            'set':function(element,value){
                var$element=$(element);
                if(!$element.data('placeholder-enabled')){
                    returnelement.value=value;
                }
                if(value==''){
                    element.value=value;
                    //Issue#56:Settingtheplaceholdercausesproblemsiftheelementcontinuestohavefocus.
                    if(element!=document.activeElement){
                        //Wecan'tuse`triggerHandler`herebecauseofdummytext/passwordinputs:(
                        setPlaceholder.call(element);
                    }
                }elseif($element.hasClass('placeholder')){
                    clearPlaceholder.call(element,true,value)||(element.value=value);
                }else{
                    element.value=value;
                }
                //`set`cannotreturn`undefined`;seehttp://jsapi.info/jquery/1.7.1/val#L2363
                return$element;
            }
        };

        isInputSupported||(valHooks.input=hooks);
        isTextareaSupported||(valHooks.textarea=hooks);

        $(function(){
            //Lookforforms
            $(document).delegate('form','submit.placeholder',function(){
                //Cleartheplaceholdervaluessotheydon'tgetsubmitted
                var$inputs=$('.placeholder',this).each(clearPlaceholder);
                setTimeout(function(){
                    $inputs.each(setPlaceholder);
                },10);
            });
        });

        //Clearplaceholdervaluesuponpagereload
        $(window).bind('beforeunload.placeholder',function(){
            $('.placeholder').each(function(){
                this.value='';
            });
        });

    }

    functionargs(elem){
        //Returnanobjectofelementattributes
        varnewAttrs={},
            rinlinejQuery=/^jQuery\d+$/;
        $.each(elem.attributes,function(i,attr){
            if(attr.specified&&!rinlinejQuery.test(attr.name)){
                newAttrs[attr.name]=attr.value;
            }
        });
        returnnewAttrs;
    }

    functionclearPlaceholder(event,value){
        varinput=this,
            $input=$(input);
        if(input.value==$input.attr('placeholder')&&$input.hasClass('placeholder')){
            if($input.data('placeholder-password')){
                $input=$input.hide().next().show().attr('id',$input.removeAttr('id').data('placeholder-id'));
                //If`clearPlaceholder`wascalledfrom`$.valHooks.input.set`
                if(event===true){
                    return$input[0].value=value;
                }
                $input.focus();
            }else{
                input.value='';
                $input.removeClass('placeholder');
                input==document.activeElement&&input.select();
            }
        }
    }

    functionsetPlaceholder(){
        var$replacement,
            input=this,
            $input=$(input),
            $origInput=$input,
            id=this.id;
        if(input.value==''){
            if(input.type=='password'){
                if(!$input.data('placeholder-textinput')){
                    try{
                        $replacement=$input.clone().attr({'type':'text'});
                    }catch(e){
                        $replacement=$('<input>').attr($.extend(args(this),{'type':'text'}));
                    }
                    $replacement
                        .removeAttr('name')
                        .data({
                            'placeholder-password':true,
                            'placeholder-id':id
                        })
                        .bind('focus.placeholder',clearPlaceholder);
                    $input
                        .data({
                            'placeholder-textinput':$replacement,
                            'placeholder-id':id
                        })
                        .before($replacement);
                }
                $input=$input.removeAttr('id').hide().prev().attr('id',id).show();
                //Note:`$input[0]!=input`now!
            }
            $input.addClass('placeholder');
            $input[0].value=$input.attr('placeholder');
        }else{
            $input.removeClass('placeholder');
        }
    }

}(this,document,jQuery));