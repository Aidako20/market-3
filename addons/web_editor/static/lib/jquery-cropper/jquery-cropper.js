/*!
 *jQueryCropperv1.0.0
 *https://github.com/fengyuanchen/jquery-cropper
 *
 *Copyright(c)2018ChenFengyuan
 *ReleasedundertheMITlicense
 *
 *Date:2018-04-01T06:20:13.168Z
 */

(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?factory(require('jquery'),require('cropperjs')):
    typeofdefine==='function'&&define.amd?define(['jquery','cropperjs'],factory):
    (factory(global.jQuery,global.Cropper));
  }(this,(function($,Cropper){'usestrict';

    $=$&&$.hasOwnProperty('default')?$['default']:$;
    Cropper=Cropper&&Cropper.hasOwnProperty('default')?Cropper['default']:Cropper;

    if($.fn){
      varAnotherCropper=$.fn.cropper;
      varNAMESPACE='cropper';

      $.fn.cropper=functionjQueryCropper(option){
        for(var_len=arguments.length,args=Array(_len>1?_len-1:0),_key=1;_key<_len;_key++){
          args[_key-1]=arguments[_key];
        }

        varresult=void0;

        this.each(function(i,element){
          var$element=$(element);
          varisDestroy=option==='destroy';
          varcropper=$element.data(NAMESPACE);

          if(!cropper){
            if(isDestroy){
              return;
            }

            varoptions=$.extend({},$element.data(),$.isPlainObject(option)&&option);

            cropper=newCropper(element,options);
            $element.data(NAMESPACE,cropper);
          }

          if(typeofoption==='string'){
            varfn=cropper[option];

            if($.isFunction(fn)){
              result=fn.apply(cropper,args);

              if(result===cropper){
                result=undefined;
              }

              if(isDestroy){
                $element.removeData(NAMESPACE);
              }
            }
          }
        });

        returnresult!==undefined?result:this;
      };

      $.fn.cropper.Constructor=Cropper;
      $.fn.cropper.setDefaults=Cropper.setDefaults;
      $.fn.cropper.noConflict=functionnoConflict(){
        $.fn.cropper=AnotherCropper;
        returnthis;
      };
    }

  })));
