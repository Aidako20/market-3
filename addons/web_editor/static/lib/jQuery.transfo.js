/*
Copyright(c)2014ChristopheMatthieu,

Permissionisherebygranted,freeofcharge,toanyperson
obtainingacopyofthissoftwareandassociateddocumentation
files(the"Software"),todealintheSoftwarewithout
restriction,includingwithoutlimitationtherightstouse,
copy,modify,merge,publish,distribute,sublicense,and/orsell
copiesoftheSoftware,andtopermitpersonstowhomthe
Softwareisfurnishedtodoso,subjecttothefollowing
conditions:

Theabovecopyrightnoticeandthispermissionnoticeshallbe
includedinallcopiesorsubstantialportionsoftheSoftware.

THESOFTWAREISPROVIDED"ASIS",WITHOUTWARRANTYOFANYKIND,
EXPRESSORIMPLIED,INCLUDINGBUTNOTLIMITEDTOTHEWARRANTIES
OFMERCHANTABILITY,FITNESSFORAPARTICULARPURPOSEAND
NONINFRINGEMENT.INNOEVENTSHALLTHEAUTHORSORCOPYRIGHT
HOLDERSBELIABLEFORANYCLAIM,DAMAGESOROTHERLIABILITY,
WHETHERINANACTIONOFCONTRACT,TORTOROTHERWISE,ARISING
FROM,OUTOFORINCONNECTIONWITHTHESOFTWAREORTHEUSEOR
OTHERDEALINGSINTHESOFTWARE.
*/

