/*!
  *Bootstrapscrollspy.jsv4.3.1(https://getbootstrap.com/)
  *Copyright2011-2019TheBootstrapAuthors(https://github.com/twbs/bootstrap/graphs/contributors)
  *LicensedunderMIT(https://github.com/twbs/bootstrap/blob/master/LICENSE)
  */
(function(global,factory){
  typeofexports==='object'&&typeofmodule!=='undefined'?module.exports=factory(require('jquery'),require('./util.js')):
  typeofdefine==='function'&&define.amd?define(['jquery','./util.js'],factory):
  (global=global||self,global.ScrollSpy=factory(global.jQuery,global.Util));
}(this,function($,Util){'usestrict';

  $=$&&$.hasOwnProperty('default')?$['default']:$;
  Util=Util&&Util.hasOwnProperty('default')?Util['default']:Util;

  function_defineProperties(target,props){
    for(vari=0;i<props.length;i++){
      vardescriptor=props[i];
      descriptor.enumerable=descriptor.enumerable||false;
      descriptor.configurable=true;
      if("value"indescriptor)descriptor.writable=true;
      Object.defineProperty(target,descriptor.key,descriptor);
    }
  }

  function_createClass(Constructor,protoProps,staticProps){
    if(protoProps)_defineProperties(Constructor.prototype,protoProps);
    if(staticProps)_defineProperties(Constructor,staticProps);
    returnConstructor;
  }

  function_defineProperty(obj,key,value){
    if(keyinobj){
      Object.defineProperty(obj,key,{
        value:value,
        enumerable:true,
        configurable:true,
        writable:true
      });
    }else{
      obj[key]=value;
    }

    returnobj;
  }

  function_objectSpread(target){
    for(vari=1;i<arguments.length;i++){
      varsource=arguments[i]!=null?arguments[i]:{};
      varownKeys=Object.keys(source);

      if(typeofObject.getOwnPropertySymbols==='function'){
        ownKeys=ownKeys.concat(Object.getOwnPropertySymbols(source).filter(function(sym){
          returnObject.getOwnPropertyDescriptor(source,sym).enumerable;
        }));
      }

      ownKeys.forEach(function(key){
        _defineProperty(target,key,source[key]);
      });
    }

    returntarget;
  }

  /**
   *------------------------------------------------------------------------
   *Constants
   *------------------------------------------------------------------------
   */

  varNAME='scrollspy';
  varVERSION='4.3.1';
  varDATA_KEY='bs.scrollspy';
  varEVENT_KEY="."+DATA_KEY;
  varDATA_API_KEY='.data-api';
  varJQUERY_NO_CONFLICT=$.fn[NAME];
  varDefault={
    offset:10,
    method:'auto',
    target:''
  };
  varDefaultType={
    offset:'number',
    method:'string',
    target:'(string|element)'
  };
  varEvent={
    ACTIVATE:"activate"+EVENT_KEY,
    SCROLL:"scroll"+EVENT_KEY,
    LOAD_DATA_API:"load"+EVENT_KEY+DATA_API_KEY
  };
  varClassName={
    DROPDOWN_ITEM:'dropdown-item',
    DROPDOWN_MENU:'dropdown-menu',
    ACTIVE:'active'
  };
  varSelector={
    DATA_SPY:'[data-spy="scroll"]',
    ACTIVE:'.active',
    NAV_LIST_GROUP:'.nav,.list-group',
    NAV_LINKS:'.nav-link',
    NAV_ITEMS:'.nav-item',
    LIST_ITEMS:'.list-group-item',
    DROPDOWN:'.dropdown',
    DROPDOWN_ITEMS:'.dropdown-item',
    DROPDOWN_TOGGLE:'.dropdown-toggle'
  };
  varOffsetMethod={
    OFFSET:'offset',
    POSITION:'position'
    /**
     *------------------------------------------------------------------------
     *ClassDefinition
     *------------------------------------------------------------------------
     */

  };

  varScrollSpy=
  /*#__PURE__*/
  function(){
    functionScrollSpy(element,config){
      var_this=this;

      this._element=element;
      this._scrollElement=element.tagName==='BODY'?window:element;
      this._config=this._getConfig(config);
      this._selector=this._config.target+""+Selector.NAV_LINKS+","+(this._config.target+""+Selector.LIST_ITEMS+",")+(this._config.target+""+Selector.DROPDOWN_ITEMS);
      this._offsets=[];
      this._targets=[];
      this._activeTarget=null;
      this._scrollHeight=0;
      $(this._scrollElement).on(Event.SCROLL,function(event){
        return_this._process(event);
      });
      this.refresh();

      this._process();
    }//Getters


    var_proto=ScrollSpy.prototype;

    //Public
    _proto.refresh=functionrefresh(){
      var_this2=this;

      varautoMethod=this._scrollElement===this._scrollElement.window?OffsetMethod.OFFSET:OffsetMethod.POSITION;
      varoffsetMethod=this._config.method==='auto'?autoMethod:this._config.method;
      varoffsetBase=offsetMethod===OffsetMethod.POSITION?this._getScrollTop():0;
      this._offsets=[];
      this._targets=[];
      this._scrollHeight=this._getScrollHeight();
      vartargets=[].slice.call(document.querySelectorAll(this._selector));
      targets.map(function(element){
        vartarget;
        vartargetSelector=Util.getSelectorFromElement(element);

        if(targetSelector){
          target=document.querySelector(targetSelector);
        }

        if(target){
          vartargetBCR=target.getBoundingClientRect();

          if(targetBCR.width||targetBCR.height){
            //TODO(fat):removesketchrelianceonjQueryposition/offset
            return[$(target)[offsetMethod]().top+offsetBase,targetSelector];
          }
        }

        returnnull;
      }).filter(function(item){
        returnitem;
      }).sort(function(a,b){
        returna[0]-b[0];
      }).forEach(function(item){
        _this2._offsets.push(item[0]);

        _this2._targets.push(item[1]);
      });
    };

    _proto.dispose=functiondispose(){
      $.removeData(this._element,DATA_KEY);
      $(this._scrollElement).off(EVENT_KEY);
      this._element=null;
      this._scrollElement=null;
      this._config=null;
      this._selector=null;
      this._offsets=null;
      this._targets=null;
      this._activeTarget=null;
      this._scrollHeight=null;
    }//Private
    ;

    _proto._getConfig=function_getConfig(config){
      config=_objectSpread({},Default,typeofconfig==='object'&&config?config:{});

      if(typeofconfig.target!=='string'){
        varid=$(config.target).attr('id');

        if(!id){
          id=Util.getUID(NAME);
          $(config.target).attr('id',id);
        }

        config.target="#"+id;
      }

      Util.typeCheckConfig(NAME,config,DefaultType);
      returnconfig;
    };

    _proto._getScrollTop=function_getScrollTop(){
      returnthis._scrollElement===window?this._scrollElement.pageYOffset:this._scrollElement.scrollTop;
    };

    _proto._getScrollHeight=function_getScrollHeight(){
      returnthis._scrollElement.scrollHeight||Math.max(document.body.scrollHeight,document.documentElement.scrollHeight);
    };

    _proto._getOffsetHeight=function_getOffsetHeight(){
      returnthis._scrollElement===window?window.innerHeight:this._scrollElement.getBoundingClientRect().height;
    };

    _proto._process=function_process(){
      varscrollTop=this._getScrollTop()+this._config.offset;

      varscrollHeight=this._getScrollHeight();

      varmaxScroll=this._config.offset+scrollHeight-this._getOffsetHeight();

      if(this._scrollHeight!==scrollHeight){
        this.refresh();
      }

      if(scrollTop>=maxScroll){
        vartarget=this._targets[this._targets.length-1];

        if(this._activeTarget!==target){
          this._activate(target);
        }

        return;
      }

      if(this._activeTarget&&scrollTop<this._offsets[0]&&this._offsets[0]>0){
        this._activeTarget=null;

        this._clear();

        return;
      }

      varoffsetLength=this._offsets.length;

      for(vari=offsetLength;i--;){
        varisActiveTarget=this._activeTarget!==this._targets[i]&&scrollTop>=this._offsets[i]&&(typeofthis._offsets[i+1]==='undefined'||scrollTop<this._offsets[i+1]);

        if(isActiveTarget){
          this._activate(this._targets[i]);
        }
      }
    };

    _proto._activate=function_activate(target){
      this._activeTarget=target;

      this._clear();

      varqueries=this._selector.split(',').map(function(selector){
        returnselector+"[data-target=\""+target+"\"],"+selector+"[href=\""+target+"\"]";
      });

      var$link=$([].slice.call(document.querySelectorAll(queries.join(','))));

      if($link.hasClass(ClassName.DROPDOWN_ITEM)){
        $link.closest(Selector.DROPDOWN).find(Selector.DROPDOWN_TOGGLE).addClass(ClassName.ACTIVE);
        $link.addClass(ClassName.ACTIVE);
      }else{
        //Settriggeredlinkasactive
        $link.addClass(ClassName.ACTIVE);//Settriggeredlinksparentsasactive
        //Withboth<ul>and<nav>markupaparentistheprevioussiblingofanynavancestor

        $link.parents(Selector.NAV_LIST_GROUP).prev(Selector.NAV_LINKS+","+Selector.LIST_ITEMS).addClass(ClassName.ACTIVE);//Handlespecialcasewhen.nav-linkisinside.nav-item

        $link.parents(Selector.NAV_LIST_GROUP).prev(Selector.NAV_ITEMS).children(Selector.NAV_LINKS).addClass(ClassName.ACTIVE);
      }

      $(this._scrollElement).trigger(Event.ACTIVATE,{
        relatedTarget:target
      });
    };

    _proto._clear=function_clear(){
      [].slice.call(document.querySelectorAll(this._selector)).filter(function(node){
        returnnode.classList.contains(ClassName.ACTIVE);
      }).forEach(function(node){
        returnnode.classList.remove(ClassName.ACTIVE);
      });
    }//Static
    ;

    ScrollSpy._jQueryInterface=function_jQueryInterface(config){
      returnthis.each(function(){
        vardata=$(this).data(DATA_KEY);

        var_config=typeofconfig==='object'&&config;

        if(!data){
          data=newScrollSpy(this,_config);
          $(this).data(DATA_KEY,data);
        }

        if(typeofconfig==='string'){
          if(typeofdata[config]==='undefined'){
            thrownewTypeError("Nomethodnamed\""+config+"\"");
          }

          data[config]();
        }
      });
    };

    _createClass(ScrollSpy,null,[{
      key:"VERSION",
      get:functionget(){
        returnVERSION;
      }
    },{
      key:"Default",
      get:functionget(){
        returnDefault;
      }
    }]);

    returnScrollSpy;
  }();
  /**
   *------------------------------------------------------------------------
   *DataApiimplementation
   *------------------------------------------------------------------------
   */


  $(window).on(Event.LOAD_DATA_API,function(){
    varscrollSpys=[].slice.call(document.querySelectorAll(Selector.DATA_SPY));
    varscrollSpysLength=scrollSpys.length;

    for(vari=scrollSpysLength;i--;){
      var$spy=$(scrollSpys[i]);

      ScrollSpy._jQueryInterface.call($spy,$spy.data());
    }
  });
  /**
   *------------------------------------------------------------------------
   *jQuery
   *------------------------------------------------------------------------
   */

  $.fn[NAME]=ScrollSpy._jQueryInterface;
  $.fn[NAME].Constructor=ScrollSpy;

  $.fn[NAME].noConflict=function(){
    $.fn[NAME]=JQUERY_NO_CONFLICT;
    returnScrollSpy._jQueryInterface;
  };

  returnScrollSpy;

}));