(function($){
    'usestrict';
        varrad=Math.PI/180;

        //publicmethods
        varmethods={
                init:function(settings){
                    returnthis.each(function(){
                        var$this=$(this),transfo=$this.data('transfo');
                        if(!transfo){
                            _init($this,settings);
                        }else{
                            _overwriteOptions($this,transfo,settings);
                            _targetCss($this,transfo);
                        }
                    });
                },

                destroy:function(){
                    returnthis.each(function(){
                        var$this=$(this);
                        if($this.data('transfo')){
                            _destroy($this);
                        }
                    });
                },

                reset:function(){
                    returnthis.each(function(){
                        var$this=$(this);
                        if($this.data('transfo')){
                            _reset($this);
                        }
                    });
                },

                toggle:function(){
                    returnthis.each(function(){
                        var$this=$(this);
                        vartransfo=$this.data('transfo');
                        if(transfo){
                            transfo.settings.hide=!transfo.settings.hide;
                            _showHide($this,transfo);
                        }
                    });
                },

                hide:function(){
                    returnthis.each(function(){
                        var$this=$(this);
                        vartransfo=$this.data('transfo');
                        if(transfo){
                            transfo.settings.hide=true;
                            _showHide($this,transfo);
                        }
                    });
                },

                show:function(){
                    returnthis.each(function(){
                        var$this=$(this);
                        vartransfo=$this.data('transfo');
                        if(transfo){
                            transfo.settings.hide=false;
                            _showHide($this,transfo);
                        }
                    });
                },

                settings: function(){
                    if(this.length>1){
                        this.map(function(){
                            var$this=$(this);
                            return$this.data('transfo')&&$this.data('transfo').settings;
                        });
                    }
                    returnthis.data('transfo')&&$this.data('transfo').settings;
                },
                center: function(){
                    if(this.length>1){
                        this.map(function(){
                            var$this=$(this);
                            return$this.data('transfo')&&$this.data('transfo').$center.offset();
                        });
                    }
                    returnthis.data('transfo')&&this.data('transfo').$center.offset();
                }
        };

        $.fn.transfo=function(method){
            if(methods[method]){
                    returnmethods[method].apply(this,Array.prototype.slice.call(arguments,1));
            }elseif(typeofmethod==='object'||!method){
                    returnmethods.init.apply(this,arguments);
            }else{
                    $.error('Method'+ method+'doesnotexistonjQuery.transfo');
            }
            returnfalse;
        };

        function_init($this,settings){
            vartransfo={};
            $this.data('transfo',transfo);
            transfo.settings=settings;

            //generateallthecontrolsmarkup
            varcss="box-sizing:border-box;position:absolute;background-color:#fff;border:1pxsolid#ccc;width:8px;height:8px;margin-left:-4px;margin-top:-4px;";
            transfo.$markup=$(''
                +'<divclass="transfo-container">'
                + '<divclass="transfo-controls">'
                +  '<divstyle="cursor:crosshair;position:absolute;margin:-30px;top:0;right:0;padding:1px001px;"class="transfo-rotator">'
                +   '<spanclass="fa-stackfa-lg">'
                +   '<iclass="fafa-circlefa-stack-2x"></i>'
                +   '<iclass="fafa-repeatfa-stack-1xfa-inverse"></i>'
                +   '</span>'
                +  '</div>'
                +  '<divstyle="'+css+'top:0%;left:0%;cursor:nw-resize;"class="transfo-scaler-tl"></div>'
                +  '<divstyle="'+css+'top:0%;left:100%;cursor:ne-resize;"class="transfo-scaler-tr"></div>'
                +  '<divstyle="'+css+'top:100%;left:100%;cursor:se-resize;"class="transfo-scaler-br"></div>'
                +  '<divstyle="'+css+'top:100%;left:0%;cursor:sw-resize;"class="transfo-scaler-bl"></div>'
                +  '<divstyle="'+css+'top:0%;left:50%;cursor:n-resize;"class="transfo-scaler-tc"></div>'
                +  '<divstyle="'+css+'top:100%;left:50%;cursor:s-resize;"class="transfo-scaler-bc"></div>'
                +  '<divstyle="'+css+'top:50%;left:0%;cursor:w-resize;"class="transfo-scaler-ml"></div>'
                +  '<divstyle="'+css+'top:50%;left:100%;cursor:e-resize;"class="transfo-scaler-mr"></div>'
                +  '<divstyle="'+css+'border:0;width:0px;height:0px;top:50%;left:50%;"class="transfo-scaler-mc"></div>'
                + '</div>'
                +'</div>');
            transfo.$center=transfo.$markup.find(".transfo-scaler-mc");

            //initsettingandgetcsstosetwrap
            _setOptions($this,transfo);
            _overwriteOptions($this,transfo,settings);

            //appendcontrolstocontainer
            $("body").append(transfo.$markup);

            //settransfocontainerandmarkup
            setTimeout(function(){
                _targetCss($this,transfo);
            },0);

            _bind($this,transfo);
            
            _targetCss($this,transfo);
            _stop_animation($this[0]);
        }

        function_overwriteOptions($this,transfo,settings){
            transfo.settings=$.extend(transfo.settings,settings||{});
        }

        function_stop_animation(target){
            target.style.webkitAnimationPlayState="paused";
            target.style.animationPlayState="paused";
            target.style.webkitTransition="none";
            target.style.transition="none";
        }

        function_setOptions($this,transfo){
            varstyle=$this.attr("style")||"";
            vartransform=style.match(/transform\s*:([^;]+)/)?style.match(/transform\s*:([^;]+)/)[1]:"";

            transfo.settings={};

            transfo.settings.angle=     transform.indexOf('rotate')!=-1?parseFloat(transform.match(/rotate\(([^)]+)deg\)/)[1]):0;
            transfo.settings.scalex=    transform.indexOf('scaleX')!=-1?parseFloat(transform.match(/scaleX\(([^)]+)\)/)[1]):1;
            transfo.settings.scaley=    transform.indexOf('scaleY')!=-1?parseFloat(transform.match(/scaleY\(([^)]+)\)/)[1]):1;

            transfo.settings.style=style.replace(/[^;]*transform[^;]+/g,'').replace(/;+/g,';');

            $this.attr("style",transfo.settings.style);
            _stop_animation($this[0]);
            transfo.settings.pos=$this.offset();

            transfo.settings.height=$this.innerHeight();
            transfo.settings.width=$this.innerWidth();

            vartranslatex=transform.match(/translateX\(([0-9.-]+)(%|px)\)/);
            vartranslatey=transform.match(/translateY\(([0-9.-]+)(%|px)\)/);
            transfo.settings.translate="%";

            if(translatex&&translatex[2]==="%"){
                transfo.settings.translatexp=parseFloat(translatex[1]);
                transfo.settings.translatex=transfo.settings.translatexp/100*transfo.settings.width;
            }else{
                transfo.settings.translatex=translatex?parseFloat(translatex[1]):0;
            }
            if(translatey&&translatey[2]==="%"){
                transfo.settings.translateyp=parseFloat(translatey[1]);
                transfo.settings.translatey=transfo.settings.translateyp/100*transfo.settings.height;
            }else{
                transfo.settings.translatey=translatey?parseFloat(translatey[1]):0;
            }

            transfo.settings.css=window.getComputedStyle($this[0],null);

            transfo.settings.rotationStep=5;
            transfo.settings.hide=false;
            transfo.settings.callback=function(){};
        }

        function_bind($this,transfo){
            functionmousedown(event){
                _mouseDown($this,this,transfo,event);
                $(document).on("mousemove",mousemove).on("mouseup",mouseup);
            }
            functionmousemove(event){
                _mouseMove($this,this,transfo,event);
            }
            functionmouseup(event){
                _mouseUp($this,this,transfo,event);
                $(document).off("mousemove",mousemove).off("mouseup",mouseup);
            }

            transfo.$markup.off().on("mousedown",mousedown);
            transfo.$markup.find(".transfo-controls>:not(.transfo-scaler-mc)").off().on("mousedown",mousedown);
        }

        function_mouseDown($this,div,transfo,event){
            event.preventDefault();
            if(transfo.active||event.which!==1)return;

            vartype="position",$e=$(div);
            if($e.hasClass("transfo-rotator"))type="rotator";
            elseif($e.hasClass("transfo-scaler-tl"))type="tl";
            elseif($e.hasClass("transfo-scaler-tr"))type="tr";
            elseif($e.hasClass("transfo-scaler-br"))type="br";
            elseif($e.hasClass("transfo-scaler-bl"))type="bl";
            elseif($e.hasClass("transfo-scaler-tc"))type="tc";
            elseif($e.hasClass("transfo-scaler-bc"))type="bc";
            elseif($e.hasClass("transfo-scaler-ml"))type="ml";
            elseif($e.hasClass("transfo-scaler-mr"))type="mr";

            transfo.active={
                "type":type,
                "scalex":transfo.settings.scalex,
                "scaley":transfo.settings.scaley,
                "pageX":event.pageX,
                "pageY":event.pageY,
                "center":transfo.$center.offset(),
            };
        }
        function_mouseUp($this,div,transfo,event){
            transfo.active=null;
        }

        function_mouseMove($this,div,transfo,event){
            event.preventDefault();
            if(!transfo.active)return;
            varsettings=transfo.settings;
            varcenter=transfo.active.center;
            varcdx=center.left-event.pageX;
            varcdy=center.top-event.pageY;

            if(transfo.active.type=="rotator"){
                varang,dang=Math.atan((settings.width*settings.scalex)/(settings.height*settings.scaley))/rad;

                if(cdy)ang=Math.atan(-cdx/cdy)/rad;
                elseang=0;
                if(event.pageY>=center.top&&event.pageX>=center.left)ang+=180;
                elseif(event.pageY>=center.top&&event.pageX<center.left)ang+=180;
                elseif(event.pageY<center.top&&event.pageX<center.left)ang+=360;
                
                ang-=dang;
                if(settings.scaley<0&&settings.scalex<0)ang+=180;

                if(!event.ctrlKey){
                    settings.angle=Math.round(ang/transfo.settings.rotationStep)*transfo.settings.rotationStep;
                }else{
                    settings.angle=ang;
                }

                //resetposition:don'tmovecenter
                _targetCss($this,transfo);
                varnew_center=transfo.$center.offset();
                varx=center.left-new_center.left;
                vary=center.top-new_center.top;
                varangle=ang*rad;
                settings.translatex+=x*Math.cos(angle)-y*Math.sin(-angle);
                settings.translatey+=-x*Math.sin(angle)+y*Math.cos(-angle);
            }
            elseif(transfo.active.type=="position"){
                varangle=settings.angle*rad;
                varx=event.pageX-transfo.active.pageX;
                vary=event.pageY-transfo.active.pageY;
                transfo.active.pageX=event.pageX;
                transfo.active.pageY=event.pageY;
                vardx=x*Math.cos(angle)-y*Math.sin(-angle);
                vardy=-x*Math.sin(angle)+y*Math.cos(-angle);

                settings.translatex+=dx;
                settings.translatey+=dy;
            }
            elseif(transfo.active.type.length===2){
                varangle=settings.angle*rad;
                vardx=  cdx*Math.cos(angle)-cdy*Math.sin(-angle);
                vardy=-cdx*Math.sin(angle)+cdy*Math.cos(-angle);
                if(transfo.active.type.indexOf("t")!=-1){
                    settings.scaley=dy/(settings.height/2);
                }
                if(transfo.active.type.indexOf("b")!=-1){
                    settings.scaley=-dy/(settings.height/2);
                }
                if(transfo.active.type.indexOf("l")!=-1){
                    settings.scalex=dx/(settings.width/2);
                }
                if(transfo.active.type.indexOf("r")!=-1){
                    settings.scalex=-dx/(settings.width/2);
                }
                if(settings.scaley>0&&settings.scaley<0.05)settings.scaley=0.05;
                if(settings.scalex>0&&settings.scalex<0.05)settings.scalex=0.05;
                if(settings.scaley<0&&settings.scaley>-0.05)settings.scaley=-0.05;
                if(settings.scalex<0&&settings.scalex>-0.05)settings.scalex=-0.05;

                if(event.shiftKey&&
                    (transfo.active.type==="tl"||transfo.active.type==="bl"||
                     transfo.active.type==="tr"||transfo.active.type==="br")){
                    settings.scaley=settings.scalex;
                }
            }

            settings.angle=Math.round(settings.angle);
            settings.translatex=Math.round(settings.translatex);
            settings.translatey=Math.round(settings.translatey);
            settings.scalex=Math.round(settings.scalex*100)/100;
            settings.scaley=Math.round(settings.scaley*100)/100;

            _targetCss($this,transfo);
            _stop_animation($this[0]);
            returnfalse;
        }

        function_setCss($this,css,settings){
            vartransform="";
            vartrans=false;
            if(settings.angle!==0){
                trans=true;
                transform+="rotate("+settings.angle+"deg)";
            }
            if(settings.translatex){
                trans=true;
                transform+="translateX("+(settings.translate==="%"?settings.translatexp+"%":settings.translatex+"px")+")";
            }
            if(settings.translatey){
                trans=true;
                transform+="translateY("+(settings.translate==="%"?settings.translateyp+"%":settings.translatey+"px")+")";
            }
            if(settings.scalex!=1){
                trans=true;
                transform+="scaleX("+settings.scalex+")";
            }
            if(settings.scaley!=1){
                trans=true;
                transform+="scaleY("+settings.scaley+")";
            }

            if(trans){
                css+=";"
                        /*Safari*/
                css+="-webkit-transform:"+transform+";"
                        /*Firefox*/
                    +"-moz-transform:"+transform+";"
                        /*IE*/
                    +"-ms-transform:"+transform+";"
                        /*Opera*/
                    +"-o-transform:"+transform+";"
                        /*Other*/
                    +"transform:"+transform+";";
            }

            css=css.replace(/(\s*;)+/g,';').replace(/^\s*;|;\s*$/g,'');

            $this.attr("style",css);
        }

        function_targetCss($this,transfo){
            varsettings=transfo.settings;
            varwidth=parseFloat(settings.css.width);
            varheight=parseFloat(settings.css.height);
            settings.translatexp=Math.round(settings.translatex/width*1000)/10;
            settings.translateyp=Math.round(settings.translatey/height*1000)/10;

            _setCss($this,settings.style,settings);

            transfo.$markup.css({
                "position":"absolute",
                "width":width+"px",
                "height":height+"px",
                "top":settings.pos.top+"px",
                "left":settings.pos.left+"px"
            });

            var$controls=transfo.$markup.find('.transfo-controls');
            _setCss($controls,
                "width:"+width+"px;"+
                "height:"+height+"px;"+
                "cursor:move;",
                settings);

            $controls.children().css("transform","scaleX("+(1/settings.scalex)+")scaleY("+(1/settings.scaley)+")");

            _showHide($this,transfo);

            transfo.settings.callback.call($this[0],$this);
        }

        function_showHide($this,transfo){
            transfo.$markup.css("z-index",transfo.settings.hide?-1:1000);
            if(transfo.settings.hide){
                transfo.$markup.find(".transfo-controls>*").hide();
                transfo.$markup.find(".transfo-scaler-mc").show();
            }else{
                transfo.$markup.find(".transfo-controls>*").show();
            }
        }

        function_destroy($this){
            $this.data('transfo').$markup.remove();
            $this.removeData('transfo');
        }

        function_reset($this){
            vartransfo=$this.data('transfo');
            _destroy($this);
            $this.transfo(transfo.settings);
        }

})(jQuery);
